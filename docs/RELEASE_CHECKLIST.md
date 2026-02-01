# ✅ Release Checklist (Holonet Galactic Console)

## Pré-publicação
- [ ] Remover arquivos locais (ex.: `.coverage*`, `.venv/`, `__pycache__/`).
- [ ] Garantir `.env` fora do repo (usar apenas `.env.example`).
- [ ] Confirmar OpenAPI válido: `api/openapi-gateway.yaml`.
- [ ] README atualizado (deploy, CI/CD, Postman, endpoints, arquitetura).

## Qualidade
- [ ] `ruff check src tests`
- [ ] `ruff format --check src tests`
- [ ] `pytest -q --cov=holonet --cov-report=term-missing`

## GitHub
- [ ] CI e CD configurados (`.github/workflows/ci.yml`, `deploy.yml`).
- [ ] Secrets definidos no GitHub (GCP_PROJECT_ID, GCP_REGION, etc.).
- [ ] Repositório público criado.

## Deploy (opcional)
- [ ] Cloud Function Gen2 ok.
- [ ] API Gateway atualizado.
- [ ] Smoke tests (`/v1/health`, `/v1/meta`).

