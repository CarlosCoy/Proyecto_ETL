# ETL Excel → CSV → PostgreSQL

ETL desarrollada en Python para extraer información desde un archivo Excel con múltiples hojas, identificar las tablas de interés, limpiar y transformar los datos y cargarlos en PostgreSQL.

La solución genera un archivo CSV por cada tabla procesada y realiza la carga hacia PostgreSQL mediante `psycopg`, utilizando una estrategia de **UPSERT** para actualizar registros existentes e insertar registros nuevos.

La versión actual de la ETL se encuentra enfocada en cuatro tablas principales:

* `actdb`
* `vac`
* `polivalencia`
* `calendario`

---

# 1. Descripción

El flujo general de la ETL es:

```text
                    Archivo Excel
                         │
                         ▼
                  ┌─────────────┐
                  │   Extract   │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   Cleaning  │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ SQL Transform│
                  └──────┬──────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        ┌───────────┐        ┌─────────────┐
        │    CSV    │        │  PostgreSQL │
        └───────────┘        └──────┬──────┘
                                    │
                                    ▼
                                 UPSERT
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                      INSERT                 UPDATE
```

La arquitectura separa las responsabilidades de:

```text
Extract → Transform → Load
```

Esto permite modificar una etapa sin tener que reconstruir las demás.

---

# 2. Tablas procesadas

La ETL actual procesa únicamente las siguientes hojas:

| Hoja Excel     | Tabla PostgreSQL |
| -------------- | ---------------- |
| `ACTDB`        | `actdb`          |
| `VAC`          | `vac`            |
| `POLIVALENCIA` | `polivalencia`   |
| `CALENDARIO`   | `calendario`     |

Las demás hojas del archivo Excel se omiten.

La selección se controla mediante:

```python
Config.SHEETS_TO_PROCESS
```

Ejemplo:

```python
SHEETS_TO_PROCESS = {
    "VAC",
    "POLIVALENCIA",
    "CALENDARIO",
    "ACTDB",
}
```

Durante la ejecución, las hojas no configuradas aparecen como:

```text
[SKIP] NOMBRE_HOJA: hoja fuera del filtro.
```

---

# 3. Características principales

La ETL permite:

* Leer archivos `.xlsx` y `.xlsm`.
* Procesar múltiples hojas.
* Filtrar las hojas que participan en la carga.
* Detectar tablas aunque no comiencen en `A1`.
* Utilizar tablas estructuradas de Excel.
* Limpiar espacios y valores vacíos.
* Conservar columnas completamente vacías.
* Normalizar nombres de columnas.
* Resolver nombres de columnas duplicados.
* Transformar datos según cada tabla SQL.
* Convertir fechas, enteros, decimales y booleanos.
* Convertir valores como `#N/A` a `NULL`.
* Generar CSV por tabla.
* Crear las tablas PostgreSQL si no existen.
* Utilizar claves primarias y foráneas.
* Realizar `UPSERT`.
* Completar automáticamente ciertos registros faltantes en tablas referenciadas.
* Descartar filas que no pueden cumplir las restricciones de la base de datos.
* Reportar las filas descartadas y sus motivos.
* Generar un reporte general de ejecución.

---

# 4. Requisitos

## Python

Se requiere Python 3.10 o superior.

Verificar la instalación:

```powershell
python --version
```

Ejemplo:

```text
Python 3.13.x
```

Se recomienda utilizar un entorno virtual.

---

## PostgreSQL

La ETL utiliza PostgreSQL como sistema gestor de base de datos.

La conexión se realiza mediante la librería Python:

```text
psycopg
```

---

# 5. Instalación

Ubicarse en la carpeta del proyecto:

```powershell
cd "D:\Maestria\Semestre I\ETL\Proyecto"
```

Crear el entorno virtual:

