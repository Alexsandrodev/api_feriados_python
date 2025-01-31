from fastapi import status
from sqlalchemy.orm.attributes import flag_modified

from db.models import Municipio as ModelMunicipio
from db.database import sessionLocal
from db.models import Estado as ModelEstado

from utils.utils import get_feriados_moveis

def criateFeriadoMovel(codigo_ibge:str, feriado_movel:str):    
    municipio = sessionLocal.query(ModelMunicipio).filter_by(codigo_ibge=codigo_ibge).first()

    print(feriado_movel)
    feriados_moveis = get_feriados_moveis(2025)
    estado = municipio.estado
    
    if feriado_movel == estado.movel_estadual:
        return status.HTTP_404_NOT_FOUND
    
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


def removeFeriadoMovel(codigo_ibge:str, feriado:str):

    if len(codigo_ibge) == 2:
        estado = sessionLocal.query(ModelEstado).filter_by(codigo_ibge=codigo_ibge).first()

        if estado:
            if estado.movel_estadual:
                if feriado["name"] == estado.movel_estadual:
                    return status.HTTP_403_FORBIDDEN
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
    