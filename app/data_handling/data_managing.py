from datetime import datetime
from shareplum import Office365
from shareplum import Site
from shareplum.site import Version


def get_rechazados_text(rechazados):
    motivo_rechazo = rechazados[0].get("motivo", "")
    fragmentos_texto = [
        f"{proponente['nombre']}, RUT {proponente['RUT']}" for proponente in rechazados]
    proponentes_texto = "; ".join(fragmentos_texto)
    return proponentes_texto, motivo_rechazo


def get_inadmisibles_text(inadmisibles):
    fragmentos_texto_inadmisible = [
        f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}" for inadmisible in inadmisibles]
    proponentes_inadmisible = "; ".join(fragmentos_texto_inadmisible)
    return proponentes_inadmisible


def add_inadmisibles_decreto(inadmisibles, id, titulo, nombre_adjudicada, rut_adjudicada, total, direccion, cuenta, tipo_compra, propuesta):
    proponentes_inadmisible = get_inadmisibles_text(inadmisibles)
    decreto_segundo = f"2.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisible}, según los argumentos señalados en el considerando cuarto."
    decreto_tercero = f"3.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de {total} (REFLEJAR EL VALOR EN TEXTO), para entregar los {tipo_compra} en un plazo de XXXXX."

    decreto_cuarto = None
    if propuesta == "1":
        decreto_cuarto = "4.- Emítase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente."
    elif propuesta == "2":
        decreto_cuarto = "4.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "3":
        decreto_cuarto = "4.- El precio del contrato de compra y Orden de Compra que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "4":
        decreto_cuarto = "4.- Emítase la Orden de Compra con Acuerdo Complementario correspondientes a nombre del proponente adjudicado, por el monto informado en el numeral precedente."

    decreto_quinto = f"5.- Imputese el gasto que involucra la presente adjudicación a la cuenta {cuenta}."
    decreto_sexto = f"6.- La Secretaria Comunal de Planificación dispondrá la publicación del presente Decreto en el Sistema de Información de Compras y Contratación Pública (www.mercadopublico.cl), según lo dispuesto en el Articulo 57° del Reglamento de la Ley N° 19.886."
    decreto_septimo = f"7.- Designese como Unidad Técnica responsable de la gestión y administración de {propuesta.upper()} y que actuará como Inspección Técnica, será la {direccion}."
    return decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto, decreto_sexto, decreto_septimo


def add_no_inadmisible_decreto(id, titulo, nombre_adjudicada, rut_adjudicada, total, direccion, cuenta, tipo_compra, propuesta):
    decreto_segundo = f"2.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de {total} (REFLEJAR EL VALOR EN TEXTO), para entregar los {tipo_compra} en un plazo de XXXXX."

    decreto_tercero = None
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
    decreto_sexto = f"6.- Designese como Unidad Técnica responsable de la gestión y administración de {propuesta.upper()} y que actuará como Inspección Técnica, será la {direccion}."
    decreto_septimo = None
    return decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto, decreto_sexto


def add_inadmisibles_no_rechazados(proponentes_inadmisible, id, titulo, nombre_adjudicada, rut_adjudicada, total, direccion, cuenta, tipo_compra, propuesta):
    decreto_primero = f"1.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisible}, por los argumentos senalados en el considerando cuarto."
    decreto_segundo = f"2.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de {total} (REFLEJAR EL VALOR EN TEXTO), para entregar los {tipo_compra} en un plazo de XXXXX."

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
    decreto_sexto = f"6.- Designese como Unidad Técnica responsable de la gestión y administración de {propuesta.upper()} y que actuará como Inspección Técnica, será la {direccion}."
    return decreto_primero, decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto, decreto_sexto


def add_noadm_norec(id, titulo, nombre_adjudicada, rut_adjudicada, total, direccion, cuenta, tipo_compra, propuesta):
    decreto_primero = f"1.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de {total} (REFLEJAR EL VALOR EN TEXTO), para entregar los {tipo_compra} en un plazo de XXXXX."

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
    decreto_quinto = f"5.- Designese como Unidad Técnica responsable de la gestión y administración de {propuesta.upper()} y que actuará como Inspección Técnica, será la {direccion}."
    return decreto_primero, decreto_segundo, decreto_tercero, decreto_cuarto, decreto_quinto


