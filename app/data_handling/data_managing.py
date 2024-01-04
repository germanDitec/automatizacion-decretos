from datetime import datetime
from shareplum import Office365
from shareplum import Site
from shareplum.site import Version


def get_rechazados_text(rechazados):
    motivo_rechazo = rechazados[0].get("motivo", "")
    fragmentos_texto = [f"{proponente['nombre']}, RUT {proponente['RUT']}" for proponente in rechazados]
    proponentes_texto = "; ".join(fragmentos_texto)
    return proponentes_texto, motivo_rechazo

def get_inadmisibles_text(inadmisibles):
    fragmentos_texto_inadmisible = [f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}" for inadmisible in inadmisibles]
    proponentes_inadmisible = "; ".join(fragmentos_texto_inadmisible)
    return proponentes_inadmisible

def add_inadmisibles_decreto(inadmisibles, id, titulo,nombre_adjudicada, rut_adjudicada, total, plazo, direccion, cuenta, tipo_compra, propuesta):
    proponentes_inadmisible = get_inadmisibles_text(inadmisibles)
    decreto_segundo = f"2.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisible}, según los argumentos señalados en el considerando cuarto."
    decreto_tercero = f"3.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de {total} (REFLEJAR EL VALOR EN TEXTO), para entregar los {tipo_compra} en un plazo de {plazo}."

    decreto_cuarto = ""
    if propuesta == "1":
        decreto_cuarto = "4.- Emítase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente."
    elif propuesta == "2":
        decreto_cuarto = "4.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "3":
        decreto_cuarto = "4.- El precio del contrato de compra y Orden de Compra que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "4":
        decreto_cuarto = "4.- Emítase la Orden de Compra con Acuerdo Complementario correspondientes a nombre del proponente adjudicado, por el monto informado en el numeral precedente."

    decreto_quinto =f"5.- Imputese el gasto que involucra la presente adjudicación a la cuenta {cuenta}."
    decreto_sexto = f"6.- La Secretaria Comunal de Planificación dispondrá la publicación del presente Decreto en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), según lo dispuesto en el Articulo 57° del Reglamento de la Ley N° 19.886."
    decreto_septimo = f"7.- Designese como Unidad Técnica responsable de la gestión y administración de la orden de compra y que actuará como Inspección Técnica, será la {direccion}."
    return decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto, decreto_sexto, decreto_septimo

def add_no_inadmisible_decreto(id, titulo, nombre_adjudicada, rut_adjudicada, total, plazo, direccion, cuenta, tipo_compra, propuesta):
    decreto_segundo = f"2.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de {total} (REFLEJAR EL VALOR EN TEXTO), para entregar los {tipo_compra} en un plazo de {plazo}."

    decreto_tercero = ""
    if propuesta == "1":
        decreto_tercero = "3.- Emítase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente."
    elif propuesta == "2":
        decreto_tercero = "3.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "3":
        decreto_tercero = "3.- El precio del contrato de compra y Orden de Compra que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "4":
        decreto_tercero = "3.- Emítase la Orden de Compra con Acuerdo Complementario correspondientes a nombre del proponente adjudicado, por el monto informado en el numeral precedente."

    decreto_cuarto = f"4.- Imputese el gasto que involucra la presente adjudicación a la cuenta {cuenta}."
    decreto_quinto = f"5.- La Secretaria Comunal de Planificación dispondrá la publicación del presente Decreto en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), según lo dispuesto en el Articulo 57° del Reglamento de la Ley N° 19.886."
    decreto_sexto = f"6.- Designese como Unidad Técnica responsable de la gestión y administración de la orden de compra y que actuará como Inspección Técnica, será la {direccion}."
    return decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto, decreto_sexto

def add_inadmisibles_no_rechazados(proponentes_inadmisible, id, titulo, nombre_adjudicada, rut_adjudicada, total, plazo, direccion, cuenta, tipo_compra, propuesta):
    decreto_primero = f"1.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisible}, por los argumentos senalados en el considerando cuarto."
    decreto_segundo = f"2.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de {total} (REFLEJAR EL VALOR EN TEXTO), para entregar los {tipo_compra} en un plazo de {plazo}."

    decreto_tercero = ""
    if propuesta == "1":
        decreto_tercero = "3.- Emítase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente."
    elif propuesta == "2":
        decreto_tercero = "3.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "3":
        decreto_tercero = "3.- El precio del contrato de compra y Orden de Compra que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "4":
        decreto_tercero = "3.- Emítase la Orden de Compra con Acuerdo Complementario correspondientes a nombre del proponente adjudicado, por el monto informado en el numeral precedente."

    decreto_cuarto = f"4.- Imputese el gasto que involucra la presente adjudicación a la cuenta {cuenta}."
    decreto_quinto = f"5.- La Secretaria Comunal de Planificación dispondrá la publicación del presente Decreto en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), según lo dispuesto en el Articulo 57° del Reglamento de la Ley N° 19.886."
    decreto_sexto = f"6.- Designese como Unidad Técnica responsable de la gestión y administración de la orden de compra y que actuará como Inspección Técnica, será la {direccion}."
    return decreto_primero, decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto, decreto_sexto


