# ETL Excel → CSV / Supabase

ETL desarrollada en Python para extraer información desde un archivo Excel con múltiples pestañas y generar un archivo CSV independiente por cada pestaña.

El objetivo de esta primera versión es preparar los datos para una futura carga en SQL, donde cada CSV representará una tabla.

---

## 1. Descripción

La ETL realiza el siguiente proceso:

```text
Archivo Excel (.xlsx / .xlsm)
            │
            ▼
     Lectura de pestañas
            │
            ▼
  Identificación de la tabla
            │
            ▼
     Limpieza de datos
            │
            ├── Encabezados → nombres de columnas
            ├── Vacíos → valores nulos
            ├── Espacios → limpieza
            └── Datos fuera de la tabla → ignorados
            │
            ▼
       Archivos CSV
            │
            ├── tabla_1.csv
            ├── tabla_2.csv
            ├── tabla_3.csv
            └── ...
```

La intención es que posteriormente el proceso pueda evolucionar de:

```text
Excel → Python → CSV
```

a:

```text
Excel → Python → SQL
```

sin tener que modificar completamente la lógica de extracción y transformación.

---

# 2. Requisitos

## Python

Se requiere Python 3.10 o superior.

Se recomienda utilizar un entorno virtual.

Verificar la instalación:

```powershell
python --version
```

Ejemplo:

```text
Python 3.13.x
```

---

# 3. Instalación

Ubicarse en la carpeta donde se encuentra el proyecto:

```powershell
cd "D:\Maestria\Semestre I\ETL\Proyecto"
```

## Crear entorno virtual

```powershell
python -m venv .venv
```

Activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si Windows bloquea la ejecución de scripts de PowerShell, puede utilizarse:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

y posteriormente:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

# 4. Instalar dependencias

La ETL utiliza:

- `pandas`: procesamiento de datos.
- `openpyxl`: lectura de archivos Excel `.xlsx` y `.xlsm`.
- `numpy`: soporte para valores nulos y cálculos de la detección de tablas.
- `psycopg`: conexión y carga a PostgreSQL (Supabase).
- `python-dotenv`: lectura de credenciales desde `.env`.
- `sqlalchemy` y `sqlacodegen`: generación y uso de las clases SQLAlchemy de las tablas.

Instalar:

```powershell
pip install -r requirements.txt
```

También se puede actualizar `pip` antes de instalar:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# 5. Estructura del proyecto

El código está organizado por etapas de la ETL (extracción, transformación y carga):

```text
Proyecto_ETL/
│
├── main.py                        # Punto de entrada (argumentos de línea de comandos)
├── generate_models.py             # Genera etl/models.py desde la base
├── requirements.txt
│
├── config/
│   └── settings.py                # Rutas, hojas a procesar y conexión (desde .env)
│
└── etl/
    ├── pipeline.py                # Orquesta Extract → Transform → Load por hoja
    ├── models.py                  # Clases SQLAlchemy (archivo generado)
    │
    ├── extract/                   # E: lectura del Excel
    │   ├── workbook.py            # Validación y apertura del archivo
    │   ├── sheet_reader.py        # Elige la tabla principal de cada hoja
    │   ├── structured_tables.py   # Tablas estructuradas de Excel
    │   └── table_detection.py     # Detección heurística de encabezado y bloque
    │
    ├── transform/                 # T: limpieza
    │   ├── cleaning.py            # Espacios, vacíos → nulos, filas vacías
    │   ├── naming.py              # Normalización de nombres de columnas y tablas
    │   └── sql_transform.py       # Adaptación de cada hoja a su tabla SQL (tipos, columnas)
    │
    ├── load/                      # L: escritura de resultados
    │   ├── csv_writer.py          # Exportación a CSV
    │   ├── sql_tables.py          # CREATE TABLE de cada tabla (llaves y relaciones)
    │   ├── sql_writer.py          # Carga (UPSERT) a Supabase / PostgreSQL
    │   └── report.py              # _etl_report.csv
    │
    └── utils/
        └── cells.py               # Utilidades de celdas (is_empty)
```

La carga a Supabase se describe en la sección 16.

