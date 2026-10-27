<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-light.svg">
  <img alt="NainWrite Architectural Blueprint" src="docs/assets/banner-dark.svg" width="100%">
</picture>

# NainWrite ES — Entorno de Reescritura Editorial en Español con Puertas Deterministas

[![English](https://img.shields.io/badge/Language-English-blue?style=flat-square)](README.md)
[![Español](https://img.shields.io/badge/Idioma-Espa%C3%B1ol-emerald?style=flat-square)](README.es.md)
[![Architecture Tests](https://img.shields.io/badge/Architecture%20Tests-AST%20enforced-80FF00?style=flat-square&logo=python&logoColor=white)](tests/test_architecture.py)
[![CI](https://github.com/Nain9Dev/nainwrite-es/actions/workflows/ci.yml/badge.svg)](https://github.com/Nain9Dev/nainwrite-es/actions/workflows/ci.yml)
[![Demo Online](https://img.shields.io/badge/demo-online-blueviolet?style=flat&logo=githubpages&logoColor=white)](https://write.naindev.com/)
[![Ecosystem Status](https://img.shields.io/badge/status-100%25%20operational-success)](https://status.naindev.com)
[![Engineering Handbook](https://img.shields.io/badge/paved%20road-Python%20%2B%20Ollama-blue)](https://github.com/Nain9Dev/engineering-handbook)
[![Cost](https://img.shields.io/badge/cost-0.00_%E2%82%AC-22c55e)](https://github.com/Nain9Dev/engineering-handbook/blob/main/governance/zero-cost-philosophy.md)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Inference](https://img.shields.io/badge/inferencia-local%20y%20fail--closed-success)

NainWrite ES es un agente de reescritura local y determinista (*fail-closed*) para español de España natural, claro y profesional (`es-ES`). Reescribe borradores producidos por personas o modelos de lenguaje preservando el significado exacto, la incertidumbre, las condiciones, las negaciones, la atribución y los literales protegidos.

> **Demo Online Interactiva:** Prueba el banco de trabajo editorial directamente en [write.naindev.com](https://write.naindev.com/) con contratos de ejemplo, propuestas técnicas, análisis de diferencias (*diffs*) y compuertas de aprobación humana sin necesidad de instalar modelos locales.

## Flujo de Trabajo Actual

1. Qwen produce una reescritura estructurada mediante Ollama en ejecución local.
2. Un validador determinista compara los invariantes protegidos y los detectados automáticamente.
3. Se admite una reparación acotada si se detecta desviación determinista en literales o fechas.
4. LanguageTool en local valida ortografía, gramática y tipografía española. Una reparación lingüística acotada repite la comprobación de invariantes.
5. Un auditor dual independiente evalúa el significado y el estilo. Ambos deben certificar la salida antes de considerarse `accepted`; en caso contrario se marca como `review_required`.

```mermaid
sequenceDiagram
    autonumber
    actor User as Usuario / Cliente
    participant Orchestrator as Motor NainWrite
    participant LLM1 as Reescritor (Qwen)
    participant Invariant as Verificador de Invariantes
    participant LangTool as Motor LanguageTool
    participant LLM2 as Auditor Dual
    User->>Orchestrator: Ingesta de borrador (PDF/MD/TXT) + Invariantes protegidos
    Orchestrator->>LLM1: Solicitud de reescritura estructurada en es-ES
    LLM1-->>Orchestrator: Texto candidato
    Orchestrator->>Invariant: Verificación de invariantes
    alt Invariante alterado
        Orchestrator->>LLM1: Reparación determinista acotada
    end
    Orchestrator->>LangTool: Auditoría ortográfica y tipográfica
    Orchestrator->>LLM2: Validación semántica y estilística
    LLM2-->>Orchestrator: Dictamen (Accepted / Review Required)
    Orchestrator-->>User: Documento validado con compuerta humana
```

## Arquitectura y Pruebas de Aptitud

Las fronteras arquitectónicas se validan automáticamente con pruebas AST:
- `spanish_rewriter.invariants` y `models`: Capa de dominio puro sin dependencias de HTTP ni CLI.
- `spanish_rewriter.service` y `evaluator`: Capa de orquestación desacoplada de la interfaz de usuario.
- `tests/test_architecture.py`: Pruebas continuas de aislamiento de capas ejecutadas en pytest.

## Ejecución Local

```bash
# Entorno virtual y dependencias
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-documents.txt

# Ejecutar suite de pruebas y reglas de arquitectura
pytest tests/ -v
```
