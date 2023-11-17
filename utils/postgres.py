import pandas as pd
import os


class PostgresDB(object):

    def __init__(
            self,
            port: int = 5432,
            db_name: str = 'spoticluster'
    ):
        self.db_name = db_name
        self.port = int(port)


    @property
    def conn(
        self
    ):
        username = os.environ['POSTGRES_USER']
        password = os.environ['POSTGRES_PASSWORD']
        host = os.environ['POSTGRES_HOST']

        if not hasattr(self, "_conn"):
            url_object = URL.create(
                'postgresql',
                username=username,
                password=password,
                host=host,
                port=self.port,
                database=self.db_name
            )

            self._conn = create_engine(
                url_object,
                echo=True,
                pool_size=5,
                max_overflow=0,
                pool_pre_ping=False,
            )
        return self._conn

    def engine(self):
        return self.conn


def df_to_db(
    df,
    table_name,
    insert_method="append",
    chunksize=None,
    method="multi",
):
    """Wrap df_to_db function to create engine and write to database table."""
    db = PostgresDB()

    df.to_sql(
        table_name,
        con=db.engine(),
        index=False,
        if_exists=insert_method,
        schema="public",
        chunksize=chunksize,
        method=method,
    )
