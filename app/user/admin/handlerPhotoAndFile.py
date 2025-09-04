from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext



router = Router()


class EditPhotoOrFile(StatesGroup):
    photoStart = State()





from app.database.requests import requestsPhotoAndFile
from app.keyboards import kbInline, kbReply
from app.businessLogic.admin.logicAdmin import Admin


@router.message(F.text == 'Изменить фото/файл', Admin.admin)
async def message_editPhotoOrFile(message: Message):
    await message.answer('Выберите что изменить', reply_markup=kbInline.whatsEditPhotoAndFile)

@router.callback_query(F.data == 'editPhotoStart')
async def callback_editPhotoStart(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPhotoOrFile.photoStart)
    await callback.message.edit_text('Отправьте новое изображение')

@router.message(EditPhotoOrFile.photoStart)
async def message_editPhotoStart(message: Message, state: FSMContext):
    await state.set_state(Admin.admin)
    await requestsPhotoAndFile.delete_photo_or_file_by_function('start')
    await requestsPhotoAndFile.add_photo_or_file(message.photo[-1].file_id, 'start')
    await message.answer('Изменения сохранены', reply_markup=kbReply.kbAdminMain)





