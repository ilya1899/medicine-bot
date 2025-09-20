import asyncio

from aiogram.fsm.context import FSMContext, StorageKey
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaDocument, ReplyKeyboardRemove

from app.businessLogic.logicRegistration import EditUser
from app.loader import bot, dp
from texts import type_consultation

from config_reader import config


class AttachFile(StatesGroup):
    photoJustAsk = State()
    photoDecoding = State()
    main_first = State()
    main_repeated = State()
    secondOpinion = State()

    justAsk_name = State()
    decoding_name = State()
    main_first_name = State()
    secondOpinion_name = State()

    secondOpinion_link = State()


groupToSend = []

lock = asyncio.Lock()


class FailedConsultation(StatesGroup):
    text = State()


class ChatPatient(StatesGroup):
    openDialog = State()
    replyToDoctor = State()


class Payment(StatesGroup):
    receipt = State()


from app.keyboards import kbInline, kbReply
from app.database.requests import requestsDoctor, requestsMessageToSend, requestsBundle, requestsStatistics, \
    requestsReview, \
    requestsUser, requestsSpecialty, requestsHistoryMessage, requestsHistoryConsultation, requestsLastMessage, \
    requestsMessageToRepeat


async def askDoctor(patient_id, function):
    if await requestsBundle.is_bundle_by_patient_id(patient_id):
        await function('Вы хотите продолжить консультацию или начать новую?', reply_markup=kbInline.continueOrNew)
    else:
        specialties = await requestsSpecialty.get_all_specialties()
        await function('Выберите специальность:',
                       reply_markup=await kbInline.getKeyboardSpecialties(specialties, 0, False))


async def askDoctorMessage(message: Message):
    patient_id = message.from_user.id
    await askDoctor(patient_id, message.answer)


async def askDoctorCallback(callback: CallbackQuery):
    patient_id = callback.from_user.id
    await askDoctor(patient_id, callback.message.edit_text)


async def newConsultation(callback: CallbackQuery):
    specialties = await requestsSpecialty.get_all_specialties()
    await callback.message.edit_text('Выберите специальность:',
                                     reply_markup=await kbInline.getKeyboardSpecialties(specialties, 0, False))


async def continueConsultation(callback: CallbackQuery):
    patient_id = callback.from_user.id
    if await requestsBundle.is_bundle_by_patient_id(patient_id):
        await callback.message.edit_text('Выберите доктора',
                                         reply_markup=await kbInline.getKeyboardContinueConsultation(patient_id))
    else:
        await callback.answer('Активных консультаций нет')


async def continueConsultationDoctor(callback: CallbackQuery, state: FSMContext):
    patient_id = callback.from_user.id
    doctor_id = int(callback.data.split('_')[1])
    await requestsBundle.edit_is_open_dialog_patient(patient_id, doctor_id, True)
    chat_type = await requestsBundle.get_chat_type(patient_id, doctor_id)
    keyboard = kbReply.kbPatientDialog
    await callback.message.delete()
    await callback.message.answer(f'Вы открыли чат с доктором, тип консультации: {type_consultation[chat_type]}',
                                  reply_markup=keyboard)

    try:
        await show_patient_conversation_paginated(callback, doctor_id, patient_id, page=1)
    except Exception as e:
        print(f"Error showing conversation history: {e}")
        # If there's an error, just continue without showing history

    if await requestsMessageToSend.is_message_to_send(doctor_id, patient_id):
        messages = await requestsMessageToSend.get_messages_to_send(doctor_id, patient_id)
        for messageToSend in messages:
            match messageToSend.media_type:
                case 'text':
                    await callback.message.answer(messageToSend.text, parse_mode='html')
                case 'photo':
                    await callback.message.answer(text=messageToSend.text,
                                                  parse_mode='html')
                case 'document':
                    await callback.message.answer_document(document=messageToSend.media_id, caption=messageToSend.text,
                                                           parse_mode='html')
                case 'mediaGroupPhoto' | 'mediaGroupPhoto':
                    group = messageToSend.media_id.split(', ')
                    mediaGroup = []
                    if messageToSend.media_type == 'mediaGroupPhoto':
                        mediaGroup = [InputMediaPhoto(media=photo, parse_mode='html') for photo in group]
                    elif messageToSend.media_type == 'mediaGroupDocument':
                        mediaGroup = [InputMediaDocument(media=document, parse_mode='html') for document in group]

                    if messageToSend.text != '':
                        mediaGroup[0].caption = messageToSend.text
                    await callback.message.answer_media_group(mediaGroup)
        await requestsMessageToSend.delete_messages_to_send(doctor_id, patient_id)
    await state.set_state(ChatPatient.openDialog)
    await state.update_data(doctor_id=doctor_id, chat_type=chat_type)


async def goBack(callback: CallbackQuery):
    page = int(callback.data.split('_')[1])
    specialties = await requestsSpecialty.get_all_specialties()
    if page > 0:
        await callback.message.edit_text('Выберите специальность:',
                                         reply_markup=await kbInline.getKeyboardSpecialties(specialties, page - 1,
                                                                                            False))
    else:
        await callback.answer('Это начало')


async def goForward(callback: CallbackQuery):
    page = int(callback.data.split('_')[1])
    specialties = await requestsSpecialty.get_all_specialties()
    if len(specialties) % 10 == 0:
        maxPage = len(specialties) // 10 - 1
    else:
        maxPage = len(specialties) // 10
    if page < maxPage:
        await callback.message.edit_text('Выберите специальность:',
                                         reply_markup=await kbInline.getKeyboardSpecialties(specialties, page + 1,
                                                                                            False))
    else:
        await callback.answer('Это конец')


async def specialty(callback: CallbackQuery):
    id = int(callback.data.split('_')[1])
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    try:
        await callback.message.edit_text('Выберите специалиста:',
                                         reply_markup=await kbInline.getKeyboardDoctors(doctors, 0, id))
    except:
        await callback.message.delete()
        await callback.message.answer('Выберите специалиста:',
                                      reply_markup=await kbInline.getKeyboardDoctors(doctors, 0, id))


async def goBackDoctor(callback: CallbackQuery):
    page = int(callback.data.split('_')[1])
    if page > 0:
        id = int(callback.data.split('_')[2])
        specialty = await requestsSpecialty.get_specialty_by_id(id)
        doctors = await requestsDoctor.get_doctors_by_specialty(specialty)
        await callback.message.edit_text('Выберите специалиста:',
                                         reply_markup=await kbInline.getKeyboardDoctors(doctors, page - 1, id))
    else:
        await callback.answer('Это начало')


async def goForwardDoctor(callback: CallbackQuery):
    page = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[2])
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty)
    if len(doctors) % 5 == 0:
        maxPage = len(doctors) // 5 - 1
    else:
        maxPage = len(doctors) // 5
    if page < maxPage:
        await callback.message.edit_text('Выберите специалиста:',
                                         reply_markup=await kbInline.getKeyboardDoctors(doctors, page + 1, id))
    else:
        await callback.answer('Это конец')


async def openDoctorInfo(callback: CallbackQuery):
    doctor_id = int(callback.data.split('_')[1])
    doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)
    id = int(callback.data.split('_')[2])
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    index = 0
    for i in range(len(doctors)):
        if doctor.user_id == doctors[i].user_id:
            index = i
            break
    if doctor:
        work_experience = doctor.work_experience
        if work_experience == 1:
            work_experience = str(work_experience) + ' год'
        elif 2 <= work_experience <= 4:
            work_experience = str(work_experience) + ' года'
        else:
            work_experience = str(work_experience) + ' лет'

        number_of_consultation = await requestsReview.get_number_of_reviews_by_doctor_id(doctor_id)
        if number_of_consultation == 1 or (number_of_consultation % 10 == 1 and not number_of_consultation != 11):
            number_of_consultation = str(number_of_consultation) + ' консультация'
        elif 2 <= number_of_consultation <= 4 or (
                2 <= number_of_consultation % 10 <= 4 and not 12 <= number_of_consultation <= 14):
            number_of_consultation = str(number_of_consultation) + ' консультации'
        else:
            number_of_consultation = str(number_of_consultation) + ' консультаций'

        emoji = ''
        prices = [doctor.price_just_ask, doctor.price_decoding, doctor.price_main_first, doctor.price_main_repeated,
                  doctor.price_second_opinion]
        if doctor.price_just_ask * doctor.price_decoding * doctor.price_main_first * doctor.price_main_repeated * doctor.price_second_opinion == 0:
            emoji = '🕊️ '
        price = max(prices)
        for i in prices:
            if i < price and i != 0:
                price = i
        price = int(price * 1.2)

        await callback.message.delete()
        await callback.message.answer(text=f'''{doctor.full_name}
Общий рейтинг: {doctor.rating_all} / {number_of_consultation}

Детальный рейтинг:
• Внимание к деталям, подробно и понятно объясняет - {doctor.rating_1}
• Вежливость - {doctor.rating_2}
• Удовлетворенность результатом консультации - {doctor.rating_3}
• Рекомендуют близким - {doctor.rating_4}


Стаж работы: {work_experience}

{emoji}
От {price} руб.
''', reply_markup=await kbInline.getKeyboardDoctorsInfo(1, index, doctors, id))