def add_decretos_lineas(doc, id, titulo, rechazadas, inadmisibles, empresas_adjudicadas, direccion, cuenta, tipo_compra, propuesta, valor_propuesta, desiertas):
    start = 1

    if rechazadas:
        proponentes_rechazadas, motivo = get_rechazados_text(rechazadas)
        decreto_primero = f"{start}.- Declárense rechazadas las ofertas de los proponentes {proponentes_rechazadas}, según los argumentos señalados en el considerando tercero."
        doc.add_paragraph(decreto_primero)

        if inadmisibles:
            proponentes_rechazadas_nombres = [
                proponente['nombre'] for proponente in rechazadas]

            proponentes_inadmisibles_text = "; ".join([
                f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}" +
                (f", para las líneas N° {inadmisible['linea']}" if 'linea' in inadmisible and inadmisible['linea'] else "")
                for inadmisible in inadmisibles
                if inadmisible['nombre'] not in proponentes_rechazadas_nombres
            ] + [
                f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}"
                for inadmisible in inadmisibles
                if inadmisible['nombre'] not in proponentes_rechazadas_nombres and 'linea' not in inadmisible
            ])

            if proponentes_inadmisibles_text:
                start += 1
                decreto_inadmisibles = f"{start}.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisibles_text}, por los argumentos señalados en el considerando cuarto."
                doc.add_paragraph(decreto_inadmisibles)

        if desiertas and 'desiertas' in desiertas:
            start += 1
            lineas_desiertas = desiertas.get('desiertas')
            lineas_desiertas_text = ', '.join(map(str, lineas_desiertas))
            motivo_desiertas = desiertas.get(
                'motivo', "motivo no especificada")
            decreto_desiertas = f"{start}.- Declárense desiertas las ofertas de las empresas {lineas_desiertas_text} por el motivo {motivo_desiertas}."
            doc.add_paragraph(decreto_desiertas)

    elif inadmisibles:
        proponentes_inadmisibles_text = "; ".join([
            f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}" +
            (f", para las líneas N° {inadmisible['linea']}" if 'linea' in inadmisible and inadmisible['linea'] else "")
            for inadmisible in inadmisibles
        ] + [
            f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}"
            for inadmisible in inadmisibles
            if 'linea' not in inadmisible
        ])

        start += 1
        decreto_primero = f"{start}.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisibles_text}, por los argumentos señalados en el considerando cuarto."
        doc.add_paragraph(decreto_primero)

        if desiertas and 'desiertas' in desiertas:
            start += 1
            lineas_desiertas = desiertas.get('desiertas')
            lineas_desiertas_text = ', '.join(map(str, lineas_desiertas))
            motivo_desiertas = desiertas.get(
                'motivo', "motivo no especificada")
            decreto_desiertas = f"{start}.- En uso de las facultades que la ley otorga y para todos los efectos legales"
            doc.add_paragraph(decreto_desiertas)

    print("START: ", start)

    for indice, empresa in enumerate(empresas_adjudicadas, start=start):
        nombre = empresa.get('nombre')
        rut = empresa.get('RUT')
        total = empresa.get('total')
        linea = empresa.get('linea')
        decreto_adjudicacion = f"{indice + 1}.- Adjudiquese la propuesta pública ID {id}, denominada {titulo}, línea n°{linea}, al proponente {nombre} RUT {rut}, por la suma total de {total} (reflejar el valor en texto), para entregar los {tipo_compra} en un plazo de XXXXX."
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
    decreto_responsable = f"{last_index + 4}.- Designese como unidad técnica responsable de la gestión y administración de {valor_propuesta.upper()} y que actuará como inspección técnica, será la {direccion}."
    doc.add_paragraph(decreto_responsable)


