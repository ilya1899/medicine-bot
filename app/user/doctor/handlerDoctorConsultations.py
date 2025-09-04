from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaDocument, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

router = Router()


class ChatDoctor(StatesGroup):
    openDialog = State()


groupToSend = []

lock = asyncio.Lock()

from app.database.requests import requestsDoctor, requestsBundle, requestsMessageToSend, requestsHistoryMessage, \
    requestsUser, requestsMessageToRepeat
from app.keyboards import kbInline, kbReply
from run import bot
from config import type_consultation


@router.message(F.text == 'Консультации')
async def message_doctorConsultations(message: Message):
    doctor_id = message.from_user.id
    if await requestsDoctor.is_doctor(doctor_id):
        bundles = await requestsBundle.get_bundles_by_doctor_id(doctor_id)
        await message.answer('Выберите чат', reply_markup=await kbInline.getKeyboardPatients(bundles))


@router.message(F.text == 'Свернуть диалог', ChatDoctor.openDialog)
async def message_closeDoctorDialog(message: Message):
    await message.answer('Вы уверены?', reply_markup=kbInline.closeDialogDoctor)


@router.callback_query(F.data == 'yesCloseDialogDoctor', ChatDoctor.openDialog)
async def callback_yesCloseDialog(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    doctor_id = callback.from_user.id
    for bundle in await requestsBundle.get_bundles_by_doctor_id(doctor_id):
        if bundle.is_open_dialog_doctor:
            await requestsBundle.edit_is_open_dialog_doctor(bundle.patient_id, doctor_id, False)
    await callback.message.delete()
    await callback.message.answer('Вы открыли меню доктора', reply_markup=kbReply.kbDoctorMain)


@router.callback_query(F.data == 'notCloseDialogDoctor', ChatDoctor.openDialog)
async def callback_notCloseDialogDoctor(callback: CallbackQuery):
    await callback.message.edit_text('Вы продолжили консультацию')


@router.message(F.text == 'Завершить консультацию', ChatDoctor.openDialog)
async def message_endDoctorDialog(message: Message):
    await message.answer('Вы уверены, что хотите завершить консультацию?', reply_markup=kbInline.endConsultation)


@router.callback_query(F.data == 'endConsultation', ChatDoctor.openDialog)
async def callback_endConsultation(callback: CallbackQuery, state: FSMContext):
    doctor_id = callback.from_user.id
    data = await state.get_data()
    patient_id = data['patient_id']
    chat_type = data['chat_type']
    await state.clear()
    await callback.message.delete()
    await requestsMessageToSend.delete_messages_to_send(doctor_id, patient_id)
    await requestsMessageToSend.delete_first_message(patient_id, doctor_id)
    await requestsBundle.delete_bundle(patient_id, doctor_id)
    await requestsMessageToSend.delete_first_message(patient_id, doctor_id)
    await bot.send_message(chat_id=patient_id, text='Врач завершил консультацию', reply_markup=ReplyKeyboardRemove())
    await bot.send_message(chat_id=patient_id,
                           text='Насколько подробно доктор погрузился в суть проблемы, дал исчерпывающий и понятный ответ?',
                           reply_markup=await kbInline.keyboardStars(doctor_id, 1, chat_type))
    await callback.message.answer('Вы завершили консультацию', reply_markup=kbReply.kbDoctorMain)


@router.callback_query(F.data == 'endNotConsultation', ChatDoctor.openDialog)
async def callback_endNotConsultation(callback: CallbackQuery):
    await callback.message.edit_text('Вы продолжили консультацию, напишите ваш ответ.')


@router.callback_query(F.data.startswith('dialogDoctor_'))
async def callback_dialogDoctor(callback: CallbackQuery, state: FSMContext):
    doctor_id = callback.from_user.id
    patient_id = int(callback.data.split('_')[1])
    patient = await requestsUser.get_user(patient_id)
    await requestsBundle.edit_is_open_dialog_doctor(patient_id, doctor_id, True)
    await callback.message.delete()
    chat_type = await requestsBundle.get_chat_type(patient_id, doctor_id)
    keyboard = ''
    match chat_type:
        case 'justAsk' | 'secondOpinion':
            keyboard = kbReply.kbDoctorDialog1
        case 'decoding' | 'mainFirst' | 'mainRepeated':
            keyboard = kbReply.kbDoctorDialog2
    await callback.message.answer(f'Вы открыли чат с пациентом, тип консультации: {type_consultation[chat_type]}',
                                  reply_markup=keyboard)
    if await requestsMessageToSend.is_message_to_send(patient_id, doctor_id):
        messages = await requestsMessageToSend.get_messages_to_send(patient_id, doctor_id)
        for messageToSend in messages:
            text = f'''<code>{'Мужчина' if patient.gender == 'male' else 'Женщина'}</code>, <code>{patient.age}</code>, <code>{patient.city}</code>


{messageToSend.text}'''
            match messageToSend.media_type:
                case 'text':
                    await callback.message.answer(text, parse_mode='html')
                case 'photo':
                    await callback.message.answer_photo(photo=messageToSend.media_id, caption=text,
                                                        parse_mode='html')
                case 'document':
                    await callback.message.answer_document(document=messageToSend.media_id, caption=text,
                                                           parse_mode='html')
                case 'mediaGroup':
                    photos = messageToSend.media_id.split(', ')
                    mediaGroup = [InputMediaPhoto(media=photo, parse_mode='html') for photo in photos]
                    if messageToSend.text != '':
                        mediaGroup[0].caption = messageToSend.text
                    await callback.message.answer_media_group(mediaGroup)
        await requestsMessageToSend.delete_messages_to_send(patient_id, doctor_id)
    await state.set_state(ChatDoctor.openDialog)
    await state.update_data(patient_id=patient_id, chat_type=chat_type)


@router.callback_query(F.data.startswith('seeNewConsultation_'))
async def callback_seeNewConsultation(callback: CallbackQuery):
    patient_id = int(callback.data.split('_')[1])
    doctor_id = callback.from_user.id
    messageToSend = await requestsMessageToSend.get_first_message_to_send(patient_id, doctor_id)
    await callback.message.delete()
    match messageToSend.media_type:
        case 'text':
            await callback.message.answer(messageToSend.text, parse_mode='html',
                                          reply_markup=await kbInline.getKeyboardStartOrBack(patient_id))
        case 'photo':
            await callback.message.answer_photo(photo=messageToSend.media_id, caption=messageToSend.text,
                                                parse_mode='html',
                                                reply_markup=await kbInline.getKeyboardStartOrBack(patient_id))
        case 'document':
            await callback.message.answer_document(document=messageToSend.media_id, caption=messageToSend.text,
                                                   parse_mode='html',
                                                   reply_markup=await kbInline.getKeyboardStartOrBack(patient_id))
        case 'mediaGroup':
            photos = messageToSend.media_id.split(', ')
            mediaGroup = [InputMediaPhoto(media=photo, parse_mode='html') for photo in photos]
            if messageToSend.text != '':
                mediaGroup[0].caption = messageToSend.text
            await callback.message.answer_media_group(mediaGroup)
            await callback.message.answer('Выберите действие', parse_mode='html',
                                          reply_markup=await kbInline.getKeyboardStartOrBack(patient_id))


@router.callback_query(F.data.startswith('startNewConsultation_'))
async def callback_startNewConsultation(callback: CallbackQuery, state: FSMContext):
    await callback_dialogDoctor(callback, state)


@router.callback_query(F.data.startswith('backNewConsultation_'))
async def callback_backNewConsultation(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() == ChatDoctor.openDialog:
        await callback.message.delete()
        await callback.message.answer('Вы вернулись в консультацию')
    else:
        await callback.message.delete()
        await callback.message.answer('Вы вернулись в главное меню', reply_markup=kbReply.kbDoctorMain)


async def timerConsultation(patient_id, doctor_id, chat_type):
    await asyncio.sleep(86400)
    if await requestsBundle.is_bundle(patient_id, doctor_id):
        await requestsBundle.delete_bundle(patient_id, doctor_id)
        await bot.send_message(chat_id=doctor_id, text='''<code>Бот</code>

Время истекло, консультация с пациентом завершена.''', parse_mode='html', reply_markup=kbReply.kbDoctorMain)
        await bot.send_message(chat_id=patient_id, text='''<code>Бот</code>

Время истекло, консультация с врачом завершена.''', parse_mode='html',
                               reply_markup=await kbReply.kbPatientMain(patient_id))

        await bot.send_message(chat_id=patient_id,
                               text='Насколько подробно доктор погрузился в суть проблемы, дал исчерпывающий и понятный ответ?',
                               reply_markup=await kbInline.keyboardStars(doctor_id, 1, chat_type))


@router.callback_query(F.data == 'deleteMessage', ChatDoctor.openDialog)
async def callback_deleteMessage(callback: CallbackQuery):
    await callback.message.delete()


async def notifyToPatientAboutNewMessage(patient_id, doctor_fullname):
    await bot.send_message(chat_id=patient_id, text=f'''<code>Бот</code>

У вас новое сообщение от <code>{doctor_fullname}</code>!
''', parse_mode='html')


@router.callback_query(F.data.startswith('sendMessage_'), ChatDoctor.openDialog)
async def callback_sendMessage(callback: CallbackQuery, state: FSMContext):
    doctor_id = callback.from_user.id
    data = await state.get_data()
    _, message_id, patient_id = callback.data.split('_')
    message_id, patient_id = map(int, (message_id, patient_id))
    message_to_repeat = await requestsMessageToRepeat.get_message_to_repeat_by_id(message_id)
    chat_type = data['chat_type']
    media_type = message_to_repeat.media_type
    media_id = message_to_repeat.media_id
    fullName = await requestsDoctor.get_full_name_by_user_id(doctor_id)
    text = f'<code>{fullName}</code>\n\n' + message_to_repeat.text
    id_consultation = await requestsBundle.get_id_consultation(patient_id, doctor_id)
    await requestsHistoryMessage.add_message(id_consultation, patient_id, doctor_id, 'doctor', text, media_type,
                                             media_id)

    await callback.message.delete()

    match media_type:
        case 'text':
            match chat_type:
                case 'justAsk' | 'secondOpinion':
                    await bot.send_message(chat_id=patient_id, text=text,
                                           parse_mode='html')
                    await bot.send_message(chat_id=patient_id,
                                           text='Насколько подробно доктор погрузился в суть проблемы, дал исчерпывающий и понятный ответ?',
                                           reply_markup=await kbInline.keyboardStars(doctor_id, 1, chat_type))
                    await callback.message.answer('Ответ отправлен!', reply_markup=kbReply.kbDoctorMain)
                    await requestsMessageToSend.delete_first_message(patient_id, doctor_id)
                    await requestsBundle.delete_bundle(patient_id, doctor_id)
                    await state.clear()
                case 'decoding' | 'mainFirst' | 'mainRepeated':
                    if await requestsBundle.is_bundle(patient_id, doctor_id):
                        if await requestsBundle.is_open_dialog_patient(patient_id, doctor_id):
                            await bot.send_message(chat_id=patient_id, text=text, parse_mode='html')
                        else:
                            await requestsMessageToSend.add_message_to_send(doctor_id, patient_id, text, 'text', '',
                                                                            False)
                            await notifyToPatientAboutNewMessage(patient_id, fullName)
                        await asyncio.create_task(timerConsultation(patient_id, doctor_id, chat_type))
        case 'photo':
            if await requestsBundle.is_bundle(patient_id, doctor_id):
                match chat_type:
                    case 'justAsk' | 'secondOpinion':
                        await bot.send_photo(chat_id=patient_id, photo=media_id,
                                             caption=text, parse_mode='html')
                        await bot.send_message(chat_id=patient_id,
                                               text='Насколько подробно доктор погрузился в суть проблемы, дал исчерпывающий и понятный ответ?',
                                               reply_markup=await kbInline.keyboardStars(doctor_id, 1, chat_type))
                        await callback.message.answer('Ответ отправлен!', reply_markup=kbReply.kbDoctorMain)
                        await requestsMessageToSend.delete_first_message(patient_id, doctor_id)
                        await requestsBundle.delete_bundle(patient_id, doctor_id)
                        await state.clear()
                    case 'decoding' | 'mainFirst' | 'mainRepeated':
                        if await requestsBundle.is_open_dialog_patient(patient_id, doctor_id):
                            await bot.send_photo(chat_id=patient_id, photo=media_id, caption=text, parse_mode='html')
                        else:
                            await requestsMessageToSend.add_message_to_send(doctor_id, patient_id, text, 'photo',
                                                                            media_id, False)
                            await notifyToPatientAboutNewMessage(patient_id, fullName)
                        await asyncio.create_task(timerConsultation(patient_id, doctor_id, chat_type))
        case 'document':
            if await requestsBundle.is_bundle(patient_id, doctor_id):
                match chat_type:
                    case 'justAsk' | 'secondOpinion':
                        await bot.send_document(chat_id=patient_id, document=media_id,
                                                caption=text, parse_mode='html')
                        await bot.send_message(chat_id=patient_id,
                                               text='Насколько подробно доктор погрузился в суть проблемы, дал исчерпывающий и понятный ответ?',
                                               reply_markup=await kbInline.keyboardStars(doctor_id, 1, chat_type))
                        await callback.message.answer('Ответ отправлен!', reply_markup=kbReply.kbDoctorMain)
                        await requestsMessageToSend.delete_first_message(patient_id, doctor_id)
                        await requestsBundle.delete_bundle(patient_id, doctor_id)
                        await state.clear()
                    case 'decoding' | 'mainFirst' | 'mainRepeated':
                        if await requestsBundle.is_open_dialog_patient(patient_id, doctor_id):
                            await bot.send_document(chat_id=patient_id, document=media_id, caption=text,
                                                    parse_mode='html')
                        else:
                            await requestsMessageToSend.add_message_to_send(doctor_id, patient_id, text, 'document',
                                                                            media_id, False)
                            await notifyToPatientAboutNewMessage(patient_id, fullName)
                        await asyncio.create_task(timerConsultation(patient_id, doctor_id, chat_type))
        case 'mediaGroupPhoto' | 'mediaGroupDocument':
            if media_type == 'mediaGroupPhoto':
                mediaGroup = [InputMediaPhoto(media=id) for id in media_id.split(', ')]
                mediaGroup[0].caption = text
            else:
                mediaGroup = [InputMediaDocument(media=id) for id in media_id.split(', ')]
                mediaGroup[-1].caption = text
            if text != '':
                match chat_type:
                    case 'justAsk' | 'secondOpinion':
                        await bot.send_media_group(chat_id=patient_id, media=mediaGroup)
                        await bot.send_message(chat_id=patient_id,
                                               text='Насколько подробно доктор погрузился в суть проблемы, дал исчерпывающий и понятный ответ?',
                                               reply_markup=await kbInline.keyboardStars(doctor_id, 1, chat_type))
                        await callback.message.answer('Ответ отправлен!', reply_markup=kbReply.kbDoctorMain)
                        await requestsMessageToSend.delete_first_message(patient_id, doctor_id)
                        await requestsBundle.delete_bundle(patient_id, doctor_id)
                        await state.clear()
                    case 'decoding' | 'mainFirst' | 'mainRepeated':
                        if await requestsBundle.is_open_dialog_patient(patient_id, doctor_id):
                            await bot.send_media_group(chat_id=patient_id, media=mediaGroup)
                        else:
                            await requestsMessageToSend.add_message_to_send(doctor_id, patient_id, text, media_type,
                                                                            media_id, False)
                            await notifyToPatientAboutNewMessage(patient_id, fullName)
                        await asyncio.create_task(timerConsultation(patient_id, doctor_id, chat_type))

    await requestsMessageToRepeat.delete_message_to_repeat_by_id(message_id)


async def sendMediaGroupPhoto(message, doctor_id, data):
    photos = []
    for photo in groupToSend:
        if photo['doctor_id'] == doctor_id and photo['message'].photo:
            photos.append(photo)
    if photos:
        mediaGroup = [InputMediaPhoto(media=photo['message'].photo[-1].file_id, parse_mode='html') for photo in photos]

        if photos[0]['message'].html_text != '':
            mediaGroup[0].caption = photos[0]['message'].html_text
        if len(photos) == 1:
            await requestsMessageToRepeat.add_message_to_repeat(doctor_id, data['patient_id'], message.html_text,
                                                                'photo', message.photo[-1].file_id)
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(doctor_id, data['patient_id'])
            await message.answer_photo(photo=message.photo[-1].file_id, caption=message.html_text,
                                       parse_mode='html',
                                       reply_markup=await kbInline.sendOrDelete(message_id, data['patient_id']))
        else:
            await requestsMessageToRepeat.add_message_to_repeat(doctor_id, data['patient_id'], message.html_text,
                                                                'mediaGroupPhoto',
                                                                ', '.join(
                                                                    [photo['message'].photo[-1].file_id for photo in
                                                                     photos]))
            await message.answer_media_group(media=mediaGroup)
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(doctor_id, data['patient_id'])
            await message.answer('Выберите действие',
                                 reply_markup=await kbInline.sendOrDelete(message_id, data['patient_id']))
        for photo in photos:
            groupToSend.remove(photo)


async def sendMediaGroupDocument(message, doctor_id, data):
    documents = []
    for document in groupToSend:
        if document['doctor_id'] == doctor_id and document['message'].document:
            documents.append(document)
    if documents:
        mediaGroup = [InputMediaDocument(media=file['message'].document.file_id, parse_mode='html') for file in
                      documents]

        if len(documents) == 1:
            if documents[0]['message'].html_text != '':
                mediaGroup[0].caption = documents[0]['message'].html_text
            await requestsMessageToRepeat.add_message_to_repeat(doctor_id, data['patient_id'], message.html_text,
                                                                'document', message.document.file_id)
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(doctor_id, data['patient_id'])
            await message.answer_document(document=message.document.file_id, caption=message.html_text,
                                          parse_mode='html',
                                          reply_markup=await kbInline.sendOrDelete(message_id, data['patient_id']))
        else:
            await requestsMessageToRepeat.add_message_to_repeat(doctor_id, data['patient_id'], message.html_text,
                                                                'mediaGroupDocument',
                                                                ', '.join(
                                                                    [document['message'].document.file_id for document
                                                                     in documents]))
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(doctor_id, data['patient_id'])
            await message.answer_media_group(media=mediaGroup)
            await message.answer('Выберите действие',
                                 reply_markup=await kbInline.sendOrDelete(message_id, data['patient_id']))
        for document in documents:
            groupToSend.remove(document)


@router.message(ChatDoctor.openDialog)
async def message_openDialog(message: Message, state: FSMContext):
    doctor_id = message.from_user.id
    data = await state.get_data()
    if await requestsBundle.is_bundle(data['patient_id'], doctor_id):
        if message.photo or message.document:
            groupToSend.append({'message': message, 'doctor_id': doctor_id})
            await asyncio.sleep(1)

            async with lock:
                if message.photo:
                    await sendMediaGroupPhoto(message, doctor_id, data)
                elif message.document:
                    await sendMediaGroupDocument(message, doctor_id, data)

        else:
            await requestsMessageToRepeat.add_message_to_repeat(doctor_id, data['patient_id'], message.html_text,
                                                                'text', '')
            message_id = await requestsMessageToRepeat.get_id_last_message_to_repeat(doctor_id, data['patient_id'])
            await message.answer(message.html_text,
                                 reply_markup=await kbInline.sendOrDelete(message_id, data['patient_id']))
    else:
        await state.clear()
