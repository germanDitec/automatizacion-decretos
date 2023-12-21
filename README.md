# Generador de decretos municipales

Esta aplicación genera Decretos municipales en base a informes de evaluación para adjudicar servicios o productos necesarios en las Direcciones.

# Herramientas utilizadas
- Python Flask
- Regex (Palabras claves)
- Api GPT
- Sql Server

## Requisitos previos.
- Tener instalado GIT
- Tener instalado Python
- Tener instalado SQLServer



## Instalación y levantamiento de la aplicación.

1. Clonar el repositorio:
   
```
git clone https://github.com/germanDitec/generador-decretos.git
cd generador-decretos
```

2. Instalar entorno virtual de Python:

```
pip install virtualenv
```

3. Crear entorno de virtual de Python:

```
virtualenv venv
```

4. Activar entorno virtual de Python:

```
.\venv\Scripts\activate
```

5. Instalar librerias necesarios del proyecto:

```
pip install -r requirements.txt
```

6. Establecer variable de sesión para clave secreta:

```
set SECRET_KEY=CLAVE_SECRETA
```

7. Levantar el servidor Flask:

```
flask run
```

