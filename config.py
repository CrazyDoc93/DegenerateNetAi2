from pydantic import BaseModel


class Config(BaseModel):
    license_key: str = ""


def readConfig():
    with open("config.json", "r", encoding="utf-8") as f:
        return Config.parse_raw(f.read())


def writeConfig(config: Config):
    with open("config.json", "w", encoding="utf-8") as f:
        f.write(config.json())
