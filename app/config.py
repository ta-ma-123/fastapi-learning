from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB接続先
    database_url: str
    frontend_origins: list[str]


    # .envから設定値を読み込む
    # Settingsに定義されていない項目は無視する
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


# アプリ内で共通して使用する設定
settings = Settings()
