from fastapi import status

from sqlalchemy.orm.attributes import flag_modified

from models import Estado as ModelEstado 
from models import Municipio as ModelMunicipio

from database import sessionLocal

from feriados import FeriadosMoveis

import csv
import datetime


def formated_feriado_name(name:str):
    name = name.replace("_", "-")
    name = name.rsplit("-")
    if len(name) == 1:
        return name[0].capitalize()
    if len(name) == 2:
        name = name[0].capitalize() +" "+ name[1].capitalize()
        return name
    if len(name) == 3:
        name = name[0].capitalize() +"-"+ name[1].capitalize() + " " + name[2].capitalize()
        return name


def validar_data(data:str):

    data_list = data.split("-")
    if len(data_list)==3:
        ano = data_list[0]
        mes = data_list[1]
        dia = data_list[2]

    if len(data_list)==2:
        ano = 2020
        mes = data_list[0]
        dia = data_list[1]

    data = f"{mes}-{dia}"
    try:
        ano = int(ano)
        mes = int(mes)
        dia = int(dia)
        validação_de_dados = datetime.date(ano, mes, dia).strftime("%Y-%m-%d")
    except ValueError:
        return None, None
    return ano, data

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


def get_feriados_moveis(ano):
    """
    Calcula os feriados móveis para um determinado ano.

    Args:
        ano (int): Ano para o qual calcular os feriados móveis.

    Returns:
        dict: Dicionário com a data dos feriados móveis (formato MM-DD) e o nome de cada um.
    """

    feriados = FeriadosMoveis(ano)

    return feriados.feriados


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
    

def get_feriado_municipio(codigo_ibge:str, ano:int, data:str):
    """
        Retorna o feriado para um município específico em uma data.

        Args:
            codigo_ibge (str): Código IBGE do município.
            data (str): Data no formato MM-DD.

        Returns:
            dict: Dicionário contendo o nome do feriado,
    """

    municipio = sessionLocal.query(ModelMunicipio).filter_by(codigo_ibge=codigo_ibge).first()
    estado = municipio.estado
    feriados_moveis = get_feriados_moveis(ano)

    if feriados_moveis.get(data):
        for value in feriados_moveis.values():
            if feriados_moveis[data]["name"] == value["name"]:
                if municipio.feriados_moveis:
                    if value["name"] in municipio.feriados_moveis:
                        return value


    if estado.feriados_estaduais:
        if municipio.feriados_municipais:
            feriados = estado.feriados_nacionais | estado.feriados_estaduais | municipio.feriados_municipais

            return feriados.get(data)
    
        feriados = estado.feriados_nacionais | estado.feriados_estaduais 
        return feriados.get(data)

    if municipio.feriados_municipais:
        feriados = estado.feriados_nacionais | municipio.feriados_municipais
        
        return feriados.get(data)
    
    feriados = estado.feriados_nacionais
    return feriados.get(data)


def get_feriado_estado(codigo_ibge:str, data:str):
    """
        Retorna o feriado para um estado específico em uma data.

        Args:
            codigo_ibge (str): Código IBGE do estado.
            data (str): Data no formato MM-DD.

        Returns:
            dict: Dicionário contendo o nome do feriado.
    """
    estado = sessionLocal.query(ModelEstado).filter_by(codigo_ibge=codigo_ibge).first()
    if estado.feriados_estaduais:
        feriados = estado.feriados_nacionais | estado.feriados_estaduais
        
        return feriados.get(data)
    
    else:
        feriados = estado.feriados_nacionais
        return feriados.get(data)


def append_feriado_estado(codigo_ibge: str, data: str, feriado: dict):
    estado = sessionLocal.query(ModelEstado).filter_by(codigo_ibge=codigo_ibge).first()


    if estado:
        if estado.feriados_estaduais:  

            if estado.feriados_estaduais.get(data):
                estado.feriados_estaduais[data]["name"] = feriado["name"]
                response = status.HTTP_200_OK

            else:
                estado.feriados_estaduais.update({data: feriado})
                response = status.HTTP_201_CREATED

        else:
            estado.feriados_estaduais = {data:feriado}
            response = status.HTTP_201_CREATED
        
        flag_modified(estado, "feriados_estaduais")

        sessionLocal.commit()
        sessionLocal.close()
        return "complet", response

    else:
        return estado


def append_feriado_municipal(codigo_ibge: str, data: str, feriado:dict):
    municipio = sessionLocal.query(ModelMunicipio).filter_by(codigo_ibge=codigo_ibge).first()

    if municipio:
        if municipio.feriados_municipais:
            if municipio.feriados_municipais.get(data):
                municipio.feriados_municipais[data]["name"] = feriado["name"]
                reponse = status.HTTP_200_OK

            else:
                municipio.feriados_municipais.update({data, feriado})
                reponse =  status.HTTP_201_CREATED
        else:
            municipio.feriados_municipais = {data: feriado}
            reponse = status.HTTP_201_CREATED

        flag_modified(municipio, "feriados_municipais")
        sessionLocal.commit()
        sessionLocal.close()
        return "complet",reponse
    
    else:
        return None,municipio
    