```powershell
python -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si Windows bloquea la ejecución de scripts de PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

y posteriormente:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

# 6. Dependencias

Las principales dependencias utilizadas por la ETL son:

* `pandas` — procesamiento de datos.
* `numpy` — soporte para tipos y valores numéricos.
* `openpyxl` — lectura de archivos Excel.
* `psycopg` — conexión y carga hacia PostgreSQL.

Instalar las dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# 7. Estructura del proyecto

La estructura actual del proyecto es:

```text
Proyecto_ETL/
│
├── main.py
├── config.py
├── requirements.txt
│
├── etl/
│   │
│   ├── pipeline.py
│   │
│   ├── extract/
│   │   ├── __init__.py
│   │   ├── workbook.py
│   │   └── sheet_reader.py
│   │
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── cleaning.py
│   │   ├── naming.py
│   │   └── sql_transform.py
│   │
│   └── load/
│       ├── __init__.py
│       ├── csv_writer.py
│       ├── report.py
│       ├── sql_tables.py
│       └── sql_writer.py
│
└── CSV/
```

---

# 8. Componentes principales

## `main.py`

Es el punto de entrada de la aplicación.

Recibe los parámetros de ejecución y delega el procesamiento a:

```python
run_etl(...)
```

---

## `config.py`

Contiene la configuración general de la ETL:

* Archivo Excel de entrada.
* Directorio de salida.
* Hojas a procesar.
* Parámetros de detección.
* Configuración de PostgreSQL.

---

## `etl/pipeline.py`

Es el orquestador principal de la ETL.

La función principal es:

```python
run_etl(...)
```

Su responsabilidad es coordinar:

```text
Extract
   ↓
Cleaning
   ↓
SQL Transform
   ↓
CSV
   ↓
PostgreSQL
```

---

# 9. Extract

La extracción se encuentra en:

```text
etl/extract/
```

## `workbook.py`

Se encarga de abrir el archivo Excel.

Se soportan:

```text
.xlsx
.xlsm
```

---

## `sheet_reader.py`

Identifica y extrae la tabla principal de cada hoja.

La ETL no asume que la información comienza en `A1`.

Por ejemplo:

```text
A1: Reporte de horarios

A2: Información adicional


C5: CODIGO | NOMBRE | FECHA | TURNO
C6: 001    | Carlos | ...   | 1
C7: 002    | Juan   | ...   | 2
```

La ETL intenta identificar el bloque correspondiente a:

```text
CODIGO | NOMBRE | FECHA | TURNO
001    | Carlos | ...   | 1
002    | Juan   | ...   | 2
```

---

# 10. Tablas estructuradas de Excel

Cuando una hoja contiene una tabla estructurada de Excel, la ETL puede utilizar directamente el rango definido por dicha tabla.

Ejemplo:

```text
Tabla Excel: Tabla_Horarios
Rango: C5:H500
```

Esto permite evitar la detección heurística del rango cuando Excel ya tiene definida explícitamente la estructura de la tabla.

---

# 11. Cleaning

La limpieza genérica se encuentra en:

```text
etl/transform/cleaning.py
```

Esta etapa realiza:

* Normalización de nombres de columnas.
* Eliminación de espacios innecesarios.
* Conversión de cadenas vacías a valores nulos.
* Eliminación de filas completamente vacías.
* Conservación de columnas completamente vacías.

Por ejemplo:

```text
"   " → NULL
""    → NULL
```

Las columnas completamente vacías se conservan porque pueden formar parte de la estructura esperada de la tabla SQL.

---

# 12. Normalización de nombres

La normalización se encuentra en:

```text
etl/transform/naming.py
```

Los nombres de las columnas se adaptan a nombres compatibles con el modelo.

Ejemplo:

```text
Nombre Completo
```

se transforma en:

```text
nombre_completo
```

Otros ejemplos:

```text
Fecha Nacimiento → fecha_nacimiento
Código Cliente   → codigo_cliente
TIPO/ESTADO      → tipo_estado
```

También se controlan nombres duplicados.

Ejemplo:

```text
TMC | TMC | MP | MP
```

se transforma en:

```text
tmc | tmc_2 | mp | mp_2
```

---

# 13. Transformación para SQL

La transformación específica se encuentra en:

```text
etl/transform/sql_transform.py
```

Cada una de las cuatro tablas tiene su propia transformación:

```text
actdb
vac
polivalencia
calendario
```

---

## ACTDB

La columna:

```text
registro
```

se transforma en:

```text
codigo_empleado
```

Además se convierten los tipos correspondientes para PostgreSQL.

Entre ellos:

* Enteros.
* Fechas.
* Teléfono.
* Valores nulos.

---

## VAC

La columna:

```text
registro
```

se transforma en:

```text
codigo_empleado
```

Se convierten los campos correspondientes a:

* Enteros.
* Fechas.
* Decimales.
* Valores nulos.

Entre las columnas relevantes se encuentran:

```text
codigo_empleado
fecha_ingreso
inicio_salida
dias_a_tomar
fin
llegada
mes_de_salida
fecha
dias
```

---

## POLIVALENCIA

Las capacidades de los empleados se representan como valores booleanos.

Valores como:

```text
X
SI
SÍ
TRUE
1
YES
```

se interpretan como:

```text
TRUE
```

Los valores vacíos se interpretan como:

```text
FALSE
```

Las columnas especiales de la tabla se mantienen entre comillas en PostgreSQL, permitiendo nombres como:

```text
"117_OP_1"
"NOKIA 2/3"
"96 OP"
"M. PRIMA"
```

---

## CALENDARIO

La columna original:

```text
festivos
```

se transforma en:

```text
fecha
anio
mes
dia
```

Ejemplo:

```text
2025-01-01
```

se transforma en:

```text
fecha = 2025-01-01
anio  = 2025
mes   = 1
dia   = 1
```

La columna `fecha` es la clave primaria.

---

# 14. Modelo relacional

La ETL utiliza cuatro tablas principales:

```text
actdb
  │
  │ codigo_empleado
  ▼
