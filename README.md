# GANDOM — تعمیرکار هوشمند

نسخه یکپارچه و production-oriented پلتفرم گندم، بازطراحی‌شده بر اساس تصمیم‌های قفل‌شده پروژه و بررسی سورس‌های قبلی.

## اصول قفل‌شده
- صفحه اصلی ابتدا و در مرکز، آگهی‌های فعال تعمیرکاران را نمایش می‌دهد.
- منوی اصلی فقط «تعمیرکاران» و «کاربر عمومی» است.
- مهمان بدون ثبت‌نام می‌تواند آگهی‌ها، تعمیرکاران، دسته‌ها و نزدیک‌ترین تعمیرکاران را ببیند و جست‌وجو کند.
- هنگام پیام‌دادن، ثبت درخواست تعمیر، ثبت نظر یا عملیات هویتی، ثبت‌نام/ورود و تأیید تلفن الزامی می‌شود.
- ورود بخش تعمیرکار فقط وقتی مجاز است که نقش، پروفایل کامل/تأییدشده، وضعیت حساب و اشتراک معتبر هم‌زمان برقرار باشند.
- اشتراک تعمیرکار و هزینه آگهی کاملاً مستقل‌اند.
- پلن آگهی: ۱ روز، ۱ هفته، ۱ ماه، ۱ سال؛ قیمت‌ها از پنل مدیریت قابل تغییرند.
- آگهی فقط بعد از پرداخت تأییدشده فعال می‌شود.
- زمان‌ها با UTC ذخیره می‌شوند و در رابط کاربری به زمان محلی تبدیل می‌شوند.
- کنترل دسترسی در backend enforce می‌شود و UI فقط لایه نمایشی است.
- پرداخت idempotent است و callback قابل تکرار، دوباره حساب را شارژ نمی‌کند.

## Stack
- Backend: FastAPI, SQLAlchemy 2 async, PostgreSQL, Redis, JWT, Pydantic v2
- Frontend: React + TypeScript + Vite
- Infra: Docker Compose, Nginx
- Tests: Pytest

## اجرا
```bash
cp .env.example .env
docker compose up --build
```

Frontend: http://localhost:5173
API: http://localhost:8000
API docs: http://localhost:8000/docs

## ساخت ادمین
پس از بالا آمدن backend:
```bash
docker compose exec backend python -m app.seed
```
اطلاعات اولیه از `.env` خوانده می‌شود.

## تست
```bash
docker compose exec backend pytest -q
```

## امنیت
Secretهای واقعی داخل `.env` یا secret manager قرار می‌گیرند و در Git commit نمی‌شوند. در production مقدار `DEBUG=false`، CORS محدود، TLS در reverse proxy، PostgreSQL/Redis داخلی و کلید JWT قوی الزامی است.
