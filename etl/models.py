# ---------------------------------------------------------------------------
# Modelos SQLAlchemy: una clase por tabla del esquema "project_etl".
#
# ARCHIVO GENERADO por generate_models.py a partir de la base de datos.
# No editar a mano: se sobrescribe cada vez que se regenera.
# ---------------------------------------------------------------------------

from typing import Optional
import datetime
import decimal

from sqlalchemy import Boolean, Date, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Actdb(Base):
    __tablename__ = 'actdb'
    __table_args__ = (
        PrimaryKeyConstraint('codigo_empleado', name='actdb_pkey'),
        {'schema': 'project_etl'}
    )

    codigo_empleado: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(150))
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    fecha_nacimiento: Mapped[Optional[datetime.date]] = mapped_column(Date)
    categoria: Mapped[Optional[int]] = mapped_column(Integer)
    direccion: Mapped[Optional[str]] = mapped_column(String(200))
    barrio: Mapped[Optional[str]] = mapped_column(String(100))
    ruta: Mapped[Optional[int]] = mapped_column(Integer)
    actualizado: Mapped[Optional[str]] = mapped_column(String(20))
    ciudad: Mapped[Optional[str]] = mapped_column(String(100))

    vac: Mapped[list['Vac']] = relationship('Vac', back_populates='actdb')


class Calendario(Base):
    __tablename__ = 'calendario'
    __table_args__ = (
        PrimaryKeyConstraint('fecha', name='calendario_pkey'),
        {'schema': 'project_etl'}
    )

    fecha: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    dia: Mapped[int] = mapped_column(Integer, nullable=False)