vac

polivalencia

calendario
```

El modelo es:

| Tabla          | Clave primaria                     | Relación                                    |
| -------------- | ---------------------------------- | ------------------------------------------- |
| `actdb`        | `codigo_empleado`                  | —                                           |
| `vac`          | `codigo_empleado`, `inicio_salida` | `codigo_empleado` → `actdb.codigo_empleado` |
| `polivalencia` | `codigo_empleado`                  | —                                           |
| `calendario`   | `fecha`                            | —                                           |

---

# 15. Tabla ACTDB

`actdb` representa los empleados.

Su clave primaria es:

```text
codigo_empleado
```

Conceptualmente:

```text
actdb
────────────────────────
codigo_empleado  PK
nombre
telefono
fecha_nacimiento
categoria
direccion
barrio
ruta
actualizado
ciudad
```

---

# 16. Tabla VAC

`vac` representa los periodos de vacaciones.

Un empleado puede tener múltiples registros de vacaciones.

Por esta razón, la clave primaria es compuesta:

```text
codigo_empleado + inicio_salida
```

La relación con `actdb` es:

```text
vac.codigo_empleado
        │
        ▼
actdb.codigo_empleado
```

La tabla utiliza una llave foránea:

```sql
FOREIGN KEY (codigo_empleado)
    REFERENCES actdb(codigo_empleado)
```

La clave compuesta permite que un empleado tenga múltiples periodos:

```text
codigo_empleado | inicio_salida
----------------+--------------
337             | 2026-03-20
337             | 2026-08-18
337             | 2026-12-01
```

Si un periodo existente cambia, por ejemplo en su fecha de finalización, el registro se actualiza mediante `UPSERT`.

---

# 17. Tabla POLIVALENCIA

`polivalencia` representa las capacidades y máquinas para las que un empleado está habilitado.

Su clave primaria es:

```text
codigo_empleado
```

La tabla contiene:

```text
codigo_empleado
planta
operador
```

además de las diferentes capacidades representadas mediante columnas booleanas.

---

# 18. Tabla CALENDARIO

`calendario` contiene los días festivos.

Su clave primaria es:

```text
fecha
```

La tabla contiene:

```text
fecha
anio
mes
dia
```

---

# 19. Definición de tablas SQL

Las sentencias de creación se encuentran en:

```text
etl/load/sql_tables.py
```

Las tablas utilizan:

```sql
CREATE TABLE IF NOT EXISTS
```

Esto permite ejecutar nuevamente la ETL sin intentar crear una tabla que ya existe.

Las definiciones contienen:

* Tipos de datos.
* Claves primarias.
* Claves foráneas.
* Restricciones del modelo.

---

# 20. Carga a PostgreSQL

La carga se encuentra en:

```text
etl/load/sql_writer.py
```

La conexión utiliza:

```text
Python
  │
  ▼
psycopg
  │
  ▼
PostgreSQL
```

El proceso de carga realiza:

```text
Crear tabla si no existe
        ↓
Completar referencias necesarias
        ↓
Validar filas
        ↓
Descartar filas inválidas
        ↓
UPSERT
        ↓
COMMIT
```

---

# 21. UPSERT

La carga utiliza `INSERT ... ON CONFLICT`.

El comportamiento es:

```text
                     Registro
                        │
                        ▼
                ¿Existe la clave?
                   /          \
                 NO            SÍ
                 │             │
                 ▼             ▼
              INSERT        UPDATE
