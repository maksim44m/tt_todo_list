from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from database.db_models import Base


class DB:
    def __init__(self, engine: Engine):
        self.engine = engine

        Base.metadata.create_all(self.engine)

        self.SessionLocal = sessionmaker(bind=self.engine,
                                         autoflush=False,
                                         future=True,
                                         expire_on_commit=False)

    def __enter__(self):
        self.session = self.SessionLocal()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
            print(exc_type, exc_val, exc_tb)
        else:
            self.session.commit()
        self.session.close()
