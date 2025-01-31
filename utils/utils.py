from utils.feriados import FeriadosMoveis

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
