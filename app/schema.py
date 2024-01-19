instructions = [
    "USE Decretos;",

    "EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL;';",

    """IF OBJECT_ID('dbo.Decreto') IS NOT NULL
    DROP TABLE dbo.Decreto;""",

    """IF OBJECT_ID('dbo.Direccion') IS NOT NULL
    DROP TABLE dbo.Direccion;""",


    """IF OBJECT_ID('dbo.Usuario') IS NOT NULL
    DROP TABLE dbo.Usuario;""",


    """IF OBJECT_ID('dbo.Propuesta') IS NOT NULL
    DROP TABLE dbo.Propuesta;""",


    "EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL;';",

    """
    CREATE TABLE Usuario(
        usuario_id int IDENTITY(1,1) PRIMARY KEY,
        nombre varchar(150) NOT NULL,
        email varchar(150) NOT NULL UNIQUE,
        password varchar(300) NOT NULL,
        verification_token varchar(50),
        verified bit NOT NULL DEFAULT 0,
        created_at datetime NOT NULL DEFAULT GETDATE(),
    );
    """,

    """
    CREATE TABLE Propuesta(
        propuesta_id int IDENTITY(1,1) PRIMARY KEY,
        propuesta varchar(50) NOT NULL
    );
    """,
    """
    CREATE TABLE Direccion(
        direccion_id int IDENTITY(1,1) PRIMARY KEY,
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
    CREATE TABLE Decreto(
        decreto_id int IDENTITY(1,1) PRIMARY KEY,
        id_propuesta varchar(30) NOT NULL,
        cdp varchar(30) NOT NULL,
        fecha_cdp datetime NOT NULL,
        fecha_compra datetime NOT NULL,
        cuenta int NOT NULL,
        concejo bit NOT NULL,
        acuerdo_concejo int,
        numero_sesion int,
        fecha_sesion datetime,
        secretaria int,
        tipo_compra VARCHAR(30) NOT NULL,
        costo_total DECIMAL(10,2) NOT NULL,
        propuesta_id int FOREIGN KEY REFERENCES Propuesta (propuesta_id),
        direccion_id int FOREIGN KEY REFERENCES Direccion (direccion_id),
        created_by INT FOREIGN KEY REFERENCES Usuario (usuario_id),
        created_at datetime NOT NULL DEFAULT GETDATE()
    );
    """
]
