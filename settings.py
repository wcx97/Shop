from pydantic import BaseSettings


class _Settings(BaseSettings):
    TOKEN: str = ''
    GUILD: int = ''
    TIMEZONE: str = 'Asia/Shanghai'
    DEBUG: bool = False
    DATABASE: str = 'sqlite+aiosqlite:///database.db'
    # bot工作的channel ID
    CHANNEL_ID: int = 1026003196050673751
    # 管理员channel ID
    ADMIN_CHANNEL_ID: int = 1026003196050673751
    # 生日祝福类channel
    BIRTHDAY_CHANNEL: int = 1026003196050673751

    GIVEAWAY_MAX_MINUTES: int = 60  # 设置最大的抽奖分钟数

    class Config:
        # 使用环境变量读取
        env_file = ".env"


SETTINGS = _Settings()
