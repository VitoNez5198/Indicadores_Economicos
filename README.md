# Panel de Indicadores Económicos de Chile

Este proyecto es una aplicación web completa que rastrea, almacena y visualiza indicadores económicos clave de Chile (como el Dólar, la UF, el Euro, etc.).

Consiste en dos componentes principales que trabajan juntos:

1. Un Backend (API REST) construido con Flask y Python, que se conecta a una base de datos PostgreSQL.

2. Un Proceso ETL (Extract, Transform, Load) que se ejecuta independientemente para poblar la base de datos con datos frescos de la API pública mindicador.cl.

3. Un Frontend de una sola página (SPA) construido con HTML,  CSS y Chart.js que consume la API del backend.

## Arquitectura General

El sistema se divide en dos procesos independientes que solo se comunican a través de la base de datos:

1. Proceso ETL (Ingesta de Datos): Un script (etl_job.py) que se conecta a la API externa, limpia los datos y los escribe en la base de datos.

2. Servidor API (Backend): Un servidor web (run.py) que escucha peticiones del frontend, lee la base de datos y responde con los datos en formato JSON.

(Aquí puedes insertar tu Diagrama General de Arquitectura hecho en Draw.io)

[Placeholder para tu Diagrama de Arquitectura General]


## Stack Tecnológico

### Backend & ETL

* Python 3.9+

* Flask: Framework web para la API REST.

* SQLAlchemy: ORM para la interacción con la base de datos.

* psycopg2: Driver de PostgreSQL para Python.

* APScheduler: (Opcional) Para automatizar la ejecución del ETL.

* Requests: Para consumir la API de mindicador.cl.

* python-dotenv: Para manejar variables de entorno.

### Base de Datos

* PostgreSQL

### Frontend

* HTML5

* CSS: Para el diseño y la interfaz de usuario.

* JavaScript (Vanilla): Para la lógica del cliente (fetch, manejo de eventos).

* Chart.js: Para la visualización de gráficos históricos.

## Estructura del Proyecto

```indicadores-economicos-chile/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py         # Endpoints de la API (ej: /api/indicators)
│   │   ├── models/
│   │   │   └── indicator.py      # Modelos SQLAlchemy (Indicator, IndicatorValue)
│   │   ├── services/
│   │   │   ├── extractor.py      # Lógica para extraer de mindicador.cl
│   │   │   ├── transformer.py    # Lógica para limpiar los datos
│   │   │   └── loader.py         # Lógica para cargar datos a la DB
│   │   ├── utils/
│   │   │   └── logger.py         # Configuración del logger
│   │   ├── __init__.py           # Factory de la aplicación Flask
│   │   ├── config.py             # Carga de variables de entorno
│   │   └── extensions.py         # Inicialización de extensiones (SQLAlchemy)
│   │
│   ├── etl_job.py                # Script principal para ejecutar el ETL
│   ├── run.py                    # Script principal para iniciar el servidor API
│   ├── requirements.txt          # Dependencias de Python
│   └── .env                      # Variables de entorno (contraseñas, etc.)
│
├── database/
│   ├── __init__.sql              # Script SQL para inicializar tablas y datos maestros
│   └── seeds.sql                 # (Opcional) Datos de prueba
│
├── frontend/
│   ├── index.html                # La aplicación web de una sola página (SPA)
│   ├── css/
│   │   └── styles.css            # Estilos
│   ├── js/
│   │   ├── api.js                # Lógica de conexión con el Backend
│   │   ├── charts.js             # Lógica de renderizado de gráficos
│   │   └── main.js               # Lógica principal de la aplicación
│   └── assets/                   # (Opcional) Imágenes o íconos
├── logs/                         # Carpeta donde se guardan los logs (ignorada por .git)
├── .gitignore
└── README.md                     <-- ¡Estás aquí!
```

## Instalación y Configuración

Sigue estos pasos para levantar el proyecto en tu máquina local.

1. Prerrequisitos

    * Tener Python 3.9+ instalado.

    * Tener PostgreSQL instalado y corriendo.

    * Tener Git instalado.

2. Clonar el Repositorio

```git clone [https://github.com/VitoNez5198/Indicadores_Economicos.git](https://github.com/VitoNez5198/Indicadores_Economicos.git)
cd indicadores-economicos-chile
```


3. Configurar el Backend

    1. Navega al backend:

    ```cd backend
    ```


    2. Crea y activa un entorno virtual:

    ```# Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```


    3. Instala las dependencias:

    ```pip install -r requirements.txt
    ```


