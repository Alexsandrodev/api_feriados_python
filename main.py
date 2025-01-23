import uvicorn
from fastapi import FastAPI, HTTPException, status, Response
from database import engine, sessionLocal


from models import Estado as ModelEstado 
from models import Municipio as ModelMunicipo

from pydantic import BaseModel

import utils

from models import Base

app = FastAPI()

arquivo = "municipios-2019.csv"

Base.metadata.create_all(engine)

respose_criar_db = utils.criar_banco(arquivo)

print(respose_criar_db)

class Feriado(BaseModel):
    nome: str

@app.get('/feriados/{codigo_ibge}/{ano}-{mes}-{dia}/')
def get_feriados(codigo_ibge:str, ano:int, mes:str, dia:str):
    data = f"{mes}-{dia}"

    if len(codigo_ibge) == 7:
        feriado = utils.get_feriado_municipio(codigo_ibge, data)
        if feriado:
            return feriado
        
        else:
            raise HTTPException(status_code=404, detail='Feriado não encontrado')
        
    elif len(codigo_ibge) == 2:
        feriado = utils.get_feriado_estado(codigo_ibge, data)

        if feriado:
            return feriado
        
        else:
            raise HTTPException(status_code=404, detail='Feriado não encontrado')


    else:
        return HTTPException(status_code=404, detail="codigo do estado invalido")     


@app.put("/feriados/{codigo_ibge}/{mes}-{dia}/", status_code=200)
def append_feriado(codigo_ibge: str, mes:str, dia:str, feriado: dict, response:Response):
    data = f"{mes}-{dia}"

    if len(codigo_ibge) == 2 :

        feriado, response.status_code = utils.append_feriado_estado(codigo_ibge, data, feriado)

        if feriado:
            return response.status_code

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="estado não encontrado ")

    if len(codigo_ibge) == 7:
        feriado, response.status_code = utils.append_feriado_municipal(codigo_ibge, data, feriado)

        if feriado:
            return response.status_code
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="estado não encontrado ")
        
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código Ibge invalido")


@app.delete("/feriados/{codigo_ibge}/{mes}-{dia}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_feriado(codigo_ibge:str, mes:str, dia:str, response:Response):
    data = f"{mes}-{dia}"

    if len(codigo_ibge) == 2:
        response.status_code = utils.delete_feriado_estadual(codigo_ibge, data)
        return response.status_code

    elif len(codigo_ibge) == 7:
        response.status_code = utils.delete_feriado_municipal(codigo_ibge, data)
        return response.status_code

    else: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código Ibge invalido")

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