async def sendDoctorInfo(callback, index, doctor, doctors, id):
    work_experience = doctor.work_experience
    if work_experience == 1:
        work_experience = str(work_experience) + ' год'
    elif 2 <= work_experience <= 4:
        work_experience = str(work_experience) + ' года'
    else:
        work_experience = str(work_experience) + ' лет'

    number_of_consultation = await requestsReview.get_number_of_reviews_by_doctor_id(doctor.user_id)
    if number_of_consultation == 1 or (number_of_consultation % 10 == 1 and not number_of_consultation != 11):
        number_of_consultation = str(number_of_consultation) + ' консультация'
    elif 2 <= number_of_consultation <= 4 or (
            2 <= number_of_consultation % 10 <= 4 and not 12 <= number_of_consultation <= 14):
        number_of_consultation = str(number_of_consultation) + ' консультации'
    else:
        number_of_consultation = str(number_of_consultation) + ' консультаций'

    emoji = ''
    prices = [doctor.price_just_ask, doctor.price_decoding, doctor.price_main_first, doctor.price_main_repeated,
              doctor.price_second_opinion]
    if doctor.price_just_ask * doctor.price_decoding * doctor.price_main_first * doctor.price_main_repeated * doctor.price_second_opinion == 0:
        emoji = '🕊️ '
    price = max(prices)
    for i in prices:
        if i < price and i != 0:
            price = i
    price = int(price * 1.2)

    doctor_text = f'''{doctor.full_name}
Общий рейтинг: {doctor.rating_all} / {number_of_consultation}

Детальный рейтинг:
• Внимание к деталям, подробно и понятно объясняет - {doctor.rating_1}
• Вежливость - {doctor.rating_2}
• Удовлетворенность результатом консультации - {doctor.rating_3}
• Рекомендуют близким - {doctor.rating_4}


Стаж работы: {work_experience}

{emoji}
От {price} руб.'''

    if doctor.photo and doctor.photo.strip():
        lastMessageID = (await callback.message.edit_media(media=InputMediaPhoto(media=doctor.photo))).message_id
        await callback.message.edit_caption(inline_message_id=str(lastMessageID), caption=doctor_text,
                                            reply_markup=await kbInline.getKeyboardDoctorsInfo(1, index, doctors, id))
    else:
        await callback.message.delete()
        await callback.message.answer(text=doctor_text,
                                      reply_markup=await kbInline.getKeyboardDoctorsInfo(1, index, doctors, id))


async def goBackDoctorInfo(callback: CallbackQuery):
    index = int(callback.data.split('_')[1])
    if index > 0:
        id = int(callback.data.split('_')[2])
        specialty = await requestsSpecialty.get_specialty_by_id(id)
        doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
        doctor = doctors[index - 1]
        await sendDoctorInfo(callback, index - 1, doctor, doctors, id)
    else:
        await callback.answer('Это начало')


async def goForwardDoctorInfo(callback: CallbackQuery):
    index = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[2])
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    if index < len(doctors) - 1:
        doctor = doctors[index + 1]
        await sendDoctorInfo(callback, index + 1, doctor, doctors, id)
    else:
        await callback.answer('Это конец')


async def moreInfo(callback: CallbackQuery):
    index = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[2])
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    doctor = doctors[index]
    await callback.message.edit_caption(inline_message_id=str(callback.message.message_id),
                                        caption=f'{doctor.about_me}',
                                        reply_markup=await kbInline.returnToResume(index, id, -1),
                                        parse_mode='html')


async def resume(callback: CallbackQuery):
    try:
        data_parts = callback.data.split('_')
        index = int(data_parts[1])
        id = int(data_parts[2])

        if len(data_parts) > 3 and data_parts[3] != '-1':
            try:
                ids = data_parts[3].split(', ')
                await bot.delete_messages(
                    chat_id=callback.from_user.id,
                    message_ids=[int(msg_id) for msg_id in ids if msg_id.isdigit()]
                )
            except:
                pass

        specialty = await requestsSpecialty.get_specialty_by_id(id)
        doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
        doctor = doctors[index]

        await callback.message.answer(
            text=f'''<b>Резюме</b>

{doctor.resume or 'Не указано'}

<b>Образование</b>

{doctor.education_data or 'Не указано'}

{doctor.achievements or 'Не указано'}''',
            reply_markup=kbInline.getKeyboardResume(index, id, doctors),
            parse_mode='HTML'
        )

        try:
            await callback.message.delete()
        except:
            pass

    except Exception as e:
        print(f"Error in resume: {e}")
        await callback.answer("Ошибка загрузки резюме")


# async def resume(callback: CallbackQuery):
#     index = int(callback.data.split('_')[1])
#     id = int(callback.data.split('_')[2])
#     specialty = await requestsSpecialty.get_specialty_by_id(id)
#     doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
#     doctor = doctors[index]
#     try:
#         ids = callback.data.split('_')[3]
#         if ids != '-1':
#             ids = ids.split(', ')
#             await bot.delete_messages(chat_id=callback.from_user.id, message_ids=[int(i) for i in ids])
#         await callback.message.delete()
#         await callback.message.answer(text=f'''<b>Резюме</b>
#
# {doctor.resume}
#
# <b>Образование</b>
#
# {doctor.education_data}
#
# {doctor.achievements}''', reply_markup=await kbInline.getKeyboardResume(index, id, doctors), parse_mode='html')
#     except Exception as e:
#         await callback.message.edit_caption(inline_message_id=str(callback.message.message_id), caption=f'''<b>Резюме</b>
#
# {doctor.resume}
#
# <b>Образование</b>
#
# {doctor.education_data}
#
# {doctor.achievements}''', reply_markup=await kbInline.getKeyboardResume(index, id, doctors), parse_mode='html')


async def education(callback: CallbackQuery):
    index = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[2])
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    doctor = doctors[index]
    await callback.message.delete()
    mediaGroup = [InputMediaPhoto(media=photo) for photo in doctor.education.split(', ')]
    message = await callback.message.answer_media_group(media=mediaGroup)
    ids = ', '.join([str(message[i].message_id) for i in range(len(message))])
    await callback.message.answer('<b>Дипломы</b>', parse_mode='html',
                                  reply_markup=kbInline.returnToResume(index, id, ids))


async def socialNetworks(callback: CallbackQuery):
    index = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[2])
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    doctor = doctors[index]
    if doctor.is_social_networks:
        await callback.message.edit_caption(inline_message_id=str(callback.message.message_id), caption=f'''<b>Социальные сети</b>

Telegram: {doctor.social_networks_telegram}
Instagram: {doctor.social_networks_instagram}
''', parse_mode='html', reply_markup=kbInline.returnToResume(index, id, -1))


async def returnToDoctorInfo(callback: CallbackQuery):
    index = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[2])
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    doctor = doctors[index]
    try:
        ids = callback.data.split('_')[3]
        if ids != '-1':
            ids = ids.split(', ')
            await bot.delete_messages(chat_id=callback.from_user.id, message_ids=[int(i) for i in ids])
    except:
        pass
    work_experience = doctor.work_experience
    if work_experience == 1:
        work_experience = str(work_experience) + ' год'
    elif 2 <= work_experience <= 4:
        work_experience = str(work_experience) + ' года'
    else:
        work_experience = str(work_experience) + ' лет'

    number_of_consultation = await requestsReview.get_number_of_reviews_by_doctor_id(doctor.user_id)
    if number_of_consultation == 1 or (number_of_consultation % 10 == 1 and not number_of_consultation != 11):
        number_of_consultation = str(number_of_consultation) + ' консультация'
    elif 2 <= number_of_consultation <= 4 or (
            2 <= number_of_consultation % 10 <= 4 and not 12 <= number_of_consultation <= 14):
        number_of_consultation = str(number_of_consultation) + ' консультации'
    else:
        number_of_consultation = str(number_of_consultation) + ' консультаций'

    emoji = ''
    prices = [doctor.price_just_ask, doctor.price_decoding, doctor.price_main_first, doctor.price_main_repeated,
              doctor.price_second_opinion]
    if doctor.price_just_ask * doctor.price_decoding * doctor.price_main_first * doctor.price_main_repeated * doctor.price_second_opinion == 0:
        emoji = '🕊️ '
    price = max(prices)
    for i in prices:
        if i < price and i != 0:
            price = i
    price = int(price * 1.2)

    await callback.message.delete()
    await callback.message.answer(text=f'''{doctor.full_name}
Общий рейтинг: {doctor.rating_all} / {number_of_consultation}

Детальный рейтинг:
• Внимание к деталям, подробно и понятно объясняет - {doctor.rating_1}
• Вежливость - {doctor.rating_2}
• Удовлетворенность результатом консультации - {doctor.rating_3}
• Рекомендуют близким - {doctor.rating_4}


Стаж работы: {work_experience}

{emoji}
От {price} руб.
''', reply_markup=await kbInline.getKeyboardDoctorsInfo(1, index, doctors, id))


