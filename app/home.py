from flask import (Blueprint, render_template, request, flash, send_file, redirect, url_for, Response, g, send_from_directory, session)
from werkzeug.utils import secure_filename
from docx import Document
from docx.shared import Inches
import os
import json
import base64
import mammoth
from app.auth import login_required

from app.data_handling.data_extracting import (extract_table_from_pdf, extract_paragraph_after_keyword, extract_num_decreto, extract_id_decreto, 
extract_paragraphs_containing_keyword, replace_word_in_paragraph, extract_line_below_propuesta_publica, add_indented_paragraph, extract_date_from_keyword, 
extract_date_below_keyword, extract_date_from_last_page, extract_last_page)

from app.data_handling.data_managing import (get_rechazados_text, get_inadmisibles_text, 
add_inadmisibles_decreto, add_no_inadmisible_decreto, add_inadmisibles_no_rechazados, add_noadm_norec, add_decretos_lineas)

from app.data_handling.data_managing import formate_date_text
from app.data_handling.data_writing import generate_word_document, add_table_to_word_document

import openai
from flask import abort
import json
openai.api_key = "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"



bp = Blueprint('home', __name__, url_prefix= "/")

SESSION_TYPE = 'filesystem'
ALLOWED_EXTENSIONS = {'pdf'}
image_path = os.path.join(os.path.dirname(__file__), "encabezado_decretos.png")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST' and 'file' in request.files:
        cdp = request.form.get('cdp')
        datecdp = request.form.get('datecdp')
        datecompra = request.form.get('datecompra')
        direccion = request.form.get('direccion')
        
        pdf_file = request.files['file']

        if pdf_file and allowed_file(pdf_file.filename):
            filename = secure_filename(pdf_file.filename)
            upload_folder = 'app/static/documents_folder'
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            pdf_file.save(file_path)
            session['process_ejected'] = False

            
            return redirect(url_for('home.generate_word', filename=filename, cdp=cdp, datecdp=datecdp, datecompra=datecompra, direccion=direccion))
    else:
        return render_template("home/index.html")

@bp.route("/prueba/<filename>", methods=['GET'])
def prueba(filename):
    cdp = request.args.get('cdp')
    print(cdp)
    datecdp = request.args.get('datecdp')
    print(datecdp)
    datecompra = request.args.get('datecompra')
    print(datecompra)
    direccion = request.args.get('direccion')
    print(direccion)
    return "lala"


