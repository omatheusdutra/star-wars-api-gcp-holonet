# 🌌 Holonet Galactic Console

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) ![HTTPX](https://img.shields.io/badge/HTTPX-0.27.2-000000?logo=python&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-2.6.1-E92063?logo=pydantic&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-0.30.6-2F855A?logo=uvicorn&logoColor=white) ![pytest](https://img.shields.io/badge/pytest-7.4.4-0A9EDC?logo=pytest&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-5.0.1-DC382D?logo=redis&logoColor=white) ![GCP](https://img.shields.io/badge/GCP-Cloud%20Run%20%2B%20API%20Gateway-4285F4?logo=googlecloud&logoColor=white)

![Holonet Banner](docs/banner.jpg)

API em Python (FastAPI) para explorar a **SWAPI** (`https://swapi.dev/api`). A solução roda no **Google Cloud Platform (GCP)** com **API Gateway** como camada pública e **Cloud Run** (privado via IAM) como backend serverless.

> **Documentação técnica (para avaliação):** este `README.md` + pasta `docs/` (deploys, Postman e checklist).

---

## ✨ Features

- 🔎 Busca unificada por recurso (`/v1/search`) + filtros e paginação
- 📄 Paginação normalizada (`page`, `page_size`) e limites de segurança
- 🔀 Ordenação local com whitelist de campos + aliases (`order_by`, `reverse`)
- 🎯 Projeção de campos via `fields`
- 🌐 Endpoints públicos sem `/v1` para navegação rápida no browser (ex.: `/films`, `/planets`)
- 🧠 Cache (in-memory ou Redis) com TTL configurável
- 🔗 Correlações (ex.: `/v1/films/{id}/characters`, `/v1/people/{id}/films`)
- 🕸️ Grafo de relacionamentos (`/v1/graph`) e dataset de planetas para mapa (`/v1/planets/map`)
- 🧾 OpenAPI + Postman
- 🧪 Testes com cobertura **100%** (ver seção “Testes”)

---

## 🧭 Arquitetura (GCP)

```mermaid
flowchart LR
  U[Cliente] --> G[API Gateway]
  G --> R[Cloud Run (privado via IAM)]
  R --> S[SWAPI (swapi.dev)]
  R --> C[Cache (in-memory/Redis)]
  R --> L[Cloud Logging]
```

Notas:
- 🔐 **IAM**: o Cloud Run fica **sem acesso público**; somente o API Gateway (service account gerenciada) recebe `roles/run.invoker`.
- 🔑 **API Key**: rotas `/v1/*` exigem `x-api-key` (configurado no API Gateway). Rotas públicas (sem `/v1`) são usadas para navegação/demonstração.

---

## 🔗 Acesso em Produção (API Gateway)

Base URL (Gateway):

```text
https://holonet-gateway-1vyyz0cb.uc.gateway.dev
```

Swagger UI:

```text
https://holonet-gateway-1vyyz0cb.uc.gateway.dev/docs
```

OpenAPI JSON:

```text
https://holonet-gateway-1vyyz0cb.uc.gateway.dev/openapi.json
```

Endpoints principais (navegação):
- `/` (boas-vindas)
- `/films`, `/characters`, `/planets`, `/starships`, `/vehicles`, `/species`

Rotas protegidas:
- `/v1/*` exige `x-api-key` (API Gateway).

Notas:
- O backend do Gateway é **Cloud Run privado via IAM**; por isso a URL do Cloud Run pode retornar `403` no browser (esperado).
- O Swagger/OpenAPI acima é servido **via Gateway** (sem precisar expor o Cloud Run publicamente).

---

## 🗂️ Estrutura do projeto

```text
src/
  holonet/
    main.py                # app FastAPI + middlewares + exception handlers
    config.py              # settings via env vars
    deps.py                # dependências (API key + correlation-id)
    clients/swapi_client.py
    routes/
      public.py            # endpoints públicos (sem /v1)
      health.py            # /health, /v1/health, /v1/meta
      search.py            # /v1/search
      resources.py         # /v1/{resource}/{id}, /v1/films/{id}/characters, etc.
      graph.py             # /v1/graph
      planets_map.py       # /v1/planets/map
    services/              # regras (search/graph/map/expand)
    utils/                 # cache/pagination/sorting/fields
api/
  openapi-gateway.yaml     # spec do API Gateway (com template ${backend_url})
  openapi-local.yaml       # spec local (referência)
  postman_collection.json
  postman_collection_local.json
  postman_environment_gateway.json
  postman_environment_local.json
infra/
  gcloud/                  # scripts (deploy + gateway)
  terraform/               # IaC (bônus)
docs/
  CLOUD_RUN_GATEWAY.md
  POSTMAN.md
  RELEASE_CHECKLIST.md
scripts/
  verify_all.ps1           # smoke test (local + Cloud Run + Gateway)
```

---

## ✅ Requisitos do case (resumo)

- ✅ GCP (API Gateway + backend serverless; scripts e documentação)
- ✅ Python como linguagem principal
- ✅ Dados via SWAPI (`https://swapi.dev/api`)
- ✅ Endpoints para filmes, personagens, planetas, naves (e extras)
- ✅ Filtros por query/path params, documentados

---

## 🛠️ Execução Local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crie um `.env` (não comitar) baseado em `.env.example`.

Rodar API:

```powershell
$env:PYTHONPATH = "src"
uvicorn --app-dir src holonet.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger local:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

---

## ⚙️ Variáveis de ambiente

Principais (ver `.env.example`):
- `SWAPI_BASE_URL` (default: `https://swapi.dev/api`)
- `CACHE_BACKEND` (`inmemory` | `redis`)
- `CACHE_TTL_SECONDS`, `CACHE_MAX_ENTRIES`, `REDIS_URL`
- `HTTP_TIMEOUT_SECONDS`, `HTTP_RETRIES`, `HTTP_BACKOFF_FACTOR`
- `MAX_PAGE_SIZE`, `MAX_UPSTREAM_PAGES`, `MAX_EXPAND_CONCURRENCY`
- `REQUIRE_API_KEY`, `API_KEY` (apenas para execução sem API Gateway)

Em produção (Cloud Run), as variáveis são definidas pelo script `infra/gcloud/deploy_cloudrun.ps1`.

---

## 📚 Endpoints (referência rápida)

🏠 Root:
```
GET /
```

❤️ Health / Meta:
```
GET /health
GET /v1/health
GET /v1/meta
```

🌐 Públicos (sem /v1):
```
GET /films
GET /characters
GET /planets
GET /starships
GET /vehicles
GET /species
```

Query params (públicos):
- `q` ou `search`: termo de busca (delegado à SWAPI)
- `page`, `page_size`: paginação normalizada
- `all=true|false`: agrega páginas (default `true`)
- `sort` ou `order_by`: ordenação local (whitelist por recurso)
- `order=asc|desc` ou `reverse=true`
- `fields`: projeção de campos (ex.: `fields=name,id`)

🔎 Search (v1):
```
GET /v1/search?resource=people&q=luke&page=1&page_size=5&sort=name&order=asc&fields=name,id
```

🎞️ Recursos (v1):
```
GET /v1/films/{resource_id}
GET /v1/people/{resource_id}
GET /v1/planets/{resource_id}
GET /v1/starships/{resource_id}
```

🔗 Correlacionados (v1):
```
GET /v1/films/{resource_id}/characters
GET /v1/people/{resource_id}/films
```

🧭 Extras (v1):
```
GET /v1/planets/map
GET /v1/graph
```

> Lista completa de parâmetros e schemas: Swagger UI (`/docs`) ou OpenAPI JSON (`/openapi.json`).

---

## 🔒 Segurança (resumo)

- 🔑 **API Key**: rotas `/v1/*` exigem header `x-api-key` no API Gateway.
- 🔐 **IAM (Cloud Run)**: backend fica privado; apenas o API Gateway invoca.
- 🧼 **Segredos**: não commitar chaves/credenciais (use `.env` local + GitHub Secrets).

---

## 🚀 Deploy no GCP (Cloud Run + API Gateway + IAM)

Documentação detalhada: `docs/CLOUD_RUN_GATEWAY.md`.

1) Deploy Cloud Run:
```powershell
.\infra\gcloud\deploy_cloudrun.ps1 -ProjectId "SEU_PROJETO" -Region "us-central1" -ServiceName "holonet-api"
```

