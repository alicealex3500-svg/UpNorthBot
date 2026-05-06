# FX Hustle Paid Crypto Website + Telegram Onboarding Bot

## What it does
- Landing page like a trading bot SaaS website
- Crypto checkout using your own wallet addresses
- User submits TxHash
- Admin receives Telegram approval buttons
- User continues to Telegram bot with order code
- After admin approval, bot unlocks EA download, install guide, private channel/group, copier link, and license key
- FastAPI license endpoint for MT5 EA checks
- Streamlit admin panel

## Local setup
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add real values.

For local database testing with Railway Postgres, use Railway PUBLIC database URL, usually containing `proxy.rlwy.net`.
Do not use `railway.internal` on your local PC.

Run:
```powershell
uvicorn main:app --host 0.0.0.0 --port 8080
```

Open:
```text
http://localhost:8080
```

Admin panel:
```powershell
streamlit run admin_panel/streamlit_app.py
```

## Railway deployment
1. Push this folder to GitHub.
2. Create Railway project.
3. Add PostgreSQL service.
4. Add Web service from GitHub.
5. Add all `.env.example` variables in Railway Variables.
6. For Railway service database URL, you can use internal URL.
7. Start command is already in `railway.json`.

## Important
This crypto payment is manual verification. User submits TxHash, admin checks wallet/explorer, then approves.
For automatic on-chain verification later, add TronGrid/BscScan/Etherscan API integration.
