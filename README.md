# AI Architecture Blueprint

A dependency-free Python CLI for checking and documenting AI system
architecture plans using a practical nine-layer blueprint.

The tool checks that all nine architecture layers are described, reviews
selected security and operational controls, and writes a Markdown report
and JSON assessment.

## Features

- Validate a JSON architecture specification.
- Check nine layers: ingestion, storage and processing, retrieval, models,
  orchestration, application/API, integrations, security/governance, and
  infrastructure/observability.
- Flag unmarked controls such as authentication, backups, secrets management,
  and CI/CD.
- Generate `architecture-report.md` and `assessment.json`.
- Run locally without API keys or external service dependencies.

## Requirements

- Python 3.11 or newer
- Bash for the setup script

## Setup

From the repository root:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
source .venv/bin/activate

Usage
Validate the example:

bash


aibp validate examples/architecture.json
Generate a report:

bash


aibp build examples/architecture.json
Choose an output directory:

bash


aibp build examples/architecture.json --output build/review
You can also run the CLI as a Python module:

bash


python -m aibp build examples/architecture.json
Input format
Use examples/architecture.json as a starting point. Each of the nine
entries under layers must be a non-empty list of strings. The project
object must include a project name and goal.

The controls object is optional. Controls not explicitly set to true
are reported as follow-up items. The tool does not verify that a control
has actually been implemented.

Output
The build command creates:

architecture-report.md — readable architecture overview and review notes.
assessment.json — machine-readable validity, warnings, and passed checks.
Scope and security
This is a planning and documentation utility, not a security scanner,
compliance certification, capacity model, or deployment system. Review
recommendations against your actual requirements and threat model before
production use.

Do not commit credentials or production secrets. The current version does
not need an .env file or external API keys.

License
MIT