class Polivalencia(Base):
    __tablename__ = 'polivalencia'
    __table_args__ = (
        PrimaryKeyConstraint('codigo_empleado', name='polivalencia_pkey'),
        {'schema': 'project_etl'}
    )

    codigo_empleado: Mapped[int] = mapped_column(Integer, primary_key=True)
    planta: Mapped[Optional[int]] = mapped_column(Integer)
    operador: Mapped[Optional[str]] = mapped_column(String(150))
    _117_OP_1: Mapped[Optional[bool]] = mapped_column('117_OP_1', Boolean)
    _118_OP_1: Mapped[Optional[bool]] = mapped_column('118_OP_1', Boolean)
    _202_OP_1: Mapped[Optional[bool]] = mapped_column('202_OP_1', Boolean)
    _202_AY_1: Mapped[Optional[bool]] = mapped_column('202_AY_1', Boolean)
    _203_OP_1: Mapped[Optional[bool]] = mapped_column('203_OP_1', Boolean)
    _203_AY: Mapped[Optional[bool]] = mapped_column('203_AY', Boolean)
    _207_OP_1: Mapped[Optional[bool]] = mapped_column('207_OP_1', Boolean)
    _208_OP_1: Mapped[Optional[bool]] = mapped_column('208_OP_1', Boolean)
    _209_OP_1: Mapped[Optional[bool]] = mapped_column('209_OP_1', Boolean)
    BO1_OP_1: Mapped[Optional[bool]] = mapped_column(Boolean)
    _300_OP_1: Mapped[Optional[bool]] = mapped_column('300_OP_1', Boolean)
    _300_AY_1: Mapped[Optional[bool]] = mapped_column('300_AY_1', Boolean)
    _301_OP_1: Mapped[Optional[bool]] = mapped_column('301_OP_1', Boolean)
    _301_AY_1: Mapped[Optional[bool]] = mapped_column('301_AY_1', Boolean)
    _315_OP_1: Mapped[Optional[bool]] = mapped_column('315_OP_1', Boolean)
    _315_AY_1: Mapped[Optional[bool]] = mapped_column('315_AY_1', Boolean)
    _316_OP_1: Mapped[Optional[bool]] = mapped_column('316_OP_1', Boolean)
    _316_PL_1: Mapped[Optional[bool]] = mapped_column('316_PL_1', Boolean)
    _316_EM_1: Mapped[Optional[bool]] = mapped_column('316_EM_1', Boolean)
    _323_OP_1: Mapped[Optional[bool]] = mapped_column('323_OP_1', Boolean)
    _323_AY_1: Mapped[Optional[bool]] = mapped_column('323_AY_1', Boolean)
    _910_OP_1: Mapped[Optional[bool]] = mapped_column('910_OP_1', Boolean)
    _429_OP_1: Mapped[Optional[bool]] = mapped_column('429_OP_1', Boolean)
    _429_AY_1: Mapped[Optional[bool]] = mapped_column('429_AY_1', Boolean)
    _429_AZ_1: Mapped[Optional[bool]] = mapped_column('429_AZ_1', Boolean)
    _213_OP_1: Mapped[Optional[bool]] = mapped_column('213_OP_1', Boolean)
    _213_O2_1: Mapped[Optional[bool]] = mapped_column('213_O2_1', Boolean)
    _224_OP_1: Mapped[Optional[bool]] = mapped_column('224_OP_1', Boolean)
    _340_OP_1: Mapped[Optional[bool]] = mapped_column('340_OP_1', Boolean)
    _341_OP_1: Mapped[Optional[bool]] = mapped_column('341_OP_1', Boolean)
    _343_OP_1: Mapped[Optional[bool]] = mapped_column('343_OP_1', Boolean)
    UTL_OP_1: Mapped[Optional[bool]] = mapped_column(Boolean)
    TMC_OP_1: Mapped[Optional[bool]] = mapped_column(Boolean)
    MONTACARGA: Mapped[Optional[bool]] = mapped_column(Boolean)
    MP: Mapped[Optional[bool]] = mapped_column(Boolean)
    DESPERDICIO: Mapped[Optional[bool]] = mapped_column(Boolean)
    ENTREGAS: Mapped[Optional[bool]] = mapped_column(Boolean)
    NOKIA_2_3: Mapped[Optional[bool]] = mapped_column('NOKIA 2/3', Boolean)
    _94: Mapped[Optional[bool]] = mapped_column('94', Boolean)
    _96_OP: Mapped[Optional[bool]] = mapped_column('96 OP', Boolean)
    _96_AYU: Mapped[Optional[bool]] = mapped_column('96 AYU', Boolean)
    _105: Mapped[Optional[bool]] = mapped_column('105', Boolean)
    _101: Mapped[Optional[bool]] = mapped_column('101', Boolean)
    _97: Mapped[Optional[bool]] = mapped_column('97', Boolean)
    _204_OP: Mapped[Optional[bool]] = mapped_column('204 OP', Boolean)
    _204_AYU: Mapped[Optional[bool]] = mapped_column('204 AYU', Boolean)
    _205_OP: Mapped[Optional[bool]] = mapped_column('205 OP', Boolean)
    _205_AYU: Mapped[Optional[bool]] = mapped_column('205 AYU', Boolean)
    _230: Mapped[Optional[bool]] = mapped_column('230', Boolean)
    _235: Mapped[Optional[bool]] = mapped_column('235', Boolean)
    _324_OP: Mapped[Optional[bool]] = mapped_column('324 OP', Boolean)
    _324_AY: Mapped[Optional[bool]] = mapped_column('324 AY', Boolean)
    _482_OP: Mapped[Optional[bool]] = mapped_column('482 OP', Boolean)
    _482_AY: Mapped[Optional[bool]] = mapped_column('482 AY', Boolean)
    _481_OP: Mapped[Optional[bool]] = mapped_column('481 OP', Boolean)
    _481_AY: Mapped[Optional[bool]] = mapped_column('481 AY', Boolean)
    _318_OP: Mapped[Optional[bool]] = mapped_column('318 OP', Boolean)
    _318_AY: Mapped[Optional[bool]] = mapped_column('318 AY', Boolean)
    LP100: Mapped[Optional[bool]] = mapped_column(Boolean)
    NOKIA_1: Mapped[Optional[bool]] = mapped_column('NOKIA 1', Boolean)
    _935_OP: Mapped[Optional[bool]] = mapped_column('935 OP', Boolean)
    _935_AY: Mapped[Optional[bool]] = mapped_column('935 AY', Boolean)
    _260_OP: Mapped[Optional[bool]] = mapped_column('260 OP', Boolean)
    _260_AY: Mapped[Optional[bool]] = mapped_column('260 AY', Boolean)
    PEELING: Mapped[Optional[bool]] = mapped_column(Boolean)
    _729: Mapped[Optional[bool]] = mapped_column('729', Boolean)
    _136: Mapped[Optional[bool]] = mapped_column('136', Boolean)
    _137: Mapped[Optional[bool]] = mapped_column('137', Boolean)
    _443_OP: Mapped[Optional[bool]] = mapped_column('443 OP', Boolean)
    _443_AY: Mapped[Optional[bool]] = mapped_column('443 AY', Boolean)
    _430: Mapped[Optional[bool]] = mapped_column('430', Boolean)
    _435: Mapped[Optional[bool]] = mapped_column('435', Boolean)
    UTILLAJE: Mapped[Optional[bool]] = mapped_column(Boolean)
    TMC: Mapped[Optional[bool]] = mapped_column(Boolean)
    ENTREGAS_2: Mapped[Optional[bool]] = mapped_column('ENTREGAS 2', Boolean)
    M__PRIMA: Mapped[Optional[bool]] = mapped_column('M. PRIMA', Boolean)
    DESPERDICIO_2: Mapped[Optional[bool]] = mapped_column('DESPERDICIO 2', Boolean)
    MONTACARGA_2: Mapped[Optional[bool]] = mapped_column('MONTACARGA 2', Boolean)
    _132_OP_1: Mapped[Optional[bool]] = mapped_column('132_OP_1', Boolean)
    _109_OP_1: Mapped[Optional[bool]] = mapped_column('109_OP_1', Boolean)
    _150_OP_1: Mapped[Optional[bool]] = mapped_column('150_OP_1', Boolean)
    _151_OP_1: Mapped[Optional[bool]] = mapped_column('151_OP_1', Boolean)
    _99_OP_1: Mapped[Optional[bool]] = mapped_column('99_OP_1', Boolean)
    _129_OP_1: Mapped[Optional[bool]] = mapped_column('129_OP_1', Boolean)
    _130_OP_1: Mapped[Optional[bool]] = mapped_column('130_OP_1', Boolean)
    _229_OP_1: Mapped[Optional[bool]] = mapped_column('229_OP_1', Boolean)
    _234_OP_1: Mapped[Optional[bool]] = mapped_column('234_OP_1', Boolean)
    _219_OP_1: Mapped[Optional[bool]] = mapped_column('219_OP_1', Boolean)
    _225_OP_1: Mapped[Optional[bool]] = mapped_column('225_OP_1', Boolean)
    _210_OP_1: Mapped[Optional[bool]] = mapped_column('210_OP_1', Boolean)
    _233_OP_1: Mapped[Optional[bool]] = mapped_column('233_OP_1', Boolean)
    _308_OP_1: Mapped[Optional[bool]] = mapped_column('308_OP_1', Boolean)
    _310_OP_1: Mapped[Optional[bool]] = mapped_column('310_OP_1', Boolean)
    _227_OP_1: Mapped[Optional[bool]] = mapped_column('227_OP_1', Boolean)
    _227_AYU_1: Mapped[Optional[bool]] = mapped_column('227_AYU_1', Boolean)
    _321_OP_1: Mapped[Optional[bool]] = mapped_column('321_OP_1', Boolean)
    _319_OP_1: Mapped[Optional[bool]] = mapped_column('319_OP_1', Boolean)
    _302_OP_1: Mapped[Optional[bool]] = mapped_column('302_OP_1', Boolean)
    _302_AYU_1: Mapped[Optional[bool]] = mapped_column('302_AYU_1', Boolean)
    _311_OP_1: Mapped[Optional[bool]] = mapped_column('311_OP_1', Boolean)
    _311_AYU_1: Mapped[Optional[bool]] = mapped_column('311_AYU_1', Boolean)
    _1251_OP_1: Mapped[Optional[bool]] = mapped_column('1251_OP_1', Boolean)
    _505_OP_1: Mapped[Optional[bool]] = mapped_column('505_OP_1', Boolean)
    _506_OP_1: Mapped[Optional[bool]] = mapped_column('506_OP_1', Boolean)
    _520_OP_1: Mapped[Optional[bool]] = mapped_column('520_OP_1', Boolean)
    _533_OP_1: Mapped[Optional[bool]] = mapped_column('533_OP_1', Boolean)
    _711_OP_1: Mapped[Optional[bool]] = mapped_column('711_OP_1', Boolean)
    _509_OP_1: Mapped[Optional[bool]] = mapped_column('509_OP_1', Boolean)
    _519_OP_1: Mapped[Optional[bool]] = mapped_column('519_OP_1', Boolean)
    _708_OP_1: Mapped[Optional[bool]] = mapped_column('708_OP_1', Boolean)
    UTL_OP1: Mapped[Optional[bool]] = mapped_column(Boolean)
    TMC_2: Mapped[Optional[bool]] = mapped_column('TMC 2', Boolean)
    MP_2: Mapped[Optional[bool]] = mapped_column('MP 2', Boolean)
    ENTREGA: Mapped[Optional[bool]] = mapped_column(Boolean)
    DESPERDICIO_3: Mapped[Optional[bool]] = mapped_column('DESPERDICIO 3', Boolean)
    PEELING_2: Mapped[Optional[bool]] = mapped_column('PEELING 2', Boolean)
    MONTACARGAS: Mapped[Optional[bool]] = mapped_column(Boolean)


