
# API de Feriados (FastAPI)

Este projeto é uma API para consultar, adicionar e remover feriados municipais e estaduais no Brasil, utilizando Python com FastAPI e documentação interativa com Swagger.

## 📌Tecnologias

*   Python
*   FastAPI
*   Uvicorn (servidor ASGI)
*   Swagger (documentação interativa)

## Como rodar o projeto

1.  Clone o repositório:

    ```bash
    git clone [https://github.com/Alexsandrodev/api_feriados_node.git]
    cd seu-repositorio
    ```

2.  Crie um ambiente virtual (recomendado):

    ```bash
    python3 -m venv .venv  # Cria o ambiente virtual
    source .venv/bin/activate  # Ativa o ambiente virtual (Linux/macOS)
    .venv\Scripts\activate  # Ativa o ambiente virtual (Windows)
    ```

3.  Instale as dependências:

    ```bash
    pip install -r requirements.txt  # Instala as dependências do arquivo requirements.txt
    ```

6.  Inicie o servidor:

    ```bash
    uvicorn main:app --reload  # Inicia o servidor com reload automático
    ```
    A API estará rodando em `http://localhost:8000`.

## Documentação da API

Após iniciar o servidor, acesse:

*   Swagger UI → `http://localhost:8000/docs` (ou `/redoc` para Redoc UI)

## Rotas da API

*   **Buscar feriado:**

    ```http
    GET /feriados/{codigo_ibge}/{data}
    ```

    Exemplo de resposta:

    ```json
    {
        "name": "Consciência Negra"
    }
    ```

*   **Adicionar feriado:**

    ```http
    PUT /feriados/{codigo_ibge}/{data}
    ```

    Body (exemplo em JSON):

    ```json
    {
        "name": "Feriado Teste"
    }
    ```

    Exemplo de resposta:

    ```json
    {
        "message": "Feriado adicionado com sucesso!"
    }
    ```

*   **Remover feriado:**

    ```http
    DELETE /feriados/{codigo_ibge}/{data}
    ```

    Exemplo de resposta:

    ```json
    {
        "message": "Feriado removido com sucesso!"
    }
    ```

