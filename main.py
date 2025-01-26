import uvicorn
from fastapi import FastAPI, HTTPException, status, Response, Body
from database import engine

import utils

from models import Base

app = FastAPI()

arquivo = "municipios-2019.csv"

Base.metadata.create_all(engine)

respose_criar_db = utils.criar_banco(arquivo)

print(respose_criar_db)

@app.get('/feriados/{codigo_ibge}/{data}/')
def get_feriados(codigo_ibge:str, data :str):
    try:
        ano, date = utils.validar_data(data)
    except:
        return status.HTTP_400_BAD_REQUEST


    if len(codigo_ibge) == 7:
        feriado = utils.get_feriado_municipio(codigo_ibge=codigo_ibge, ano=ano, data=date)
        if feriado:
            return feriado
        
        else:
            raise HTTPException(status_code=404, detail='Feriado não encontrado')
        
    elif len(codigo_ibge) == 2:
        feriado = utils.get_feriado_estado(codigo_ibge, data=date)

        if feriado:
            
            return feriado
        
        else:
            raise HTTPException(status_code=404, detail='Feriado não encontrado')


    else:
        return HTTPException(status_code=404, detail="codigo do estado invalido")     


@app.put("/feriados/{codigo_ibge}/{data}/", status_code=status.HTTP_201_CREATED)
def append_feriado(codigo_ibge: str, data: str, response: Response, feriado: dict | None = Body(default=None)):
    print(feriado)
    if feriado:  
        if "name" not in feriado:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Campo 'name' é obrigatório")

        try:
            ano, date = utils.validar_data(data)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data inválida")

        if len(codigo_ibge) == 2:
            feriado, response.status_code = utils.append_feriado_estado(codigo_ibge, date, feriado)
            if feriado:
                return response.status_code
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estado não encontrado")

        elif len(codigo_ibge) == 7:
            feriado, response.status_code = utils.append_feriado_municipal(codigo_ibge, date, feriado)
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

        response.status_code = utils.criate_feriado_movel(codigo_ibge, feriado_movel)
        return response.status_code
        



@app.delete("/feriados/{codigo_ibge}/{data}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_feriado(codigo_ibge:str, data:str, response:Response):
    feriado_movel = data
    ano, data = utils.validar_data(data)

    if ano == None and data == None:
        feriado_movel = utils.formated_feriado_name(feriado_movel)
        response.status_code = utils.remove_feriado_movel(codigo_ibge, feriado_movel)
        return response.status_code
        
    response.status_code = utils.delete_feriado_by_id(codigo_ibge, data)
    return response.status_code



if __name__ == "__main__":
    uvicorn.run(app, port=8000)
