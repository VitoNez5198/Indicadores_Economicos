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

* **Python 3.9+**
* **Flask:** Framework web para la API REST.
* **SQLAlchemy:** ORM para la interacción con la base de datos.
* **psycopg2-binary:** Driver de PostgreSQL para Python.
* **Requests:** Para consumir la API de mindicador.cl.
* **python-dotenv:** Para manejar variables de entorno.
* **gunicorn:** Servidor WSGI listo para producción (aunque se use en local).

### Base de Datos

* **PostgreSQL**

### Frontend

* **HTML5**
* **CSS:** Para el diseño y la interfaz de usuario.
* **JavaScript (Vanilla):** Para la lógica del cliente (fetch, manejo de eventos).
* **Chart.js:** Para la visualización de gráficos históricos.

## Estructura del Proyecto

```
indicadores-economicos-chile/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py         # Endpoints de la API (ej: /api/indicators)
│   │   ├── models/
│   │   │   └── indicator.py      # Modelos SQLAlchemy (Indicator, IndicatorValue)
│   │   ├── services/
│   │   │   ├── extractor.py    # Lógica para extraer de mindicador.cl
│   │   │   ├── transformer.py  # Lógica para limpiar los datos
│   │   │   └── loader.py       # Lógica para cargar datos a la DB
│   │   ├── utils/
│   │   │   └── logger.py         # Configuración del logger
│   │   └── __init__.py           # Factory (create_app, init_db, get_db)
│   │
│   ├── etl_job.py                # Script principal para ejecutar el ETL
│   ├── run.py                    # Script principal para iniciar el servidor API
│   ├── requirements.txt          # Dependencias de Python
│   └── .env.example              # Plantilla de variables de entorno
│
├── database/
│   └── __init__.sql              # Script SQL para inicializar tablas y datos maestros
│
├── frontend/
│   ├── index.html                # La aplicación web de una sola página (SPA)
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── api.js
│       ├── charts.js
│       └── main.js
│
├── logs/                         # Carpeta donde se guardan los logs (ignorada por .git)
├── .gitignore
└── README.md
```

## Instalación y Configuración

Sigue estos pasos para levantar el proyecto en tu máquina local.

### 1. Prerrequisitos

* Tener **Python 3.9+** instalado.
* Tener **PostgreSQL** instalado y corriendo.
* Tener **Git** instalado.

### 2. Clonar el Repositorio

```
git clone [https://github.com/VitoNez5198/indicadores-economicos-chile.git](https://github.com/VitoNez5198/indicadores-economicos-chile.git)
cd indicadores-economicos-chile
```

### 3. Configurar el Backend

  1. Navega al backend:

  ```
  cd backend
  ```

  2. Crea y activa un entorno virtual:

  ```
  # Windows
  python -m venv venv
  venv\Scripts\activate
  ```

  3. Instala las dependencias:

  ```
  pip install -r requirements.txt
  ```

## 4. Configurar la Base de Datos

  1. Abre `psql` (o tu cliente de DB preferido) y crea la base de datos:

```
  CREATE DATABASE indicadores_db;
```

  2. Ejecuta el script de inicialización para crear las tablas y cargar los indicadores maestros. (Asegúrate de estar en la carpeta raíz del proyecto).

```
  psql -U postgres -d indicadores_db -f database/__init__.sql
```

  Nota: Si tienes problemas de codificación con las tildes (ej. `Dolar observado`), asegúrate de que el archivo `__init__.sql` esté guardado con codificación UTF-8.

## Variables de Entorno

  1. En la carpeta backend/, renombra el archivo .env.example a .env.

  2. Abre el archivo .env y edita los valores (especialmente DB_PASSWORD) con tus credenciales de PostgreSQL.

```
  # Base de datos
  DB_HOST=localhost
  DB_PORT=5432
  DB_NAME=indicadores_db
  DB_USER=postgres
  DB_PASSWORD=tu_password_aqui

  # Flask
  FLASK_ENV=development
  FLASK_DEBUG=True
  SECRET_KEY=dev-secret-key-cambiar-en-produccion

  # APIs externas
  MINDICADOR_API_URL=[https://mindicador.cl/api](https://mindicador.cl/api)

  # Scheduler
  ETL_INTERVAL_HOURS=24
```

## Cómo Ejecutar el Proyecto

Debes tener dos terminales abiertas en la carpeta backend/ (ambas con el entorno virtual venv activado).

