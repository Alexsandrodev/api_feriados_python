import uvicorn
from fastapi import FastAPI, HTTPException
from database import engine

from utils import criar_banco, get_feriado_estado, get_feriado_municipio

from models import Base

app = FastAPI()

arquivo = "municipios-2019.csv"

Base.metadata.create_all(engine)

@app.get('/feriados/{codigo_ibge}/{ano}-{mes}-{dia}')
def get_feriados(codigo_ibge:str, ano:int, mes:str, dia:str,):
    data = f"{mes}-{dia}"
    respose_criar_db = criar_banco(arquivo, ano)

    print(respose_criar_db)
    if len(codigo_ibge) == 7:
        feriado = get_feriado_municipio(codigo_ibge, data)
        if feriado:
            return feriado
        
        else:
            raise HTTPException(status_code=404, detail='Feriado não encontrado')
        
    elif len(codigo_ibge) == 2:
        feriado = get_feriado_estado(codigo_ibge, data)

        if feriado:
            return feriado
        
        else:
            raise HTTPException(status_code=404, detail='Feriado não encontrado')


    else:
        return HTTPException(status_code=404, detail="codigo do estado invalido")     


if __name__ == "__main__":
    uvicorn.run(app, port=8000)