```

Esto permite ejecutar la ETL varias veces sin duplicar registros cuya clave ya existe.

---

## ACTDB

Clave:

```text
codigo_empleado
```

Se utiliza:

```sql
ON CONFLICT ("codigo_empleado")
DO UPDATE SET ...
```

---

## POLIVALENCIA

Clave:

```text
codigo_empleado
```

Se utiliza:

```sql
ON CONFLICT ("codigo_empleado")
DO UPDATE SET ...
```

---

## CALENDARIO

Clave:

```text
fecha
```

Se utiliza:

```sql
ON CONFLICT ("fecha")
DO UPDATE SET ...
```

---

## VAC

Clave:

```text
codigo_empleado + inicio_salida
```

Se utiliza:

```sql
ON CONFLICT ("codigo_empleado", "inicio_salida")
DO UPDATE SET ...
```

Por ejemplo, si un empleado tiene:

```text
codigo_empleado = 7102
inicio_salida   = 2026-03-20
fin             = 2026-04-14
```

y posteriormente el Excel cambia:

```text
fin = 2026-04-20
```

el registro existente se actualiza.

---

# 22. Manejo de llaves foráneas

La relación definida actualmente es:

```text
vac.codigo_empleado
        │
        ▼
actdb.codigo_empleado
```

El `sql_writer.py` valida esta relación antes de realizar la carga.

La configuración se encuentra en:

```python
FOREIGN_KEYS = {
    "vac": ("codigo_empleado", "actdb", "codigo_empleado"),
}
```

---

# 23. Completar empleados faltantes

Existe un caso particular en `VAC`.

Puede haber operarios con labores administrativas que aparecen en `VAC`, pero que no figuran inicialmente en `ACTDB`.

Para evitar que la llave foránea impida la carga, la ETL puede crear previamente el empleado faltante en `actdb`.

La configuración es:

```python
COMPLETE_REFERENCED = {
    "vac": ["codigo_empleado", "nombre"],
}
```

Cuando se encuentra un empleado de `VAC` que no existe en `ACTDB`, se crea con:

```text
codigo_empleado
nombre
```

Los demás atributos de `ACTDB` quedan como `NULL`.

Si posteriormente el empleado aparece en `ACTDB`, la carga normal de `actdb` actualiza y completa su información.

Los registros creados de esta forma no reemplazan información existente en `ACTDB`, ya que se utiliza:

```sql
ON CONFLICT DO NOTHING
```

---

# 24. Filas descartadas

Antes de realizar el `UPSERT`, la ETL identifica filas que no pueden ser cargadas correctamente.

Se contemplan principalmente:

### Filas sin clave primaria

Por ejemplo, en `VAC`:

```text
inicio_salida = NULL
```

Estas filas no pueden formar la clave:

```text
codigo_empleado + inicio_salida
```

En este caso se reportan como:

```text
pendientes por programar (sin inicio_salida)
```

Esto no se considera necesariamente un error del proceso.

La información se conserva en el CSV, pero la fila no se inserta en PostgreSQL.

---

### Filas sin llave foránea

Si una fila de `VAC` tiene:

```text
codigo_empleado
```

pero dicho empleado no existe en `ACTDB` y no puede ser completado mediante la lógica correspondiente, la fila se descarta para evitar una violación de la llave foránea.

El motivo se reporta como:

```text
sin codigo_empleado en actdb
```

---

# 25. Reporte de filas descartadas

Los descartes se informan tanto en consola como en el reporte de ejecución.

Ejemplo:

```text
[WARN] VAC: filas no cargadas:
20 pendientes por programar (sin inicio_salida)
```

El reporte permite diferenciar entre:

```text
filas extraídas
filas cargadas
filas descartadas
motivo del descarte
```

El CSV de la hoja conserva las filas originales procesadas, aunque algunas no sean cargadas a PostgreSQL.

---

# 26. Orden de carga

Las tablas deben cargarse respetando sus dependencias.

Actualmente:

```text
ACTDB
  ↓
