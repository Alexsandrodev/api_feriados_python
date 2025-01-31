from fastapi import status
from sqlalchemy.orm.attributes import flag_modified

from db.models import Municipio as ModelMunicipio
from db.database import sessionLocal

from utils.feriados import FeriadosMoveis
from utils.utils import get_feriados_moveis

def getFeriadoMunicipial(codigo_ibge:str, ano:int, data:str):
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
                if estado.movel_estadual:
                    if value["name"] in estado.movel_estadual:
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


def appendFeriadoMunicipal(codigo_ibge: str, data: str, feriado:dict):
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
    

def deleteFeriadoMunicipal(codigo_ibge: str, data:str):

    municipio = sessionLocal.query(ModelMunicipio).filter_by(codigo_ibge=codigo_ibge).first()
    
    print (municipio)
    estado = municipio.estado
    print (estado)
        
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
    