def add_noadm_norec(id, titulo, nombre_adjudicada, rut_adjudicada, total, plazo, direccion, cuenta, tipo_compra, propuesta):
    decreto_primero = f"1.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de {total} (REFLEJAR EL VALOR EN TEXTO), para entregar los {tipo_compra} en un plazo de {plazo}."

    decreto_segundo = ""
    if propuesta == "1":
        decreto_segundo = "2.- Emítase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente."
    elif propuesta == "2":
        decreto_segundo = "2.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "3":
        decreto_segundo = "2.- El precio del contrato de compra y Orden de Compra que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "4":
        decreto_segundo = "2.- Emítase la Orden de Compra con Acuerdo Complementario correspondientes a nombre del proponente adjudicado, por el monto informado en el numeral precedente."

    decreto_tercero = f"3.- Imputese el gasto que involucra la presente adjudicación a la cuenta {cuenta}."
    decreto_cuarto = f"4.- La Secretaria Comunal de Planificación dispondrá la publicación del presente Decreto en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), según lo dispuesto en el Articulo 57° del Reglamento de la Ley N° 19.886."
    decreto_quinto = f"5.- Designese como Unidad Técnica responsable de la gestión y administración de la orden de compra y que actuará como Inspección Técnica, será la {direccion}."
    return decreto_primero, decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto

def add_decretos_lineas(doc, id, titulo, rechazadas, inadmisibles, empresas_adjudicadas, direccion, cuenta, tipo_compra, propuesta): 
    start = 0
    if rechazadas:
        proponentes_rechazadas, motivo = get_rechazados_text(rechazadas)
        decreto_primero = f"1.- Declárense rechazadas las ofertas de los proponentes {proponentes_rechazadas}, según los argumentos señalados en el considerando tercero."
        doc.add_paragraph(decreto_primero)

        if inadmisibles:
            proponentes_inadmisible = get_inadmisibles_text(inadmisibles)
            decreto_segundo = f"2.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisible}, por los argumentos senalados en el considerando cuarto."
            doc.add_paragraph(decreto_segundo)
            start += 2

        start += 1

    elif inadmisibles:
        proponentes_inadmisible = get_inadmisibles_text(inadmisibles)
        decreto_primero = f"1.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisible}, por los argumentos senalados en el considerando tercero."
        doc.add_paragraph(decreto_primero)
        start += 1

    for indice, empresa in enumerate(empresas_adjudicadas, start=start):
        nombre = empresa.get('nombre')
        rut = empresa.get('RUT')
        total = empresa.get('total')
        plazo = empresa.get('plazo')
        linea = empresa.get('linea')
        decreto_adjudicacion = f"{indice + 1}.- Adjudiquese la propuesta pública ID {id}, denominada {titulo}, línea n°{linea}, al proponente {nombre} RUT {rut}, por la suma total de {total} (reflejar el valor en texto), para entregar los {tipo_compra} en un plazo de {plazo}."
        doc.add_paragraph(decreto_adjudicacion)

    last_index = start + len(empresas_adjudicadas)

    decreto_servicio = ""
    if propuesta == "1":
        decreto_servicio = f"{last_index + 1}.- Emítase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente."
    elif propuesta == "2":
        decreto_servicio = f"{last_index + 1}.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "3":
        decreto_servicio = f"{last_index + 1}.- El precio del contrato de compra y Orden de Compra que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "4":
        decreto_servicio = f"{last_index + 1}.- Emítase la Orden de Compra con Acuerdo Complementario correspondientes a nombre del proponente adjudicado, por el monto informado en el numeral precedente."

    doc.add_paragraph(decreto_servicio)
    decreto_gasto = f"{last_index + 2}.- Imputese el gasto que involucra la presente adjudicación a la cuenta {cuenta}."
    doc.add_paragraph(decreto_gasto)
    decreto_publicacion = f"{last_index + 3}.- La secretaria comunal de planificación dispondrá la publicación del presente decreto en el sistema de información de compras y contratación pública (www.mercadopublico.cl), según lo dispuesto en el articulo 57° del reglamento de la ley n° 19.886."
    doc.add_paragraph(decreto_publicacion)
    decreto_responsable = f"{last_index + 4}.- Designese como unidad técnica responsable de la gestión y administración de la orden de compra y que actuará como inspección técnica, será la {direccion}."
    doc.add_paragraph(decreto_responsable)


def formate_date_text(date):
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    months = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    day = date_obj.day
    month = months[date_obj.month -1]
    year = date_obj.year

    date_text = f"{day} de {month} de {year}"
    return date_text


def informe_to_sharepoint(server_url, username, password, site_url, file, file_name):
    sharepoint_folder = 'Documentos Compartidos/Informes de evaluación'
    authcookie = Office365(server_url, username = username, password=password).GetCookies()
    site = Site(site_url, version=Version.v365, authcookie=authcookie)
    folder = site.Folder(sharepoint_folder)
    with open(file, mode='rb') as file:
        fileContent = file.read()
    folder.upload_file(fileContent, file_name)


def decreto_to_sharepoint(server_url, username, password, site_url, file, file_name):
    sharepoint_folder = 'Documentos Compartidos/Decretos generados'
    authcookie = Office365(server_url, username = username, password=password).GetCookies()
    site = Site(site_url, version=Version.v365, authcookie=authcookie)
    folder = site.Folder(sharepoint_folder)
    with open(file, mode='rb') as file:
        fileContent = file.read()
    folder.upload_file(fileContent, file_name)
