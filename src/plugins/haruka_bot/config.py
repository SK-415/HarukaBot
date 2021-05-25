from typing import Optional
from pydantic import BaseSettings


class Config(BaseSettings):
    
    haruka_dir: Optional[str] = None
    haruka_to_me: bool = True

    class Config:
        extra = "ignore"