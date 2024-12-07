import os
from dotenv import load_dotenv
from sqlalchemy import ForeignKey, String, BigInteger, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, backref
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

load_dotenv()
engine = create_async_engine(url=os.getenv("DB_URL"), echo=True, future=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=True)
    tg_id = mapped_column(BigInteger)


class Test(Base):
    __tablename__ = 'tests'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))


class Samples(Base):
    __tablename__ = 'samples'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    test = Column(Integer, ForeignKey('tests.id'))
    tests = relationship('Test', backref=backref(''))
    title: Mapped[str] = mapped_column(String(120))


class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sample = Column(Integer, ForeignKey('samples.id'))
    title: Mapped[str] = mapped_column(String(160))


class Choice(Base):
    __tablename__ = 'choices'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question = Column(Integer, ForeignKey('questions.id'))
    title: Mapped[str] = mapped_column(String(160))
    answer_text: Mapped[str] = mapped_column(String(10))
    is_true: Mapped[bool] = mapped_column(default=False)

    quizzes = relationship("Quiz", back_populates="choice")
    # choices = relationship("Choice", back_populates="question")


class QuizResult(Base):
    __tablename__ = 'quiz_results'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user = Column(ForeignKey('users.id'))
    sample = Column(ForeignKey('samples.id'))
    correct_total: Mapped[int] = mapped_column(default=0)
    incorrect_total: Mapped[int] = mapped_column(default=0)


class Quiz(Base):
    __tablename__ = 'quizzes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_result = Column(Integer, ForeignKey('quiz_results.id'))
    question = Column(Integer, ForeignKey('questions.id'))
    selected_option = Column(Integer, ForeignKey('choices.id'))

    choice = relationship("Choice", back_populates="quizzes", foreign_keys=[selected_option])


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