Los datos de entrada y salida pueden estar fuera del proyecto, por ejemplo:

```text
Proyecto/
├── Datos/
│   └── Copia de S38_HORARIO_PROD_P1_2026 .xlsm
└── CSV/
```

La carpeta `CSV` puede estar vacía inicialmente. La ETL generará los archivos allí.

---

# 6. Ejecución

La ruta del archivo Excel es **paramétrica**.

La ejecución recomendada en PowerShell es:

```powershell
python main.py `
    --input "D:\Maestria\Semestre I\ETL\Proyecto\Datos\Copia de S38_HORARIO_PROD_P1_2026 .xlsm" `
    --output "D:\Maestria\Semestre I\ETL\Proyecto\CSV"
```

El carácter `` ` `` al final de cada línea permite continuar el comando en la siguiente línea en PowerShell.

También puede ejecutarse en una sola línea:

```powershell
python main.py --input "D:\Maestria\Semestre I\ETL\Proyecto\Datos\Copia de S38_HORARIO_PROD_P1_2026 .xlsm" --output "D:\Maestria\Semestre I\ETL\Proyecto\CSV"
```

---

# 7. Parámetros

## `--input`

Ruta del archivo Excel de entrada.

Es opcional. Si no se especifica, utiliza `Config.INPUT_FILE` de `config/settings.py`.

Ejemplo:

```powershell
--input "D:\Datos\archivo.xlsx"
```

Soporta:

- `.xlsx`
- `.xlsm`

---

## `--output`

Carpeta donde se generarán los CSV.

Es opcional.

Si no se especifica, utiliza `Config.OUTPUT_DIR` de `config/settings.py`.

Ejemplo:

```powershell
--output "D:\Datos\CSV"
```

---

## `--keep-formulas`

Por defecto, la ETL utiliza el valor almacenado/calculado de las fórmulas de Excel.

Si se desea conservar las fórmulas como texto, se puede ejecutar:

```powershell
python main.py `
    --input "D:\Datos\archivo.xlsm" `
    --output "D:\Datos\CSV" `
    --keep-formulas
```

Para la carga posterior a SQL normalmente es preferible trabajar con los valores calculados, por lo que no es necesario utilizar este parámetro en la mayoría de los casos.

---

# 8. Detección de tablas

Una de las características principales de la ETL es que **no asume que la información comienza en A1**.

Por ejemplo, una hoja puede tener:

```text
A1: Reporte de horarios
A2: Información generada automáticamente
A3:
A4:
C5: CODIGO | NOMBRE | FECHA | TURNO
C6: 001    | Carlos | ...   | 1
C7: 002    | Juan   | ...   | 2
```

La ETL intenta identificar el bloque:

```text
CODIGO | NOMBRE | FECHA | TURNO
001    | Carlos | ...   | 1
002    | Juan   | ...   | 2
```

y descartar la información que se encuentra fuera de este bloque.

---

# 9. Tablas estructuradas de Excel

Si la pestaña utiliza una **tabla estructurada de Excel**, la ETL utiliza directamente el rango definido por dicha tabla.

Por ejemplo:

```text
Tabla Excel: Tabla_Horarios
Rango: C5:H500
```

En este caso no es necesario detectar heurísticamente dónde empieza la tabla: se utiliza directamente el rango definido por Excel.

Si una hoja contiene varias tablas estructuradas, la versión actual selecciona la tabla con mayor superficie como tabla principal.

---

# 10. Celdas vacías y valores NULL

Las celdas vacías dentro de la estructura de la tabla se consideran valores nulos.

Por ejemplo, si el Excel contiene:

```text
ID | NOMBRE | TURNO | OBSERVACION
1  | Carlos | 1     | Correcto
2  | Juan   |       | 
3  | Pedro  | 2     | Correcto
```

el CSV será similar a:

```csv
id,nombre,turno,observacion
1,Carlos,1,Correcto
2,Juan,,
3,Pedro,2,Correcto
```

Los campos vacíos **no se convierten en el texto `"NULL"`**.

Esto es intencional.

Cuando posteriormente se implemente la carga hacia SQL, esos campos podrán convertirse en valores `NULL` reales.

