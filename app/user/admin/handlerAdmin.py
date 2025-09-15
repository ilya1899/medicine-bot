from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()

from app.businessLogic.admin.logicAdmin import Admin
from app.businessLogic.admin import logicAdmin


@router.message(Command('admin'))
async def cmd_admin(message: Message, state: FSMContext):
    await logicAdmin.admin(message, state)


@router.message(F.text == 'На главную', Admin.admin)
async def message_goToMainPage(message: Message, state: FSMContext):
    await logicAdmin.goToMainPage(message, state)
