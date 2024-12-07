from aiogram import Router, F
from app.keyboards import get_samples

from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.database.requests import (
    result_answers, create_result,
    add_question_to_quiz, get_last_result,

    set_user, get_question_choices_from_db,
    get_next_question_id, get_first_question
)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(int(message.from_user.id))

    await message.answer(
        "Essential uchun test shablonlar ro'yhati",
        reply_markup=await get_samples())


@router.callback_query(F.data.startswith("sample_"))
async def sample_quizzes_callback(call: CallbackQuery):
    await call.answer('successfully!')
    sample_id = int(call.data.split('_')[1])
    first_question = await get_first_question(sample_id=sample_id)
    await create_result(user_id=call.from_user.id, sample_id=sample_id)

    return call.message.answer(
        text=first_question.title,
        reply_markup=await get_question_choices_from_db(question=first_question))


@router.callback_query(F.data.startswith("choice_"))
async def choice_callback(call: CallbackQuery):
    await call.answer('successfully!')
    result = await get_last_result(user_id=call.from_user.id)
    await add_question_to_quiz(
        result_id=result.id, question_id=int(call.data.split('_')[3]), option_id=int(call.data.split('_')[1]))

    next_question = await get_next_question_id(
        question_id=int(call.data.split('_')[3]),
        sample_id=int(call.data.split('_')[5]))

    if next_question:
        return call.message.answer(
            text=next_question.title,
            reply_markup=await get_question_choices_from_db(question=next_question))

    response = await result_answers(quiz_result_id=result.id)

    return call.message.answer(
        text=f"correct answers: {response.get('total_correct')}\n\nincorrect answers: {response.get('total_incorrect')}",
    )
