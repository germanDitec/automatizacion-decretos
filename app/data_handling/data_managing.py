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


def add_visto(doc, n_decreto, fecha_decreto, acuerdo, sesion, datesesion, secretaria, idp, titulo, fecha_apertura, fecha_informe, cdp, datecdp_str, concejo):

    primer_parrafo = doc.add_paragraph()
    modified_paragraph = f"el Decreto Alcaldicio N° {n_decreto} de fecha {fecha_decreto}, que aprueba las Bases Administrativas, Bases Técnicas, Anexos y demás antecedentes de la licitación;"

    pp_concejo = f"el Acuerdo N° {acuerdo}, adoptado en Sesión Ordinaria N° {sesion} de fecha {datesesion}, según consta en Cerficiado N° {secretaria} de Secretaria Municipal, del Honorable Concejo Muncipal; "
    pp_final_line = " la Ley N°19.886 de Bases sobre Contratos Administrativos de Suministro y Prestación de Servicios y su respectivo Reglamento, el cual fue aprobado mediante Decreto Supremo N° 250, del año 2004, del Ministerio de Hacienda y sus modificaciones; y las facultades conferidas en el articulo 63 del D.F.L.N°1, del año 2006, del Ministerio del Interior, que fijo el texto refundido, coordinado y sistematizado de la Ley N°18.695, Organica Constitucional de Municipalidades."

    run_pp = primer_parrafo.add_run("La Propuesta Pública con ID ")
    run_pp_idp = primer_parrafo.add_run(idp)
    run_pp_idp.bold = True
    run_pp = primer_parrafo.add_run(" denominada ")
    run_pp_titulo = primer_parrafo.add_run(f"\"{titulo}\"")
    run_pp_titulo.bold = True
    run_pp = primer_parrafo.add_run(f"; {modified_paragraph}")
    run_pp = primer_parrafo.add_run(
        f" El Acta de Apertura de Ofertas, de fecha {fecha_apertura}; el Informe de Evaluación de la comisión evaluadora, de fecha {fecha_informe}; el Certificado de Factibilidad N° {cdp}, de fecha {datecdp_str}; ")
    if concejo == 'on':
        run_pp_concejo = primer_parrafo.add_run(pp_concejo)
        run_pp = primer_parrafo.add_run(
            "el Acta de Proclamación de Alcalde y Concejales de la comuna de Maipú, de fecha 22 de junio de 2021, del Primer Tribunal Electoral Región Metropolitana, que proclamó como alcalde de la comuna de Maipú, a don ")
        run_pp_alcalde = primer_parrafo.add_run(
            "TOMÁS VODANOVIC ESCUDERO;")
        run_pp_alcalde.bold = True
    else:
        run_pp = primer_parrafo.add_run("El Decreto Alcaldicio N° 4182 DAP, de fecha 9 de diciembre de 2016, que delega las atribuciones alcaldicias en el Administrador Municipal y sus modificiaciones; El Decreto Alcaldicio N° 1554 DAP, de fecha 29 de junio del 2021, que designa como Administrador Municipal a don")
        run_pp_administrador = primer_parrafo.add_run(
            "JORGE CÓRDOVA OBREQUEN;"
        )
        run_pp_administrador.bold = True

    run_pp = primer_parrafo.add_run(
        " el Decreto Alcaldicio N°1656 DAP, de fecha 17 de junio del 2020, que designa como Secretario Municipal a don ")
    run_pp_secretario = primer_parrafo.add_run(
        "RICARDO HENRIQUEZ VALDÉS;")
    run_pp_secretario.bold = True

    run_pp = primer_parrafo.add_run(pp_final_line)


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

        decreto_primero = f"{start}.- Declárense inadmisibles las ofertas de la empresa {proponentes_inadmisibles_text}, por los argumentos señalados en el considerando cuarto."
        doc.add_paragraph(decreto_primero)

        if desiertas and 'desiertas' in desiertas:
            start += 1
            lineas_desiertas = desiertas.get('desiertas')
            lineas_desiertas_text = ', '.join(map(str, lineas_desiertas))
            motivo_desiertas = desiertas.get(
                'motivo', "motivo no especificada")
            decreto_desiertas = f"{start}.- Declárense desiertas las ofertas de las empresas {lineas_desiertas_text} por el motivo {motivo_desiertas}."
            doc.add_paragraph(decreto_desiertas)

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


def informe_to_sharepoint(server_url, username, password, site_url, file, file_name, direccion):
    sharepoint_folder = f'Documentos Compartidos/Informes de evaluación/{direccion}'
    authcookie = Office365(server_url, username=username,
                           password=password).GetCookies()
    site = Site(site_url, version=Version.v365, authcookie=authcookie)
    folder = site.Folder(sharepoint_folder)
    with open(file, mode='rb') as file:
        fileContent = file.read()
    folder.upload_file(fileContent, file_name)


def decreto_to_sharepoint(server_url, username, password, site_url, file, file_name, direccion):
    sharepoint_folder = f'Documentos Compartidos/Decretos generados/{direccion}'
    authcookie = Office365(server_url, username=username,
                           password=password).GetCookies()
    site = Site(site_url, version=Version.v365, authcookie=authcookie)
    folder = site.Folder(sharepoint_folder)
    with open(file, mode='rb') as file:
        fileContent = file.read()
    folder.upload_file(fileContent, file_name)
