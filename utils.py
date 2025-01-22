from models import Estado as ModelEstado 
from models import Municipio as ModelMunicipo

from database import sessionLocal

from feriados import FeriadosMoveis

import csv

def feriados_fixos():
    """
    Cria um dicionário com os feriados fixos de todos os anos.

    Returns:
        dict: Dicionário com a chave data (formato MM-DD), contendo outro dicionário com o nome do feriado.
    """


    feriados = {}
    feriados['01-01'] = { "name" : "Ano Novo"}
    feriados['04-21'] = { "name" : "Tiradentes"}
    feriados['05-01'] = { "name" : "Dia do Trabalhador"}
    feriados['09-07'] = { "name" : "Independencia"}
    feriados['10-12'] = { "name" : "Nossa Senhora Aparecida"}
    feriados['11-02'] = { "name" : "Finados"}
    feriados['11-15'] = { "name" : "Proclamação da República"}
    feriados['12-25'] = { "name" : "Natal"}

    return feriados


def feriados_moveis(ano):
    """
    Calcula os feriados móveis para um determinado ano.

    Args:
        ano (int): Ano para o qual calcular os feriados móveis.

    Returns:
        dict: Dicionário com a data dos feriados móveis (formato MM-DD) e o nome de cada um.
    """

    feriados = FeriadosMoveis(ano)

    return feriados.feriados


def carregar_dados(arquivo_csv, ano):
    """
    Lê o arquivo CSV, linha a linha, e adiciona os dados no banco de dados,
    incluindo os feriados nacionais.

    Args:
        arquivo_csv (str): Caminho para o arquivo CSV contendo os dados dos municípios.
        ano (int): Ano para o qual calcular os feriados móveis.
    """

    with open(arquivo_csv, 'r', encoding="utf-8", errors='replace') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            estado_existente = sessionLocal.query(ModelEstado).filter_by(codigo_ibge=row["codigo_ibge"][0:2]).first()

            if not estado_existente:
                estado = ModelEstado(
                    codigo_ibge=row["codigo_ibge"][0:2],
                    feriados_nacionais= feriados_moveis(ano) | feriados_fixos(),
                    )

                sessionLocal.add(estado)
                sessionLocal.commit()
                
            municipo = ModelMunicipo(
                    codigo_ibge=row["codigo_ibge"],
                    nome=row['nome'],
                    estado_id = row['codigo_ibge'][0:2],
                    )                   

            sessionLocal.add(municipo)   
            sessionLocal.commit()



def criar_banco(arquivo, ano):
    """
    Verifica se o banco de dados já foi criado. Se não, ele cria o banco de dados.

    Args:
        ano (int): Ano para calcular os feriados móveis, caso o banco precise ser criado.

    Returns:
        str: Mensagem indicando se o banco foi criado ou se já existia.
    """

    dados = sessionLocal.query(ModelEstado).all()

    if not dados:
        carregar_dados(arquivo , ano)
        return 'banco de dados criado'
    return 'banco de dados já exite.'
    

def get_feriado_municipio(codigo_ibge, data):
    """
    Retorna o feriado para um município específico em uma data.

    Args:
        codigo_ibge (str): Código IBGE do município.
        data (str): Data no formato MM-DD.

    Returns:
        dict: Dicionário contendo o nome do feriado,
    """


    municipio = sessionLocal.query(ModelMunicipo).filter_by(codigo_ibge=codigo_ibge).first()
    if municipio.estado.feriados_estaduais:
        feriados = municipio.estado.feriados_nacionais | municipio.estado.feriados_estaduais
        return feriados.get(data)
    
    else:
        feriados = municipio.estado.feriados_nacionais
        return feriados.get(data)


def get_feriado_estado(codigo_ibge, data):
    """
    Retorna o feriado para um estado específico em uma data.

    Args:
        codigo_ibge (str): Código IBGE do estado.
        data (str): Data no formato MM-DD.

    Returns:
        dict: Dicionário contendo o nome do feriado.
    """
    estado = sessionLocal.query(ModelEstado).filter_by(codigo_ibge=codigo_ibge).first()
    feriados = estado.feriados_nacionais
    return feriados[data]

