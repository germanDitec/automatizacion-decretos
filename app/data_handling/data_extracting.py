import pdfplumber
import re
import PyPDF2
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


def extract_table_from_pdf(pdf_file):
    table = None
    with pdfplumber.open(pdf_file) as pdf:
        for page_num in range(1, len(pdf.pages)):
            page = pdf.pages[page_num]
            table = page.extract_table()

            if table:
                break

    return table


def extract_paragraph_after_keyword(pdf_file, keyword):
    paragraph = ""
    with open(pdf_file, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            match = re.search(keyword, page_text)
            if match:
                paragraph_match = re.search(
                    r'(?<=\n).*?(?=\n|$)', page_text[match.end():])
                if paragraph_match:
                    paragraph = paragraph_match.group(0)
                    break
    return paragraph.strip()


def extract_num_decreto(pdf_file):
    with open(pdf_file, 'rb') as pdf:
        pdf_reader = PyPDF2.PdfReader(pdf)

        for page in pdf_reader.pages:
            texto = page.extract_text()
            coincidencias = re.findall(r'N°(\d+)', texto)

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


# def extract_paragraphs_containing_keyword(pdf_file, keyword):
#     paragraphs = []
#     with open(pdf_file, "rb") as pdf_file:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)
#         for page in pdf_reader.pages:
#             text = page.extract_text()
#             text = text.replace('\n', ' ')
#             while keyword in text:
#                 start = text.index(keyword)
#                 end = text.index('\n', start) if '\n' in text[start:] else None
#                 paragraph = text[start:end].strip()
#                 paragraphs.append(paragraph)
#                 text = text[end:] if end else ""
#     return paragraphs


def extract_paragraphs_containing_keyword(pdf_file, keyword, case_sensitive=False):
    paragraphs = []
    keyword_found = False

    with open(pdf_file, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)

        for i in range(total_pages):
            page = pdf_reader.pages[i]
            text = page.extract_text()
            text = text.replace('\n', ' ')

            if not case_sensitive:
                keyword = keyword.lower()
                text = text.lower()

            if keyword in text:
                keyword_found = True
                start = text.index(keyword)
                end = text.index('\n', start) if '\n' in text[start:] else None
                paragraph = text[start:end].strip()
                paragraphs.append(paragraph)

                if end is not None:
                    text = text[end:]
            elif keyword_found:
                paragraphs[-1] += " " + text.strip()

    return paragraphs


def replace_word_in_paragraph(paragraph, old_word, new_word):
    return paragraph.replace(old_word, new_word)


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
                    date = re.findall(regex_fecha, paragraph_text)
                    if date:
                        return date[0]
    return date[0]


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
                    fecha_comision = re.findall(regex_fecha, paragraph_text)
                    if fecha_comision:
                        return fecha_comision[0]


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


def obtener_direccion(direccion):
    opciones = {
        "0": "-- Seleccione Dirección --",
        "1": "Dirección de Administración y Finanzas (DAF)",
        "2": "Dirección de Asesoría Jurídica (DAJ)",
        "3": "Dirección de Control",
        "4": "Secretaría Comunal de Planificación (SECPLA)",
        "5": "Dirección de Aseo, Ornato y Gestión Ambiental (DAOGA)",
        "6": "Dirección de Tránsito y Transporte Público",
        "7": "Dirección de Operaciones",
        "8": "Dirección de Riesgos, Desastres y Emergencias (DRDE)",
        "9": "Dirección de Inspección",
        "10": "Dirección de Prevención y Seguridad Ciudadana (DIPRESEC)",
        "11": "Dirección de Tecnología y Comunicaciones (DITEC)",
        "12": "Dirección de Salud Municipal (DISAM)",
        "13": "Dirección de Desarrollo Comunitario (DIDECO)",
        "14": "Dirección de Obras Municipales (DOM)",
        "15": "Servicio Municipal de Agua Potable y Alcantarillado (SMAPA)",
    }
    return opciones.get(direccion, "Opción no válida")


def obtener_propuesta(propuesta):
    opciones = {
        "0": "-- Seleccione Propuesta --",
        "1": "Orden de Compra",
        "2": "Contrato",
        "3": "Contrato y Orden de Compra",
        "4": "Orden de Compra con Acuerdo Complementario",
    }
    return opciones.get(propuesta, "Opción no válida")
