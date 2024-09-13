import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine

load_dotenv()


class DBConfig:
    def __init__(self) -> None:
        username = os.getenv("POSTGRES_USERNAME")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST")
        database_name = os.getenv("POSTGRES_DBNAME")

        connection_url = (
            f"postgresql+psycopg2://{username}:{password}@{host}/{database_name}"
        )
        self.__engine = (engine := create_engine(connection_url))
        metadata = MetaData()
        metadata.reflect(bind=engine)

        self.__metadata = metadata

    def get_table(self, table: str):
        return self.__metadata.tables[table]

    def get_engine(self):
        return self.__engine


dbconfig = DBConfig()
