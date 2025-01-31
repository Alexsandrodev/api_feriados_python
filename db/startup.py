from db.models import Estado as ModelEstado 
from db.models import Municipio as ModelMunicipio

from db.database import sessionLocal

from utils.feriados import FeriadosMoveis

import csv

def feriados_nacionais():
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





def carregar_dados(arquivo_csv):
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
                    feriados_nacionais=feriados_nacionais(),
                    movel_estadual = "Sexta-Feira Santa"
                    )

                sessionLocal.add(estado)
                sessionLocal.commit()
                
            municipo = ModelMunicipio(
                    codigo_ibge=row["codigo_ibge"],
                    nome=row['nome'],
                    estado_id = row['codigo_ibge'][0:2],
                    )                   

            sessionLocal.add(municipo)   
            sessionLocal.commit()


def criar_banco(arquivo):
    """
    Verifica se o banco de dados já foi criado. Se não, ele cria o banco de dados.

    Args:
        ano (int): Ano para calcular os feriados móveis, caso o banco precise ser criado.

    Returns:
        str: Mensagem indicando se o banco foi criado ou se já existia.
    """

    dados = sessionLocal.query(ModelEstado).all()

    if not dados:
        carregar_dados(arquivo)
        return 'banco de dados criado'
    return 'banco de dados já exite.'
