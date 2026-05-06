import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot, Dispatcher

from app.config import settings
from app.db import init_db, get_session, AsyncSessionLocal
from app.models import Payment
from app.utils import make_order_code
from app.keyboards import admin_payment_keyboard
from app.routers.bot import router as bot_router
from app.api.license import router as license_router


bot = Bot(settings.bot_token)
dp = Dispatcher()


class DbSessionMiddleware:
    async def __call__(self, handler, event, data):
        async with AsyncSessionLocal() as session:
            data["session"] = session
            return await handler(event, data)


dp.message.middleware(DbSessionMiddleware())
dp.callback_query.middleware(DbSessionMiddleware())
dp.include_router(bot_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    await bot.delete_webhook(drop_pending_updates=True)

    polling_task = asyncio.create_task(dp.start_polling(bot))

    try:
        yield
    finally:
        polling_task.cancel()
        await bot.session.close()


app = FastAPI(title="UpNorthBot Paid Crypto System", lifespan=lifespan)
app.include_router(license_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


PLANS = {
    "pro": 99,
    "vip": 199,
    "pro_yearly": 891,
    "vip_yearly": 1791,
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "brand_name": settings.brand_name,
        },
    )


@app.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request, plan: str = "pro"):
    plan = plan if plan in PLANS else "pro"
    amount = PLANS[plan]

    return templates.TemplateResponse(
        "checkout.html",
        {
            "request": request,
            "brand_name": settings.brand_name,
            "plan": plan,
            "amount": amount,
            "usdt_trc20": settings.usdt_trc20_address,
            "usdt_bep20": settings.usdt_bep20_address,
            "btc": settings.btc_address,
            "usdt_trc20_qr": settings.usdt_trc20_qr,
            "usdt_bep20_qr": settings.usdt_bep20_qr,
            "btc_qr": settings.btc_qr,
        },
    )


@app.post("/checkout/submit", response_class=HTMLResponse)
async def checkout_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    telegram_username: str = Form(""),
    plan: str = Form(...),
    amount: float = Form(...),
    network: str = Form(...),
    tx_hash: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    wallet_map = {
        "USDT_TRC20": settings.usdt_trc20_address,
        "USDT_BEP20": settings.usdt_bep20_address,
        "BTC": settings.btc_address,
    }

    order_code = make_order_code()

    payment = Payment(
        order_code=order_code,
        full_name=full_name,
        email=email,
        telegram_username=telegram_username,
        plan=plan,
        amount_usd=amount,
        network=network,
        wallet_address=wallet_map.get(network, ""),
        tx_hash=tx_hash,
        status="PENDING",
    )

    session.add(payment)
    await session.commit()
    await session.refresh(payment)

    for admin_id in settings.admin_chat_ids:
        await bot.send_message(
            admin_id,
            "💰 New Crypto Payment Submitted\n\n"
            f"Brand: {settings.brand_name}\n"
            f"Order: {payment.order_code}\n"
            f"Name: {payment.full_name}\n"
            f"Email: {payment.email}\n"
            f"Telegram: {payment.telegram_username}\n"
            f"Plan: {payment.plan}\n"
            f"Amount: ${payment.amount_usd}\n"
            f"Network: {payment.network}\n"
            f"Wallet: {payment.wallet_address}\n"
            f"Tx Hash: {payment.tx_hash}\n\n"
            "Approve only after confirming the transaction in your wallet/explorer.",
            reply_markup=admin_payment_keyboard(payment.id),
        )

    return templates.TemplateResponse(
        "paid.html",
        {
            "request": request,
            "brand_name": settings.brand_name,
            "order_code": order_code,
            "bot_username": settings.telegram_bot_username,
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}