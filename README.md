# ClientPulse

_The project description will be written in Phase 5._

## Requirements

- Python 3.14 (developed and tested with 3.14.7)
- Git
- OpenAI API key

## Setup (Windows)

```powershell
git clone https://github.com/ttugcettuncu/clientpulse.git
cd clientpulse
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then put your OPENAI_API_KEY into .env
```

## Folder Structure

```
src/         application code (STT, Call Brief, RAG, BudgetGuard, FastAPI)
tests/       pytest tests
data/        synthetic call audio and the RAG document set
docs/        cost experiment report and evaluation sets
dev_tools/   development-only tools (not part of the product)
```