### Terminal 1: Iniciar el Servidor API

Este servidor debe estar siempre encendido para que el frontend funcione.

```
# (venv) .../backend>
python run.py
```

* Verás logs indicando que el servidor Flask está corriendo en http://127.0.0.1:5000.

* Puedes probar que funciona abriendo `http://127.0.0.1:5000/api/health` en tu navegador. Deberías ver un JSON con `{"status": "healthy"}`.

### Terminal 2: Ejecutar el Proceso ETL

Este script se ejecuta una sola vez para poblar la base de datos. Si la base de datos está vacía, cargará miles de registros (puede tomar 30-60 segundos).

```
# (venv) .../backend>
python etl_job.py
```

* Verás los logs del `extractor`, `transformer` y `loader` trabajando.

* Cuando termine, tu base de datos estará llena con todo el historial.

* Vuelve a ejecutar este comando en cualquier momento (ej. al día siguiente) para cargar solo los datos más nuevos (el `loader` omitirá los duplicados).

### Paso 3: Abrir el Frontend

  1. Navega a la carpeta `frontend/`.

  2. Abre el archivo `index.html` directamente en tu navegador (Google Chrome, Firefox, etc.).

  3. ¡El panel de control debería aparecer, conectarse a tu API en `localhost:5000` y mostrar los datos y gráficos!

## Flujo del ETL (Proceso de Ingesta)

Este es el proceso que se ejecuta con `python etl_job.py` para obtener y guardar los datos.

`insertar diagrama de flujo etl`

## Flujo de la API (Proceso de Consulta)

Este es el flujo que ocurre cuando el frontend (`index.html`) le pide datos al backend (`run.py`).

`insertar diagrama de flujo de la api`

## Endpoints de la API

La API REST expone los siguientes puntos de acceso. Todos responden con `JSON`.


`GET /api/health`

* **Descripción:** Verifica el estado de la API y la conexión a la base de datos. Es ideal para saber si el servidor está encendido.

* **Respuesta Exitosa (200):**

```
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-06T17:30:00.123456"
}
```


* **Respuesta Fallida (500):**

```
{
  "status": "unhealthy",
  "error": "...",
  "timestamp": "..."
}
```


`GET /api/indicators`

* **Descripción:** Obtiene la lista de todos los indicadores maestros (los 6 de `database/__init__.sql`) junto con su último valor registrado en la base de datos (usando la vista `latest_indicators`).

* **Respuesta Exitosa (200):**

```
[
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
  // ... 4 indicadores más
]
```


`GET /api/indicators/<code>`

* **Descripción:** Obtiene la información de un solo indicador (sin su historial), junto con su último valor.

* **Ejemplo:** `GET /api/indicators/dolar`

* **Respuesta Exitosa (200):**

```
{
  "id": 1,
  "code": "dolar",
  "name": "Dolar observado",
  "unit": "CLP",
  "latest_value": 945.13,
  "latest_date": "2025-11-05"
}
```


* **Respuesta Fallida (404):**

```
{
  "error": "Indicador no encontrado"
}
```


`GET /api/indicators/<code>/history`

* **Descripción:** Obtiene el historial de valores para un indicador específico, filtrado por un rango de días.

* **Parámetros de Query (Opcionales):**

  * `days` (int): El número de días de historial hacia atrás desde hoy. (Ej: `days=30`). **Default: 30.**

  * `limit` (int): Limita el número de registros devueltos. **Default: 100.**

Ejemplo: `GET /api/indicators/uf/history?days=7`

* **Respuesta Exitosa (200):**

```
{
  "indicator": {
    "code": "uf",
    "name": "Unidad de Fomento (UF)",
    "unit": "CLP"
  },
  "values": [
    {
      "value": 39623.18,
      "date": "2025-11-05"
    },
    {
      "value": 39620.00,
      "date": "2025-11-04"
    }
    // ... 5 valores más
  ],
  "count": 7
}
```


`GET /api/stats/latest`

* **Descripción:** Obtiene un objeto con los últimos valores de todos los indicadores, similar a `/api/indicators` pero envuelto en un objeto con metadata.

* **Respuesta Exitosa (200):**

```
{
  "timestamp": "2025-11-06T17:40:00.123456",
  "indicators": [
    {
      "code": "dolar",
      "name": "Dolar observado",
      "unit": "CLP",
      "value": 945.13,
      "date": "2025-11-05"
    }
    // ... 5 indicadores más
  ],
  "count": 6
}
```