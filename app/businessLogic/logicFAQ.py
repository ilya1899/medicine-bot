from aiogram.types import Message, CallbackQuery


from app.keyboards import kbInline
from texts import faq



async def FAQ(message: Message):
    await message.answer('Здесь представлены ответы на частые вопросы.', reply_markup=kbInline.faqKeyboard)

async def returnToFAQ(callback: CallbackQuery):
    await callback.message.edit_text('Здесь представлены ответы на частые вопросы.', reply_markup=kbInline.faqKeyboard)

async def c_FAQ(callback: CallbackQuery):
    number = int(callback.data.split('_')[2])
    await callback.message.edit_text(faq[number - 1], parse_mode='html', reply_markup=await kbInline.getKeyboardForFAQ(number))








