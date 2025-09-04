from aiogram import Router, F
from aiogram.types import Message



router = Router()


from app.businessLogic import logicAboutUs


@router.message(F.text == 'О нас')
async def message_aboutUs(message: Message):
    await logicAboutUs.aboutUs(message)






