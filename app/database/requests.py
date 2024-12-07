from app.database.models import (
    User, Test, Question, Choice,
    Samples, QuizResult, Quiz,
    async_session,
)
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder, InlineKeyboardBuilder
)
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from sqlalchemy import func, case, and_
from sqlalchemy.future import select


def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return wrapper


@connection
async def set_user(session, tg_id: int):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if not user:
        session.add(User(tg_id=tg_id))
        await session.commit()


@connection
async def get_questions_from_db(session, sample_id):
    questions = await session.scalars(select(Question).where(Question.sample == sample_id))
    return questions.all()


@connection
async def get_question_choices_from_db(session, question):
    choices = await session.scalars(select(Choice).where(Choice.question == question.id))
    keyboard = InlineKeyboardBuilder()

    for choice in choices:
        keyboard.add(
            InlineKeyboardButton(
                text=choice.answer_text,
                callback_data=f"choice_{choice.id}_question_{question.id}_sample_{question.sample}"))

    return keyboard.adjust(2).as_markup()


@connection
async def get_samples_from_db(session):
    samples = await session.execute(select(Samples))
    return samples.scalars().all()


@connection
async def get_first_question(session, sample_id):
    question = await session.execute(select(Question).where(
        Question.sample == sample_id).order_by(Question.id.asc()))
    question = question.scalars().first()

    return question


@connection
async def get_next_question_id(session, question_id, sample_id):
    new_question = await session.execute(
        select(Question).where(
            and_
            (Question.id > question_id,
             Question.sample == sample_id)
        ).order_by(Question.id).limit(1))

    return new_question.scalar_one_or_none()


# ---------------------- User answers ---------------------------

@connection
async def user_results(session, user_id: int):
    results = await session.query(QuizResult).filter_by(user=user_id).all()
    return results


@connection
async def create_result(session, user_id: int, sample_id: int):
    result = QuizResult(user=user_id, sample=sample_id)
    session.add(result)
    await session.commit()

    return result


@connection
async def get_last_result(session, user_id: int):
    query = select(QuizResult).filter_by(user=user_id).order_by(QuizResult.id.desc())
    result = await session.execute(query)
    result = result.scalars().first()

    return result if result else None


@connection
async def add_question_to_quiz(session, result_id, question_id, option_id):
    quiz = Quiz(quiz_result=result_id, question=question_id, selected_option=option_id)
    session.add(quiz)
    await session.commit()


@connection
async def result_answers(session, quiz_result_id):
    response = {}

    user_result = await session.execute(
        select(
            QuizResult.id, Quiz.question, Quiz.selected_option, Choice.is_true,
            func.sum(case(
                (Choice.is_true == True, 1),  # Condition for True
                else_=0  # Default case
            )).label('correct_total'),
            func.sum(case(
                (Choice.is_true == False, 1),  # Condition for False
                else_=0  # Default case
            )).label('incorrect_total')
        )
        .join(Quiz, QuizResult.id == Quiz.quiz_result)
        .join(Choice, Choice.id == Quiz.selected_option)
        .where(QuizResult.id == quiz_result_id).group_by(QuizResult.id)
    )

    result = user_result.fetchone()
    correct_total = result.correct_total if result.correct_total else 0
    incorrect_total = result.incorrect_total if result.incorrect_total else 0
    print(f"Total Correct Answers: {correct_total}, Total Incorrect Answers: {incorrect_total}")

    response.update({'total_correct': correct_total, 'total_incorrect': incorrect_total})
    return response

# ---------------------------------------------------------------