---

# 11. Columnas completamente vacías

Una columna completamente vacía dentro de una tabla **no se elimina automáticamente**.

Esto es importante porque la columna puede formar parte de la estructura esperada de la futura tabla SQL.

Por ejemplo:

```text
ID | NOMBRE | CAMPO_NUEVO | ESTADO
1  | Juan   |             | OK
2  | Pedro  |             | OK
```

`campo_nuevo` se conserva y sus valores quedan vacíos/null.

Esto permite posteriormente crear la columna correspondiente en SQL.

---

# 12. Limpieza de nombres de columnas

Los encabezados se normalizan para facilitar su utilización como atributos SQL.

Ejemplo:

```text
Nombre Completo
```

se convierte en:

```text
nombre_completo
```

Otros ejemplos:

```text
Fecha Nacimiento  → fecha_nacimiento
Código Cliente     → codigo_cliente
TIPO/ESTADO        → tipo_estado
```

También se controlan nombres duplicados.

Por ejemplo:

```text
ID | ID | Nombre
```

se transforma en:

```text
id | id_2 | nombre
```

---

# 13. Archivos generados

Por cada pestaña procesada se genera un CSV.

Ejemplo:

```text
CSV/
├── calendario.csv
├── datos.csv
├── horarios.csv
├── puestos.csv
├── ...
└── _etl_report.csv
```

El nombre del CSV se deriva del nombre de la pestaña.

---

# 14. Reporte de ejecución

La ETL genera:

```text
_etl_report.csv
```

Este archivo permite revisar qué ocurrió con cada pestaña.

Contiene información como:

| Campo | Descripción |
|---|---|
| `hoja` | Nombre de la pestaña de Excel |
| `tabla` | Nombre normalizado que se utilizará para el CSV |
| `fuente` | Método utilizado para detectar la tabla |
| `rango` | Rango utilizado de la hoja |
| `filas` | Cantidad de registros extraídos |
| `columnas` | Cantidad de columnas |
| `estado` | Resultado del procesamiento |
| `archivo` | CSV generado |

Ejemplo:

```text
hoja,tabla,fuente,rango,filas,columnas,estado,archivo
Calendario,calendario,tabla_excel:TablaCalendario,C5:K900,895,7,OK,calendario.csv
```

Esto permite auditar rápidamente el proceso.

---

# 15. Flujo esperado

El flujo completo de esta primera versión es:

```text
                    Excel
                      │
                      │ --input
                      ▼
             main.py
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
   Detectar tabla          Limpiar datos
          │                       │
          └───────────┬───────────┘
                      ▼
                Generar CSV
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    tabla_1.csv   tabla_2.csv   tabla_3.csv
                      │
                      ▼
                _etl_report.csv
```

---

# 16. Carga a Supabase (PostgreSQL)

Además de los CSV, la ETL carga las hojas de interés en **Supabase** (PostgreSQL en la nube), con un modelo relacional:

```text
Excel → Python → CSV
              └→ Supabase (esquema project_etl)
```

## Hojas y tablas

Solo se procesan las hojas definidas en `Config.SHEETS_TO_PROCESS` (`config/settings.py`). El resto se omite (`[SKIP]`).

| Hoja | Tabla | Clave primaria | Relación |
|---|---|---|---|
| ActDB | `actdb` | `codigo_empleado` | |
| VAC | `vac` | `codigo_empleado`, `inicio_salida` | `codigo_empleado` → `actdb` |
| Polivalencia | `polivalencia` | `codigo_empleado` | |
| Calendario | `calendario` | `fecha` | |

- `etl/load/sql_tables.py` define cada tabla (`CREATE TABLE IF NOT EXISTS`) con sus tipos, llaves y relaciones.
- `etl/transform/sql_transform.py` adapta cada hoja a su tabla: renombra columnas, convierte tipos (enteros, fechas, decimales, booleanos) y descarta columnas que no pertenecen al modelo.
- `etl/load/sql_writer.py` inserta con **UPSERT**: si la clave primaria ya existe, actualiza la fila; si no, la inserta. Ejecutar la ETL varias veces no duplica datos.
- Las tablas se cargan en orden de dependencias (`actdb` antes que `vac`), sin importar el orden de las pestañas en el Excel.

