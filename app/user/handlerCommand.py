from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

router = Router()


from app.businessLogic import logicCommand


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await logicCommand.start(message, state)

@router.callback_query(F.data == 'returnToMenu')
async def callback_returnToMenu(callback: CallbackQuery, state: FSMContext):
    await logicCommand.returnToMenu(callback, state)



