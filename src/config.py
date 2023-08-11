from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_initdb_root_username: str
    mongo_initdb_root_password: str
    database_name: str
    navigation_ip_address: str
    navigation_port: str
    map_name: str = "map_a"
    redis_host: str = "cache"
    redis_port: str = "6379"
    db_type: str = "local"

    class Config:
        env_file = "./.env"


settings = Settings()
