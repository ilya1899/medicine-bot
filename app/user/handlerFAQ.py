from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

router = Router()

from app.businessLogic import logicFAQ


@router.message(F.text == 'Частые вопросы')
async def message_FAQ(message: Message):
    await logicFAQ.FAQ(message)


@router.callback_query(F.data == 'returnToFAQ')
async def callback_backToFAQ(callback: CallbackQuery):
    await logicFAQ.returnToFAQ(callback)


@router.callback_query(F.data.startswith('faq_button_'))
async def callback_FAQ(callback: CallbackQuery):
    await logicFAQ.c_FAQ(callback)
