from typing import Optional

from pydantic import BaseSettings, validator


# 其他地方出现的类似 from .. import config，均是从 __init__.py 导入的 Config 实例
class Config(BaseSettings):
    fastapi_reload: bool = False
    haruka_dir: Optional[str] = None
    haruka_to_me: bool = True
    haruka_live_off_notify: bool = False
    haruka_proxy: Optional[str] = None
    haruka_interval: int = 10
    haruka_live_interval: int = haruka_interval
    haruka_dynamic_interval: int = 1
    haruka_dynamic_at: bool = False
    haruka_screenshot_style: str = "mobile"

    @validator("haruka_interval", "haruka_live_interval", "haruka_dynamic_interval")
    def positive_only(cls, v):
        if v < 1:
            return 1
        return v

    class Config:
        extra = "ignore"
