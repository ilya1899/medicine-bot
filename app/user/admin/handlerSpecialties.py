from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


router = Router()


class EditSpecialty(StatesGroup):
    add = State()






from app.database.requests import requestsSpecialty
from app.keyboards import kbInline, kbReply
from app.businessLogic.admin.logicAdmin import Admin, admin



@router.message(F.text == 'Специальности', Admin.admin)
async def message_specialties(message: Message):
    await message.answer('Выберите действие', reply_markup=kbInline.specialtiesCommand)

@router.callback_query(F.data == 'returnToAdminMenu')
async def callback_specialties(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Admin.admin)
    await callback.message.delete()
    await callback.message.answer('Вы открыли панель администратора', reply_markup=kbReply.kbAdminMain)


@router.callback_query(F.data == 'addSpecialty')
async def callback_addSpecialty(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditSpecialty.add)
    await callback.message.edit_text('Введите название специальности', reply_markup=kbInline.returnToAdminMenu)


@router.message(EditSpecialty.add)
async def message_addSpecialty(message: Message, state: FSMContext):
    await requestsSpecialty.add_specialty(message.text)
    await state.set_state(Admin.admin)
    await message.answer('Специальность добавлена!', reply_markup=kbReply.kbAdminMain)




