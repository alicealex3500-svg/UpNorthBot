from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import User, Payment
from app.keyboards import (
    join_keyboard,
    download_next_keyboard,
    install_video_keyboard,
    copier_license_keyboard,
)
from app.utils import make_license_key, next_expiry

router = Router()


async def is_member(bot: Bot, telegram_id: int, chat_id: int) -> bool:
    try:
        if not chat_id:
            return True

        member = await bot.get_chat_member(chat_id, telegram_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


async def unlock_user(session: AsyncSession, user: User):
    user.paid = True
    user.access_active = True
    user.state = "ACCESS_ACTIVE"

    if not user.license_key:
        user.license_key = make_license_key()

    user.license_expires_at = next_expiry(30)
    await session.commit()


def safe_url(url: str, fallback: str = "https://t.me/") -> str:
    url = (url or "").strip()

    if url.startswith("http://") or url.startswith("https://"):
        return url

    return fallback


def private_join_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Join Private Channel",
                    url=safe_url(settings.private_channel_link),
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Join Private Group",
                    url=safe_url(settings.private_group_link),
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ I Have Joined",
                    callback_data="access_step_install",
                )
            ],
        ]
    )


async def send_access_step_1(bot_or_message, user: User):
    text = (
        "✅ Access Granted!\n\n"
        "Step 1/4: Download your automated trading bot EA below.\n\n"
        "After downloading, click Next."
    )

    if isinstance(bot_or_message, Message):
        await bot_or_message.answer(
            text,
            reply_markup=download_next_keyboard(
                safe_url(settings.ea_download_link)
            ),
        )
    else:
        await bot_or_message.send_message(
            user.telegram_id,
            text,
            reply_markup=download_next_keyboard(
                safe_url(settings.ea_download_link)
            ),
        )


@router.message(CommandStart())
async def start(message: Message, session: AsyncSession, bot: Bot):
    arg = ""
    parts = (message.text or "").split(maxsplit=1)

    if len(parts) > 1:
        arg = parts[1]

    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            state="START",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    if arg.startswith("pay_"):
        order_code = arg.replace("pay_", "")

        pay_result = await session.execute(
            select(Payment).where(Payment.order_code == order_code)
        )
        payment = pay_result.scalar_one_or_none()

        if payment:
            payment.user_id = user.id
            user.email = payment.email
            await session.commit()

            if payment.status == "APPROVED":
                await unlock_user(session, user)
                await send_access_step_1(message, user)
                return

            await message.answer(
                "✅ Your payment order is connected to this Telegram account.\n\n"
                "Status: PENDING admin verification.\n\n"
                "You will receive access here after approval."
            )
            return

    await message.answer(
        "🚀 Welcome to UpNorthBot Automated Trading Bot\n\n"
        "To unlock access:\n"
        "1. Pay on the website\n"
        "2. Continue here after payment\n"
        "3. Join our channel and group\n"
        "4. Admin verifies your payment\n"
        "5. Receive EA, guide, private community and copier access\n\n"
        "Click below after payment to complete community onboarding.",
        reply_markup=join_keyboard(
            safe_url(settings.public_channel_link),
            safe_url(settings.public_group_link),
        ),
    )


@router.callback_query(F.data == "check_join")
async def check_join(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    joined_channel = await is_member(
        bot,
        callback.from_user.id,
        settings.public_channel_id,
    )
    joined_group = await is_member(
        bot,
        callback.from_user.id,
        settings.public_group_id,
    )

    if not joined_channel or not joined_group:
        await callback.answer(
            "Please join both channel and group first.",
            show_alert=True,
        )
        return

    await callback.answer("Joined confirmed")
    await callback.message.answer(
        "✅ Community joined successfully.\n\n"
        "If your payment is approved, your access will be sent here automatically."
    )


@router.callback_query(F.data.startswith("approve_payment:"))
async def approve_payment(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    if callback.from_user.id not in settings.admin_chat_ids:
        await callback.answer("Admin only", show_alert=True)
        return

    payment_id = int(callback.data.split(":")[1])

    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one()

    payment.status = "APPROVED"
    payment.approved_at = datetime.utcnow()

    user = None

    if payment.user_id:
        user_result = await session.execute(
            select(User).where(User.id == payment.user_id)
        )
        user = user_result.scalar_one_or_none()

        if user:
            await unlock_user(session, user)

    await session.commit()

    if user and user.telegram_id:
        await send_access_step_1(bot, user)

    await callback.message.edit_text(
        f"✅ Payment approved: {payment.order_code}"
    )
    await callback.answer("Approved")


@router.callback_query(F.data.startswith("reject_payment:"))
async def reject_payment(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    if callback.from_user.id not in settings.admin_chat_ids:
        await callback.answer("Admin only", show_alert=True)
        return

    payment_id = int(callback.data.split(":")[1])

    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one()

    payment.status = "REJECTED"
    await session.commit()

    await callback.message.edit_text(
        f"❌ Payment rejected: {payment.order_code}"
    )
    await callback.answer("Rejected")


@router.callback_query(F.data == "access_step_join")
async def access_step_join(callback: CallbackQuery):
    await callback.message.answer(
        "Step 2/4: Join our private community.\n\n"
        "You must join both the private channel and private group before continuing.",
        reply_markup=private_join_keyboard(),
    )

    await callback.answer()


@router.callback_query(F.data == "access_step_install")
async def access_step_install(callback: CallbackQuery, bot: Bot):
    joined_channel = await is_member(
        bot,
        callback.from_user.id,
        settings.private_channel_id,
    )
    joined_group = await is_member(
        bot,
        callback.from_user.id,
        settings.private_group_id,
    )

    if not joined_channel or not joined_group:
        await callback.answer(
            "Please join both private channel and private group first.",
            show_alert=True,
        )
        return

    await callback.message.answer(
        "Step 3/4: Watch the installation guide.\n\n"
        "This video will show you how to install the EA on MT5 correctly.",
        reply_markup=install_video_keyboard(
            safe_url(settings.install_guide_link)
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "access_step_copier")
async def access_step_copier(callback: CallbackQuery, session: AsyncSession):
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.access_active:
        await callback.answer("Your access is not active.", show_alert=True)
        return

    await callback.message.answer(
        "Step 4/4: Trade Copier Setup + License Key\n\n"
        f"⚡ Trade Copier Setup:\n{safe_url(settings.copier_link)}\n\n"
        f"🔑 Your License Key:\n`{user.license_key}`\n\n"
        "⚠️ Forex trading involves risk. This bot does not guarantee profit.",
        reply_markup=copier_license_keyboard(
            safe_url(settings.copier_link)
        ),
        parse_mode="Markdown",
    )
    await callback.answer()