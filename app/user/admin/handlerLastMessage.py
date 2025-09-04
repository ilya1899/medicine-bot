from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


router = Router()

class EditText(StatesGroup):
    text = State()



from app.businessLogic.admin.logicAdmin import Admin
from app.database.requests import requestsLastMessage
from app.keyboards import kbReply, kbInline


@router.message(F.text == 'Изменить текст', Admin.admin)
async def message_lastMessage(message: Message):
    await message.answer('Выберите, что нужно изменить', reply_markup=kbInline.whatsEditLastMessage)


async def editTextLastMessage(callback, state, function):
    await state.set_state(EditText.text)
    await state.update_data(function=function)
    await callback.message.edit_text('Напишите новый текст')



@router.callback_query(F.data == 'editTextLastMessageReview')
async def callback_editTextLastMessageReview(callback: CallbackQuery, state: FSMContext):
    await editTextLastMessage(callback, state, 'review')

@router.callback_query(F.data == 'editTextLastMessageBeforeConsultations')
async def callback_editTextLastMessageBeforeConsultations(callback: CallbackQuery, state: FSMContext):
    await editTextLastMessage(callback, state, 'before_consultations')

@router.message(EditText.text)
async def message_editTextLastMessage(message: Message, state: FSMContext):
    data = await state.get_data()
    if await requestsLastMessage.is_last_message_by_function(data['function']):
        await requestsLastMessage.edit_last_message_by_function(message.html_text, data['function'])
    else:
        await requestsLastMessage.add_last_message(message.html_text, data['function'])
    await state.clear()
    await state.set_state(Admin.admin)
    await message.answer('Изменения сохранены', reply_markup=kbReply.kbAdminMain)