class Vac(Base):
    __tablename__ = 'vac'
    __table_args__ = (
        ForeignKeyConstraint(['codigo_empleado'], ['project_etl.actdb.codigo_empleado'], name='vac_codigo_empleado_fkey'),
        PrimaryKeyConstraint('codigo_empleado', 'inicio_salida', name='vac_pkey'),
        {'schema': 'project_etl'}
    )

    codigo_empleado: Mapped[int] = mapped_column(Integer, primary_key=True)
    inicio_salida: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(150))
    maquina: Mapped[Optional[str]] = mapped_column(String(100))
    mes: Mapped[Optional[int]] = mapped_column(Integer)
    fecha_ingreso: Mapped[Optional[datetime.date]] = mapped_column(Date)
    turno_actual: Mapped[Optional[int]] = mapped_column(Integer)
    vacaciones_dic: Mapped[Optional[str]] = mapped_column(String(20))
    tipo: Mapped[Optional[str]] = mapped_column(String(50))
    dias_a_tomar: Mapped[Optional[int]] = mapped_column(Integer)
    fin: Mapped[Optional[datetime.date]] = mapped_column(Date)
    llegada: Mapped[Optional[datetime.date]] = mapped_column(Date)
    observaciones: Mapped[Optional[str]] = mapped_column(String(255))
    mes_de_salida: Mapped[Optional[int]] = mapped_column(Integer)
    estado: Mapped[Optional[str]] = mapped_column(String(50))
    fecha: Mapped[Optional[datetime.date]] = mapped_column(Date)
    dias: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))

    actdb: Mapped['Actdb'] = relationship('Actdb', back_populates='vac')
