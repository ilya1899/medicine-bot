from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):
    admin = State()


from app.database.requests import requestsAdmin
from app.keyboards import kbReply


async def admin(message: Message, state: FSMContext):
    if await requestsAdmin.is_admin(message.from_user.id):
        await state.clear()
        await state.set_state(Admin.admin)
        await message.answer('Вы открыли панель администратора', reply_markup=kbReply.kbAdminMain)


async def goToMainPage(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Добро пожаловать!', reply_markup=await kbReply.kbPatientMain(message.from_user.id))
