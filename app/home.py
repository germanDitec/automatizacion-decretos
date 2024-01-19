from flask import (Blueprint, render_template, request, flash, send_file,
                   redirect, url_for, Response, g, send_from_directory, session, current_app, abort)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import concurrent.futures
import os
import json
import mammoth
from app.auth import login_required

from app.data_handling.data_extracting import (extract_table_from_pdf, extract_paragraph_after_keyword, extract_num_decreto, extract_id_decreto,
                                               extract_paragraphs_containing_keyword, replace_word_in_paragraph, extract_line_below_propuesta_publica, add_indented_paragraph, extract_date_from_keyword,
                                               extract_date_below_keyword, extract_date_from_last_page, extract_last_page, obtener_direccion, obtener_propuesta)

from app.data_handling.data_managing import (get_rechazados_text, get_inadmisibles_text, add_inadmisibles_decreto, add_no_inadmisible_decreto,
                                             add_inadmisibles_no_rechazados, add_noadm_norec, add_decretos_lineas, add_decretos, formate_date_text, informe_to_sharepoint, decreto_to_sharepoint)

from app.data_handling.data_writing import generate_word_document, add_table_to_word_document


from openai import OpenAI
import json


bp = Blueprint('home', __name__, url_prefix="/")

SESSION_TYPE = 'filesystem'
ALLOWED_EXTENSIONS = {'pdf'}
# CUENTA SHAREPOINT, DEBE IR EN VARIABLES DE SESIÓN
username = 'german.astudillo@maipu.cl'
password = 'G.ast023#'
server_url = "https://immaipu.sharepoint.com/"
site_url = server_url + "sites/Generadordedecretos"

client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
)

image_path = os.path.join(os.path.dirname(
    __file__), "media/encabezado_decretos.png")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == 'POST' and 'file' in request.files:
        idp = request.form.get('idp')
        titulo = request.form.get('titulo')
        cdp = request.form.get('cdp')
        datecdp = request.form.get('datecdp')
        cuenta = request.form.get('cuenta')
        datecompra = request.form.get('datecompra')
        direccion = request.form.get('direccion')
        concejo = request.form.get('concejo')
        acuerdo = request.form.get('acuerdo')
        sesion = request.form.get('sesion')
        datesesion = request.form.get('datesesion')
        secretaria = request.form.get('secretaria')

        propuesta = request.form.get('propuesta')
        tipo_compra = request.form.get('compra')

        if concejo != 'on':
            acuerdo = None
            sesion = None
            datesesion = None
            secretaria = None

        error = None

        if not all([cdp, datecdp, datecompra, direccion]):
            error = "Por favor, rellena todos los campos."
            return render_template("home/index.html")

        valor_direccion = obtener_direccion(direccion)
        if direccion == "0":
            error = "Por favor, rellena todos los campos."

        if propuesta == "0":
            error = "Por favor, rellena todos los campos."

        pdf_file = request.files['file']
        if pdf_file and allowed_file(pdf_file.filename):
            filename = secure_filename(pdf_file.filename)
            upload_folder = 'app/static/documents_folder'
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            pdf_file.save(file_path)
            informe_to_sharepoint(server_url, username,
                                  password, site_url, file_path, filename)
            session['process_ejected'] = False
            return redirect(url_for('home.generate_word', filename=filename, idp=idp, cdp=cdp, datecdp=datecdp, datecompra=datecompra,
                                    direccion=valor_direccion, concejo=concejo, acuerdo=acuerdo, sesion=sesion, datesesion=datesesion,
                                    secretaria=secretaria, cuenta=cuenta, propuesta=propuesta, tipo_compra=tipo_compra, titulo=titulo))
        else:
            error = "El documento debe tener un formato PDF"

        flash(error, 'error')
    return render_template("home/index.html")


def get_rechazados(pdf_path):
    try:
        input_promt = """Verifica si hay proponentes que fuéron rechazados, y si es así retornalos en formato JSON y hazlo con la siguiente estructura: 
            rechazados: [
            nombre: nombre empresa, 
            RUT: rut empresa, 
            motivo: motivo de rechazo ]
            Y el caso de que no haya ningún proponente rechazado, retorna este json vacio:
                rechazados:[] 
            Solo quiero el JSON, no incluyas texto adicional, haz esto en base a este texto. {}"""

        paragraphs_propmt = input_promt.format(extract_paragraphs_containing_keyword(
            pdf_path, "OBSERVACIONES DEL ACTO DE APERTURA"))
        rechazados_prompt = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Quiero que analices la información que te estoy pasando y quiero que me retornes lo que te pido, solo lo que te pido, sin añadir texto adicional. El contexto del texto es sobre una comisión evaluadora."},
                {"role": "user", "content": paragraphs_propmt}
            ]
        )
        data = rechazados_prompt.choices[0].message.content
        datos = json.loads(data)
        rechazados = datos.get("rechazados", [])
        print("rechazados:", rechazados)
        return rechazados

    except:
        return []


