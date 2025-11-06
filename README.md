# Panel de Indicadores Económicos de Chile

Este proyecto es una aplicación web completa que rastrea, almacena y visualiza indicadores económicos clave de Chile (como el Dólar, la UF, el Euro, etc.).

Consiste en dos componentes principales que trabajan juntos:

1. **Proceso ETL (Extract, Transform, Load):** Un script de Python (`etl_job.py`) que se conecta a la API pública mindicador.cl, extrae el historial completo de los indicadores, los transforma y los carga en una base de datos PostgreSQL.

2. **Backend (API REST):** Un servidor web (`run.py`) construido con Flask que expone los datos almacenados en la base de datos a través de varios endpoints (ej. `/api/indicators`)

3. **Frontend (SPA):** Una aplicación de una sola página (SPA) construida con HTML, CSS y Chart.js que consume la API del backend para mostrar los datos de forma interactiva.

## Características

* **Ingesta de Datos Históricos:** El proceso ETL está diseñado para poblar la base de datos con el historial completo de los indicadores, no solo con el valor del día.

* **Manejo de Datos "Upsert":** El script de carga (`loader.py`) es inteligente. Inserta registros nuevos, actualiza los que han cambiado y omite los duplicados, asegurando que la base de datos esté siempre actualizada sin redundancia.

* **API REST Completa:** Expone múltiples endpoints para consultar los datos, incluyendo un health check y un endpoint de historial con parámetros (`?days=`).

* **Arquitectura Limpia:** El backend utiliza un patrón Factory (`create_app`) y una arquitectura de servicios (Extractor, Transformador, Cargador) para mantener el código ordenado y testeable.

* **Panel Interactivo:** El frontend (no incluido en el backend) permite visualizar los datos en un panel y explorar el historial de cada indicador en gráficos dinámicos.

## Arquitectura General

El sistema se divide en dos procesos independientes que solo se comunican a través de la base de datos:

1. **Proceso ETL (Ingesta de Datos):** Un script (`etl_job.py`) que se conecta a la API externa, limpia los datos y los escribe en la base de datos.

2. **Servidor API (Backend):** Un servidor web (run.py) que escucha peticiones del frontend, lee la base de datos y responde con los datos en formato JSON.

``Aqui tengo que colocar el diagrama de arquitectura general``

## Stack Tecnológico

### Backend & ETL

* Python 3.9+
* Flask: Framework web para la API REST.
* SQLAlchemy: ORM para la interacción con la base de datos.
* psycopg2-binary: Driver de PostgreSQL para Python.
* Requests: Para consumir la API de mindicador.cl.
* python-dotenv: Para manejar variables de entorno.
* gunicorn: Servidor WSGI listo para producción (aunque se use en local).

### Base de Datos

* PostgreSQL

### Frontend

* HTML5
* CSS: Para el diseño y la interfaz de usuario.
* JavaScript (Vanilla): Para la lógica del cliente (fetch, manejo de eventos).
* Chart.js: Para la visualización de gráficos históricos.