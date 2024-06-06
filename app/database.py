from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import URL, create_engine, text

# Подключение к базе данных
engine = create_engine(
    url='sqlite:///kino.db',
    echo=True,
)

Session = sessionmaker(engine)


class Base(DeclarativeBase):
    pass
