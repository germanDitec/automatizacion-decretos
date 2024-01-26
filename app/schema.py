instructions = [
    "SET CONSTRAINTS ALL DEFERRED;",

    "DROP TABLE IF EXISTS decreto;",
    "DROP TABLE IF EXISTS informe;",
    "DROP TABLE IF EXISTS usuario;",
    "DROP TABLE IF EXISTS propuesta;",
    "DROP TABLE IF EXISTS direccion;",

    "SET CONSTRAINTS ALL IMMEDIATE;",

    """
    CREATE TABLE Usuario(
        usuario_id SERIAL PRIMARY KEY,
        nombre varchar(150) NOT NULL,
        email varchar(150) NOT NULL UNIQUE,
        password varchar(300) NOT NULL,
        verification_token varchar(50),
        verified boolean NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,

    """
    CREATE TABLE Propuesta(
        propuesta_id SERIAL PRIMARY KEY,
        propuesta varchar(50) NOT NULL
    );
    """,
    """
    CREATE TABLE Direccion(
        direccion_id SERIAL PRIMARY KEY,
        direccion varchar(200) NOT NULL
    );
    """,

    "INSERT INTO Propuesta(propuesta) VALUES ('Orden de Compra');",
    "INSERT INTO Propuesta(propuesta) VALUES ('Contrato');",
    "INSERT INTO Propuesta(propuesta) VALUES ('Contrato y Orden de Compra');",
    "INSERT INTO Propuesta(propuesta) VALUES ('Orden de Compra con Acuerdo Complementario');",

    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Administración y Finanzas (DAF)');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Asesoria Juridica (DAJ)');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Control');",
    "INSERT INTO Direccion(direccion) VALUES ('Secretaria Comunal de Planificación (SECPLA)');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Aseo, Ornato y Gestión Ambiental (DAOGA)');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Tránsito y Transporte Público');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Operaciones');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Riesgos, Desastres y Emergencias (DRDE)');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Inspección');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Prevención y Seguridad Ciudadana (DIPRESEC)');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Tecnología y Comunicaciones (DITEC');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Salud Municipal (DISAM)');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Desarrollo Comunitario (DIDECO)');",
    "INSERT INTO Direccion(direccion) VALUES ('Dirección de Obras Municipales (DOM)');",
    "INSERT INTO Direccion(direccion) VALUES ('Servicio Municipal de Agua Potable y Alcantarillado (SMAPA');",


    """
    CREATE TABLE Informe(
        informe_id SERIAL PRIMARY KEY,
        idp varchar(40) NOT NULL,
        propuesta_id INT REFERENCES propuesta (propuesta_id),
        direccion_id INT REFERENCES direccion (direccion_id),
        titulo VARCHAR(200) NOT NULL,
        cdp varchar(30) NOT NULL,
        fecha_cdp timestamp NOT NULL,
        fecha_compra timestamp NOT NULL,
        cuenta bigint NOT NULL,
        concejo boolean NOT NULL,
        acuerdo_concejo int,
        numero_sesion int,
        fecha_sesion timestamp,
        secretaria int,
        tipo_compra VARCHAR(30) NOT NULL,
        created_by INT REFERENCES Usuario (usuario_id),
        created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
CREATE TABLE Decreto(
        decreto_id SERIAL PRIMARY KEY,
        informe_id int REFERENCES Informe (informe_id),
        costo_total DECIMAL(10,2) NOT NULL,
        propuesta_id int REFERENCES propuesta(propuesta_id),
        direccion_id int REFERENCES direccion(direccion_id),
        created_by INT REFERENCES usuario (usuario_id),
        created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """

]
