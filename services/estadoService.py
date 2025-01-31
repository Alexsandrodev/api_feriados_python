from fastapi import status
from sqlalchemy.orm.attributes import flag_modified

from db.models import Estado as ModelEstado 
from db.database import sessionLocal

from utils.utils import get_feriados_moveis


def getFeriadoEstado(codigo_ibge:str,ano:int , data:str):
    """
        Retorna o feriado para um estado específico em uma data.

        Args:
            codigo_ibge (str): Código IBGE do estado.
            data (str): Data no formato MM-DD.

        Returns:
            dict: Dicionário contendo o nome do feriado.
    """
    estado = sessionLocal.query(ModelEstado).filter_by(codigo_ibge=codigo_ibge).first()
    feriados_moveis = get_feriados_moveis(ano)
    if feriados_moveis.get(data):
        for value in feriados_moveis.values():
            if feriados_moveis[data]["name"] == value["name"]:
                if estado.movel_estadual:
                    if value["name"] in estado.movel_estadual:
                        return value
                    
    print(estado)               
    if estado.feriados_estaduais:
        feriados = estado.feriados_nacionais | estado.feriados_estaduais
        
        return feriados.get(data)
    
    else:
        feriados = estado.feriados_nacionais
        return feriados.get(data)


def appendFeriadoEstado(codigo_ibge: str, data: str, feriado: dict):
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


def deleteFeriadosEstaduais(codigo_ibge: str, data: str):
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