def get_rechazados(pdf_path):
    try:
        input_promt = """Verifica si en los parrafos que comienzan con este caracter '•' hay algún proponente que se rechaza, y si es así retornalos en formato JSON y hazlo con la siguiente estructura: 
            rechazados: [
            nombre: nombre empresa, 
            RUT: rut empresa, 
            motivo: motivo de rechazo ]
            Y el caso de que no haya ningún proponente rechazado, retorna este json vacio:
                rechazados:[] 
            Solo quiero el JSON, no incluyas texto adicional, haz esto en base a este texto y los parrafos que no comiencen con '•' ignoralos. {}"""


        paragraphs_propmt = input_promt.format(extract_paragraphs_containing_keyword(pdf_path, "OBSERVACIONES DEL ACTO DE APERTURA"))
        rechazados_prompt = openai.ChatCompletion.create(
            model= "gpt-4-1106-preview",
            response_format = {"type": "json_object"},
            messages = [
                {"role" : "system", "content": "Quiero que analices la información que te estoy pasando y quiero que me retornes lo que te pido, solo lo que te pido, sin añadir texto adicional. El contexto del texto es sobre una comisión evaluadora."},
                {"role" : "user", "content" : paragraphs_propmt}
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


        paragraphs_propmt = input_promt.format(extract_paragraphs_containing_keyword(pdf_path, "PROCEDIMIENTO DE EVALUACIÓN DE LAS OFERTAS"))
        rechazados_prompt = openai.ChatCompletion.create(
            model= "gpt-4-1106-preview",
            response_format = {"type": "json_object"},
            messages = [
                {"role" : "system", "content": "Quiero que analices la información que te estoy pasando y quiero que me retornes lo que te pido, solo lo que te pido, sin añadir texto adicional. El contexto del texto es sobre una comisión evaluadora."},
                {"role" : "user", "content" : paragraphs_propmt}
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

        evaluacion_input = "Quiero que hagas un extenso resumen SOLO del parrafo de 'ADMISIBILIDAD', lo demás ignoralo, redacta el resumen sin especificar que es lo que te pedí ni tampoco mencionando el parrafo 8.1. También quiero que me listes con viñetas el resumen, recuerda retornar en texto sin formato, haz esto en base a este texto: {}"
        evaluacion_page = evaluacion_input.format(extract_paragraphs_containing_keyword(pdf_path, "PROCEDIMIENTO DE EVALUACIÓN DE LAS OFERTAS"))

        evaluacion_prompt = openai.ChatCompletion.create(
            model= "gpt-4-1106-preview",
            messages = [
                {"role" : "system", "content": "Quiero que analices el texto que solicito y me retornes lo que te pido, el contexto del texto es sobre una comisión evaluadora que ha realizado un informe. No escribas porcentajes y utiliza un lenguaje muy formal"},
                {"role" : "user", "content" : evaluacion_page}
                ]
            )

        data_evaluacion = evaluacion_prompt.choices[0].message.content
        print("data evaluacion: ", data_evaluacion)
        return data_evaluacion
    except: 
        return abort(400)

def get_datos_adjudicacion(pdf_path):
    try:
        adjudicacion = """Quiero que me retornes nombre, RUT y monto total de la o las empresas que hayan sido nombradas en formato JSON, extrae la información desde el párrafo de 'PROPOSICIÓN DE ADJUDICACIÓN'. Retorna solo el JSON con la siguiente estructura: 
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
        adjudicacion_prompt = openai.ChatCompletion.create(
                model= "gpt-4-1106-preview",
                response_format = {"type": "json_object"},
                messages = [
                    {"role" : "system", "content": "Quiero que actues como un asistente y analices el texto que te estoy entregando y me retornes un JSON, solo con lo que te pido, sin añadir texto adicional. El contexto del texto es sobre una comisión evaluadora."},
                    {"role" : "user", "content" : adjudicacion_page}
                ]
            )

        data_adjudicacion = adjudicacion_prompt.choices[0].message.content
        data = json.loads(data_adjudicacion)
        empresas = data.get("empresas", [])
        print("empresas: ", empresas)
        return empresas
    except:
        return abort(400)


@bp.route("/generate/<filename>", methods=['GET'])
def generate_word(filename):
    if filename.endswith(".pdf"):
        try:
            regenerate = request.args.get('regenerate', 'false')
            if regenerate.lower() == 'true':
                session['process_ejected'] = False

            if session.get('process_ejected'):
                return render_template('home/process.html', html=session.get('generated_document', ''), filename=filename, cdp=cdp, datecdp=datecdp, datecompra=datecompra, direccion=direccion)


            doc = Document()
            pdf_path = os.path.join('app/static/documents_folder', filename)
            cdp = request.args.get('cdp')
            datecdp = request.args.get('datecdp')
            datecompra = request.args.get('datecompra')
            datecdp_str = formate_date_text(datecdp)
            datecompra_str = formate_date_text(datecompra)
            direccion = request.args.get('direccion')
            n_decreto = extract_num_decreto(pdf_path)
            id = extract_id_decreto(pdf_path)
            titulo = extract_line_below_propuesta_publica(pdf_path)
            fecha_apertura = extract_date_from_keyword(pdf_path, "El Acto de Apertura")
            fecha_informe = extract_date_from_last_page(pdf_path)
            fecha_decreto = extract_date_from_keyword(pdf_path, "Decreto Alcaldicio")
            fecha_comision = extract_date_below_keyword(pdf_path, "CONSTITUCIÓN Y SESIONES DE LA COMISIÓN EVALUADORA")
            modified_paragraph = f"el Decreto Alcaldicio N° {n_decreto} de fecha {fecha_decreto}, que aprueba las Bases Administrativas, Bases Técnicas, Anexos y demás antecedentes de la licitación;"
            primer_parrafo = f"La propuesta Pública con ID {id} denominada {titulo}  {modified_paragraph}  El Acto de Apertura de Ofertas, de fecha {fecha_apertura}; el Informe de Evaluación de la comisión evaluadora, de fecha {fecha_comision}; el Certificado de Factibilidad N° {cdp}, de fecha {datecdp_str}; el Acta de Proclamación de Alcalde y Concejales de la comuna de Maipú, de fecha 22 de junio de 2021, del Primer Tribunal Electoral Región Metropolitana, que proclamó como alcalde de la comuna de Maipú, al don TOMÁS VODANOVIC ESCUDERO; el Decreto Alcaldicio N°1656 DAP, de fecha 17 de junio del 2020, que designa como Secretario Municipal a don RICARDO HENRIQUEZ VALDÉS; la Ley N°19.886 de Bases sobre Contratos Administrativos de Suministro y Prestación de Servicios y su respectivo Reglamento, el cual fue aprobado mediante Decreto Supremo N° 250, del año 2004, del Ministerio de Hacienda y sus modificaciones; y las facultades conferidas en el articulo 63 del D.F.L.N°1, del año 2006, del Ministerio del Interior, que fijo el texto refundido, coordinado y sistematizado de la Ley N°18.695, Organica Constitucional de Municipalidades."
            considerando_primer = f"1.- Que, con fecha {datecompra_str}, se publicó en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), la propuesta pública {id}, denominada {titulo}, según Bases administrativas y Técnicas, aprobadas por Decreto Alcaldicio N°{n_decreto} de fecha {fecha_decreto}"
            considerando_segundo = "2.- Que, en el llamado a licitación los siguientes proponentes presentaron ofertas:"
            considerando_tercer = ""
            rechazados = get_rechazados(pdf_path)
            inadmisibles = get_inadmisibles(pdf_path)
            data_evaluacion = get_evaluacion(pdf_path)
            empresas_adjudicadas = get_datos_adjudicacion(pdf_path)
            fragmento_adjudicadas = []
            posee_linea = False
            for empresa in empresas_adjudicadas:
                nombre_adjudicada = empresa.get("nombre", "")
                rut_adjudicada = empresa.get("RUT", "")
                linea = empresa.get("linea", None)
                total = empresa.get("total", "")
                plazo = empresa.get("plazo", "")
                fragmento_empresas = f"{nombre_adjudicada} RUT {rut_adjudicada}, {linea}"
                fragmento_adjudicadas.append(fragmento_empresas)
                proponentes_adjudicados = "; ".join(fragmento_adjudicadas)
                if linea is not None:
                    lista_empresa_adjudicada = f"- Del resultado de la evaluación, se establece que la oferta presentada por los proponentes {proponentes_adjudicados} . Son más convenientes para los intereses municipales, por lo que se propone su adjudicación"
                    posee_linea = True
                else:
                    lista_empresa_adjudicada = f"- Del resultado de la evaluación, se establece que la oferta presentada por el proponente {nombre_adjudicada}, RUT {rut_adjudicada}. Es más conveniente para los intereses municipales, por lo que se propone su adjudicación"

            decreto_primero = ""
            decreto_segundo =""
            decreto_tercero =""
            decreto_cuarto = ""
            decreto_quinto =""
            decreto_sexto = None
            decreto_septimo = None
            if rechazados:
                considerando_tercer = f"\n3.- Que, en el Acta de Apertura de las ofertas, de fecha {fecha_apertura}, se rechazaron las siguientes ofertas:"
                proponentes_rechazados, motivo_rechazo = get_rechazados_text(rechazados)
                lista_rechazados = f"La de los proponentes {proponentes_rechazados}, por motivo de {motivo_rechazo}."

                decreto_primero = f"1.- Declárense rechazadas las ofertas de los proponentes {proponentes_rechazados}, según los argumentos señalados en el considerando tercero."
                if inadmisibles:
                    decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto, decreto_sexto, decreto_septimo = add_inadmisibles_decreto(inadmisibles, id, titulo,nombre_adjudicada, rut_adjudicada, total, plazo, direccion)
                else:
                    decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto = add_no_inadmisible_decreto(id, titulo, nombre_adjudicada, rut_adjudicada, total, plazo, direccion)
            else:
                considerando_tercer = "\n3.- Que, en el Acto de Apertura de las ofertas, de fecha {}, no existen ofertas rechazadas.".format(fecha_apertura)
                lista_rechazados = ""
                if inadmisibles:
                    proponentes_inadmisible = get_inadmisibles_text(inadmisibles)
                    decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto, decreto_sexto = add_inadmisibles_no_rechazados(proponentes_inadmisible, id, titulo,nombre_adjudicada, rut_adjudicada, total, plazo, direccion)

            if not rechazados and not inadmisibles:
                decreto_primero, decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto = add_noadm_norec(id, titulo, nombre_adjudicada, rut_adjudicada, total, plazo, direccion)

          
            considerando_cuarto = f"\n4.-Que de acuerdo con el informe de Evaluación de Ofertas, de fecha {fecha_informe}, la comisión evaluadora propone lo siguiente:"
            considerando_quinto = f"\n5.- Que, se cuenta con la disponibilidad presupuestaria para este fin, según da cuenta el Certificado de Factibilidad N° {cdp}, de fecha {datecdp_str}."
            considerando_sexto = f"\n6.- Que, en el Numeral 13 de las Bases Administrativas, establece que la Unidad Técnica responsable de supervisar la ejecución de la ORDEN DE COMPRA / CONTRATO será la Dirección de {direccion} (SIGLA)"
        

            table = extract_table_from_pdf(pdf_path)
            print("Table", table)

            output_file_path = pdf_path.replace(".pdf", "-PLANTILLA_DECRETO.docx")
            header = doc.sections[0].header
        
            paragraph = header.paragraphs[0]
        
            logo_run = paragraph.add_run()
            logo_run.add_picture(image_path, width= Inches(6), height=Inches(0.5))
            visto_p = doc.add_paragraph()
            visto_r = visto_p.add_run("VISTO:")
            visto_r.bold = True
            doc.add_paragraph(primer_parrafo)
            considerando_p = doc.add_paragraph()
            considerando_r = considerando_p.add_run("CONSIDERANDO:")
            considerando_r.bold = True
            doc.add_paragraph(considerando_primer)
            doc.add_paragraph(considerando_segundo)
            #add_table_to_word_document(doc, table)
            doc.add_paragraph(considerando_tercer)
            doc.add_paragraph(lista_rechazados, style="List Bullet")
            doc.add_paragraph(considerando_cuarto)
            doc.add_paragraph(data_evaluacion)
            doc.add_paragraph(lista_empresa_adjudicada)
            doc.add_paragraph(considerando_quinto)
            doc.add_paragraph(considerando_sexto)
            decreto_p = doc.add_paragraph()
            decreto_r = decreto_p.add_run("DECRETO:")

            decreto_r.bold = True
            if posee_linea:
                add_decretos_lineas(doc, id, titulo, rechazados, inadmisibles, empresas_adjudicadas, direccion)
            else:
                doc.add_paragraph(decreto_primero)
                doc.add_paragraph(decreto_segundo)
                doc.add_paragraph(decreto_tercero)
                doc.add_paragraph(decreto_cuarto)
                doc.add_paragraph(decreto_quinto)
                if decreto_sexto:
                    doc.add_paragraph(decreto_sexto)
                if decreto_septimo:
                    doc.add_paragraph(decreto_septimo)

            doc.save(output_file_path)
        
            with open(output_file_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
                html = result.value
                session['generated_document'] = html
                session['process_ejected'] = True 
        
            return render_template('home/process.html', html=html, filename=filename,cdp=cdp,datecdp=datecdp,datecompra=datecompra,direccion=direccion)
        except Exception as e:
                return f"Error inesperado {str(e)}"

@bp.route("/download/<filename>")
def download_file(filename):
    output_file_path = filename.replace(".pdf", "-PLANTILLA_DECRETO.docx")
    return send_from_directory('static/documents_folder', output_file_path, as_attachment=True)

