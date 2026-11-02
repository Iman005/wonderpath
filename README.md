# WanderPath

برنامه‌ریز سفر داخلی ایران — فارسی و راست‌چین. شهر و جاذبه پیدا کنید، برنامهٔ روزانه بچینید، بودجه و نقشه را ببینید.

بدون رزرو، پرداخت، یا دستیار هوش مصنوعی.


| | |
| --- | --- |
| فرانت‌اند | Next.js 14، React 18، TypeScript |
| بک‌اند | Python 3.12، FastAPI، SQLite (لوکال) |
| ورود | گوگل، یا **ورود آزمایشی** برای دموی لوکال |

---

## اجرای سریع (حدود ۵ دقیقه)

دو ترمینال لازم است. اول بک‌اند، بعد فرانت.

### پیش‌نیاز

- [Python 3.12](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) (همراه npm)
- Git

کلون (آدرس ریپوی خودتان را بگذارید):

```bash
git clone https://github.com/YOUR_USER/wanderpath.git
cd wanderpath
```

اگر همین پوشه را دارید، همان `cd` به ریشهٔ پروژه کافی است.

---

### ۱) بک‌اند — پورت `8000`

**ویندوز (PowerShell):**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts/seed_data.py
python -m uvicorn app.main:app --reload --port 8000
```

اگر اجرای اسکریپت بسته بود:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**macOS / Linux:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_data.py
python -m uvicorn app.main:app --reload --port 8000
```

آماده است وقتی ببینید سرور روی `http://127.0.0.1:8000` گوش می‌دهد.