def get_inadmisibles(pdf_path):
    try:
        input_promt = """Verifica si en el parrafo de 'ADMISIBILIDAD' hay algún proponente que es inadmisible, y si es así retornalos en formato JSON y hazlo con la siguiente estructura: 
            inadmisibles: [
            nombre: nombre empresa, 
            RUT: rut empresa
            ]

            Y el caso de que no haya ningún proponente rechazado, retorna este json vacio:
                inadmisibles:[] 
            Solo quiero el JSON, no incluyas texto adicional, haz esto en base a este texto y los parrafos que no comiencen con '•' ignoralos. {}"""

        paragraphs_propmt = input_promt.format(extract_paragraphs_containing_keyword(
            pdf_path, "ADMISIBILIDAD"))
        rechazados_prompt = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Quiero que analices la información que te estoy pasando y quiero que me retornes lo que te pido, solo lo que te pido, sin añadir texto adicional. El contexto del texto es sobre una comisión evaluadora."},
                {"role": "user", "content": paragraphs_propmt}
            ]
        )
        data = rechazados_prompt.choices[0].message.content
        datos = json.loads(data)
        inadmisibles = datos.get("inadmisibles", [])
        print("inadmisibles:", inadmisibles)
        return inadmisibles

    except:
        return []


def get_evaluacion(pdf_path):
    try:
        evaluacion_input = "Quiero que hagas un resumen de los proponentes desde el parrafo de 'ADMISIBILIDAD',  redacta el resumen sin especificar que es lo que te pedí ni tampoco mencionando el parrafo 8.1. También quiero que me listes con viñetas el resumen, recuerda retornar en texto sin formato, haz esto en base a este texto: {}"
        evaluacion_page = evaluacion_input.format(
            extract_paragraphs_containing_keyword(pdf_path, "ADMISIBILIDAD"))

        evaluacion_prompt = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "Quiero que analices el texto que solicito y me retornes lo que te pido, el contexto del texto es sobre una comisión evaluadora que ha realizado un informe. Esto ya pasó entonces escribe en tiempo pasado, no quiero que agregues porcentajes y utiliza un lenguaje muy formal"},
                {"role": "user", "content": evaluacion_page}
            ]
        )

        data_evaluacion = evaluacion_prompt.choices[0].message.content
        print("PROMPT EVALUACIÓN: ", evaluacion_page)
        return data_evaluacion

    except Exception as e:
        return f"No se pudo realizar la evaluación: {e}"


def get_datos_adjudicacion(pdf_path):
    try:
        adjudicacion = """Quiero que me retornes nombre, RUT y monto total de la o las empresas que hayan sido nombradas. Esto en formato JSON, extrae la información desde el párrafo de 'PROPOSICIÓN DE ADJUDICACIÓN'. Retorna solo el JSON con la siguiente estructura. 
        En el caso de que existan más lineas en el parrafo de 'PROPOSICIÓN DE ADJUDICACION', retorna con el siguiente formato:
            empresas: [
            nombre: nombre empresa, 
            RUT: rut empresa,
            linea: linea,
            total: total,
            plazo: plazo
            ]
            Y en el caso de que exista solamente una empresa retorna con el siguiente formato: 
            empresas: [
            nombre: nombre empresa,
            RUT: rut empresa,
            total: total,
            plazo: plazo
            ]
            Esto en base a todo este texto, toma en cuenta solamente el parrafo de la 'PROPOSICIÓN DE ADJUDICACION', lo demás ignoralo. {}
            """
        adjudicacion_page = adjudicacion.format(extract_last_page(pdf_path))
        print("adjudicacion_page:", adjudicacion_page)
        adjudicacion_prompt = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Quiero que analices el texto que te estoy entregando y me retornes un JSON, solo con lo que te pido, sin añadir texto adicional. El contexto del texto es sobre una comisión evaluadora."},
                {"role": "user", "content": adjudicacion_page}
            ]
        )

        data_adjudicacion = adjudicacion_prompt.choices[0].message.content
        data = json.loads(data_adjudicacion)
        empresas = data.get("empresas", [])
        print("empresas: ", empresas)
        return empresas

    except Exception as e:
        return []


