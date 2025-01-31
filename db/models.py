from sqlalchemy import  Column, String, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Estado(Base):
    """
    Classe que representa um Estado brasileiro.

    Attributes:
        codigo_ibge (str): Código IBGE do estado (2 caracteres).
        feriados_nacionais (dict): Dicionário contendo os feriados nacionais observados no estado.
        feriados_estaduais (dict): Dicionário contendo os feriados estaduais observados no estado.
        municipios (list): Lista de objetos Municipio relacionados ao estado.
    """
    __tablename__ = 'estados'
    codigo_ibge = Column(String(2), primary_key=True)
    feriados_nacionais = Column(JSON)
    feriados_estaduais = Column(JSON)
    movel_estadual = Column(String)
    municipios = relationship("Municipio", backref='estado')
   


class Municipio(Base):
    """
    Classe que representa um Município brasileiro.

    Attributes:
        codigo_ibge (str): Código IBGE do município (7 caracteres).
        nome (str): Nome do município.
        estado_id (str): Código IBGE do estado ao qual o município pertence.
        feriados_municipais (dict): Dicionário contendo os feriados municipais observados no município.
    """
    __tablename__ = 'municipios'
    codigo_ibge = Column(String(7), primary_key=True)
    nome = Column(String)
    estado_id = Column(String(2), ForeignKey("estados.codigo_ibge"))
    feriados_municipais = Column(JSON)
    feriados_moveis = Column(JSON)
