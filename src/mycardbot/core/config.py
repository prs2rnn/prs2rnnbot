from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    bot_token: str
    admin_ids: list[int]
    debug: bool


setting = Setting()