def get_desiertas(pdf_path):
    try:
        input_promt = """{}
        Analiza el texto y retorna un JSON que contiene las líneas desiertas, representadas por el formato: {"desiertas": []}, donde se listarán los números de línea que no tienen ofertas o adjudicaciones.
        Y el caso de que no haya ninguna linea desierta, retorna este json vacio:
                linea:[
                    numero: numero linea,
                    razón: razon de porque está desierta
                ]
        Solo quiero el JSON, no incluyas texto adicional, haz esto en base al texto que te estoy proporcionando toma en cuenta solamente el parrafo de 'PROPOSICIÓN DE ADJUDICACIÓN'"""

        paragraphs_propmt = input_promt.format(extract_last_page(pdf_path))

        rechazados_prompt = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Quiero que analices la información que te estoy pasando y quiero que me retornes la información en formato JSON."},
                {"role": "user", "content": paragraphs_propmt}
            ]
        )
        print(paragraphs_propmt)
        data = rechazados_prompt.choices[0].message.content
        datos = json.loads(data)
        desiertas = datos.get("desiertas", [])
        print("=========================================")
        print("desiertas:", desiertas)
        print("=========================================\n")
        return desiertas

    except:
        return []


# CONCURRENCY FUNCTIONS
functions_list = [get_rechazados, get_inadmisibles,
                  get_evaluacion, get_datos_adjudicacion, get_desiertas]