4. Configurar la Base de Datos

    1. Abre ```psql``` y crea la base de datos:

    ```psql -U postgres
    CREATE DATABASE indicadores_db;
    \q
    ```


    2. Ejecuta el script de inicialización para crear las tablas y cargar los indicadores maestros.
    Asegúrate de estar en la carpeta raíz del proyecto (indicadores-economicos-chile/).

    ```psql -U postgres -d indicadores_db -f database/__init__.sql
    ```


    Nota: Si tienes problemas de codificación con las tildes, edita __init__.sql y guárdalo como UTF-8.

5. Variables de Entorno

    1. En la carpeta backend/, crea un archivo llamado .env.

    2. Copia y pega el siguiente contenido, reemplazando con tus credenciales:

    ```# Base de datos
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=indicadores_db
    DB_USER=postgres
    DB_PASSWORD=tu_password_aqui # <-- CAMBIA ESTO

    # Flask
    FLASK_ENV=development
    FLASK_DEBUG=True
    SECRET_KEY=mi-clave-secreta-de-desarrollo

    # APIs externas
    MINDICADOR_API_URL=[https://mindicador.cl/api](https://mindicador.cl/api)

    # Scheduler
    ETL_INTERVAL_HOURS=24
    ```


## Cómo Ejecutar el Proyecto

Debes tener dos terminales abiertas en la carpeta backend/ (ambas con el venv activado).

**Terminal 1: Iniciar la API REST**

Este servidor "Mesero" debe estar siempre encendido para que el frontend funcione.

```(venv) C:\...\backend> python run.py
```


* Tu API ahora está corriendo en http://127.0.0.1:5000

* Puedes probarla en tu navegador: http://127.0.0.1:5000/api/health

**Terminal 2: Ejecutar el ETL**

Este es el "Trabajador". Lo ejecutas una vez para poblar la base de datos.

```(venv) C:\...\backend> python etl_job.py
```


Esto se conectará a mindicador.cl, procesará los datos y los cargará en tu PostgreSQL.

Vuelve a ejecutarlo en cualquier momento para cargar los datos más recientes.

**Paso 3: Abrir el Frontend**

    1. Navega a la carpeta frontend/.

    2. Abre el archivo index.html directamente en tu navegador (Google Chrome, Firefox, etc.).

    3. ¡El panel de control debería aparecer y mostrar los datos cargados por el ETL!

## Flujo del ETL (Proceso "Trabajador")

Este es el proceso que se ejecuta con python etl_job.py para obtener y guardar los datos.

(Aquí puedes insertar tu Diagrama de Flujo del ETL)

[Placeholder para tu Diagrama de Flujo del ETL]


## Flujo de la API (Proceso "Mesero")

Este es el flujo que ocurre cuando el frontend (index.html) le pide datos al backend (run.py).

(Aquí puedes insertar tu Diagrama de Flujo de la API)

[Placeholder para tu Diagrama de Flujo de la API]


## Endpoints de la API

La API REST expone los siguientes puntos de acceso:

`GET /api/health`

* Descripción: Verifica el estado de la API y la conexión a la base de datos.

* Respuesta Exitosa (200):

```{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-05T15:30:00.123456"
}
```


`GET /api/indicators`

* **Descripción:** Obtiene la lista de todos los indicadores maestros (dolar, uf, etc.) junto con su último valor registrado en la base de datos.

* **Respuesta Exitosa (200):**

```[
  {
    "id": 1,
    "code": "dolar",
    "name": "Dolar observado",
    "unit": "CLP",
    "latest_value": 945.13,
    "latest_date": "2025-11-05"
  },
  {
    "id": 2,
    "code": "uf",
    "name": "Unidad de Fomento (UF)",
    "unit": "CLP",
    "latest_value": 39623.18,
    "latest_date": "2025-11-05"
  }
  // ... más indicadores
]
```


`GET /api/indicators/<code>/history`

* Descripción: Obtiene el historial de valores para un indicador específico.

* Parámetros de Query (Opcionales):

    * `days` (int): El número de días de historial (ej: days=30). Default: 30.

    * `limit` (int): Limita el número de registros. Default: 100.

* Ejemplo: `GET /api/indicators/dolar/history?days=7`

* Respuesta Exitosa (200):

```{
  "indicator": {
    "code": "dolar",
    "name": "Dolar observado",
    "unit": "CLP"
  },
  "values": [
    {
      "value": 945.13,
      "date": "2025-11-05"
    }
    // ... más valores históricos
  ],
  "count": 1
}
```
