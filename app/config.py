from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(alias="BOT_TOKEN")
    admin_chat_ids_raw: str = Field(default="", alias="ADMIN_CHAT_IDS")
    database_url: str = Field(alias="DATABASE_URL")
    database_sync_url: str = Field(alias="DATABASE_SYNC_URL")

    brand_name: str = Field(default="UpNorthBot", alias="BRAND_NAME")

    public_channel_id: int = Field(alias="PUBLIC_CHANNEL_ID")
    public_group_id: int = Field(alias="PUBLIC_GROUP_ID")
    public_channel_link: str = Field(alias="PUBLIC_CHANNEL_LINK")
    public_group_link: str = Field(alias="PUBLIC_GROUP_LINK")
    telegram_bot_username: str = Field(alias="TELEGRAM_BOT_USERNAME")

    usdt_trc20_address: str = Field(default="", alias="USDT_TRC20_ADDRESS")
    usdt_bep20_address: str = Field(default="", alias="USDT_BEP20_ADDRESS")
    btc_address: str = Field(default="", alias="BTC_ADDRESS")

    usdt_trc20_qr: str = Field(default="/static/img/usdt-trc20.png", alias="USDT_TRC20_QR")
    usdt_bep20_qr: str = Field(default="/static/img/usdt-bep20.png", alias="USDT_BEP20_QR")
    btc_qr: str = Field(default="/static/img/btc.png", alias="BTC_QR")

    ea_download_link: str = Field(default="", alias="EA_DOWNLOAD_LINK")
    install_guide_link: str = Field(default="", alias="INSTALL_GUIDE_LINK")
    private_channel_id: int = Field(default=0, alias="PRIVATE_CHANNEL_ID")
    private_group_id: int = Field(default=0, alias="PRIVATE_GROUP_ID")
    private_channel_link: str = Field(default="", alias="PRIVATE_CHANNEL_LINK")
    private_group_link: str = Field(default="", alias="PRIVATE_GROUP_LINK")
    copier_link: str = Field(default="", alias="COPIER_LINK")

    app_base_url: str = Field(default="http://localhost:8080", alias="APP_BASE_URL")
    secret_key: str = Field(default="change-this-secret", alias="SECRET_KEY")

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def admin_chat_ids(self) -> list[int]:
        return [
            int(x.strip())
            for x in self.admin_chat_ids_raw.split(",")
            if x.strip()
        ]


settings = Settings()