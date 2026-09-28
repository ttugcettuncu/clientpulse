# ClientPulse

_Proje açıklaması Faz 5'te yazılacak._

## Gereksinimler

- Python 3.14 (3.14.7 ile geliştirildi ve test edildi)
- Git
- OpenAI API anahtarı

## Kurulum (Windows)

```powershell
git clone https://github.com/ttugcettuncu/clientpulse.git
cd clientpulse
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # ardından .env içine OPENAI_API_KEY değerini yaz
```

## Klasör Yapısı

```
src/         uygulama kodu (STT, Call Brief, RAG, BudgetGuard, FastAPI)
tests/       pytest testleri
data/        sentetik ses kayıtları ve RAG doküman seti
docs/        maliyet deneyi raporu ve değerlendirme setleri
dev_tools/   sadece geliştirme amaçlı araçlar (ürünün parçası değil)
```