2) IAM (remover público e permitir somente o API Gateway):
```powershell
gcloud run services remove-iam-policy-binding holonet-api `
  --region us-central1 `
  --member="allUsers" `
  --role="roles/run.invoker"

$number = gcloud projects describe SEU_PROJETO --format="value(projectNumber)"
gcloud run services add-iam-policy-binding holonet-api `
  --region us-central1 `
  --member="serviceAccount:service-$number@gcp-sa-apigateway.iam.gserviceaccount.com" `
  --role="roles/run.invoker"
```

3) Atualizar API Gateway apontando para o Cloud Run:
```powershell
$cfg = "holonet-config-$(Get-Date -Format yyyyMMddHHmmss)"
$runUrl = "https://SEU_CLOUD_RUN"

.\infra\gcloud\create_gateway.ps1 `
  -ProjectId "SEU_PROJETO" `
  -Region "us-central1" `
  -FunctionName "holonet-api" `
  -BackendUrl $runUrl `
  -GatewayApiId "holonet-api" `
  -GatewayConfigId $cfg `
  -GatewayId "holonet-gateway"
```

---

## 🚀 Deploy no GCP (Cloud Functions Gen2 + API Gateway) (alternativo)

```powershell
powershell -ExecutionPolicy Bypass -File "infra\gcloud\deploy.ps1" -ProjectId "SEU_PROJETO" -Region "us-central1" -FunctionName "holonet-api"
```

---

## 🧪 Testes

Comandos:
```powershell
python -m ruff check src tests
python -m ruff format --check src tests
pytest -q
coverage run -m pytest -q
coverage report
```

Evidência (cobertura total do repositório):
```text
TOTAL  1497  0  100%
```

---

## 🧪 Smoke test (Local + Cloud Run + Gateway)

O script `scripts/verify_all.ps1` valida rapidamente:
- qualidade (ruff/pytest)
- endpoints públicos
- Cloud Run (com token IAM)
- API Gateway (com API key)

Exemplo (não commitar a API key):
```powershell
$env:HOLONET_API_KEY = "SUA_API_KEY"