@bp.route("/generate/<filename>", methods=['GET'])
@login_required
def generate_word(filename):
    if filename.endswith(".pdf"):
        try:
            regenerate = request.args.get('regenerate', 'false')
            if regenerate.lower() == 'true':
                session['process_ejected'] = False

            doc = Document()
            pdf_path = os.path.join('app/static/documents_folder', filename)
            cdp = request.args.get('cdp')
            cuenta = request.args.get('cuenta')
            concejo = request.args.get("concejo")
            acuerdo = request.args.get('acuerdo')
            sesion = request.args.get('sesion')
            datesesion = request.args.get('datesesion')
            if datesesion is not None:
                datesesion_str = formate_date_text(datesesion)
            secretaria = request.args.get('secretaria')
            datecdp = request.args.get('datecdp')
            datecompra = request.args.get('datecompra')
            datecdp_str = formate_date_text(datecdp)
            datecompra_str = formate_date_text(datecompra)
            direccion = request.args.get('direccion')
            n_decreto = extract_num_decreto(pdf_path)
            idp = request.args.get('idp')
            titulo = request.args.get('titulo')
            titulo = titulo.upper()
            propuesta = request.args.get('propuesta')
            valor_propuesta = obtener_propuesta(propuesta)
            tipo_compra = request.args.get('tipo_compra')
            fecha_apertura = extract_date_from_keyword(
                pdf_path, "El Acto de Apertura")
            fecha_informe = extract_date_from_last_page(pdf_path)
            fecha_decreto = extract_date_from_keyword(
                pdf_path, "Decreto Alcaldicio")
            fecha_comision = extract_date_below_keyword(
                pdf_path, "CONSTITUCIÓN Y SESIONES DE LA COMISIÓN EVALUADORA")
            modified_paragraph = f"el Decreto Alcaldicio N° {n_decreto} de fecha {fecha_decreto}, que aprueba las Bases Administrativas, Bases Técnicas, Anexos y demás antecedentes de la licitación;"

            primer_parrafo = f"La propuesta Pública con ID {idp} denominada \"{titulo}\" {modified_paragraph}  El Acto de Apertura de Ofertas, de fecha {fecha_apertura}; el Informe de Evaluación de la comisión evaluadora, de fecha {fecha_comision}; el Certificado de Factibilidad N° {cdp}, de fecha {datecdp_str}; el Acta de Proclamación de Alcalde y Concejales de la comuna de Maipú, de fecha 22 de junio de 2021, del Primer Tribunal Electoral Región Metropolitana, que proclamó como alcalde de la comuna de Maipú, al don TOMÁS VODANOVIC ESCUDERO; el Decreto Alcaldicio N°1656 DAP, de fecha 17 de junio del 2020, que designa como Secretario Municipal a don RICARDO HENRIQUEZ VALDÉS; la Ley N°19.886 de Bases sobre Contratos Administrativos de Suministro y Prestación de Servicios y su respectivo Reglamento, el cual fue aprobado mediante Decreto Supremo N° 250, del año 2004, del Ministerio de Hacienda y sus modificaciones; y las facultades conferidas en el articulo 63 del D.F.L.N°1, del año 2006, del Ministerio del Interior, que fijo el texto refundido, coordinado y sistematizado de la Ley N°18.695, Organica Constitucional de Municipalidades."

            considerando_primer = f"1.- Que, con fecha {datecompra_str}, se publicó en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), la propuesta pública {idp}, denominada {titulo}, según Bases administrativas y Técnicas, aprobadas por Decreto Alcaldicio N°{n_decreto} de fecha {fecha_decreto}"
            considerando_segundo = "2.- Que, en el llamado a licitación los siguientes proponentes presentaron ofertas:"
            considerando_tercer = ""
            considerando_cuarto = ""
            considerando_quinto = ""
            considerando_sexto = ""
            considerando_septimo = None

            if session.get('process_ejected'):
                return render_template('home/process.html', html=session.get('generated_document', ''), filename=filename,
                                       cdp=cdp, datecdp=datecdp, datecompra=datecompra, cuenta=cuenta,
                                       concejo=concejo, acuerdo=acuerdo, sesion=sesion,
                                       datesesion=datesesion, secretaria=secretaria,
                                       direccion=direccion, tipo_compra=tipo_compra,
                                       propuesta=propuesta, idp=idp, titulo=titulo)

            # CONCURRENCY
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(
                    lambda func: func(pdf_path), functions_list))

            rechazados = results[0]
            inadmisibles = results[1]
            data_evaluacion = results[2]
            empresas_adjudicadas = results[3]
            desiertas = results[4]

            fragmento_adjudicadas = []
            posee_linea = False
            for empresa in empresas_adjudicadas:
                nombre_adjudicada = empresa.get("nombre", "")
                rut_adjudicada = empresa.get("RUT", "")
                linea = empresa.get("linea", None)
                total = empresa.get("total", "")
                fragmento_empresas = f"{nombre_adjudicada} RUT {rut_adjudicada}, para la línea {linea}"
                fragmento_adjudicadas.append(fragmento_empresas)
                proponentes_adjudicados = "; ".join(fragmento_adjudicadas)
                if linea is not None:
                    lista_empresa_adjudicada = f"- Del resultado de la evaluación, se establece que la oferta presentada por los proponentes {proponentes_adjudicados} . Se propone sean adjudicadas dado que son las ofertas más convenientes para los intereses municipales."
                    posee_linea = True
                else:
                    lista_empresa_adjudicada = f"- Del resultado de la evaluación, se establece que la oferta presentada por el proponente {nombre_adjudicada}, RUT {rut_adjudicada}. Se propone sea adjudicada dado que es la oferta más conveniente para los intereses muncipales."

            if rechazados:
                considerando_tercer = f"\n3.- Que, en el Acta de Apertura de las ofertas, de fecha {fecha_apertura}, se rechazaron las siguientes ofertas:"
                proponentes_rechazados, motivo_rechazo = get_rechazados_text(
                    rechazados)
                lista_rechazados = f"La de los proponentes {proponentes_rechazados}, por motivo de {motivo_rechazo}."

            else:
                considerando_tercer = "\n3.- Que, en el Acto de Apertura de las ofertas, de fecha {}, no existen ofertas rechazadas.".format(
                    fecha_apertura)
                lista_rechazados = ""

            considerando_cuarto = f"\n4.-Que, de acuerdo con el informe de Evaluación de Ofertas, de fecha {fecha_informe}, la comisión evaluadora propone lo siguiente:"

            if concejo == 'on':
                considerando_quinto = f"\n5.-Que, la propuesta de adjudicación cuenta con el Acuerdo N° {acuerdo}, adoptado en Sesión Ordinaria N° {sesion} de fecha {datesesion_str}, según consta en Certificado N° {secretaria} de Secretaria Municipal, del Honorable Concejo Municipal."
                considerando_sexto = f"\n6.- Que, se cuenta con la disponibilidad presupuestaria para este fin, según da cuenta el Certificado de Factibilidad N° {cdp}, de fecha {datecdp_str}."
                considerando_septimo = f"\n7.- Que, en el Numeral 13 de las Bases Administrativas, establece que la Unidad Técnica responsable de supervisar la ejecución de {valor_propuesta.upper()} será la {direccion}."

            else:
                considerando_quinto = f"\n5.- Que, se cuenta con la disponibilidad presupuestaria para este fin, según da cuenta el Certificado de Factibilidad N° {cdp}, de fecha {datecdp_str}."
                considerando_sexto = f"\n6.- Que, en el Numeral 13 de las Bases Administrativas, establece que la Unidad Técnica responsable de supervisar la ejecución de {valor_propuesta.upper()} será la {direccion}."

            table = extract_table_from_pdf(pdf_path)
            print("Table", table)
            output_file_path = pdf_path.replace(
                ".pdf", "-PLANTILLA_DECRETO.docx")
            header = doc.sections[0].header
            paragraph = header.paragraphs[0]
            logo_run = paragraph.add_run()
            logo_run.add_picture(
                image_path, width=Inches(7), height=Inches(0.5))
            fecha_decreto_alcaldicio = doc.add_paragraph()
            fecha_decreto_alcaldicio_r = fecha_decreto_alcaldicio.add_run(
                "Maipú,"
            )
            fecha_decreto_alcaldicio_r.jc = 'left'
            fecha_decreto_alcaldicio_r.font.size = Pt(10)
            fecha_decreto_alcaldicio_r.bold = True
            titulo_decreto = doc.add_paragraph()
            titulo_decreto_r = titulo_decreto.add_run("DECRETO ALCALDICIO N° ")
            titulo_decreto_r.jc = 'left'
            titulo_decreto_r.font.size = Pt(10)
            titulo_decreto_r.bold = True
            visto_p = doc.add_paragraph()
            visto_r = visto_p.add_run("VISTO:")
            visto_r.bold = True
            doc.add_paragraph(primer_parrafo)
            considerando_p = doc.add_paragraph()
            considerando_r = considerando_p.add_run("CONSIDERANDO:")
            considerando_r.bold = True
            doc.add_paragraph(considerando_primer)
            doc.add_paragraph(considerando_segundo)
            add_table_to_word_document(doc, table)
            doc.add_paragraph(considerando_tercer)
            doc.add_paragraph(lista_rechazados, style="List Bullet")
            doc.add_paragraph(considerando_cuarto)
            doc.add_paragraph(data_evaluacion)
            doc.add_paragraph(lista_empresa_adjudicada)
            doc.add_paragraph(considerando_quinto)
            doc.add_paragraph(considerando_sexto)
            if considerando_septimo is not None:
                doc.add_paragraph(considerando_septimo)
            decreto_p = doc.add_paragraph()
            decreto_r = decreto_p.add_run("DECRETO:")

            decreto_r.bold = True
            if posee_linea:
                print(titulo)
                add_decretos_lineas(doc, idp, titulo, rechazados, inadmisibles,
                                    empresas_adjudicadas, direccion, cuenta, tipo_compra, propuesta, valor_propuesta, desiertas)
            else:
                add_decretos(doc, idp, titulo, rechazados, inadmisibles, direccion, cuenta,
                             tipo_compra, propuesta, valor_propuesta, desiertas, nombre_adjudicada, total, rut_adjudicada)

            doc.save(output_file_path)

            with open(output_file_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
                html = result.value
                session['generated_document'] = html
                session['process_ejected'] = True

            output_filename = filename.replace(
                ".pdf", "-PLANTILLA_DECRETO.docx")

            decreto_to_sharepoint(
                server_url, username, password, site_url, output_file_path, output_filename)

            return render_template('home/process.html', html=html, filename=filename,
                                   cdp=cdp, datecdp=datecdp, datecompra=datecompra,
                                   cuenta=cuenta, concejo=concejo, acuerdo=acuerdo,
                                   sesion=sesion, datesesion=datesesion, secretaria=secretaria,
                                   direccion=direccion, tipo_compra=tipo_compra, propuesta=propuesta, idp=idp, titulo=titulo)
        except HTTPException as e:
            if e.code == 400:
                return render_template('errors/400.html'), 400

        except Exception as e:
            return render_template('errors/error_general.html', error=str(e)), 500


@bp.route("/download/<filename>")
def download_file(filename):
    output_file_path = filename.replace(".pdf", "-PLANTILLA_DECRETO.docx")
    return send_from_directory('static/documents_folder', output_file_path, as_attachment=True)


@bp.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html'), 400
