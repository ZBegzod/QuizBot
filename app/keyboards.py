from app.database.requests import get_samples_from_db, get_questions_from_db
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


async def get_samples():
    all_samples = await get_samples_from_db()
    keyboard = InlineKeyboardBuilder()

    for sample in all_samples:
        keyboard.add(InlineKeyboardButton(text=sample.title, callback_data=f"sample_{sample.id}"))

    return keyboard.adjust(5).as_markup()


async def get_question_choices(sample_id: int):
    all_questions = await get_questions_from_db(sample_id=sample_id)
    keyboard = InlineKeyboardBuilder()
    for question in all_questions:
        keyboard.add(InlineKeyboardButton(text=question.title))

