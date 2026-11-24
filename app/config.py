"""Settings come from the environment (12-factor). See .env.example."""
import os


class Config:
    def __init__(self, overrides=None):
        env = os.environ
        self.HOST = env.get("HOST", "127.0.0.1")
        self.PORT = int(env.get("PORT", "5000"))
        self.DEBUG = env.get("DEBUG", "0") == "1"
        self.LOG_LEVEL = env.get("LOG_LEVEL", "INFO").upper()
        # Business settings
        self.MAX_COPIES = int(env.get("MAX_COPIES", "10"))
        self.MAX_ACTIVE_LOANS = int(env.get("MAX_ACTIVE_LOANS", "3"))
        for key, value in (overrides or {}).items():
            setattr(self, key, value)
