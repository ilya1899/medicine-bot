import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

router = Router()


class WriteReview(StatesGroup):
    star = State()
    text = State()
    temp = State()


from app.keyboards import kbReply, kbInline
from app.database.requests import requestsDoctor, requestsReview, requestsLastMessage
from app.businessLogic import logicConsultation


@router.callback_query(F.data.startswith('star_'))
async def callback_selectStar(callback: CallbackQuery, state: FSMContext):
    patient_id = callback.from_user.id
    number_of_stars = int(callback.data.split('_')[1])
    doctor_id = int(callback.data.split('_')[2])
    number_of_review = int(callback.data.split('_')[3])
    chat_type = callback.data.split('_')[4]
    match number_of_review:
        case 1:
            await state.set_state(WriteReview.star)
            await state.update_data(review_1=number_of_stars)
            await callback.message.edit_text('Был ли доктор вежлив?',
                                             reply_markup=await kbInline.keyboardStars(doctor_id, 2, chat_type))
        case 2:
            await state.update_data(review_2=number_of_stars)
            await callback.message.edit_text('Смог ли доктор помочь Вам?',
                                             reply_markup=await kbInline.keyboardStars(doctor_id, 3, chat_type))
        case 3:
            await state.update_data(review_3=number_of_stars)
            await callback.message.edit_text('Порекомендовали бы Вы этого доктора близким и знакомым?',
                                             reply_markup=await kbInline.keyboardStars(doctor_id, 4, chat_type))
        case 4:
            await state.update_data(review_4=number_of_stars, doctor_id=doctor_id, chat_type=chat_type)
            await state.set_state(WriteReview.temp)
            await callback.message.edit_text('Пожалуйста, оставьте отзыв о враче',
                                             reply_markup=kbInline.notLeaveReview)


@router.callback_query(F.data == 'leaveReview')
async def callback_leaveReview(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WriteReview.text)
    await callback.message.edit_text('Напишите Ваш отзыв о специалисте')


async def writeReview(state, review, patient_id, function):
    data = await state.get_data()
    await state.clear()
    doctor_id = data['doctor_id']
    chat_type = data['chat_type']
    await requestsReview.add_review(patient_id, doctor_id, data['review_1'], data['review_2'],
                                    data['review_3'], data['review_4'], review)
    reviews = await requestsReview.get_reviews_by_doctor_id(doctor_id)
    amount_1 = amount_2 = amount_3 = amount_4 = 0
    for review in reviews:
        amount_1 += review.stars_1
        amount_2 += review.stars_2
        amount_3 += review.stars_3
        amount_4 += review.stars_4
    averageValue_1 = round(amount_1 / len(reviews), 1)
    averageValue_2 = round(amount_2 / len(reviews), 1)
    averageValue_3 = round(amount_3 / len(reviews), 1)
    averageValue_4 = round(amount_4 / len(reviews), 1)
    averageValue = round((averageValue_1 + averageValue_2 + averageValue_3 + averageValue_4) / 4, 1)

    await requestsDoctor.edit_rating_1(doctor_id, averageValue_1)
    await requestsDoctor.edit_rating_2(doctor_id, averageValue_2)
    await requestsDoctor.edit_rating_3(doctor_id, averageValue_3)
    await requestsDoctor.edit_rating_4(doctor_id, averageValue_4)
    await requestsDoctor.edit_rating_all(doctor_id, averageValue)
    price = await logicConsultation.getPrice(doctor_id, chat_type)

    if price == 0:
        await function('''Посылая благодарность доктору, вы не только благодарите его за помощь вам, но и поддерживаете в нем стремление помогать тем, кто не имеет финансовой возможности обратиться к врачу! 
Наша цель — сделать медицину доступнее для каждого, и Ваше участие крайне важно для этого! Вы можете помочь, отправив любую удобную сумму на развитие проекта.  
Каждое пожертвование направляется на улучшение сервисов, создание новых функций и качественную поддержку пользователей.  

Спасибо, что разделяете наши ценности!
''',
                       reply_markup=await kbInline.getKeyboardSupportDoctor(doctor_id))
    else:
        await function('Спасибо! Ваше мнение помогает сделать сервис ещё лучше!',
                       reply_markup=await kbReply.kbPatientMain(patient_id))


@router.callback_query(F.data.startswith('returnToSupportDoctor_'))
async def callback_returnToSupportDoctor(callback: CallbackQuery):
    doctor_id = int(callback.data.split('_')[1])
    await callback.message.edit_text('''Посылая благодарность доктору, вы не только благодарите его за помощь вам, но и поддерживаете в нем стремление помогать тем, кто не имеет финансовой возможности обратиться к врачу! 
Наша цель — сделать медицину доступнее для каждого, и Ваше участие крайне важно для этого! Вы можете помочь, отправив любую удобную сумму на развитие проекта.  
Каждое пожертвование направляется на улучшение сервисов, создание новых функций и качественную поддержку пользователей.  

Спасибо, что разделяете наши ценности!
''', reply_markup=await kbInline.getKeyboardSupportDoctor(doctor_id))


@router.message(WriteReview.text)
async def message_writeReview(message: Message, state: FSMContext):
    await writeReview(state, message.text, message.from_user.id, message.answer)


@router.callback_query(F.data == 'notLeaveReview')
async def callback_notWriteReview(callback: CallbackQuery, state: FSMContext):
    await writeReview(state, '', callback.from_user.id, callback.message.edit_text)


@router.callback_query(F.data.startswith('supportDoctor_'))
async def callback_supportDoctor(callback: CallbackQuery):
    doctor_id = int(callback.data.split('_')[1])
    doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)
    await callback.message.edit_text(f'''{doctor.full_name}

Номер карты МИР:
{doctor.bank_details_russia}

Название банка и номер карты VISA / MASTERCARD:
{doctor.bank_details_abroad}
''', reply_markup=await kbInline.returnToSupportDoctor(doctor_id))


@router.callback_query(F.data == 'lastMessageReview')
async def callback_lastMessageReview(callback: CallbackQuery):
    message = await requestsLastMessage.get_last_message_by_function('review')
    await callback.message.delete()
    if message:
        await callback.message.answer(message.text)
        await asyncio.sleep(15)
    await callback.message.answer('Вы вернулись в главное меню',
                                  reply_markup=await kbReply.kbPatientMain(callback.from_user.id))
