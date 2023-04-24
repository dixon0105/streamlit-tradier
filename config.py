from pydantic import BaseSettings, BaseModel

class Crednetial(BaseModel):
    email: str
    name: str
    password: str


class Config(BaseModel):
    credentials: dict
    cookie: dict

class Settings(BaseSettings):
    base32secret: str
    CMC_APIKEY: str
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str