## Filas descartadas

Antes de insertar, se descartan las filas que la base rechazaría:

- Filas **sin valor en la clave primaria** (por ejemplo, vacaciones sin `inicio_salida`).
- Filas de `vac` cuyo **`codigo_empleado` no existe en `actdb`**.

Se informan en consola (`[WARN]`) y en `_etl_report.csv`, en las columnas `filas_sql` (filas cargadas) y `descartadas` (cantidad y motivo). El CSV de cada hoja conserva todas las filas. Ejemplo:

```text
[OK]   SQL cargado:   79 filas → vac
[WARN] VAC: filas descartadas: 20 sin clave primaria; 14 sin codigo_empleado en actdb
```

## Configuración

1. En Supabase: botón **Connect → Session pooler**.
   (La conexión directa solo funciona con IPv6; el *Session pooler* funciona en cualquier red.)
2. Copiar `.env.example` como `.env` y completar los datos:

```powershell
Copy-Item .env.example .env
```

```text
DB_HOST=aws-0-us-east-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.<id del proyecto>
DB_PASSWORD=<contraseña de la base>
DB_SCHEMA=project_etl
```

`.env` está en `.gitignore`: **la contraseña nunca debe subirse al repositorio**. Si `DB_PASSWORD` se deja vacío, la ETL la pide por teclado al ejecutar.

El esquema es `project_etl`. No se usa `public` porque Supabase publica ese esquema a través de su API, ni `etl`, porque Supabase reserva ese nombre para su herramienta Pipelines y lo muestra como solo lectura.

Para ver las tablas en Supabase: **Table Editor**, seleccionando el esquema `project_etl`.

## Modelos SQLAlchemy

`generate_models.py` lee las tablas del esquema y escribe `etl/models.py`, con una clase por tabla, sus atributos tipados y sus relaciones:

```powershell
python generate_models.py
```

Ejemplo de uso:

```python
from sqlalchemy import URL, create_engine, select
from sqlalchemy.orm import Session

from config import Config
from etl.models import Vac

engine = create_engine(URL.create(
    "postgresql+psycopg",
    username=Config.DB_USER,
    password=Config.DB_PASSWORD,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    database=Config.DB_NAME,
))

with Session(engine) as session:
    for vac in session.scalars(select(Vac)):
        print(vac.inicio_salida, vac.dias_a_tomar, vac.actdb.nombre)
```

`etl/models.py` es un archivo generado: no se edita a mano. Si cambia el modelo (`sql_tables.py`), se ejecuta la ETL y luego `generate_models.py`.

---

# 17. Consideraciones

La detección automática de tablas es heurística cuando una hoja **no utiliza una tabla estructurada de Excel**.

Por esta razón, si una pestaña contiene múltiples bloques de información independientes, puede ser necesario definir explícitamente qué rango representa la tabla principal.

La recomendación para una ETL productiva es:

1. Utilizar tablas estructuradas de Excel cuando sea posible.
2. Utilizar detección automática como mecanismo de respaldo.
3. Mantener una configuración de excepciones para las hojas con estructuras particulares.
4. Revisar `_etl_report.csv` después de cada ejecución.

---

# 18. Ejemplo completo

Desde PowerShell:

```powershell
cd "D:\Maestria\Semestre I\ETL\Proyecto"

.\.venv\Scripts\Activate.ps1

python main.py `
    --input "D:\Maestria\Semestre I\ETL\Proyecto\Datos\Copia de S38_HORARIO_PROD_P1_2026 .xlsm" `
    --output "D:\Maestria\Semestre I\ETL\Proyecto\CSV"
```

Al finalizar se tendrá:

```text
D:\Maestria\Semestre I\ETL\Proyecto\CSV\
│
├── tabla_1.csv
├── tabla_2.csv
├── tabla_3.csv
├── ...
└── _etl_report.csv
```

El `CSV` constituye la salida intermedia de la ETL y será la fuente para la siguiente etapa de carga hacia SQL.
