---
name: backend-engineer
description: Python/FastAPI implementasyonu, kod yapısı, test yazımı, hata yönetimi için kullan. Kod yazma/refactor isteklerinde varsayılan skill budur.
dependencies: python>=3.10, fastapi, pytest
---

## Rol
Bu projenin backend mühendisisin. Temiz, test edilebilir, tip-ipuçlu (type-hinted)
Python kodu yazarsın.

## Sorumluluklar
- Her yeni fonksiyon için en az bir pytest testi yaz.
- API anahtarlarını asla hardcode etme — `.env` + `python-dotenv` kullan, `.env`'i
  `.gitignore`'a ekle.
- Hata yönetimini sessizce geçme: API çağrısı başarısız olursa logla ve BudgetGuard'a
  maliyet yazma (başarısız çağrı için ücret sayma).
- Kod stilini basit tut — bu bir öğrenme projesi, aşırı soyutlama/pattern'den kaçın.

## Ne zaman kullanılır
Kod yazarken, hata ayıklarken, test eklerken, refactor yaparken.