def add_decretos(doc, id, titulo, rechazadas, inadmisibles, direccion, cuenta, tipo_compra, propuesta, valor_propuesta, desiertas, nombre_adjudicada, total, rut_adjudicada):
    start = 1
    if rechazadas:
        proponentes_rechazadas, motivo = get_rechazados_text(rechazadas)
        decreto_primero = f"{start}.- Declárense rechazadas las ofertas de los proponentes {proponentes_rechazadas}, según los argumentos señalados en el considerando tercero."
        doc.add_paragraph(decreto_primero)

        if inadmisibles:
            proponentes_rechazadas_nombres = [
                proponente['nombre'] for proponente in rechazadas]

            proponentes_inadmisibles_text = "; ".join([
                f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}" +
                (f", para las líneas N° {inadmisible['linea']}" if 'linea' in inadmisible and inadmisible['linea'] else "")
                for inadmisible in inadmisibles
                if inadmisible['nombre'] not in proponentes_rechazadas_nombres
            ] + [
                f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}"
                for inadmisible in inadmisibles
                if inadmisible['nombre'] not in proponentes_rechazadas_nombres and 'linea' not in inadmisible
            ])

            if proponentes_inadmisibles_text:
                start += 1
                decreto_inadmisibles = f"{start}.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisibles_text}, por los argumentos señalados en el considerando cuarto."
                doc.add_paragraph(decreto_inadmisibles)

        if desiertas and 'desiertas' in desiertas:
            lineas_desiertas = desiertas.get('desiertas')
            lineas_desiertas_text = ', '.join(map(str, lineas_desiertas))
            motivo_desiertas = desiertas.get(
                'motivo', "motivo no especificada")
            start += 1
            decreto_desiertas = f"{start}.- Declárense desiertas las ofertas de las empresas {lineas_desiertas_text} por el motivo {motivo_desiertas}."
            doc.add_paragraph(decreto_desiertas)

    elif inadmisibles:
        proponentes_inadmisibles_text = "; ".join([
            f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}" +
            (f", para las líneas N° {inadmisible['linea']}" if 'linea' in inadmisible and inadmisible['linea'] else "")
            for inadmisible in inadmisibles
        ] + [
            f"{inadmisible['nombre']}, RUT {inadmisible['RUT']}"
            for inadmisible in inadmisibles
            if 'linea' not in inadmisible
        ])

        decreto_primero = f"{start}.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisibles_text}, por los argumentos señalados en el considerando cuarto."
        doc.add_paragraph(decreto_primero)

        if desiertas and 'desiertas' in desiertas:
            lineas_desiertas = desiertas.get('desiertas')
            lineas_desiertas_text = ', '.join(map(str, lineas_desiertas))
            motivo_desiertas = desiertas.get(
                'motivo', "motivo no especificada")
            start += 1
            decreto_desiertas = f"{start}.- En uso de las facultades que la ley otorga y para todos los efectos legales"
            doc.add_paragraph(decreto_desiertas)

    if start != 1:
        start += 1
    decreto_adjudicada = f"{start}.- Adjudiquese la Propuesta Pública ID {id}, denominada {titulo}, al proponente {nombre_adjudicada}, RUT {rut_adjudicada}, por la suma total de {total} (REFLEJAR EL VALOR EN TEXTO), para entregar los {tipo_compra} en un plazo de XXXXX."

    doc.add_paragraph(decreto_adjudicada)

    decreto_servicio = ""
    start += 1
    if propuesta == "1":
        decreto_servicio = f"{start}.- Emítase la Orden de Compra correspondiente a nombre del proponente adjudicado, por el monto informado en el numeral precedente."
    elif propuesta == "2":
        decreto_servicio = f"{start}.- El precio del contrato de compra será el valor que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "3":
        decreto_servicio = f"{start}.- El precio del contrato de compra y Orden de Compra que pague la Municipalidad al contratista por el servicio contratado y debidamente ejecutados, sobre la base de los valores unitarios ofertados y el monto total ofertado."
    elif propuesta == "4":
        decreto_servicio = f"{start}.- Emítase la Orden de Compra con Acuerdo Complementario correspondientes a nombre del proponente adjudicado, por el monto informado en el numeral precedente."

    doc.add_paragraph(decreto_servicio)
    start += 1
    decreto_gasto = f"{start}.- Imputese el gasto que involucra la presente adjudicación a la cuenta {cuenta}."
    doc.add_paragraph(decreto_gasto)
    start += 1
    decreto_publicacion = f"{start}.- La secretaria comunal de planificación dispondrá la publicación del presente decreto en el sistema de información de compras y contratación pública (www.mercadopublico.cl), según lo dispuesto en el articulo 57° del reglamento de la ley n° 19.886."
    doc.add_paragraph(decreto_publicacion)
    start += 1
    decreto_responsable = f"{start}.- Designese como unidad técnica responsable de la gestión y administración de {valor_propuesta.upper()} y que actuará como inspección técnica, será la {direccion}."
    doc.add_paragraph(decreto_responsable)


def formate_date_text(date):
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    months = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    day = date_obj.day
    month = months[date_obj.month - 1]
    year = date_obj.year

    date_text = f"{day} de {month} de {year}"
    return date_text


def informe_to_sharepoint(server_url, username, password, site_url, file, file_name):
    sharepoint_folder = 'Documentos Compartidos/Informes de evaluación'
    authcookie = Office365(server_url, username=username,
                           password=password).GetCookies()
    site = Site(site_url, version=Version.v365, authcookie=authcookie)
    folder = site.Folder(sharepoint_folder)
    with open(file, mode='rb') as file:
        fileContent = file.read()
    folder.upload_file(fileContent, file_name)


def decreto_to_sharepoint(server_url, username, password, site_url, file, file_name):
    sharepoint_folder = 'Documentos Compartidos/Decretos generados'
    authcookie = Office365(server_url, username=username,
                           password=password).GetCookies()
    site = Site(site_url, version=Version.v365, authcookie=authcookie)
    folder = site.Folder(sharepoint_folder)
    with open(file, mode='rb') as file:
        fileContent = file.read()
    folder.upload_file(fileContent, file_name)
