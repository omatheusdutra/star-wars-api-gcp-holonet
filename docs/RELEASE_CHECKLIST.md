# ✅ Release Checklist (Holonet Galactic Console)

## Pré-publicação

- [ ] Remover arquivos locais (ex.: `.coverage*`, `.venv/`, `__pycache__/`).
- [ ] Garantir `.env` fora do repo (usar apenas `.env.example`).
- [ ] Confirmar OpenAPI válido: `api/openapi-gateway.yaml`.
- [ ] README atualizado (deploy, Postman, endpoints, arquitetura, segurança).

## Qualidade

- [ ] `python -m ruff check src tests`
- [ ] `python -m ruff format --check src tests`
- [ ] `pytest -q`
- [ ] `coverage run -m pytest -q`
- [ ] `coverage report`

## GitHub

- [ ] CI e CD configurados (`.github/workflows/ci.yml`, `deploy.yml`).
- [ ] Secrets definidos no GitHub (GCP_PROJECT_ID, GCP_REGION, etc.).
- [ ] Repositório público criado.

## Deploy (opcional)

- [ ] Cloud Run ok (IAM + backend privado).
- [ ] API Gateway atualizado (API Key para `/v1/*`).
- [ ] Smoke tests completos (script).

## Smoke test (evidência)

Rodar (sem commitar a API key):

```powershell
$env:HOLONET_API_KEY = "SUA_API_KEY"
.\scripts\verify_all.ps1 `
  -StartLocal `
  -GatewayHost "holonet-gateway-1vyyz0cb.uc.gateway.dev" `
  -ApiKey $env:HOLONET_API_KEY `
  -RunUrl "https://holonet-api-147959006843.us-central1.run.app"
```

Exemplo de output esperado (resumo):

```text
== Lint & Tests ==
All checks passed!

== Cloud Run (IAM) ==
[OK] Run /health -> https://.../health
True
[OK] Run /films -> https://.../films
True

== API Gateway (API Key) ==
[OK] Gateway /v1/health -> https://.../v1/health
True
[OK] Gateway /films -> https://.../films
True
[OK] Gateway /v1/search -> https://.../v1/search?resource=people&q=luke
True
```

Ultima validacao (2026-02-05, API key redigida):

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

## Cobertura (evidência)

```text
TOTAL  1497  0  100%
```