- مستندات API: [http://localhost:8000/docs](http://localhost:8000/docs)
- دادهٔ نمونه (تهران، شیراز، اصفهان، مشهد، یزد و جاذبه‌ها) با `seed_data.py` می‌آید؛ برای دمو کلید Neshan لازم نیست.

---

### ۲) فرانت‌اند — پورت `3000`

ترمینال دوم، از ریشهٔ پروژه:

**ویندوز:**

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

**macOS / Linux:**

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

مرورگر: **[http://localhost:3000](http://localhost:3000)**

---

### ۳) ورود و ساخت سفر

1. [http://localhost:3000/login](http://localhost:3000/login)
2. دکمهٔ **ورود آزمایشی** (بدون گوگل کار می‌کند؛ در `.env` بک‌اند `ALLOW_DEV_LOGIN=true` و `ENV=development` باشد)
3. بعد از ورود به `/app` می‌روید: نام سفر و بازهٔ تاریخ را بگذارید
4. در هاب، روی هر روز بزنید و مثلاً «شیراز» را جست‌وجو کنید

بدون این دو سرور همزمان، صفحه خالی یا خطای شبکه می‌دهد.

---

## تنظیمات اختیاری

فایل‌های واقعی `.env` را commit نکنید. نمونه در ریپو هست.

| فایل | حداقل لازم برای دمو |
| --- | --- |
| `backend/.env` | کپی از `.env.example` کافی است (`JWT_SECRET` و `ALLOW_DEV_LOGIN=true`) |
| `frontend/.env.local` | `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` |

**ورود با گوگل** (اختیاری): در [Google Cloud Console](https://console.cloud.google.com/) یک OAuth Client از نوع Web بسازید.

- JavaScript origin: `http://localhost:3000`
- Redirect: `http://localhost:3000/login/google/callback`
- همان Client ID را در `backend/.env` → `GOOGLE_CLIENT_ID` و `frontend/.env.local` → `NEXT_PUBLIC_GOOGLE_CLIENT_ID` بگذارید

اسکریپت کمکی: `scripts/setup-google-oauth.ps1`

**نقشه / مکان‌های بیشتر:** `NESHAN_API_KEY` در بک‌اند (کلید سرویس). تایل نقشه در مرورگر جداست: `NEXT_PUBLIC_NESHAN_API_KEY` (کلید وب). بدون آن‌ها هم با دادهٔ seed و تایل OpenFreeMap کار می‌کند.

---

## داخل برنامه چه می‌بینید

- صفحهٔ معرفی و برنامه‌های پیشنهادی (`/tours`)
- ساخت سفر چندروزه، برنامهٔ هر روز، اقامت و غذا
- بودجه به تومان، هوا، یادداشت، اشتراک خلاصهٔ فقط‌خواندنی
- رابط کاملاً فارسی (RTL)

جزئیات معماری: [`docs/architecture-spec.md`](docs/architecture-spec.md)

---

## ساختار پوشه

```
backend/     FastAPI
frontend/    Next.js
docs/        مشخصات معماری
scripts/     اسکریپت‌های کمکی لوکال
```

جزئیات بیشتر: [`backend/README.md`](backend/README.md) · [`frontend/README.md`](frontend/README.md)

---

## تست بک‌اند

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

---

## English — run locally

You need **two terminals**. Python 3.12 and Node 18+.

**Backend** (`http://localhost:8000`):

```bash
cd backend
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Unix:    source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Windows: Copy-Item .env.example .env
python scripts/seed_data.py
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend** (`http://localhost:3000`):

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `/login` and use **ورود آزمایشی** (dev login). Google OAuth and Neshan keys are optional for a local demo.

WanderPath is an Iran-only trip planner (RTL Persian UI). No bookings or payments.

## 🤖 ابزارهای هوش مصنوعی استفاده‌شده

این پروژه با کمک ابزارهای هوش مصنوعی ساخته شده:

- **Claude** و **ChatGPT**: برای ساخت کانتکست پروژه
- **Cursor**: برای ساخت دمو


اسکرین شات های مربوط به صفحات پروژه :
<img width="1817" height="874" alt="Screenshot 2026-11-02 105334" src="https://github.com/user-attachments/assets/9d4162ea-61d9-4d9f-b691-ff05a4eecbb6" />
<img width="1817" height="934" alt="Screenshot 2026-11-02 105316" src="https://github.com/user-attachments/assets/f9f96545-93db-49a4-9020-f1b3b4019737" />
<img width="1805" height="912" alt="Screenshot 2026-11-02 105248" src="https://github.com/user-attachments/assets/6baf1f7f-7deb-4d24-b0ee-f646c2c28f7a" />
<img width="1648" height="741" alt="Screenshot 2026-11-02 105153" src="https://github.com/user-attachments/assets/28d9cfbb-f782-4419-8935-ced45649764c" />
<img width="1570" height="891" alt="Screenshot 2026-11-02 105127" src="https://github.com/user-attachments/assets/7e3a2ac2-9406-46a1-8bdf-c06aaabea154" />
<img width="1795" height="905" alt="Screenshot 2026-11-02 105033" src="https://github.com/user-attachments/assets/ab96e3ca-fddd-4639-af1a-723d97cbcf98" />
<img width="1238" height="899" alt="Screenshot 2026-11-02 104953" src="https://github.com/user-attachments/assets/55676ab3-f803-49a1-a169-bc164ed92341" />
<img width="758" height="450" alt="Screenshot 2026-11-02 105705" src="https://github.com/user-attachments/assets/af9dac67-a199-49ae-8821-97f2c656d214" />
<img width="768" height="491" alt="Screenshot 2026-11-02 105630" src="https://github.com/user-attachments/assets/d579d905-72ea-4b09-bb9c-7806e224df7f" />
<img width="1152" height="746" alt="Screenshot 2026-11-02 105606" src="https://github.com/user-attachments/assets/b5d23021-0b22-47b0-a70c-4bdf9b87311b" />
<img width="1396" height="873" alt="Screenshot 2026-11-02 105550" src="https://github.com/user-attachments/assets/687e60b1-0f74-4496-8304-92a3bfaa0474" />
<img width="1606" height="843" alt="Screenshot 2026-11-02 105521" src="https://github.com/user-attachments/assets/6cc5c3ef-a1b9-49a4-853b-fc1c6b97555f" />
<img width="1361" height="861" alt="Screenshot 2026-11-02 105359" src="https://github.com/user-attachments/assets/374dd4cc-3f3f-460d-a4e9-5ca3e6ec9770" />
