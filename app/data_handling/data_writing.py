from docx import Document
from docx.shared import Pt
from docx.shared import Inches


def generate_word_document(output_file, data):
    doc = Document()
    doc.add_paragraph(data)
    doc.save(output_file)



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