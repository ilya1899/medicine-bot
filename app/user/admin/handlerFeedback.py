from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext



router = Router()


from app.database.requests import requestsReview, requestsDoctor
from app.keyboards import kbInline, kbReply
from app.businessLogic.admin.logicAdmin import Admin




@router.message(F.text == 'Отзывы', Admin.admin)
async def message_feedbackAdmin(message: Message):
    await message.answer('Выберите врача',
                         reply_markup=await kbInline.getKeyboardAllDoctors(await requestsDoctor.get_all_doctors(),
                                                                           'feedbackAdmin'))

@router.callback_query(F.data == 'returnToFeedbackAdmin')
async def callback_returnToFeedbackAdmin(callback: CallbackQuery):
    await callback.message.edit_text('Выберите врача',
                                     reply_markup=await kbInline.getKeyboardAllDoctors(await requestsDoctor.get_all_doctors(),
                                                                                       'feedbackAdmin'))



async def feedbackAdminDoctor(callback, doctor_id, index):
    reviews = await requestsReview.get_reviews_by_doctor_id(doctor_id)
    if len(reviews) > 0:
        review = reviews[index]
        await callback.message.edit_text(f'''Оценка пациента <code>{review.patient_id}</code>

• Внимание к деталям, подробно и понятно объясняет - {review.stars_1}
• Вежливость - {review.stars_2}
• Удовлетворенность результатом консультации - {review.stars_3}
• Рекомендуют близким - {review.stars_4}

<b>Отзыв</b>

<i>{review.review}</i>

''', parse_mode='html', reply_markup=await kbInline.getKeyboardFeedbackAdmin(index, len(reviews), review.id, doctor_id))
    else:
        await callback.message.delete()
        await callback.message.answer('Отзывы не найдены', reply_markup=kbReply.kbAdminMain)


@router.callback_query(F.data.startswith('feedbackAdmin_'))
async def callback_feedbackAdminDoctor(callback: CallbackQuery):
    doctor_id = int(callback.data.split('_')[1])
    await feedbackAdminDoctor(callback, doctor_id, 0)

@router.callback_query(F.data.startswith('goBackFeedbackAdmin_'))
async def callback_goBackFeedbackAdmin(callback: CallbackQuery):
    index = int(callback.data.split('_')[1])
    doctor_id = int(callback.data.split('_')[2])
    if index > 0:
        await feedbackAdminDoctor(callback, doctor_id, index - 1)
    else:
        await callback.answer('Это начало')

@router.callback_query(F.data.startswith('goForwardFeedbackAdmin_'))
async def callback_goForwardFeedbackAdmin(callback: CallbackQuery):
    index = int(callback.data.split('_')[1])
    doctor_id = int(callback.data.split('_')[2])
    if index < await requestsReview.get_number_of_reviews_by_doctor_id(doctor_id) - 1:
        await feedbackAdminDoctor(callback, doctor_id, index + 1)
    else:
        await callback.answer('Это конец')

@router.callback_query(F.data.startswith('deleteReview_'))
async def callback_deleteReview(callback: CallbackQuery):
    id = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    doctor_id = int(callback.data.split('_')[3])
    await callback.message.edit_text('Вы уверены?', reply_markup=await kbInline.getKeyboardDeleteReview(index, id, doctor_id))


@router.callback_query(F.data.startswith('yesDeleteReview_'))
async def callback_yesDeleteReview(callback: CallbackQuery):
    id = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    doctor_id = int(callback.data.split('_')[3])
    await requestsReview.delete_review(id)
    await callback.message.edit_text('Удалено',
                                     reply_markup=await kbInline.getKeyboardFeedbackAdmin(index,
                                                                                          await requestsReview.get_number_of_reviews_by_doctor_id(doctor_id),
                                                                                          -1,
                                                                                          doctor_id))


@router.callback_query(F.data.startswith('noDeleteReview_'))
async def callback_noDeleteReview(callback: CallbackQuery):
    index = int(callback.data.split('_')[1])
    doctor_id = int(callback.data.split('_')[2])
    await feedbackAdminDoctor(callback, doctor_id, index)





