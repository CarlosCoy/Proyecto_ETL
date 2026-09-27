# ---------------------------------------------------------------------------
# Definición de tablas SQL destino
# ---------------------------------------------------------------------------

SQL_TABLES = {

    # -----------------------------------------------------------------------
    # ACTDB
    # -----------------------------------------------------------------------

    "actdb": """
        CREATE TABLE IF NOT EXISTS actdb (
            codigo_empleado INTEGER PRIMARY KEY,
            nombre VARCHAR(150),
            telefono VARCHAR(20),
            fecha_nacimiento DATE,
            categoria INTEGER,
            direccion VARCHAR(200),
            barrio VARCHAR(100),
            ruta INTEGER,
            actualizado VARCHAR(10),
            ciudad VARCHAR(100)
        );
    """,

    # -----------------------------------------------------------------------
    # VAC
    # -----------------------------------------------------------------------

    "vac": """
    CREATE TABLE IF NOT EXISTS vac (
        codigo_empleado INTEGER NOT NULL,
        nombre VARCHAR(150),
        maquina VARCHAR(100),
        mes INTEGER,
        fecha_ingreso DATE,
        turno_actual INTEGER,
        vacaciones_dic VARCHAR(20),
        tipo VARCHAR(50),
        inicio_salida DATE NOT NULL,
        dias_a_tomar INTEGER,
        fin DATE,
        llegada DATE,
        observaciones VARCHAR(255),
        mes_de_salida INTEGER,
        estado VARCHAR(50),
        fecha DATE,
        dias DECIMAL(10,2),

        PRIMARY KEY (codigo_empleado, inicio_salida),

        FOREIGN KEY (codigo_empleado)
            REFERENCES actdb(codigo_empleado)
    );
""",

    # -----------------------------------------------------------------------
    # POLIVALENCIA
    # -----------------------------------------------------------------------

    "polivalencia": """
        CREATE TABLE IF NOT EXISTS polivalencia (
            codigo_empleado INTEGER PRIMARY KEY,
            planta INTEGER,
            operador VARCHAR(150),

            "117_OP_1" BOOLEAN,
            "118_OP_1" BOOLEAN,
            "202_OP_1" BOOLEAN,
            "202_AY_1" BOOLEAN,
            "203_OP_1" BOOLEAN,
            "203_AY" BOOLEAN,
            "207_OP_1" BOOLEAN,
            "208_OP_1" BOOLEAN,
            "209_OP_1" BOOLEAN,
            "BO1_OP_1" BOOLEAN,
            "300_OP_1" BOOLEAN,
            "300_AY_1" BOOLEAN,
            "301_OP_1" BOOLEAN,
            "301_AY_1" BOOLEAN,
            "315_OP_1" BOOLEAN,
            "315_AY_1" BOOLEAN,
            "316_OP_1" BOOLEAN,
            "316_PL_1" BOOLEAN,
            "316_EM_1" BOOLEAN,
            "323_OP_1" BOOLEAN,
            "323_AY_1" BOOLEAN,
            "910_OP_1" BOOLEAN,
            "429_OP_1" BOOLEAN,
            "429_AY_1" BOOLEAN,
            "429_AZ_1" BOOLEAN,
            "213_OP_1" BOOLEAN,
            "213_O2_1" BOOLEAN,
            "224_OP_1" BOOLEAN,
            "340_OP_1" BOOLEAN,
            "341_OP_1" BOOLEAN,
            "343_OP_1" BOOLEAN,
            "UTL_OP_1" BOOLEAN,
            "TMC_OP_1" BOOLEAN,
            "MONTACARGA" BOOLEAN,
            "MP" BOOLEAN,
            "DESPERDICIO" BOOLEAN,
            "ENTREGAS" BOOLEAN,
            "NOKIA 2/3" BOOLEAN,

            "94" BOOLEAN,
            "96 OP" BOOLEAN,
            "96 AYU" BOOLEAN,
            "105" BOOLEAN,
            "101" BOOLEAN,
            "97" BOOLEAN,
            "204 OP" BOOLEAN,
            "204 AYU" BOOLEAN,
            "205 OP" BOOLEAN,
            "205 AYU" BOOLEAN,
            "230" BOOLEAN,
            "235" BOOLEAN,
            "324 OP" BOOLEAN,
            "324 AY" BOOLEAN,
            "482 OP" BOOLEAN,
            "482 AY" BOOLEAN,
            "481 OP" BOOLEAN,
            "481 AY" BOOLEAN,
            "318 OP" BOOLEAN,
            "318 AY" BOOLEAN,
            "LP100" BOOLEAN,
            "NOKIA 1" BOOLEAN,
            "935 OP" BOOLEAN,
            "935 AY" BOOLEAN,
            "260 OP" BOOLEAN,
            "260 AY" BOOLEAN,
            "PEELING" BOOLEAN,
            "729" BOOLEAN,
            "136" BOOLEAN,
            "137" BOOLEAN,
            "443 OP" BOOLEAN,
            "443 AY" BOOLEAN,
            "430" BOOLEAN,
            "435" BOOLEAN,
            "UTILLAJE" BOOLEAN,
            "TMC" BOOLEAN,
            "ENTREGAS 2" BOOLEAN,
            "M. PRIMA" BOOLEAN,
            "DESPERDICIO 2" BOOLEAN,
            "MONTACARGA 2" BOOLEAN,

            "132_OP_1" BOOLEAN,
            "109_OP_1" BOOLEAN,
            "150_OP_1" BOOLEAN,
            "151_OP_1" BOOLEAN,
            "99_OP_1" BOOLEAN,
            "129_OP_1" BOOLEAN,
            "130_OP_1" BOOLEAN,
            "229_OP_1" BOOLEAN,
            "234_OP_1" BOOLEAN,
            "219_OP_1" BOOLEAN,
            "225_OP_1" BOOLEAN,
            "210_OP_1" BOOLEAN,
            "233_OP_1" BOOLEAN,
            "308_OP_1" BOOLEAN,
            "310_OP_1" BOOLEAN,
            "227_OP_1" BOOLEAN,
            "227_AYU_1" BOOLEAN,
            "321_OP_1" BOOLEAN,
            "319_OP_1" BOOLEAN,
            "302_OP_1" BOOLEAN,
            "302_AYU_1" BOOLEAN,
            "311_OP_1" BOOLEAN,
            "311_AYU_1" BOOLEAN,
            "1251_OP_1" BOOLEAN,
            "505_OP_1" BOOLEAN,
            "506_OP_1" BOOLEAN,
            "520_OP_1" BOOLEAN,
            "533_OP_1" BOOLEAN,
            "711_OP_1" BOOLEAN,
            "509_OP_1" BOOLEAN,
            "519_OP_1" BOOLEAN,
            "708_OP_1" BOOLEAN,
            "UTL_OP1" BOOLEAN,
            "TMC 2" BOOLEAN,
            "MP 2" BOOLEAN,
            "ENTREGA" BOOLEAN,
            "DESPERDICIO 3" BOOLEAN,
            "PEELING 2" BOOLEAN,
            "MONTACARGAS" BOOLEAN
        );
    """,

    # -----------------------------------------------------------------------
    # CALENDARIO
    # -----------------------------------------------------------------------

    "calendario": """
        CREATE TABLE IF NOT EXISTS calendario (
            fecha DATE PRIMARY KEY,
            anio INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            dia INTEGER NOT NULL
        );
    """,

}