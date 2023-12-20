import pdfplumber
import re
import PyPDF2
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def extract_table_from_pdf(pdf_file):
    table = None  
    
    with pdfplumber.open(pdf_file) as pdf:
        for page_num in range(len(pdf.pages)):
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
