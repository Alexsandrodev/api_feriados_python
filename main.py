import uvicorn
from fastapi import FastAPI, HTTPException, status, Response, Body
from db.database import engine
import db.startup as startup
import services.estadoService as estadoService
import services.municipioService as municipioService
import services.feriadoMovel as feriadoMovel

import utils.utils as utils

from db.models import Base

app = FastAPI()

arquivo = "municipios-2019.csv"

Base.metadata.create_all(engine)

respose_criar_db = startup.criar_banco(arquivo)

print(respose_criar_db)

@app.get('/feriados/{codigo_ibge}/{data}/')
def getFeriados(codigo_ibge:str, data :str):
    try:
        ano, date = utils.validar_data(data)
    except:
        return status.HTTP_400_BAD_REQUEST


    if len(codigo_ibge) == 7:
        print(codigo_ibge, ano, date)
        feriado = municipioService.getFeriadoMunicipial(codigo_ibge,ano=ano, data=date)
        if feriado:
            return feriado
        
        else:
            raise HTTPException(status_code=404, detail='Feriado não encontrado')
        
    elif len(codigo_ibge) == 2:
        feriado = estadoService.getFeriadoEstado(codigo_ibge=codigo_ibge, ano=ano, data=date)

        if feriado:
            
            return feriado
        
        else:
            raise HTTPException(status_code=404, detail='Feriado não encontrado')


    else:
        return HTTPException(status_code=404, detail="codigo do estado invalido")     


@app.put("/feriados/{codigo_ibge}/{data}/", status_code=status.HTTP_201_CREATED)
def appendFeriado(codigo_ibge: str, data: str, response: Response, feriado: dict | None = Body(default=None)):
    if feriado:  
        if "name" not in feriado:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Campo 'name' é obrigatório")

        try:
            ano, date = utils.validar_data(data)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data inválida")

        if len(codigo_ibge) == 2:
            feriado, response.status_code = estadoService.appendFeriadoEstado(codigo_ibge, date, feriado)
            if feriado:
                return response.status_code
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estado não encontrado")

        elif len(codigo_ibge) == 7:
            feriado, response.status_code = municipioService.appendFeriadoMunicipal(codigo_ibge, date, feriado)
            if feriado:
                return response.status_code
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Município não encontrado")

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código IBGE inválido")

    else: 
        try:
            feriado_movel = utils.formated_feriado_name(data)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feriado móvel inválido")

        response.status_code = feriadoMovel.criateFeriadoMovel(codigo_ibge, feriado_movel)
        return response.status_code
        



@app.delete("/feriados/{codigo_ibge}/{data}/", status_code=status.HTTP_204_NO_CONTENT)
def deleteFeriado(codigo_ibge:str, data:str, response:Response):
    feriado_movel = data
    ano, data = utils.validar_data(data)

    if ano == None and data == None:
        feriado_movel = utils.formated_feriado_name(feriado_movel)
        response.status_code = feriadoMovel.removeFeriadoMovel(codigo_ibge, feriado_movel)
        return response.status_code
    
    if len(codigo_ibge) == 7:
        response.status_code = municipioService.deleteFeriadoMunicipal(codigo_ibge, data)
        return response.status_code
    
    elif len(codigo_ibge) == 2:
        print('entrei aqui')
        response.status_code = estadoService.deleteFeriadosEstaduais(codigo_ibge, data)
        return response.status_code
    
    else:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código ibge inválido")



if __name__ == "__main__":
    uvicorn.run(app, port=8000)