async def reviews(callback, page):
    _, doctor_id, index, specialty, _ = callback.data.split('_')
    doctor_id, index, specialty = map(int, (doctor_id, index, specialty))

    doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)

    reviews = await requestsReview.get_reviews_by_doctor_id_with_text(doctor_id)

    if len(reviews) % 5 == 0:
        all_pages = len(reviews) // 5
    else:
        all_pages = len(reviews) // 5 + 1

    index = (page - 1) * 5
    if index + 4 <= len(reviews):
        reviews = reviews[index:index + 5]
    else:
        reviews = reviews[index:]

    text = ''
    for review in reviews:
        user = await requestsUser.get_user(review.patient_id)
        gender = 'Мужчина' if user.gender == 'male' else 'Женщина'
        text += gender + ', ' + str(user.age) + ', ' + user.city + '\n<i>' + review.review + '</i>\n\n'

    await callback.message.edit_caption(inline_message_id=str(callback.message.message_id),
                                        caption=f'''{doctor.rating_all} ⭐ (средний рейтинг)

<b>Отзывы</b>

{text}
''', reply_markup=await kbInline.getKeyboardReviews(doctor_id, index, specialty, page, all_pages),
                                        parse_mode='html')


async def openReviews(callback: CallbackQuery):
    doctor_id = int(callback.data.split('_')[1])
    if await requestsReview.is_reviews_with_text_by_doctor_id(doctor_id):
        await reviews(callback, 1)
    else:
        await callback.answer('Отзывы отсутствуют')


async def goBackReview(callback: CallbackQuery):
    page = int(callback.data.split('_')[4])
    if page > 1:
        await reviews(callback, page - 1)
    else:
        await callback.answer('Это начало')


async def goForwardReview(callback: CallbackQuery):
    doctor_id = int(callback.data.split('_')[1])
    page = int(callback.data.split('_')[4])
    number = len(await requestsReview.get_reviews_by_doctor_id_with_text(doctor_id)) // 5
    if number % 5 != 0:
        number += 1

    if page < number - 1:
        await reviews(callback, page + 1)
    else:
        await callback.answer('Это конец')


async def acceptDoctor(callback):
    doctor_id = int(callback.data.split('_')[1])
    if callback.from_user.id != doctor_id:
        index = int(callback.data.split('_')[2])
        id = int(callback.data.split('_')[3])
        doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)
        consultation_price = 'от ' + str(int(min(doctor.price_main_first, doctor.price_main_repeated) * 1.2)) + ' руб.'
        if consultation_price == 0:
            consultation_price = '🕊️'
        text = f'''Прочитайте <b>«Правила консультаций»</b>, после чего выберите подходящий вид консультации.

«Просто спросить» - {'🕊️' if doctor.price_just_ask == 0 else str(int(doctor.price_just_ask * 1.2)) + ' руб.'}

«Консультация» - {consultation_price}

«Второе мнение» - {'🕊️' if doctor.price_second_opinion == 0 else str(int(doctor.price_second_opinion * 1.2)) + ' руб.'}

«Расшифровка анализов» - {'🕊️' if doctor.price_decoding == 0 else str(int(doctor.price_decoding * 1.2)) + ' руб.'}
'''
        try:
            await callback.message.edit_caption(inline_message_id=str(callback.message.message_id),
                                                caption=text,
                                                reply_markup=await kbInline.getKeyboardConsultation(doctor_id, index,
                                                                                                    id, False),
                                                parse_mode='html')
        except:
            await callback.message.delete()
            await callback.message.answer(text=text,
                                          reply_markup=await kbInline.getKeyboardConsultation(doctor_id, index,
                                                                                              id, False),
                                          parse_mode='html')
    else:
        await callback.answer('Вы не можете выбрать себя.')


async def chooseConsultation(callback, state):
    user_id = callback.from_user.id
    doctor_id = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    id = int(callback.data.split('_')[3])

    await state.update_data(doctor_id=doctor_id, index=index, specialty=id)

    await state.set_state(EditUser.setFullName)
    await callback.message.delete()
    await callback.message.answer("👤 Введите ваше имя и фамилию:")


# async def chooseConsultation(callback, state):
#     user_id = callback.from_user.id
#     doctor_id = int(callback.data.split('_')[1])
#     index = int(callback.data.split('_')[2])
#     id = int(callback.data.split('_')[3])
#     await state.set_state(EditUser.setAge)
#     await state.update_data(doctor_id=doctor_id, index=index, specialty=id)
#     await callback.message.delete()
#     await callback.message.answer('Для начала работы необходимо пройти регистрацию. Выберите ваш пол.',
#                                   reply_markup=kbInline.regChooseGender)


async def infoAboutConsultation(callback: CallbackQuery):
    doctor_id = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    id = int(callback.data.split('_')[3])
    if callback.message.caption.startswith('Прочитайте'):
        await callback.message.edit_caption(inline_message_id=str(callback.message.message_id), caption='''<b>Внимательно ознакомьтесь с видами консультаций и выберете подходящий:</b>
    
<b>«Просто спросить»</b> - Консультация завершается после ответа специалиста на ваш вопрос.  

<b>«Консультация»</b> - Это полноценная беседа с врачом. Диалог открыт 24 часа c момента ответа доктора. Специалист разберётся во всех деталях вашего состояния, задаст уточняющие вопросы, а вы сможете описать скрытые нюансы. Когда дело касается здоровья, каждая деталь может стать важной.

<b>«Расшифровка анализов»</b> - Расшифровка анализов)) 

<b>«Экстренный случай»</b> - Если время получения ответа - самое важное в вашем случае, вам поможет первый освободившийся специалист в нашем чате.

<b>«Второе мнение»</b> - Вид консультаций, где вы можете предоставить рентгенологам, хирургам и другим специалистам записи КТ, МРТ, рентгенография и т.д. Специалисты смогут дать своё экспертное мнение на основе увиденных снимков.

<b>«Очный прием»</b> - Если необходим осмотр, получение врачебного заключения и назначение лечения, то перейдите в этот раздел.
''', reply_markup=await kbInline.getKeyboardConsultation(doctor_id, index, id, True), parse_mode='html')
    else:
        await acceptDoctor(callback)


async def getDataForAttachFile(message: Message, state: FSMContext, chat_type: str):
    data = await state.get_data()
    if message.photo:
        await attachFileFirstMessage(message.html_text, 'photo', message.photo[-1].file_id, message, state, chat_type,
                                     data['id'])
    elif message.document:
        await attachFileFirstMessage(message.html_text, 'document', message.document.file_id, message, state, chat_type,
                                     data['id'])
    else:
        await attachFileFirstMessage(message.html_text, 'text', '', message, state, chat_type, data['id'])


