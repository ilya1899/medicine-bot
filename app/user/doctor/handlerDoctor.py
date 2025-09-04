from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

from app.database.requests import requestsDoctor
from app.keyboards import kbReply


@router.message(Command('doctor'))
async def cmd_doctor(message: Message):
    user_id = message.from_user.id
    if await requestsDoctor.is_doctor(user_id):
        await message.answer('Вы открыли меню доктора', reply_markup=kbReply.kbDoctorMain)


@router.message(F.text == 'Перейти в кабинет врача')
async def cmd_doctor(message: Message):
    user_id = message.from_user.id
    if await requestsDoctor.is_doctor(user_id):
        await message.answer('Вы открыли меню доктора', reply_markup=kbReply.kbDoctorMain)


@router.message(F.text == 'Перейти в аккаунт пользователя')
async def message_goToMainPage(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    if await requestsDoctor.is_doctor(user_id):
        await message.answer('Вы вернулись в главное меню', reply_markup=await kbReply.kbPatientMain(user_id))
