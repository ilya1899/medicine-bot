from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaDocument, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

from app.businessLogic.logicConsultation import ChatPatient
from app.keyboards.kbInline import consultation_keyboard, see_message_keyboard, make_consultation_keyboard, \
    make_see_message_keyboard, kb_doctor_reply_or_view, kb_doctor_reply_or_postpone

router = Router()


class ChatDoctor(StatesGroup):
    openDialog = State()


groupToSend = []

lock = asyncio.Lock()

from app.database.requests import requestsDoctor, requestsBundle, requestsMessageToSend, requestsHistoryMessage, \
    requestsUser, requestsMessageToRepeat, requestsHistoryConsultation
from app.keyboards import kbInline, kbReply
from run import bot
from config import type_consultation
from texts import GENDER_MALE, GENDER_FEMALE, NEW_MESSAGE_FROM_PATIENT, CONSULTATION_NOTIFICATION, NEW_MESSAGE_FROM_DOCTOR


@router.message(F.text == 'Консультации')
async def message_doctorConsultations(message: Message):
    doctor_id = message.from_user.id
    if await requestsDoctor.is_doctor(doctor_id):
        bundles = await requestsBundle.get_bundles_by_doctor_id(doctor_id)

        # Группируем консультации по пациенту
        patient_to_bundles: dict[int, list] = {}
        for b in bundles:
            patient_to_bundles.setdefault(b.patient_id, []).append(b)

        keyboard = InlineKeyboardBuilder()

        # Формируем кнопки: имя пациента; если консультаций >1, добавляем порядковый номер 1,2,3
        for patient_id, blist in patient_to_bundles.items():
            user = await requestsUser.get_user_by_id(user_id=patient_id)
            full_name = user.full_name if user else f"Пациент {patient_id}"
            count = len(blist)
            for idx, _ in enumerate(blist, start=1):
                label = full_name if count == 1 else f"{full_name} {idx}"
                keyboard.row(InlineKeyboardButton(text=label, callback_data=f'dialogDoctor_{patient_id}'))

        # Кнопка назад
        keyboard.row(InlineKeyboardButton(text='Назад', callback_data='returnToMenu'))

        await message.answer('Выберите консультацию', reply_markup=keyboard.as_markup())


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


async def timer_consultation(patient_id, doctor_id, chat_type):
    """Timer for consultation - closes consultation after 24 hours"""
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


async def notify_patient_about_new_message(patient_id: int, doctor_fullname: str, doctor_id: int):
    text = CONSULTATION_NOTIFICATION.format(message=NEW_MESSAGE_FROM_DOCTOR.format(doctor_name=doctor_fullname))
    await bot.send_message(
        chat_id=patient_id,
        text=text,
        parse_mode="html",
        reply_markup=kbInline.notify_keyboard(doctor_id, patient_id),
    )


async def notify_doctor_about_new_message(doctor_id: int, patient_id: int, consult_id: int):
    patient = await requestsUser.get_user_by_id(user_id=patient_id)
    gender_label = GENDER_MALE if patient.gender == 'male' else GENDER_FEMALE
    text = NEW_MESSAGE_FROM_PATIENT.format(
        gender=gender_label,
        age=patient.age,
        city=patient.city
    )

    await bot.send_message(
        chat_id=doctor_id,
        text=text,
        parse_mode='html',
        reply_markup=kbInline.doctor_notify_keyboard(patient_id, consult_id)
    )


@router.callback_query(F.data.startswith("seePatientMessage_"))
async def callback_seePatientMessage(callback: CallbackQuery, state: FSMContext):
    """Show conversation with in-message pagination (page 1)."""
    _, patient_id, consult_id = callback.data.split("_")
    patient_id, consult_id = int(patient_id), int(consult_id)

    await _open_or_edit_conversation(callback, patient_id, consult_id, page=1)


def _split_media_ids(media_id_str: str):
    if not media_id_str:
        return []
    return [m.strip() for m in media_id_str.split(",") if m.strip()]


@router.callback_query(F.data.startswith("seeConsultation_"))
async def callback_seeConsultation(callback: CallbackQuery, state: FSMContext):
    """Open consultation with in-message pagination (page 1)."""
    _, patient_id, consult_id = callback.data.split("_")
    patient_id, consult_id = int(patient_id), int(consult_id)

    await _open_or_edit_conversation(callback, patient_id, consult_id, page=1)


def _format_message_line(msg) -> str:
    sender = "Пациент" if msg.who_write == "patient" else "Врач"
    base = f"<b>{sender}:</b> "
    text = msg.text or ""
    match msg.media_type:
        case "text":
            return base + text
        case "photo":
            return base + (text if text else "") + "\n📷 Фото"
        case "document":
            return base + (text if text else "") + "\n📎 Документ"
        case "mediaGroupPhoto":
            return base + (text if text else "") + "\n🖼️ Альбом фото"
        case "mediaGroupDocument":
            return base + (text if text else "") + "\n📁 Альбом файлов"
        case _:
            return base + text