async def attachFileFirstMessage(text, media_type, media_id, message, state, chat_type, specialty):
    patient_id = message.from_user.id
    data = await state.get_data()
    patient = await requestsUser.get_user(message.from_user.id)
    match media_type:
        case 'photo' | 'document':
            groupToSend.append({'message': media_id, 'patient_id': patient_id})
            await asyncio.sleep(1)
            async with lock:
                group = []
                for file in groupToSend:
                    if file['patient_id'] == patient_id:
                        group.append(file)
                if group:
                    if len(group) == 1:
                        await requestsMessageToSend.add_message_to_send(patient_id, data['doctor_id'], text, media_type,
                                                                        media_id, True)
                        await state.update_data(text=text, media_type=media_type,
                                                media_id=media_id)
                        id = await requestsMessageToSend.get_id_last_message_to_send(patient_id, data['doctor_id'])

                        if media_type == 'photo':
                            await message.answer(text='<i>' + data['name'] + '</i>\n\n' + text,
                                                 reply_markup=await kbInline.getKeyboardFirstMessageSend(
                                                     data['doctor_id'], chat_type, specialty, id),
                                                 parse_mode='html')
                        else:
                            await message.answer_document(document=media_id,
                                                          caption='<i>' + data['name'] + '</i>\n\n' + text,
                                                          reply_markup=await kbInline.getKeyboardFirstMessageSend(
                                                              data['doctor_id'], chat_type, specialty, id),
                                                          parse_mode='html')

                    else:
                        mediaType = 'mediaGroupPhoto' if media_type == 'photo' else 'mediaGroupDocument'
                        await requestsMessageToSend.add_message_to_send(patient_id, data['doctor_id'], text,
                                                                        mediaType,
                                                                        ', '.join([file['message'] for file in group]),
                                                                        True)
                        await state.update_data(text=text, media_type=mediaType,
                                                media_id=', '.join([file['message'] for file in group]))
                        id = await requestsMessageToSend.get_id_last_message_to_send(patient_id, data['doctor_id'])
                        if media_type == 'photo':
                            mediaGroup = [InputMediaPhoto(media=photo['message'], parse_mode='html')
                                          for photo in group]
                        else:
                            mediaGroup = [InputMediaDocument(media=document['message'], parse_mode='html')
                                          for document in group]
                        if text != '':
                            mediaGroup[0].caption = '<i>' + data['name'] + '</i>\n\n' + text
                        await message.answer_media_group(media=mediaGroup)
                        await message.answer('Вы уверены, что хотите отправить информацию врачу?',
                                             reply_markup=await kbInline.getKeyboardFirstMessageSend(data['doctor_id'],
                                                                                                     chat_type,
                                                                                                     specialty, id))
                    for photo in group:
                        groupToSend.remove(photo)

        case 'text':
            await requestsMessageToSend.add_message_to_send(patient_id, data['doctor_id'], text, 'text', '', True)
            await state.update_data(text=text, media_type='text', media_id='')
            id = await requestsMessageToSend.get_id_last_message_to_send(patient_id, data['doctor_id'])
            await message.answer('<i>' + data['name'] + '</i>\n\n' + text,
                                 reply_markup=await kbInline.getKeyboardFirstMessageSend(data['doctor_id'], chat_type,
                                                                                         specialty, id),
                                 parse_mode='html')


async def getPrice(doctor_id, chat_type):
    price = 0
    match chat_type:
        case 'justAsk':
            price = await requestsDoctor.get_price_just_ask_by_user_id(doctor_id)
        case 'decoding':
            price = await requestsDoctor.get_price_decoding_by_user_id(doctor_id)
        case 'mainFirst':
            price = await requestsDoctor.get_price_main_first_by_user_id(doctor_id)
        case 'mainRepeated':
            price = await requestsDoctor.get_price_main_repeated_by_user_id(doctor_id)
        case 'secondOpinion':
            price = await requestsDoctor.get_price_second_opinion_by_user_id(doctor_id)
    return price


async def historyToMessageToSend(id_consultation):
    messages = await requestsHistoryMessage.get_all_messages_by_consultation_id(id_consultation)
    for message in messages:
        await requestsMessageToSend.add_message_to_send(message.patient_id, message.doctor_id, message.text,
                                                        message.media_type, message.media_id, False)


async def sendFirstMessage(callback: CallbackQuery, chat_type: str, state: FSMContext):
    patient_id = callback.from_user.id
    doctor_id = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[2])
    id_specialty = int(callback.data.split('_')[3])
    await callback.message.delete()
    price = await getPrice(doctor_id, chat_type)

    if price == 0:
        specialty = (await requestsSpecialty.get_specialty_by_id(id_specialty)).name
        data = await state.get_data()
        try:
            if chat_type == 'mainFirst':
                await requestsHistoryConsultation.add_consultation(data['name'], patient_id, doctor_id, 'mainRepeated',
                                                                   specialty)
            else:
                await requestsHistoryConsultation.add_consultation(data['name'], patient_id, doctor_id, chat_type,
                                                                   specialty)
        except KeyError:
            if chat_type == 'mainFirst':
                await requestsHistoryConsultation.add_consultation('', patient_id, doctor_id, 'mainRepeated', specialty)
            elif chat_type == 'mainRepeated':
                await requestsHistoryConsultation.add_consultation('Повторная', patient_id, doctor_id, 'mainRepeated',
                                                                   specialty)
            else:
                await requestsHistoryConsultation.add_consultation('', patient_id, doctor_id, chat_type, specialty)
        id_consultation = await requestsHistoryConsultation.get_last_id_consultation(patient_id)

        await requestsBundle.add_bundle(patient_id, doctor_id, chat_type, id_consultation)

        patient = await requestsUser.get_user_by_id(user_id=patient_id)
        gender_label = 'мужчина' if patient.gender == 'male' else 'женщина'
        patient_text = data.get('text', '')

        notification_text = f'''<code>Бот</code>

Новая консультация от: <b>{gender_label}</b>, <b>{patient.age}</b> лет, <b>{patient.city}</b>
Вопрос: {patient_text}'''

        await bot.send_message(chat_id=doctor_id, text=notification_text, parse_mode='html',
                               reply_markup=kbInline.doctor_notify_keyboard(patient_id, id_consultation))

        keyboard = await kbReply.kbPatientMain(patient_id) if chat_type in ['justAsk',
                                                                            'secondOpinion'] else kbReply.kbPatientDialog
        await callback.message.answer('''Информация отправлена врачу. 

Он обязательно Вам ответит, как освободится.

Благодарим за обращение!''', reply_markup=keyboard)

        if chat_type in ['decoding', 'mainFirst', 'mainRepeated']:
            await state.set_state(ChatPatient.openDialog)
            await state.update_data(doctor_id=doctor_id, chat_type=chat_type)
            await requestsBundle.edit_is_open_dialog_patient(patient_id, doctor_id, True)

        await requestsHistoryMessage.add_message(id_consultation, patient_id, doctor_id, 'patient', data['text'],
                                                 data['media_type'], data['media_id'])

        await asyncio.create_task(timerToAnswer(id, doctor_id, 0, callback, id_specialty, chat_type, patient_id))
    else:
        await state.set_state(Payment.receipt)
        await state.update_data(doctor_id=doctor_id, chat_type=chat_type, id=id, specialty=id_specialty)
        await callback.message.answer(f'''Стоимость: <b>{int(price * 1.2)} руб.</b>


<b>Для оплаты картой банка РФ (МИР):</b>
Т-банк, Николай Х.
<code>2200701963024879</code>
<code>+79104488401</code>

<b>Для оплаты иностранной картой (Visa\Mastercard)</b>
ОАО «O!Банк», Николай Х.
<code>1250320077671451</code>
<code>+996500111668</code>


После успешной оплаты пришлите чек <b>файлом.</b>''', parse_mode='html')


async def isSendFirstMessage(callback: CallbackQuery):
    consultation = callback.data.split('_')[1]
    doctor_id = callback.data.split('_')[2]
    id = callback.data.split('_')[3]
    specialty = callback.data.split('_')[4]
    if consultation == 'justAsk':
        if callback.message.photo or callback.message.document:
            await callback.message.edit_caption(inline_message_id=str(callback.message.message_id),
                                                caption='Отправить вопрос врачу?',
                                                reply_markup=await kbInline.getKeyboardFirstMessageSendTrueOrFalse(
                                                    doctor_id, consultation, id, specialty))
        else:
            await callback.message.edit_text('Отправить вопрос врачу?',
                                             reply_markup=await kbInline.getKeyboardFirstMessageSendTrueOrFalse(
                                                 doctor_id, consultation, id, specialty))
    else:
        if callback.message.photo or callback.message.document:
            await callback.message.edit_caption(inline_message_id=str(callback.message.message_id),
                                                caption='Вы уверены?',
                                                reply_markup=await kbInline.getKeyboardFirstMessageSendTrueOrFalse(
                                                    doctor_id, consultation, id, specialty))
        else:
            await callback.message.edit_text('Вы уверены?',
                                             reply_markup=await kbInline.getKeyboardFirstMessageSendTrueOrFalse(
                                                 doctor_id, consultation, id, specialty))


async def consultationTruePayment(message: Message, state: FSMContext):
    patient_id = message.from_user.id
    data = await state.get_data()
    doctor_id = data['doctor_id']
    chat_type = data['chat_type']
    id = data['id']
    specialty = data['specialty']
    # consultation = data['consultation']

    doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)

    price = await getPrice(doctor_id, chat_type)
    if message.document:
        await bot.send_document(chat_id=config.ADMIN_GROUP_ID.get_secret_value(), document=message.document.file_id,

                                caption=f'''Пациент <code>{patient_id}</code> произвел оплату на сумму: {int(price * 1.2)} руб.
        Тип консультации: {type_consultation[chat_type]}
        Врач: {doctor.full_name}
        Реквизиты врача:
        МИР: {doctor.bank_details_russia}
        VISA / MASTERCARD: {doctor.bank_details_abroad}
        ''',
                                reply_markup=await kbInline.getKeyboardAcceptPayment(patient_id, doctor_id, chat_type,
                                                                                     id, specialty),
                                parse_mode='html')

        await message.answer(
            'Заявка отправлена администратору. После подтверждения оплаты информация будет отправлена специалисту.')
    else:
        await message.answer('Пожалуйста, отправьте чек в виде <b>файла</b>', parse_mode='html')


