import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"

    DB_SHRT_STRING = 100
    DB_LONG_STRING = 500
