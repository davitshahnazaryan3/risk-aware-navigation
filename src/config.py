from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	mongo_user: str
	mongo_password: str
	database_name: str
	ip_address: str
	port: str
	map_name: str = "map_a"
	redis_host: str = "cache"
	redis_port: str = "6379"

	class Config:
		env_file = "./.env"


settings = Settings()