def delete_feriado_by_id(codigo_ibge:str, data:str):

    if len(codigo_ibge) == 7:
        municipio = sessionLocal.query(ModelMunicipio).filter_by(codigo_ibge=codigo_ibge).first()
        
        estado = municipio.estado
        
        if municipio:
            if municipio.feriados_municipais:
                if municipio.feriados_municipais.get(data):
                    del  municipio.feriados_municipais[data]

                    flag_modified(municipio, "feriados_municipais")
                    sessionLocal.commit()    
                    sessionLocal.close()    
                    return status.HTTP_204_NO_CONTENT

            if estado.feriados_estaduais:
                dados = estado.feriados_estaduais | estado.feriados_nacionais

                if dados.get(data):                            
                    return status.HTTP_403_FORBIDDEN

            if estado.feriados_nacionais.get(data):
                return status.HTTP_403_FORBIDDEN
            
            return status.HTTP_404_NOT_FOUND
        
        else:
            return status.HTTP_404_NOT_FOUND
    
    if len(codigo_ibge) == 2:
        estado = sessionLocal.query(ModelEstado).filter_by(codigo_ibge=codigo_ibge).first()

        if estado:
            if estado.feriados_estaduais:
                if estado.feriados_estaduais.get(data):
                    del  estado.feriados_estaduais[data]

                    flag_modified(estado, "feriados_estaduais")
                    sessionLocal.commit()    
                    sessionLocal.close()    
                    return status.HTTP_204_NO_CONTENT
            if estado.feriados_nacionais.get(data):
                return status.HTTP_403_FORBIDDEN
            return status.HTTP_404_NOT_FOUND
        else:
            return status.HTTP_404_NOT_FOUND


def criate_feriado_movel(codigo_ibge:str, feriado_movel:str):    
    municipio = sessionLocal.query(ModelMunicipio).filter_by(codigo_ibge=codigo_ibge).first()

    print(feriado_movel)
    feriados_moveis = get_feriados_moveis(2025)
    if municipio:
        for value in feriados_moveis.values():
            
            if feriado_movel.lower() == value["name"].lower():
                print(feriado_movel.lower() == value["name"].lower())
                print(municipio.feriados_moveis)
                if municipio.feriados_moveis == None:
                    print(feriado_movel)
                    municipio.feriados_moveis = [feriado_movel]
                    flag_modified(municipio, "feriados_moveis")
                    sessionLocal.commit()
                    sessionLocal.close()
                    return status.HTTP_201_CREATED
                else:
                    if feriado_movel in municipio.feriados_moveis:
                        return status.HTTP_201_CREATED
                    print(feriado_movel)
                    print(municipio.feriados_moveis)
                    municipio.feriados_moveis.append(feriado_movel)

                
                flag_modified(municipio, "feriados_moveis")
                sessionLocal.commit()
                sessionLocal.close()
                return status.HTTP_201_CREATED
            
        return status.HTTP_400_BAD_REQUEST

    else:
        return status.HTTP_404_NOT_FOUND
    

def remove_feriado_movel(codigo_ibge:str, feriado:str):

    if len(codigo_ibge) == 2:
        estado = sessionLocal.query(ModelEstado).filter_by(codigo_ibge=codigo_ibge).first()

        if estado:
            if estado.feriados_estaduais:
                dados = estado.feriados_estaduais
                for data, feriados in dados.items():
                    if feriados["name"] == feriado:
                        del estado.feriados_estaduais[data]

                        flag_modified(estado, "feriados_estaduais")
                        sessionLocal.commit()    
                        sessionLocal.close()    
                        return status.HTTP_204_NO_CONTENT
            else:
                return status.HTTP_404_NOT_FOUND
        else:
            return status.HTTP_404_NOT_FOUND


    if len(codigo_ibge) == 7:
        municipio = sessionLocal.query(ModelMunicipio).filter_by(codigo_ibge=codigo_ibge).first()

        if municipio:
            if municipio.feriados_moveis:
                if feriado in municipio.feriados_moveis:
                    print(municipio.feriados_moveis)
                    municipio.feriados_moveis.remove(feriado)
                    
                    flag_modified(municipio, "feriados_moveis")
                    sessionLocal.commit()
                    sessionLocal.close()
                    return status.HTTP_204_NO_CONTENT
                
                else:
                    return status.HTTP_400_BAD_REQUEST
            else:
                return status.HTTP_404_NOT_FOUND
        else:
            return status.HTTP_404_NOT_FOUND
        
