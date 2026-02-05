# 📬 Postman Guide

## Collections
- `api/postman_collection.json` (principal, rotas /v1 com API key)
- `api/postman_collection_local.json` (somente local, sem API key)

## Environments
- `api/postman_environment_local.json`
- `api/postman_environment_gateway.json`

## Como usar (Local)
1. Importar collection + `postman_environment_local.json`
2. Selecionar environment **Holonet Local**
3. Iniciar API local:
   ```bash
   uvicorn --app-dir src holonet.main:app --reload --port 8000
   ```
4. Rodar requests (ou Collection Runner)

## Como usar (Gateway)
1. Importar collection + `postman_environment_gateway.json`
2. Selecionar environment **Holonet Gateway**
3. Preencher `base_url` com o hostname do Gateway
4. Preencher `api_key` com sua API key
5. Rodar as rotas **/v1** (ex.: Core/Extras)

## Dica
- Para testes rápidos, rode `Health` ou `Search` primeiro.
- Se receber `403`, verifique se:
  - serviço gerenciado do Gateway está habilitado
  - API key está restrita para **API Gateway API** e **Holonet Galactic Console API**