VAC
```

porque `VAC` tiene una llave foránea hacia `ACTDB`.

El `sql_writer.py` mantiene una configuración de orden:

```python
LOAD_ORDER = list(SQL_TABLES)
```

El objetivo es que una tabla referenciada se encuentre disponible antes de cargar la tabla que depende de ella.

---

# 27. Conversión de valores NULL

Los valores vacíos se convierten a:

```python
None
```

antes de enviarse a PostgreSQL.

También se reconocen valores como:

```text
#N/A
#NA
N/A
NA
NULL
NONE
```

como valores nulos durante la transformación SQL.

De esta manera, PostgreSQL recibe:

```sql
NULL
```

en lugar de cadenas de texto que representen valores nulos.

---

# 28. Identificadores SQL especiales

Algunas columnas de `POLIVALENCIA` contienen espacios, `/`, puntos u otros caracteres.

Ejemplos:

```text
"117_OP_1"
"NOKIA 2/3"
"96 OP"
"M. PRIMA"
```

`sql_writer.py` utiliza `quote_identifier()` para escapar correctamente estos nombres.

Esto permite generar sentencias SQL válidas sin modificar los nombres definidos por el modelo.

---

# 29. Archivos CSV generados

Por cada tabla procesada se genera un CSV:

```text
CSV/
│
├── actdb.csv
├── vac.csv
├── polivalencia.csv
├── calendario.csv
└── _etl_report.csv
```

El CSV constituye una salida intermedia útil para:

* Revisar los datos transformados.
* Auditar la extracción.
* Verificar columnas y tipos.
* Analizar filas que posteriormente no fueron cargadas a PostgreSQL.

---

# 30. Reporte de ejecución

La ETL genera:

```text
_etl_report.csv
```

El reporte contiene información sobre cada hoja procesada.

Entre los campos se encuentran:

| Campo      | Descripción                             |
| ---------- | --------------------------------------- |
| `hoja`     | Nombre de la hoja Excel                 |
| `tabla`    | Tabla destino                           |
| `fuente`   | Método utilizado para detectar la tabla |
| `rango`    | Rango utilizado                         |
| `filas`    | Filas procesadas                        |
| `columnas` | Columnas procesadas                     |
| `estado`   | Resultado del procesamiento             |
| `archivo`  | CSV generado                            |

El reporte permite revisar rápidamente la ejecución completa.

---

# 31. Ejecución

La ruta del archivo Excel es paramétrica.

Ejemplo:

```powershell
python main.py `
    --input "D:\Maestria\Semestre I\ETL\Proyecto\Datos\Copia de S38_HORARIO_PROD_P1_2026 .xlsm" `
    --output "D:\Maestria\Semestre I\ETL\Proyecto\CSV"
```

También puede ejecutarse en una sola línea:

```powershell
python main.py --input "D:\Datos\archivo.xlsm" --output "D:\Datos\CSV"
```

---

# 32. Parámetros

## `--input`

Ruta del archivo Excel de entrada.

Si no se especifica, se utiliza:

```python
Config.INPUT_FILE
```

Ejemplo:

```powershell
--input "D:\Datos\archivo.xlsx"
```

Soporta:

```text
.xlsx
.xlsm
```

---

## `--output`

Directorio donde se generan los CSV y el reporte.

Si no se especifica, se utiliza:

```python
Config.OUTPUT_DIR
```

Ejemplo:

```powershell
--output "D:\Datos\CSV"
```

---

## `--keep-formulas`

Permite conservar las fórmulas de Excel como fórmulas en lugar de utilizar sus valores calculados.

Ejemplo:

```powershell
python main.py `
    --input "D:\Datos\archivo.xlsm" `
    --output "D:\Datos\CSV" `
    --keep-formulas
```

Para la carga SQL normalmente se utilizan los valores calculados.

---

# 33. Configuración de PostgreSQL

La configuración de conexión se encuentra en:

```text
config.py
```

Los parámetros principales son:

```python
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

La contraseña no debe almacenarse directamente en el repositorio.

La conexión debe configurarse de acuerdo con la instancia PostgreSQL utilizada para el proyecto.

---

# 34. Flujo completo de ejecución

El pipeline completo funciona de la siguiente manera:

```text
                         Excel
                           │
                           ▼
                    ┌────────────┐
                    │   Extract  │
                    └─────┬──────┘
                          │
                          ▼
                    ┌────────────┐
                    │  Cleaning  │
                    └─────┬──────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ SQL Transform  │
                  └───────┬────────┘
                          │
                    ┌─────┴─────┐
                    │           │
                    ▼           ▼
                  CSV       PostgreSQL
                              │
                              ▼
                       Validar llaves
                              │
                              ▼
                   Completar referencias
                              │
                              ▼
                        Descartar
                         inválidas
                              │
                              ▼
                           UPSERT
                              │
                              ▼
                           COMMIT
                              │
                              ▼
                           Reporte
