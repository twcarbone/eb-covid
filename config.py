import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"

    PG_DRIVER = "postgresql+psycopg2"
    PG_USER = "postgres"
    PG_PW = os.environ.get("PG_PW")
    PG_HOST_DEV = "192.168.4.68"
    PG_HOST_TEST = "192.168.4.68"
    PG_HOST_PROD = "147.182.129.114"
    PG_PORT = 5432
    PG_DB_DEV = "EBCovid_dev"
    PG_DB_TEST = "EBCovid_test"
    PG_DB_PROD = "EBCovid"

    DB_URI_DEV = f"{PG_DRIVER}://{PG_USER}:{PG_PW}@{PG_HOST_DEV}:{PG_PORT}/{PG_DB_DEV}"
    DB_URI_TEST = f"{PG_DRIVER}://{PG_USER}:{PG_PW}@{PG_HOST_TEST}:{PG_PORT}/{PG_DB_TEST}"
    DB_URI_PROD = f"{PG_DRIVER}://{PG_USER}:{PG_PW}@{PG_HOST_PROD}:{PG_PORT}/{PG_DB_PROD}"