async def consultationAcceptPayment(callback: CallbackQuery):
    chat_type = callback.data.split('_')[1]
    patient_id = int(callback.data.split('_')[2])
    doctor_id = int(callback.data.split('_')[3])
    id = int(callback.data.split('_')[4])
    id_specialty = int(callback.data.split('_')[5])

    state_user: FSMContext = FSMContext(
        storage=dp.storage,
        key=StorageKey(
            chat_id=patient_id,
            user_id=patient_id,
            bot_id=bot.id
        )
    )

    keyboard = await kbReply.kbPatientMain(patient_id) if chat_type in ['justAsk',
                                                                        'secondOpinion'] else kbReply.kbPatientDialog
    await bot.send_message(chat_id=patient_id,
                           text='Оплата принята, информация отправлена врачу, он обязательно Вам ответит, как освободится. Благодарим за обращение!',
                           reply_markup=keyboard)
    await callback.message.answer(
        text=(callback.message.caption or "") + "\n\n<b>Подтверждено</b>",
        parse_mode="HTML")

    specialty = (await requestsSpecialty.get_specialty_by_id(id_specialty)).name

    data = await state_user.get_data()
    try:
        if chat_type == 'mainFirst':
            await requestsHistoryConsultation.add_consultation(data['name'], patient_id, doctor_id, 'mainRepeated',
                                                               specialty)
        else:
            await requestsHistoryConsultation.add_consultation(data['name'], patient_id, doctor_id, chat_type,
                                                               specialty)
    except KeyError:
        if chat_type == 'mainFirst':
            await requestsHistoryConsultation.add_consultation('', patient_id, doctor_id, 'mainRepeated', specialty)
        else:
            await requestsHistoryConsultation.add_consultation('', patient_id, doctor_id, chat_type, specialty)
    id_consultation = await requestsHistoryConsultation.get_last_id_consultation(patient_id)

    await requestsHistoryMessage.add_message(id_consultation, patient_id, doctor_id, 'patient', data['text'],
                                             data['media_type'], data['media_id'])

    await requestsBundle.add_bundle(patient_id, doctor_id, chat_type, id_consultation)
    await requestsBundle.edit_is_open_dialog_patient(patient_id, doctor_id, True)
    await callback.message.delete()

    # Get patient info for notification
    patient = await requestsUser.get_user_by_id(user_id=patient_id)
    gender_label = 'мужчина' if patient.gender == 'male' else 'женщина'
    patient_text = data.get('text', '')

    notification_text = f'''<code>Бот</code>

Новая консультация от: <b>{gender_label}</b>, <b>{patient.age}</b> лет, <b>{patient.city}</b>
Вопрос: {patient_text}'''

    await bot.send_message(chat_id=doctor_id, text=notification_text, parse_mode='html',
                           reply_markup=kbInline.doctor_notify_keyboard(patient_id, id_consultation))

    if chat_type in ['decoding', 'mainFirst', 'mainRepeated']:
        await state_user.set_state(ChatPatient.openDialog)
        await state_user.update_data(doctor_id=doctor_id, chat_type=chat_type)

    await asyncio.create_task(timerToAnswer(id, doctor_id, 0, callback, id_specialty, chat_type, patient_id))


async def consultationRejectPayment(callback: CallbackQuery):
    user_id = int(callback.data.split('_')[1])
    await bot.send_message(chat_id=user_id, text='Оплата не подтверждена.',
                           reply_markup=await kbReply.kbPatientMain(user_id))
    await callback.message.edit_text('Уведомление об отказе отправлено пользователю')


async def timerToAnswer(id, doctor_id, iteration, callback, specialty, chat_type, patient_id):
    await asyncio.sleep(28800)
    if await requestsMessageToSend.is_message_to_send_by_id(id):
        if iteration < 8:
            await bot.send_message(chat_id=doctor_id, text='''<code>Бот</code>

У вас есть непрочитанные сообщения!
''', parse_mode='html')
            await timerToAnswer(id, doctor_id, iteration + 1, callback, specialty, chat_type, patient_id)
        else:
            await requestsMessageToSend.delete_messages_to_send(patient_id, doctor_id)
            await requestsMessageToSend.delete_messages_to_send(doctor_id, patient_id)
            await requestsMessageToSend.delete_first_message(patient_id, doctor_id)
            await requestsBundle.delete_bundle(patient_id, doctor_id)

            await bot.send_message(chat_id=patient_id, text='''Сервис Doc For Everyone приносит вам свои искренние извинения за то, что консультация не была оказана. Мы понимаем, как это важно для вас, и сожалеем о доставленных неудобствах.

Для урегулирования данного вопроса и поиска решения, пожалуйста, обратитесь напрямую в нашу администрацию. Они смогут проверить детали вашего обращения, прояснить ситуацию и предложить варианты компенсации или переноса консультации.
''', reply_markup=await kbInline.getKeyboardFailedConsultation(doctor_id, specialty, chat_type))


async def failedConsultation(callback: CallbackQuery, state: FSMContext):
    _, doctor_id, id_specialty, chat_type = callback.data.split('_')
    doctor_id, id_specialty = map(int, (doctor_id, id_specialty))
    specialty = await requestsSpecialty.get_specialty_by_id(id_specialty)
    await state.set_state(FailedConsultation.text)
    await state.update_data(doctor_id=doctor_id, specialty=specialty.name, chat_type=chat_type)
    await callback.message.delete()
    await callback.message.answer('Укажите ваш никнейм в телеграм, администратор свяжется с вами в ближайшее время.')


