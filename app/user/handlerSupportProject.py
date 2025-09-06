from aiogram import Router, F
from aiogram.types import Message

router = Router()

from app.businessLogic import logicSupportProject


@router.message(F.text == 'Поддержать проект')
async def message_supportProject(message: Message):
    await logicSupportProject.supportProject(message)
