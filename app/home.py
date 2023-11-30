from flask import (Blueprint, render_template, request, flash, send_file, redirect, url_for, Response, g, abort, send_from_directory)
from docx import Document
from docx.shared import Pt
from docx.shared import Inches
from werkzeug.utils import secure_filename
import os
import re
import PyPDF2
import json
import openai
import pdfplumber
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64
import subprocess
from docxtpl import DocxTemplate
import shutil
import mammoth


bp = Blueprint('home', __name__, url_prefix= "/")

openai.api_key = "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"


SESSION_TYPE = 'filesystem'
ALLOWED_EXTENSIONS = {'pdf'}
image_path = os.path.join(os.path.dirname(__file__), "encabezado_decretos.png")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_paragraph_after_keyword(pdf_file, keyword):
    paragraph = ""
    with open(pdf_file, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            match = re.search(keyword, page_text)
            if match:
                paragraph_match = re.search(r'(?<=\n).*?(?=\n|$)', page_text[match.end():])
                if paragraph_match:
                    paragraph = paragraph_match.group(0)
                    break
    return paragraph.strip()


def extract_num_decreto(pdf_file):
    with open(pdf_file, 'rb') as pdf:
        pdf_reader = PyPDF2.PdfReader(pdf)

        for page in pdf_reader.pages:
            texto = page.extract_text()

            coincidencias = re.findall(r'Nº(\d+)', texto)

            if coincidencias:

                numero = coincidencias[0]
                break

    return numero


def extract_id_decreto(pdf_file):
    texto_despues_de_id = ""
    with open(pdf_file, 'rb') as pdf:
        pdf_reader = PyPDF2.PdfReader(pdf)

        for page in pdf_reader.pages:
            texto = page.extract_text()


            coincidencia = re.search(r'ID:\s*(.+)', texto)


            if coincidencia:
                texto_despues_de_id = coincidencia.group(1).strip()
                print("Texto despues de ID: ", texto_despues_de_id)
                break

    return texto_despues_de_id


def extract_paragraphs_containing_keyword(pdf_file, keyword):
    paragraphs = []
    with open(pdf_file, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            text = text.replace('\n', ' ')  
            while keyword in text:
                start = text.index(keyword)
                end = text.index('\n', start) if '\n' in text[start:] else None
                paragraph = text[start:end].strip()
                paragraphs.append(paragraph)
                text = text[end:] if end else ""
    return paragraphs

def replace_word_in_paragraph(paragraph, old_word, new_word):
    return paragraph.replace(old_word, new_word)


def generate_word_document(output_file, data):
    doc = Document()
    doc.add_paragraph(data)
    doc.save(output_file)


def extract_table_from_pdf(pdf_file):
    table = None  
    
    with pdfplumber.open(pdf_file) as pdf:
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            table = page.extract_table()
            
            if table:
                break  
            
    return table


def add_table_to_word_document(doc, table):
    doc_table = doc.add_table(rows=len(table), cols=len(table[0]) + 1, style='Table Grid')

    for i in range(1, len(table)):
        if doc_table.cell(i, 0):
            doc_table.cell(i, 0).text = f"{i}."
        doc_table.cell(i, 1).text = f"{i + 1}."

    for i, row in enumerate(table):
        rows_count = doc_table.cell(i, 0)
        rows_count.width = Pt(50)
        cell = doc_table.cell(i, 1)  
        cell.width = Pt(500)

    for i, row in enumerate(table):
        for j, cell in enumerate(row):
            if i == 0 and j == 1:
                doc_table.cell(i, 1).text = "Proponente"
                doc_table.cell(i, 1).bold = True

            else:
                doc_table.cell(i, j + 1).text = cell

            if i == 0 and j == 2:
                doc_table.cell(i, 1).text = "RUT"
                doc_table.cell(i, 1).bold = True
            else:
                doc_table.cell(i, j + 1).text = cell

    p = doc_table.cell(0, 0).paragraphs[0]
    r = p.add_run("N°")
    r.bold = True


def extract_line_below_propuesta_publica(pdf_file):
    line = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")
            for i, line_text in enumerate(lines):
                if "PROPUESTA PÚBLICA" in line_text:
                    if i < len(lines) - 1:
                        line = lines[i + 1].strip()
                    break
    return line


def add_indented_paragraph(doc, text, indentation, alignment=WD_PARAGRAPH_ALIGNMENT.LEFT):
    paragraph = doc.add_paragraph()
    paragraph.alignment = alignment
    run = paragraph.add_run(text)
    run.font.size = Pt(12)  

    style = paragraph.style
    style.paragraph_format.left_indent = Pt(indentation)

    return paragraph


regex_fecha = r"\d{1,2}/\d{1,2}/\d{4}|\d{1,2} de [a-zA-Z]+ de \d{4}"
def extract_date_from_keyword(pdf_file, keyword):
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            paragraphs = text.split("\n")
            for paragraph_text in paragraphs:
                if keyword in paragraph_text:
                    matches = re.findall(regex_fecha, paragraph_text)
                    if matches:
                        return matches[0] 
    return matches[0]

def extract_date_below_keyword(pdf_file, keyword):
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            paragraphs = text.split("\n")

            found_keyword = False

            for paragraph_text in paragraphs:
                if keyword in paragraph_text:
                    found_keyword = True
                elif found_keyword:
                    matches = re.findall(regex_fecha, paragraph_text)
                    if matches:
                        return matches[0]


def extract_date_from_last_page(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        last_page = pdf.pages[-1]
        text = last_page.extract_text()

        expresiones_fecha = [
            r'\d{2} de [a-zA-Z]+ de \d{4}',
            r'\d{2} [a-zA-Z]+ de \d{4}',
            r'\d{2} de [a-zA-Z]+ \d{4}',
        ]

        for expresion_fecha in expresiones_fecha:
            matches = re.findall(expresion_fecha, text)
            if matches:
                return matches[0]

    return None

def extract_last_page(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        last_page = pdf.pages[-1]
        text = last_page.extract_text()
        return text

@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST' and 'file' in request.files:
        pdf_file = request.files['file']
        if pdf_file and allowed_file(pdf_file.filename):
            filename = secure_filename(pdf_file.filename)
            upload_folder = 'app/static/documents_folder'
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            pdf_file.save(file_path)
            return redirect(url_for('home.generate_word', filename=filename))
    else:
        return render_template("home/index.html")

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
                {"role" : "system", "content": "Quiero que analices el texto que solicito y me retornes lo que te pido, el contexto del texto es sobre una comisión evaluadora que ha realizado un informe."},
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
        print("empresas:", empresas)
        return empresas
    except:
        return abort(400)

@bp.route("/generate/<filename>", methods=['GET'])
def generate_word(filename):
    if filename.endswith(".pdf"):
        try:
            pdf_path = os.path.join('app/static/documents_folder', filename)
            n_decreto = extract_num_decreto(pdf_path)
            id = extract_id_decreto(pdf_path)
            titulo = extract_line_below_propuesta_publica(pdf_path)
            fecha_apertura = extract_date_from_keyword(pdf_path, "El Acto de Apertura")
            fecha_informe = extract_date_from_last_page(pdf_path)
            fecha_decreto = extract_date_from_keyword(pdf_path, "Decreto Alcaldicio")
            fecha_comision = extract_date_below_keyword(pdf_path, "CONSTITUCIÓN Y SESIONES DE LA COMISIÓN EVALUADORA")
            modified_paragraph = f"el Decreto Alcaldicio N° {n_decreto} de fecha {fecha_decreto}, que aprueba las Bases Administrativas, Bases Técnicas, Anexos y demás antecedentes de la licitación;"
            primer_parrafo = "La propuesta Pública con ID " + id + " denominada " + titulo + " "  + modified_paragraph + " El Acto de Apertura de Ofertas, de fecha " + fecha_apertura + "; el Informe de Evaluación de la comisión evaluadora, de fecha " +  fecha_comision + "; el Certificado de Factibilidad N° X/XX, de fecha XX de XXXXX; el Acta de Proclamación de Alcalde y Concejales de la comuna de Maipú, de fecha 22 de junio de 2021, del Primer Tribunal Electoral Región Metropolitana, que proclamó como alcalde de la comuna de Maipú, al don TOMÁS VODANOVIC ESCUDERO; el Decreto Alcaldicio N°1656 DAP, de fecha 17 de junio del 2020, que designa como Secretario Municipal a don RICARDO HENRIQUEZ VALDÉS; la Ley N°19.886 de Bases sobre Contratos Administrativos de Suministro y Prestación de Servicios y su respectivo Reglamento, el cual fue aprobado mediante Decreto Supremo N° 250, del año 2004, del Ministerio de Hacienda y sus modificaciones; y las facultades conferidas en el articulo 63 del D.F.L.N°1, del año 2006, del Ministerio del Interior, que fijo el texto refundido, coordinado y sistematizado de la Ley N°18.695, Organica Constitucional de Municipalidades."
            considerando_primer = "1.- Que, con fecha XX de XXXXX de 2023, se publicó en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), la propuesta pública {id}, denominada {titulo}, según Bases administrativas y Técnicas, aprobadas por Decreto Alcaldicio N° XXXX, de fecha XX de XXXX de 2023".format(id=id, titulo=titulo)
            considerando_segundo = "2.- Que, en el llamado a licitación los siguientes proponentes presentaron ofertas:"
            considerando_tercer = ""
            rechazados = get_rechazados(pdf_path)
            inadmisibles = get_inadmisibles(pdf_path)
            data_evaluacion = get_evaluacion(pdf_path)
            empresas_adjudicadas = get_datos_adjudicacion(pdf_path)
            fragmento_adjudicadas = []
            for empresa in empresas_adjudicadas:
                nombre_adjudicada = empresa.get("nombre", "")
                rut_adjudicada = empresa.get("RUT", "")
                linea = empresa.get("linea", None)
                total = empresa.get("total", "")
                plazo = empresa.get("plazo", "")
                fragmento_empresas = f"{nombre_adjudicada}, RUT {rut_adjudicada}, {linea}"
                fragmento_adjudicadas.append(fragmento_empresas)
                proponentes_adjudicados = "; ".join(fragmento_adjudicadas)
                if linea is not None:
                    lista_empresa_adjudicada = f"- Del resultado de la evaluación, se establece que la oferta presentada por los proponentes {proponentes_adjudicados} . Son más convenientes para los intereses municipales, por lo que se propone su adjudicación"
                else:
                    considerando_tercer += f"\n- {nombre_adjudicada}, RUT {rut_adjudicada}"
                    lista_empresa_adjudicada = f"- Del resultado de la evaluación, se establece que la oferta presentada por el proponente {nombre_adjudicada}, RUT {rut_adjudicada}. Es más conveniente para los intereses municipales, por lo que se propone su adjudicación"

 
            decreto_primero = ""
            decreto_segundo = ""
            decreto_tercero = ""
            decreto_cuarto = ""
            decreto_quinto = ""
            decreto_sexto = None
            decreto_septimo = None
            if rechazados:
                considerando_tercer = "\n3.- Que, en el Acta de Apertura de las ofertas, de fecha {}, se rechazaron las siguientes ofertas:".format(fecha_apertura)
                motivo_rechazo = rechazados[0].get("motivo", "")
                fragmentos_texto=[]
        
                for proponente in rechazados:
                    nombre = proponente.get("nombre", "")
                    rut = proponente.get("RUT", "")
                    fragmento = f"{nombre}, RUT {rut}"
                    fragmentos_texto.append(fragmento)
        
                proponentes_texto = "; ".join(fragmentos_texto)
                lista_rechazados = f"La de los proponentes {proponentes_texto}, debido a que {motivo_rechazo.lower()}."
                decreto_primero = f"1.- Declárense rechazadas las ofertas de los proponentes {proponentes_texto}, según los argumentos señalados en el considerando tercero."
                if inadmisibles:
                    for inadmisible in inadmisibles:
                        empresa_inadmisible = inadmisible.get("nombre", "")
                        rut_inadmisible = inadmisible.get("RUT", "")
                    decreto_segundo = f"2.- Declárense inadmisibles las ofertas de la empresa {empresa_inadmisible} con RUT {rut_inadmisible}, según los argumentos señalados en el considerando cuarto."
                    decreto_tercero = f"3.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de ${total} (REFLEJAR EL VALOR EN TEXTO), para entregar los productos en un plazo de {plazo}."
                    decreto_cuarto = f"4.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado. / Emitase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente"
                    decreto_quinto = f"5.- Imputese el gasto que involucra la presente adjudicación a la cuenta 2152205006."
                    decreto_sexto = f"6.- La Secretaria Comunal de Planificación dispondrá la publicación del presente Decreto en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), según lo dispuesto en el Articulo 57° del Reglamento de la Ley N° 19.886."
                    decreto_septimo = f"7.- Designese como Unidad Técnica responsable de la gestión y administración de la orden de compra y que actuará como Inspección Técnica, será la Dirección XXXXXXX."
                else:
                    decreto_segundo = f"2.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de ${total} (REFLEJAR EL VALOR EN TEXTO), para entregar los productos en un plazo de {plazo}."
                    decreto_tercero = f"3.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado. / Emitase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente"
                    decreto_cuarto = f"4.- Imputese el gasto que involucra la presente adjudicación a la cuenta 2152205006."
                    decreto_quinto = f"5.- La Secretaria Comunal de Planificación dispondrá la publicación del presente Decreto en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), según lo dispuesto en el Articulo 57° del Reglamento de la Ley N° 19.886."
                    decreto_sexto = f"6.- Designese como Unidad Técnica responsable de la gestión y administración de la orden de compra y que actuará como Inspección Técnica, será la Dirección XXXXXXX."

            else:
                considerando_tercer = "\n3.- Que, en el Acto de Apertura de las ofertas, de fecha {}, no existen ofertas rechazadas.".format(fecha_apertura)
                lista_rechazados = ""
                if inadmisibles:
                    for inadmisible in inadmisibles:
                        empresa_inadmisible = inadmisible.get("nombre", "")
                        rut_inadmisible = inadmisible.get("RUT", "")
                    decreto_primero = f"1.- Declárense inadmisibles las ofertas de la empresa {empresa_inadmisible} con RUT {rut_inadmisible}, por los argumentos senalados en el considerando cuarto."
                    decreto_segundo = f"2.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de ${total} (REFLEJAR EL VALOR EN TEXTO), para entregar los productos en un plazo de {plazo}."
                    decreto_tercero = f"3.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado. / Emitase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente"
                    decreto_cuarto = f"4.- Imputese el gasto que involucra la presente adjudicación a la cuenta 2152205006."
                    decreto_quinto = f"5.- La Secretaria Comunal de Planificación dispondrá la publicación del presente Decreto en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), según lo dispuesto en el Articulo 57° del Reglamento de la Ley N° 19.886."
                    decreto_sexto = f"6.- Designese como Unidad Técnica responsable de la gestión y administración de la orden de compra y que actuará como Inspección Técnica, será la Dirección XXXXXXX."

            if not rechazados and not inadmisibles:
                decreto_primero = f"1.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de ${total} (REFLEJAR EL VALOR EN TEXTO), para entregar los productos en un plazo de {plazo}."
                decreto_segundo = f"2.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado. / Emitase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente"
                decreto_tercero = f"3.- Imputese el gasto que involucra la presente adjudicación a la cuenta 2152205006."
                decreto_cuarto = f"4.- La Secretaria Comunal de Planificación dispondrá la publicación del presente Decreto en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), según lo dispuesto en el Articulo 57° del Reglamento de la Ley N° 19.886."
                decreto_quinto = f"5.- Designese como Unidad Técnica responsable de la gestión y administración de la orden de compra y que actuará como Inspección Técnica, será la Dirección XXXXXXX."
            

            considerando_cuarto = "\n4.-Que de acuerdo con el informe de Evaluación de Ofertas, de fecha {}, la comisión evaluadora propone lo siguiente:".format(fecha_informe)
            considerando_quinto = "\n5.- Que, se cuenta con la disponibilidad presupuestaria para este fin, según da cuenta el Certificado de Factibilidad N° X/XX, de fecha xx de xxxx de 2023."
            considerando_sexto = "\n6.- Que, en el Numeral 13 de las Bases Administrativas, establece que la Unidad Técnica responsable de supervisar la ejecución de la ORDEN DE COMPRA / CONTRATO será la Dirección de XXXXXX (SIGLA)"
        
            table = extract_table_from_pdf(pdf_path)

            output_file_path = pdf_path.replace(".pdf", "-PLANTILLA_DECRETO.docx")
            doc = Document()
            p = doc.add_paragraph()
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
            add_table_to_word_document(doc, table)
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
            return render_template('home/process.html', html=html, filename=filename)
        except Exception as e:
                return str(e)

@bp.route("/download/<filename>")
def download_file(filename):
    output_file_path = filename.replace(".pdf", "-PLANTILLA_DECRETO.docx")
    return send_from_directory('static/documents_folder', output_file_path, as_attachment=True)

