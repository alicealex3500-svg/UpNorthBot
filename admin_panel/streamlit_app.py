from datetime import datetime, timedelta
import secrets
import streamlit as st
from sqlalchemy import select, func
from app.db import SyncSessionLocal
from app.models import Payment, User
from app.utils import make_license_key
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

st.set_page_config(page_title='FX Hustle Admin', layout='wide')
st.title('⚡ FX Hustle Room Admin')

session = SyncSessionLocal()

pending = session.scalar(select(func.count()).select_from(Payment).where(Payment.status == 'PENDING')) or 0
approved = session.scalar(select(func.count()).select_from(Payment).where(Payment.status == 'APPROVED')) or 0
active = session.scalar(select(func.count()).select_from(User).where(User.access_active == True)) or 0
c1,c2,c3 = st.columns(3)
c1.metric('Pending Payments', pending); c2.metric('Approved Payments', approved); c3.metric('Active Users', active)

st.header('Pending Crypto Payments')
payments = session.scalars(select(Payment).where(Payment.status == 'PENDING').order_by(Payment.created_at.desc())).all()
for p in payments:
    with st.container(border=True):
        st.write(f'**Order:** {p.order_code}')
        st.write(f'**Name:** {p.full_name} | **Email:** {p.email} | **Telegram:** {p.telegram_username}')
        st.write(f'**Plan:** {p.plan} | **Amount:** ${p.amount_usd} | **Network:** {p.network}')
        st.code(p.tx_hash or '')
        col1,col2 = st.columns(2)
        if col1.button('Approve Payment', key=f'ap_{p.id}'):
            p.status = 'APPROVED'; p.approved_at = datetime.utcnow()
            if p.user_id:
                user = session.get(User, p.user_id)
                if user:
                    user.paid = True; user.access_active = True; user.state = 'ACCESS_ACTIVE'
                    if not user.license_key: user.license_key = make_license_key()
                    user.license_expires_at = datetime.utcnow() + timedelta(days=30)
            session.commit(); st.rerun()
        if col2.button('Reject Payment', key=f'rj_{p.id}'):
            p.status = 'REJECTED'; session.commit(); st.rerun()

st.header('Active Users')
users = session.scalars(select(User).order_by(User.created_at.desc()).limit(100)).all()
for u in users:
    with st.container(border=True):
        st.write(f'**{u.full_name}** @{u.username} — `{u.telegram_id}`')
        st.write(f'Email: {u.email} | Access: {u.access_active} | Expiry: {u.license_expires_at}')
        st.code(u.license_key or '')
        if u.access_active:
            if st.button('Disable Access', key=f'dis_{u.id}'):
                u.access_active = False; u.state = 'ACCESS_DISABLED'; session.commit(); st.rerun()
