from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.models import User

router = APIRouter(prefix='/license', tags=['license'])

class LicenseCheckRequest(BaseModel):
    license_key: str
    mt5_account_number: str | None = None

@router.post('/check')
async def check_license(payload: LicenseCheckRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.license_key == payload.license_key))
    user = result.scalar_one_or_none()
    if not user:
        return {'status': 'invalid', 'message': 'License not found'}
    if not user.access_active:
        return {'status': 'disabled', 'message': 'Access disabled'}
    if user.license_expires_at and user.license_expires_at < datetime.utcnow():
        user.access_active = False
        user.state = 'ACCESS_DISABLED'
        await session.commit()
        return {'status': 'expired', 'message': 'License expired'}
    if payload.mt5_account_number:
        if not user.mt5_account_number:
            user.mt5_account_number = payload.mt5_account_number
            await session.commit()
        elif user.mt5_account_number != payload.mt5_account_number:
            return {'status': 'blocked', 'message': 'License already bound to another MT5 account'}
    return {'status': 'active', 'message': 'License valid'}