async def failedConsultatationMessage(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await bot.send_message(chat_id=config.ADMIN_GROUP_ID.get_secret_value(), text=f'''<b>Невыполненная консультация</b>

<code>{message.html_text}</code>

Вид: {type_consultation[data['chat_type']]}
Стоимость: {int(await getPrice(data['doctor_id'], data['chat_type']) * 1.2)} руб.

ФИО: {await requestsDoctor.get_full_name_by_user_id(data['doctor_id'])}
Специальность: {data['specialty']}
''', parse_mode='html')
    await message.answer('Обращение отправлено', reply_markup=await kbReply.kbPatientMain(message.from_user.id))


# async def consultationLongSendMessage(callback: CallbackQuery, state: FSMContext):
#     patient_id = callback.from_user.id
#     doctor_id = int(callback.data.split('_')[1])
#     chat_type = callback.data.split('_')[2]
#     id = int(callback.data.split('_')[3])
#     id_specialty = int(callback.data.split('_')[4])


async def consultationOffer(callback, state, chat_type, function):
    doctor_id = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    id = int(callback.data.split('_')[3])
    if await function(doctor_id) > 0:
        await callback.message.delete()
        await callback.message.answer('''Я ознакомлен и принимаю условия договора оказания услуг.

<b><a href="https://docs.google.com/document/d/10xzfOSIhNGLcnTpEtv_b9QCyP5EFMPyv7JBowQWXjcU/edit?tab=t.0">Договор оказания услуг</a></b>''',
                                      reply_markup=await kbInline.getKeyboardOffer(doctor_id, index, id, chat_type),
                                      parse_mode='html')
    else:
        match chat_type:
            case 'JustAsk':
                await consultationJustAsk(callback, state)
            case 'Decoding':
                await consultationDecoding(callback, state)
            case 'MainFirst':
                await firstConsultationName(callback, state)
            case 'MainRepeated':
                await repeatedConsultation(callback)
            case 'SecondOpinion':
                await consultationSecondOpinion(callback, state)


async def message_before_consultations(message):
    messageBeforeConsultation = await requestsLastMessage.get_last_message_by_function('before_consultations')
    if message and messageBeforeConsultation is not None:
        await message.answer(messageBeforeConsultation.text, parse_mode='html')
        await asyncio.sleep(6)


async def consultationJustAsk(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[3])
    if not await requestsUser.is_user(callback.from_user.id):
        await chooseConsultation(callback, state)
    else:
        await state.set_state(AttachFile.justAsk_name)
        await state.update_data(doctor_id=doctor_id, id=id)
        await callback.message.delete()
        await callback.message.answer(
            'Для удобного поиска этой консультации в разделе “История консультаций“, придумайте название (2-3 слова)')


async def consultationJustAskOffer(callback: CallbackQuery, state: FSMContext):
    await consultationOffer(callback, state, 'JustAsk', requestsDoctor.get_price_just_ask_by_user_id)


async def just_ask(function, state, user_id, text):
    data = await state.get_data()
    doctor_id = data['doctor_id']
    id = data['id']
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    await requestsStatistics.add_data(user_id, doctor_id, 'justAsk', specialty.name)
    await state.set_state(AttachFile.photoJustAsk)
    await state.update_data(doctor_id=doctor_id, name=text)
    await function(
        'Задайте исчерпывающий вопрос врачу и прикрепите изображение/файл в хорошем качестве, если это необходимо')


async def consultationJustAskName(message: Message, state: FSMContext):
    await message_before_consultations(message)
    await just_ask(message.answer, state, message.from_user.id, message.html_text)


async def writeAgainJustAsk(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split('_')[2])
    await requestsMessageToSend.delete_message_to_send_by_id(id)
    await callback.message.delete()
    await just_ask(callback.message.answer, state, callback.from_user.id, callback.message.html_text.split()[0])


async def consultationDecoding(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[3])
    if not await requestsUser.is_user(callback.from_user.id):
        await chooseConsultation(callback, state)
    else:
        await state.set_state(AttachFile.decoding_name)
        await state.update_data(doctor_id=doctor_id, id=id)
        await callback.message.delete()
        await callback.message.answer(
            'Для удобного поиска этой консультации в разделе “История консультаций“, придумайте название (2-3 слова)')


async def consultationDecodingOffer(callback: CallbackQuery, state: FSMContext):
    await consultationOffer(callback, state, 'Decoding', requestsDoctor.get_price_decoding_by_user_id)


async def decoding(function, state, user_id, text):
    data = await state.get_data()
    doctor_id = data['doctor_id']
    id = data['id']
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    await requestsStatistics.add_data(user_id, doctor_id, 'decoding', specialty.name)
    await state.set_state(AttachFile.photoDecoding)
    await state.update_data(doctor_id=doctor_id, name=text)
    await function(
        'Опишите с какой целью сдавали анализы, получаете ли какое-либо лечение и прикрепите файлы или фотографии')


async def consultationDecodingName(message: Message, state: FSMContext):
    await message_before_consultations(message)
    await decoding(message.answer, state, message.from_user.id, message.html_text)


async def writeAgainDecoding(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split('_')[2])
    await requestsMessageToSend.delete_message_to_send_by_id(id)
    await callback.message.delete()
    await decoding(callback.message.answer, state, callback.from_user.id, callback.message.html_text.split()[0])


async def consultationMain(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    id = int(callback.data.split('_')[3])
    if not await requestsUser.is_user(callback.from_user.id):
        await chooseConsultation(callback, state)
    else:
        await state.update_data(id=id)
        specialty = await requestsSpecialty.get_specialty_by_id(id)
        await requestsStatistics.add_data(callback.from_user.id, doctor_id, 'main', specialty.name)
        await callback.message.delete()
        await callback.message.answer(f'''«Первичная консультация» - {int(await getPrice(doctor_id, 'mainFirst') * 1.2)} руб.
Если вы впервые обращаетесь к врачу с этой проблемой.

«Повторная консультация» - {int(await getPrice(doctor_id, 'mainRepeated') * 1.2)} руб.
Если нужно продолжить предыдущую консультацию.  Доктор увидит выбранный вами диалог, всю историю, рекомендации, а вы сможете дополнить её новыми деталями и изменениями в вашем самочувствии.
''', reply_markup=await kbInline.getKeyboardFirstOrSecondConsultation(doctor_id, index, id))


async def consultationMainFirstOffer(callback: CallbackQuery, state: FSMContext):
    await consultationOffer(callback, state, 'MainFirst', requestsDoctor.get_price_main_first_by_user_id)


async def consultationMainRepeatedOffer(callback: CallbackQuery, state: FSMContext):
    await consultationOffer(callback, state, 'MainRepeated', requestsDoctor.get_price_main_repeated_by_user_id)


async def firstConsultationName(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split('_')[1])
    await state.set_state(AttachFile.main_first_name)
    await state.update_data(doctor_id=doctor_id)
    await callback.message.edit_text(
        'Для удобного поиска этой консультации в разделе “История консультаций“, придумайте название (2-3 слова)')


async def firstConsultation(message: Message, state: FSMContext):
    await state.set_state(AttachFile.main_first)
    await state.update_data(name=message.html_text)
    await message_before_consultations(message)
    await message.answer('''Подробно укажите информацию в <b>одном сообщении</b>

1. Опишите жалобы (что беспокоит на данный момент?) Когда все началось (сколько дней/месяцев назад), и как развивалось ваше заболевание?

2. Обращались ли вы уже за медицинской помощью с этим вопросом? Если да, то опишите результат консультации. Укажите чем лечились и насколько было лечение эффективно?

3. Имеете ли хронические заболевания? Если да, то опишите их. Принимаете ли Вы какие-либо лекарства на данный момент? Есть ли у вас аллергия на что-либо? Если «да», опишите в чем она проявляется.

4. Проходили ли Вы обследование: анализы, инструментальное обследование? Если да, то прикрепите их.
''', parse_mode='html')


async def writeAgainFirstConsultation(callback: CallbackQuery):
    id = int(callback.data.split('_')[2])
    await requestsMessageToSend.delete_message_to_send_by_id(id)
    await callback.message.delete()
    await callback.message.answer('''Подробно укажите информацию в <b>одном сообщении</b>

1. Опишите жалобы (что беспокоит на данный момент?) Когда все началось (сколько дней/месяцев назад), и как развивалось ваше заболевание?

2. Обращались ли вы уже за медицинской помощью с этим вопросом? Если да, то опишите результат консультации. Укажите чем лечились и насколько было лечение эффективно?

3. Имеете ли хронические заболевания? Если да, то опишите их. Принимаете ли Вы какие-либо лекарства на данный момент? Есть ли у вас аллергия на что-либо? Если «да», опишите в чем она проявляется.

4. Проходили ли Вы обследование: анализы, инструментальное обследование? Если да, то прикрепите их.
''', parse_mode='html')


async def startRepeatedConsultation(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[3])
    id_consultation = int(callback.data.split('_')[4])
    consultation = await requestsHistoryConsultation.get_consultation(id_consultation)
    await state.set_state(AttachFile.main_repeated)
    await state.update_data(doctor_id=doctor_id, id=id, name=consultation.name)
    await callback.message.delete()
    await message_before_consultations(callback.message)
    await callback.message.answer(
        '''Подробно опишите какие изменения произошли в вашем самочувствии, и придерживались ли Вы в точности рекомендаций специалиста. При необходимости, прикрепите новые файлы или изображения обследований.''')


async def repeatedConsultation(callback: CallbackQuery):
    patient_id = callback.from_user.id
    doctor_id = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    id = int(callback.data.split('_')[3])
    consultations = await requestsHistoryConsultation.get_all_consultations_by_patient_doctor_id_and_type(patient_id,
                                                                                                          doctor_id,
                                                                                                          'mainFirst')
    consultations.extend(
        await requestsHistoryConsultation.get_all_consultations_by_patient_doctor_id_and_type(patient_id, doctor_id,
                                                                                              'mainRepeated'))
    if consultations:
        await callback.message.edit_text('Выберите консультацию',
                                         reply_markup=await kbInline.getKeyboardRepeatedConsultations(consultations, 1,
                                                                                                      doctor_id, index,
                                                                                                      id))
    else:
        await callback.answer('У Вас не было консультаций с этим врачом')


async def writeAgainRepeatedConsultation(callback: CallbackQuery):
    id = int(callback.data.split('_')[2])
    await requestsMessageToSend.delete_message_to_send_by_id(id)
    await repeatedConsultation(callback)


async def consultationSecondOpinion(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split('_')[1])
    id = int(callback.data.split('_')[3])
    if not await requestsUser.is_user(callback.from_user.id):
        await chooseConsultation(callback, state)
    else:
        await state.set_state(AttachFile.secondOpinion_name)
        await state.update_data(doctor_id=doctor_id, id=id)
        await callback.message.delete()
        await callback.message.answer(
            'Для удобного поиска этой консультации в разделе “История консультаций“, придумайте название (2-3 слова)')


async def consultationSecondOpinionOffer(callback: CallbackQuery, state: FSMContext):
    await consultationOffer(callback, state, 'SecondOpinion', requestsDoctor.get_price_second_opinion_by_user_id)


async def second_opinion(function, state, user_id, text):
    data = await state.get_data()
    doctor_id = data['doctor_id']
    id = data['id']
    specialty = await requestsSpecialty.get_specialty_by_id(id)
    await requestsStatistics.add_data(user_id, doctor_id, 'secondOpinion', specialty.name)
    await state.set_state(AttachFile.secondOpinion)
    await state.update_data(doctor_id=doctor_id, name=text)
    await function(
        'Укажите Ваш возраст, симптомы заболевания, диагноз, если известен, и причину выполнения исследования. Прикрепите врачебное заключение, если есть.')


async def consultationSecondOpinionName(message: Message, state: FSMContext):
    await message_before_consultations(message)
    await second_opinion(message.answer, state, message.from_user.id, message.html_text)


async def consultationSecondOpinionLink1(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(text=message.html_text, media_type='photo', media_id=message.photo[-1].file_id)
    elif message.document:
        await state.update_data(text=message.html_text, media_type='document', media_id=message.document.file_id)
    else:
        await state.update_data(text=message.html_text, media_type='text', media_id='')

    await state.set_state(AttachFile.secondOpinion_link)
    await message.answer('''Внимательно прочитайте инструкцию и прикрепите ссылку на исследование

Если необходима оценка нескольких исследований, тогда прикрепите сразу несколько ссылок.

<b>Инструкция</b>
Для прикрепления ссылки:
авторизуйтесь или зарегистрируйтесь на сайте Яндекс.Диск или Гугл диск

1. В левом верхнем углу нажмите «Загрузить».
2. Выберите файлы на вашем компьютере.
3. После окончания загрузки файла можно включить доступ по ссылке. Чтобы поделиться ссылкой, кликните на нужный файл.
4. В самом верхнем углу экрана нажмите «Поделиться».
5. Нажмите «Скопировать ссылку».

Теперь файл на диске, и вы можете поделиться ссылкой на него с любым пользователем (убедитесь, что доступ открыт всем, у кого есть ссылка).

''', parse_mode='html')


async def consultationSecondOpinionLink2(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(text=data['text'] + '\n\n' + message.html_text)
    data = await state.get_data()
    await attachFileFirstMessage(data['text'], data['media_type'], data['media_id'], message, state, 'SecondOpinion',
                                 data['id'])


async def writeAgainSecondOpinion(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split('_')[2])
    await requestsMessageToSend.delete_message_to_send_by_id(id)
    await callback.message.delete()
    await second_opinion(callback.message.answer, state, callback.from_user.id, callback.message.html_text.split()[0])


async def consultationFaceToFace(callback: CallbackQuery, state: FSMContext):
    patient_id = callback.from_user.id
    doctor_id = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    id = int(callback.data.split('_')[3])
    if not await requestsUser.is_user(callback.from_user.id):
        await chooseConsultation(callback, state)
    else:
        specialty = await requestsSpecialty.get_specialty_by_id(id)
        await requestsStatistics.add_data(callback.from_user.id, doctor_id, 'faceToFace', specialty.name)
        patient = await requestsUser.get_user(patient_id)
        doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)
        if doctor.is_face_to_face:
            if patient.city == doctor.city:
                await callback.message.delete()
                await callback.message.answer(doctor.data_face_to_face,
                                              reply_markup=await kbInline.returnToConsultations(doctor_id, index, id))
            else:
                await callback.answer('Врач не ведет очный прием в Вашем городе.',
                                      reply_markup=await kbInline.returnToDoctorInfo(index, id, -1))
        else:
            await callback.answer(
                'Этот специалист ведет прием в государственной клинике только по ОМС. Записаться на платный прием невозможно',
                reply_markup=await kbInline.returnToDoctorInfo(index, id, -1))


async def returnToMenu(callback: CallbackQuery):
    id = int(callback.data.split('_')[1])
    await requestsMessageToSend.delete_message_to_send_by_id(id)
    await callback.message.delete()
    await callback.message.answer('Добро пожаловать!', reply_markup=await kbReply.kbPatientMain(callback.from_user.id))


async def deleteMessage(callback: CallbackQuery):
    await callback.message.delete()


async def notify_doctor_about_new_message(doctor_id: int, patient_id: int, consult_id: int):
    patient = await requestsUser.get_user_by_id(user_id=patient_id)
    gender_label = 'мужчина' if patient.gender == 'male' else 'женщина'

    # Get the last message from patient
    last_message = await requestsMessageToSend.get_first_message_to_send(patient_id, doctor_id)
    message_text = last_message.text if last_message else "Новое сообщение"

    text = f'''<code>Бот</code>

Новое сообщение от: <b>{gender_label}</b>, <b>{patient.age}</b> лет, <b>{patient.city}</b>

{message_text}'''

    await bot.send_message(
        chat_id=doctor_id,
        text=text,
        parse_mode='html',
        reply_markup=kbInline.doctor_notify_keyboard(patient_id, consult_id)
    )


async def show_patient_message(callback, patient_id, consult_id):
    patient = await requestsHistoryMessage.get_patient_info(patient_id)
    header = f"Пациент: {patient.gender}, {patient.age} лет, {patient.city}\n\n"

    messages = await requestsHistoryMessage.get_all_messages_by_consultation_id(consult_id)

    await callback.message.edit_text(f"{header}История сообщений:", parse_mode='html')

    for msg in messages:
        sender = "Пациент" if msg.who_write == "patient" else "Врач"
        prefix = f"{sender}: "
        if msg.media_type == "text":
            await callback.message.answer(prefix + (msg.text or ""), parse_mode='html')
        elif msg.media_type == "photo":
            await callback.message.answer_photo(photo=msg.media_id, caption=prefix + (msg.text or ""))
        elif msg.media_type == "document":
            await callback.message.answer_document(document=msg.media_id, caption=prefix + (msg.text or ""))
        elif msg.media_type in ("mediaGroupPhoto", "mediaGroupDocument"):
            parts = (msg.media_id or "").split(", ")
            if msg.media_type == "mediaGroupPhoto":
                media = [InputMediaPhoto(media=p) for p in parts]
                media[0].caption = prefix + (msg.text or "")
            else:
                media = [InputMediaDocument(media=p) for p in parts]
                media[-1].caption = prefix + (msg.text or "")
            await callback.message.answer_media_group(media=media)
        await asyncio.sleep(0.5)

    await callback.message.answer(
        "Действия:",
        reply_markup=kbInline.kb_doctor_reply_or_postpone(patient_id, consult_id)
    )


async def show_patient_conversation_paginated(callback: CallbackQuery, doctor_id: int, patient_id: int, page: int = 1,
                                              page_size: int = 5):
    from app.database.requests import requestsHistoryConsultation
    try:
        messages = await requestsHistoryConsultation.get_consultation_messages(doctor_id, patient_id)
        if not messages:
            await callback.answer('Нет сообщений в истории')
            return

        total = len(messages)
        total_pages = total // page_size + (1 if total % page_size else 0)
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        end = min(start + page_size, total)
        chunk = messages[start:end]

        try:
            data = await callback.message.edit_text("Загружаем историю сообщений...")
        except Exception as e:
            await callback.message.delete()
            message = await callback.message.answer("Загружаем историю сообщений...")
            data = message

        history_messages = []
        for msg in chunk:
            sender = "Пациент" if msg.who_write == "patient" else "Врач"
            prefix = f"{sender}: "
            if msg.media_type == "text":
                sent_msg = await callback.message.answer(prefix + (msg.text or ""), parse_mode='html')
                history_messages.append(sent_msg.message_id)
            elif msg.media_type == "photo":
                sent_msg = await callback.message.answer_photo(photo=msg.media_id, caption=prefix + (msg.text or ""))
                history_messages.append(sent_msg.message_id)
            elif msg.media_type == "document":
                sent_msg = await callback.message.answer_document(document=msg.media_id,
                                                                  caption=prefix + (msg.text or ""))
                history_messages.append(sent_msg.message_id)
            elif msg.media_type in ("mediaGroupPhoto", "mediaGroupDocument"):
                parts = (msg.media_id or "").split(", ")
                if msg.media_type == "mediaGroupPhoto":
                    media = [InputMediaPhoto(media=p) for p in parts]
                    if media:
                        media[0].caption = prefix + (msg.text or "")
                else:
                    media = [InputMediaDocument(media=p) for p in parts]
                    if media:
                        media[-1].caption = prefix + (msg.text or "")
                if media:
                    sent_msgs = await callback.message.answer_media_group(media=media)
                    history_messages.extend([msg.message_id for msg in sent_msgs])

        from aiogram.fsm.context import FSMContext
        state = FSMContext(storage=dp.storage,
                           key=StorageKey(chat_id=callback.message.chat.id, user_id=callback.from_user.id,
                                          bot_id=bot.id))
        await state.update_data(history_message_ids=history_messages)

        await data.edit_text(
            f"Страница {page} из {total_pages}\nНавигация по диалогу:",
            reply_markup=kbInline.kb_patient_conversation_nav(doctor_id, patient_id, page, total_pages)
        )

    except Exception as e:
        print(f"Error in show_patient_conversation_paginated: {e}")
        await callback.answer('Ошибка загрузки истории')


async def sendMessage(callback: CallbackQuery):
    patient_id = callback.from_user.id
    patient = await requestsUser.get_user(patient_id)
    _, message_id, doctor_id = callback.data.split('_')
    message_id, doctor_id = map(int, (message_id, doctor_id))
    message_to_repeat = await requestsMessageToRepeat.get_message_to_repeat_by_id(message_id)

    text = f'''<code>{patient.city}</code>, <code>{'мужчина' if patient.gender == 'male' else 'женщина'}</code>, <code>{patient.age}</code>

{message_to_repeat.text}'''
    media_type = message_to_repeat.media_type
    media_id = message_to_repeat.media_id

    await callback.message.delete()

    consult_id = await requestsBundle.get_id_consultation(patient_id, doctor_id)
    match media_type:
        case 'text':
            if await requestsBundle.is_bundle(patient_id, doctor_id):
                if await requestsBundle.is_open_dialog_doctor(patient_id, doctor_id):
                    await bot.send_message(chat_id=doctor_id, text=text, parse_mode='html')
                else:
                    await requestsMessageToSend.add_message_to_send(patient_id, doctor_id, text, 'text', '', False)
                    await notify_doctor_about_new_message(doctor_id, patient_id, consult_id)
        case 'photo':
            if await requestsBundle.is_bundle(patient_id, doctor_id):
                if await requestsBundle.is_open_dialog_doctor(patient_id, doctor_id):
                    await bot.send_photo(chat_id=doctor_id, photo=media_id, caption=text, parse_mode='html')
                else:
                    await requestsMessageToSend.add_message_to_send(patient_id, doctor_id, text, 'photo', media_id,
                                                                    False)
                    await notify_doctor_about_new_message(doctor_id, patient_id, consult_id)
        case 'document':
            if await requestsBundle.is_bundle(patient_id, doctor_id):
                if await requestsBundle.is_open_dialog_doctor(patient_id, doctor_id):
                    await bot.send_document(chat_id=doctor_id, document=media_id, caption=text, parse_mode='html')
                else:
                    await requestsMessageToSend.add_message_to_send(patient_id, doctor_id, text, 'document', media_id,
                                                                    False)
                    await notify_doctor_about_new_message(doctor_id, patient_id, consult_id)
        case 'mediaGroupPhoto' | 'mediaGroupDocument':
            if media_type == 'mediaGroupPhoto':
                mediaGroup = [InputMediaPhoto(media=id, parse_mode='html') for id in media_id.split(', ')]
                mediaGroup[0].caption = text
            else:
                mediaGroup = [InputMediaDocument(media=id, parse_mode='html') for id in media_id.split(', ')]
                mediaGroup[-1].caption = text
            if text != '':

                if await requestsBundle.is_open_dialog_doctor(patient_id, doctor_id):
                    await bot.send_media_group(chat_id=doctor_id, media=mediaGroup)
                else:
                    await requestsMessageToSend.add_message_to_send(patient_id, doctor_id, text, media_type, media_id,
                                                                    False)
                    await notify_doctor_about_new_message(doctor_id, patient_id, consult_id)

    await requestsMessageToRepeat.delete_message_to_repeat_by_id(message_id)

    id_consultation = await requestsBundle.get_id_consultation(patient_id, doctor_id)
    await requestsHistoryMessage.add_message(id_consultation, patient_id, doctor_id, 'patient', text, media_type,
                                             media_id)


async def sendMediaGroupPhoto(message, patient_id, data):
    photos = []
    for photo in groupToSend:
        if photo['patient_id'] == patient_id and photo['message'].photo:
            photos.append(photo)
    if photos:
        mediaGroup = [InputMediaPhoto(media=photo['message'].photo[-1].file_id, parse_mode='html') for photo in photos]

        if photos[0]['message'].html_text != '':
            mediaGroup[0].caption = photos[0]['message'].html_text
        if len(photos) == 1:
            await requestsMessageToRepeat.add_message_to_repeat(patient_id, data['doctor_id'], message.html_text,
                                                                'photo', message.photo[-1].file_id)
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(patient_id, data['doctor_id'])
            await message.answer(text=message.html_text,
                                 parse_mode='html',
                                 reply_markup=await kbInline.sendOrDelete(message_id, data['doctor_id']))
        else:
            await requestsMessageToRepeat.add_message_to_repeat(patient_id, data['doctor_id'], message.html_text,
                                                                'mediaGroupPhoto',
                                                                ', '.join(
                                                                    [photo['message'].photo[-1].file_id for photo in
                                                                     photos]))
            await message.answer_media_group(media=mediaGroup)
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(patient_id, data['doctor_id'])
            await message.answer('Выберите действие',
                                 reply_markup=await kbInline.sendOrDelete(message_id, data['doctor_id']))
        for photo in photos:
            groupToSend.remove(photo)


async def sendMediaGroupDocument(message, patient_id, data):
    documents = []
    for document in groupToSend:
        if document['patient_id'] == patient_id and document['message'].document:
            documents.append(document)
    if documents:
        mediaGroup = [InputMediaDocument(media=file['message'].document.file_id, parse_mode='html') for file in
                      documents]

        if len(documents) == 1:
            if documents[0]['message'].html_text != '':
                mediaGroup[0].caption = documents[0]['message'].html_text
            await requestsMessageToRepeat.add_message_to_repeat(patient_id, data['doctor_id'], message.html_text,
                                                                'document', message.document.file_id)
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(patient_id, data['doctor_id'])
            await message.answer_document(document=message.document.file_id, caption=message.html_text,
                                          parse_mode='html',
                                          reply_markup=await kbInline.sendOrDelete(message_id, data['doctor_id']))
        else:
            await requestsMessageToRepeat.add_message_to_repeat(patient_id, data['doctor_id'], message.html_text,
                                                                'mediaGroupDocument',
                                                                ', '.join(
                                                                    [document['message'].document.file_id for document
                                                                     in documents]))
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(patient_id, data['doctor_id'])
            await message.answer_media_group(media=mediaGroup)
            await message.answer('Выберите действие',
                                 reply_markup=await kbInline.sendOrDelete(message_id, data['doctor_id']))
        for document in documents:
            groupToSend.remove(document)


async def openDialogPatient(message: Message, state: FSMContext):
    patient_id = message.from_user.id
    data = await state.get_data()
    if await requestsBundle.is_bundle(patient_id, data['doctor_id']):
        if message.photo or message.document:
            groupToSend.append({'message': message, 'patient_id': patient_id})
            await asyncio.sleep(1)

            async with lock:
                if message.photo:
                    await sendMediaGroupPhoto(message, patient_id, data)
                elif message.document:
                    await sendMediaGroupDocument(message, patient_id, data)

        else:
            await requestsMessageToRepeat.add_message_to_repeat(patient_id, data['doctor_id'], message.html_text,
                                                                'text', '')
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(patient_id, data['doctor_id'])
            await message.answer(message.html_text,
                                 reply_markup=await kbInline.sendOrDelete(message_id, data['doctor_id']))
    else:
        await state.clear()


async def closeDialogPatient(message: Message):
    await message.answer('Вы хотите свернуть диалог? Продолжить эту консультацию вы сможете в разделе “Задать вопрос”',
                         reply_markup=kbInline.closeDialogPatient)


async def yesCloseDialogPatient(callback: CallbackQuery, state: FSMContext):
    patient_id = callback.from_user.id
    data = await state.get_data()
    doctor_id = data['doctor_id']
    await state.clear()
    await requestsBundle.edit_is_open_dialog_patient(patient_id, doctor_id, False)
    await callback.message.delete()
    await callback.message.answer('Вы свернули диалог с доктором', reply_markup=await kbReply.kbPatientMain(patient_id))


async def notCloseDialog(callback: CallbackQuery):
    await callback.message.edit_text('Вы продолжили консультацию')


async def endDialogPatient(message: Message):
    await message.answer('Вы уверены, что хотите завершить консультацию?', reply_markup=kbInline.endConsultation)


async def endConsultation(callback: CallbackQuery, state: FSMContext):
    patient_id = callback.from_user.id
    data = await state.get_data()
    doctor_id = data['doctor_id']
    chat_type = data['chat_type']
    await state.clear()
    await callback.message.delete()
    await requestsMessageToSend.delete_messages_to_send(patient_id, doctor_id)
    await requestsMessageToSend.delete_first_message(patient_id, doctor_id)
    await requestsMessageToRepeat.delete_messages_to_repeat(patient_id, doctor_id)
    await requestsMessageToRepeat.delete_messages_to_repeat(doctor_id, patient_id)
    await requestsBundle.delete_bundle(patient_id, doctor_id)
    await bot.send_message(chat_id=doctor_id, text='Пациент завершил консультацию', reply_markup=kbReply.kbDoctorMain)
    await callback.message.answer('Вы завершили консультацию', reply_markup=ReplyKeyboardRemove())

    await callback.message.answer(
        'Насколько подробно доктор погрузился в суть проблемы, дал исчерпывающий и понятный ответ?',
        reply_markup=await kbInline.keyboardStars(doctor_id, 1, chat_type))


async def endNotConsultation(callback: CallbackQuery):
    await callback.message.edit_text('Вы продолжили консультацию')