async def _build_conversation_page_text(patient_id: int, consult_id: int, page: int, page_size: int = 5) -> tuple[str, int, int]:
    messages = await requestsHistoryMessage.get_all_messages_by_consultation_id(consult_id)
    total = len(messages)
    if total == 0:
        return ("Переписки пока нет", 0, 0)
    total_pages = total // page_size + (1 if total % page_size else 0)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = min(start + page_size, total)

    patient = await requestsUser.get_user_by_id(user_id=patient_id)
    gender_label = 'мужчина' if patient.gender == 'male' else 'женщина'
    header = f"<b>{gender_label}, {patient.age} лет, {patient.city}</b>\n\n"

    body_lines = [_format_message_line(m) for m in messages[start:end]]
    body = "\n\n".join(body_lines)
    footer = f"\n\nСтр. {page}/{total_pages}"
    return (header + body + footer, page, total_pages)


def _conversation_nav_kb(patient_id: int, consult_id: int, page: int, total_pages: int) -> InlineKeyboardMarkup:
    prev_page = max(1, page - 1)
    next_page = min(total_pages, page + 1)
    buttons = [
        [
            InlineKeyboardButton(text='⏮️ Назад', callback_data=f'conv_nav_{patient_id}_{consult_id}_{prev_page}'),
            InlineKeyboardButton(text='⏭️ Вперёд', callback_data=f'conv_nav_{patient_id}_{consult_id}_{next_page}'),
        ],
        [
            InlineKeyboardButton(text='Ответить', callback_data=f'doctorReply_{patient_id}_{consult_id}'),
            InlineKeyboardButton(text='Отложить консультацию', callback_data=f'doctorPostpone_{patient_id}_{consult_id}'),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def _open_or_edit_conversation(callback: CallbackQuery, patient_id: int, consult_id: int, page: int):
    text, page, total_pages = await _build_conversation_page_text(patient_id, consult_id, page)
    kb = _conversation_nav_kb(patient_id, consult_id, page, total_pages)
    # Edit the same message in place
    await callback.message.edit_text(text=text, reply_markup=kb, parse_mode='html')
    await callback.answer()


@router.callback_query(F.data.startswith('conv_nav_'))
async def callback_conv_nav(callback: CallbackQuery):
    _, _, patient_id, consult_id, page = callback.data.split('_')
    patient_id = int(patient_id)
    consult_id = int(consult_id)
    page = int(page)
    await _open_or_edit_conversation(callback, patient_id, consult_id, page)


@router.callback_query(F.data.startswith("doctorReply_"))
async def callback_doctor_reply(callback: CallbackQuery, state: FSMContext):
    _, patient_id, consult_id = callback.data.split("_")
    patient_id = int(patient_id)
    doctor_id = callback.from_user.id

    await requestsBundle.edit_is_open_dialog_doctor(patient_id, doctor_id, True)
    chat_type = await requestsBundle.get_chat_type(patient_id, doctor_id)

    # Fix KeyError by providing default value
    consultation_type = type_consultation.get(chat_type, "Неизвестный тип")
    
    keyboard = kbReply.kbDoctorDialog1 if chat_type in ['justAsk', 'secondOpinion'] else kbReply.kbDoctorDialog2

    await callback.message.answer(
        f"Вы открыли чат с пациентом, тип консультации: {consultation_type}",
        reply_markup=keyboard
    )

    # Show pending messages from patient with context
    if await requestsMessageToSend.is_message_to_send(patient_id, doctor_id):
        patient = await requestsUser.get_user_by_id(user_id=patient_id)
        messages = await requestsMessageToSend.get_messages_to_send(patient_id, doctor_id)
        for messageToSend in messages:
            gender_label = 'мужчина' if patient.gender == 'male' else 'женщина'
            text = f'''<b>{gender_label}, {patient.age} лет, {patient.city}</b>

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
                        mediaGroup[0].caption = text
                    await callback.message.answer_media_group(mediaGroup)
        await requestsMessageToSend.delete_messages_to_send(patient_id, doctor_id)
    
    await state.set_state(ChatDoctor.openDialog)
    await state.update_data(patient_id=patient_id, chat_type=chat_type)
    await callback.message.answer("✍️ Напишите ваш ответ и отправьте.")


@router.callback_query(F.data.startswith("doctorPostpone_"))
async def callback_doctor_postpone(callback: CallbackQuery):
    _, patient_id, consult_id = callback.data.split("_")
    patient_id = int(patient_id)
    doctor_id = callback.from_user.id

    await requestsBundle.edit_is_open_dialog_doctor(patient_id, doctor_id, False)
    await callback.message.answer("Консультация отложена. Вы можете вернуться к ней позже в меню 'Консультации'.")

@router.callback_query(F.data.startswith("replyMessage_"))
async def callback_replyMessage(callback: CallbackQuery, state: FSMContext):
    _, doctor_id, patient_id = callback.data.split("_")
    doctor_id, patient_id = int(doctor_id), int(patient_id)

    await state.set_state(ChatPatient.replyToDoctor)
    await state.update_data(doctor_id=doctor_id, patient_id=patient_id)

    await callback.message.answer("✍️ Напишите ваш ответ врачу:")


@router.message(ChatPatient.replyToDoctor, F.text)
async def process_reply_to_doctor_text(message: Message, state: FSMContext):
    data = await state.get_data()
    doctor_id = data["doctor_id"]
    patient_id = message.from_user.id

    await requestsHistoryMessage.add_message(
        id_consultation=await requestsHistoryMessage.get_last_consultation_id(patient_id, doctor_id),
        patient_id=patient_id,
        doctor_id=doctor_id,
        who_write="patient",
        text=message.text,
        media_type="text",
        media_id=""
    )

    await bot.send_message(
        chat_id=doctor_id,
        text=f"📩 Пациент {patient_id} ответил:\n\n{message.text}",
        parse_mode="html"
    )

    await message.answer("✅ Ваш ответ отправлен врачу.")
    await state.clear()


@router.message(ChatDoctor.openDialog, F.text)
async def process_doctor_message_text(message: Message, state: FSMContext):
    """Handle text messages from doctor to patient"""
    doctor_id = message.from_user.id
    data = await state.get_data()
    patient_id = data.get('patient_id')
    chat_type = data.get('chat_type')
    
    if not patient_id:
        await message.answer("Ошибка: не найден пациент")
        return
    
    # Get doctor name
    doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)
    doctor_name = doctor.full_name if doctor else f"Врач {doctor_id}"
    
    # Format message with doctor name
    text = f"<b>{doctor_name}</b>\n\n{message.text}"
    
    # Add to history
    consult_id = await requestsHistoryMessage.get_last_consultation_id(patient_id, doctor_id)
    await requestsHistoryMessage.add_message(
        id_consultation=consult_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        who_write="doctor",
        text=text,
        media_type="text",
        media_id=""
    )
    
    # Send to patient
    if await requestsBundle.is_bundle(patient_id, doctor_id):
        if await requestsBundle.is_open_dialog_patient(patient_id, doctor_id):
            await bot.send_message(chat_id=patient_id, text=text, parse_mode='html')
        else:
            await requestsMessageToSend.add_message_to_send(doctor_id, patient_id, text, 'text', '', False)
            await notify_patient_about_new_message(patient_id, doctor_name, doctor_id)
    
    # Handle different consultation types
    if chat_type in ['justAsk', 'secondOpinion']:
        await bot.send_message(chat_id=patient_id,
                               text='Насколько подробно доктор погрузился в суть проблемы, дал исчерпывающий и понятный ответ?',
                               reply_markup=await kbInline.keyboardStars(doctor_id, 1, chat_type))
        await message.answer('Ответ отправлен!', reply_markup=kbReply.kbDoctorMain)
        await requestsMessageToSend.delete_first_message(patient_id, doctor_id)
        await requestsBundle.delete_bundle(patient_id, doctor_id)
        await state.clear()
    else:
        await asyncio.create_task(timer_consultation(patient_id, doctor_id, chat_type))
        await message.answer("✅ Ваш ответ отправлен пациенту.")


@router.callback_query(F.data.startswith("endConsultation_"))
async def callback_endConsultation(callback: CallbackQuery, state: FSMContext):
    _, doctor_id, patient_id = callback.data.split("_")
    doctor_id, patient_id = int(doctor_id), int(patient_id)

    await requestsHistoryConsultation.close_consultation(doctor_id, patient_id)

    await callback.message.answer("✅ Консультация завершена. Спасибо, что воспользовались нашим сервисом!")


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
                            await notify_patient_about_new_message(patient_id, fullName, doctor_id)
                        await asyncio.create_task(timer_consultation(patient_id, doctor_id, chat_type))
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
                            await notify_patient_about_new_message(patient_id, fullName, doctor_id)
                        await asyncio.create_task(timer_consultation(patient_id, doctor_id, chat_type))
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
                            await notify_patient_about_new_message(patient_id, fullName, doctor_id)
                        await asyncio.create_task(timer_consultation(patient_id, doctor_id, chat_type))
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
                            await notify_patient_about_new_message(patient_id, fullName, doctor_id)
                        await asyncio.create_task(timer_consultation(patient_id, doctor_id, chat_type))

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