```

---

# 35. Ejemplo de ejecución

Desde PowerShell:

```powershell
cd "D:\Maestria\Semestre I\ETL\Proyecto"

.\.venv\Scripts\Activate.ps1

python main.py `
    --input "D:\Maestria\Semestre I\ETL\Proyecto\Datos\Copia de S38_HORARIO_PROD_P1_2026 .xlsm" `
    --output "D:\Maestria\Semestre I\ETL\Proyecto\CSV"
```

Durante la ejecución se muestran mensajes similares a:

```text
Excel origen: D:\...\archivo.xlsm
Salida:       D:\...\CSV
Hojas Excel:  12
Hojas filtro: ACTDB, CALENDARIO, POLIVALENCIA, VAC
```

Para una carga exitosa:

```text
[OK]   CSV generado: actdb.csv
[OK]   SQL cargado:   500 filas → actdb

[OK]   CSV generado: vac.csv
[OK]   SQL cargado:   93 filas → vac
```

Para filas no cargadas:

```text
[WARN] VAC: filas no cargadas:
20 pendientes por programar (sin inicio_salida)
```

---

# 36. Reejecución de la ETL

La ETL está diseñada para ejecutarse varias veces sobre los mismos datos.

En la primera ejecución:

```text
Tabla no existe
       ↓
CREATE TABLE
       ↓
INSERT
```

En ejecuciones posteriores:

```text
Tabla ya existe
       ↓
CREATE TABLE IF NOT EXISTS
       ↓
UPSERT
```

Para un registro cuya clave ya existe:

```text
UPDATE
```

Para un registro nuevo:

```text
INSERT
```

Esto evita duplicar registros durante ejecuciones repetidas.

---

# 37. Arquitectura

La separación de responsabilidades es:

```text
EXTRACT
│
├── workbook.py
└── sheet_reader.py

TRANSFORM
│
├── cleaning.py
├── naming.py
└── sql_transform.py

LOAD
│
├── csv_writer.py
├── sql_tables.py
├── sql_writer.py
└── report.py
```

El `pipeline.py` coordina las diferentes etapas.

Esta separación permite evolucionar cada componente de forma independiente.

---

# 38. Consideraciones

La detección automática de tablas es heurística cuando una hoja no utiliza una tabla estructurada de Excel.

Si una hoja contiene múltiples bloques de información independientes, puede ser necesario ajustar la lógica de extracción para identificar correctamente la tabla principal.

Se recomienda:

1. Utilizar tablas estructuradas de Excel cuando sea posible.
2. Utilizar la detección automática como mecanismo de respaldo.
3. Mantener la configuración de hojas limitada a las tablas requeridas.
4. Revisar los CSV generados después de cada ejecución.
5. Revisar `_etl_report.csv`.
6. Verificar especialmente las filas descartadas antes de considerar una carga como completamente exitosa.

---

# 39. Modelo actual

La versión actual de la ETL se encuentra deliberadamente enfocada en cuatro tablas:

```text
┌─────────────────────┐
│        ACTDB        │
│ codigo_empleado PK  │
└──────────┬──────────┘
           │
           │ FK
           ▼
┌──────────────────────────────┐
│             VAC              │
│ codigo_empleado              │
│ inicio_salida                │
│ PK compuesta                 │
└──────────────────────────────┘


┌──────────────────────────────┐
│        POLIVALENCIA          │
│ codigo_empleado PK           │
│ capacidades BOOLEAN          │
└──────────────────────────────┘


┌──────────────────────────────┐
│          CALENDARIO          │
│ fecha PK                     │
│ anio                         │
│ mes                          │
│ dia                          │
└──────────────────────────────┘
```

Estas cuatro tablas constituyen actualmente el alcance principal de la carga SQL.

---

# 40. Resultado final

La ETL permite transformar el archivo Excel de origen en un modelo relacional PostgreSQL mediante el siguiente proceso:

```text
Excel
  │
  ▼
Extracción de tablas
  │
  ▼
Limpieza
  │
  ▼
Transformación
  │
  ├──────────────► CSV
  │
  ▼
Validación de llaves
  │
  ▼
Carga PostgreSQL
  │
  ▼
UPSERT
  │
  ▼
Reporte de ejecución
```

El resultado es una carga reproducible que puede ejecutarse nuevamente para **insertar registros nuevos y actualizar registros existentes**, manteniendo las relaciones definidas entre las cuatro tablas principales.