# Opção A: passar explicitamente (útil para CI ou copy/paste)
.\scripts\verify_all.ps1 `
  -StartLocal `
  -GatewayHost "holonet-gateway-1vyyz0cb.uc.gateway.dev" `
  -ApiKey $env:HOLONET_API_KEY `
  -RunUrl "https://holonet-api-147959006843.us-central1.run.app"

# Opção B: omitir -ApiKey (o script lê $env:HOLONET_API_KEY automaticamente)
.\scripts\verify_all.ps1 `
  -StartLocal `
  -GatewayHost "holonet-gateway-1vyyz0cb.uc.gateway.dev" `
  -RunUrl "https://holonet-api-147959006843.us-central1.run.app"
```

Evidência (2026-02-05, API key redigida):
```text
== Cloud Run (IAM) ==
[OK] Run /health -> https://holonet-api-147959006843.us-central1.run.app/health
True
[OK] Run /films -> https://holonet-api-147959006843.us-central1.run.app/films?all=false
True

== API Gateway (API Key) ==
[OK] Gateway /v1/health -> https://holonet-gateway-1vyyz0cb.uc.gateway.dev/v1/health
True
[OK] Gateway /films -> https://holonet-gateway-1vyyz0cb.uc.gateway.dev/films?all=false
True
[OK] Gateway /v1/search -> https://holonet-gateway-1vyyz0cb.uc.gateway.dev/v1/search?resource=people&q=luke
True
```

---

## 📮 Postman

Guia: `docs/POSTMAN.md`.

Arquivos:
- `api/postman_collection.json`
- `api/postman_collection_local.json`
- `api/postman_environment_gateway.json`
- `api/postman_environment_local.json`

---

## 🔁 CI/CD

GitHub Actions:
- CI: `.github/workflows/ci.yml`
- Deploy: `.github/workflows/deploy.yml`

---

## 🏗️ IaC (Terraform) (bônus)

Infra opcional em `infra/terraform/`.

---

## 🧩 Troubleshooting

- Se `/v1/*` retornar 401/403: confira `x-api-key` (Gateway) e IAM (Cloud Run).
- Se o Gateway retornar 404 para rotas públicas: recrie API config (`create_gateway.ps1`) apontando para o backend correto.
- Se local falhar: confirme `PYTHONPATH=src` e porta 8000 livre.

---

## 👤 Autor

Matheus Dutra

## 📄 Licença

Ver `LICENSE`.
