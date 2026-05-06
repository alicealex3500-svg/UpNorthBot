from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def join_keyboard(channel_link: str, group_link: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join Channel", url=channel_link)],
        [InlineKeyboardButton(text="👥 Join Group", url=group_link)],
        [InlineKeyboardButton(text="✅ I Have Joined", callback_data="check_join")],
    ])


def admin_payment_keyboard(payment_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Approve Payment", callback_data=f"approve_payment:{payment_id}"),
        InlineKeyboardButton(text="❌ Reject Payment", callback_data=f"reject_payment:{payment_id}")
    ]])


def download_next_keyboard(download_link: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Download EA", url=download_link)],
        [InlineKeyboardButton(text="➡️ Next", callback_data="access_step_join")]
    ])


def access_join_keyboard(channel_link: str, group_link: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join Private Channel", url=channel_link)],
        [InlineKeyboardButton(text="👥 Join Private Group", url=group_link)],
        [InlineKeyboardButton(text="✅ I Have Joined", callback_data="access_step_install")]
    ])


def install_video_keyboard(install_guide_link: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Watch Installation Video", url=install_guide_link)],
        [InlineKeyboardButton(text="➡️ Next", callback_data="access_step_copier")]
    ])


def copier_license_keyboard(copier_link: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Trade Copier Setup", url=copier_link)]
    ])