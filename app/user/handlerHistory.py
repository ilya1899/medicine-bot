from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton, \
    InputMediaDocument
from aiogram.fsm.context import FSMContext
import asyncio

from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.businessLogic.logicConsultation import ChatPatient
from run import bot

router = Router()

from app.database.requests import requestsHistoryMessage, requestsHistoryConsultation, requestsDoctor, \
    requestsSpecialty, requestsMessageToSend, requestsBundle
from app.keyboards import kbInline, kbReply
from app.businessLogic import logicConsultation
from config import type_consultation


@router.message(F.text == 'История консультаций')
async def message_history_of_consultations(message: Message):
    patient_id = message.from_user.id
    consultations = await requestsHistoryConsultation.get_all_consultations_by_patient_id(patient_id)

    if not consultations:
        await message.answer('У вас пока нет истории консультаций.')
        return

    specialties_set = set(c.specialty for c in consultations)

    builder = InlineKeyboardBuilder()
    for spec in specialties_set:
        builder.button(text=spec, callback_data=f"history_spec_{spec}")
    builder.adjust(1)

    await message.answer("Выберите специальность:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('history_spec_'))
async def callback_history_specialty(callback: CallbackQuery):
    specialty = callback.data.split('_', 2)[2]
    patient_id = callback.from_user.id

    consultations = await requestsHistoryConsultation.get_all_consultations_by_patient_id(patient_id)
    doctors_set = set(c.doctor_id for c in consultations if c.specialty == specialty)

    builder = InlineKeyboardBuilder()
    for doctor_id in doctors_set:
        doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)
        builder.button(text=doctor.full_name, callback_data=f"history_doc_{doctor_id}_{specialty}")
    builder.button(text="Назад", callback_data="history_back_to_start")
    builder.adjust(1)

    await callback.message.edit_text(f"Выберите врача по специальности: {specialty}", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('history_doc_'))
async def callback_history_doctor(callback: CallbackQuery):
    parts = callback.data.split('_', 3)
    doctor_id = int(parts[2])
    specialty = parts[3]
    patient_id = callback.from_user.id

    consultations = await requestsHistoryConsultation.get_all_consultations_by_patient_and_doctor_id(
        patient_id, doctor_id
    )

    header_text = (
        "🔄- консультация, которую можно продолжить. Доктор увидит выбранный вами диалог, всю историю, "
        "рекомендации, а вы сможете дополнить её новыми деталями и изменениями в вашем самочувствии"
    )
    await callback.message.edit_text(header_text)

    builder = InlineKeyboardBuilder()
    for c in consultations:
        text = f"{c.name} {'🔄' if c.chat_type in ['mainFirst', 'mainRepeated'] else ''}"
        builder.button(text=text, callback_data=f"history_consult_{c.id}")
    builder.button(text="Назад", callback_data=f"history_spec_{specialty}")
    builder.adjust(1)

    await callback.message.answer("Выберите консультацию:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('history_consult_'))
async def callback_history_consultation(callback: CallbackQuery):
    consult_id = int(callback.data.split('_')[2])
    consultation = await requestsHistoryConsultation.get_consultation(consult_id)
    messages = await requestsHistoryConsultation.get_messages_by_consultation_id(consult_id)

    for msg in messages:
        match msg.media_type:
            case "text":
                await callback.message.answer(msg.text)
            case "photo":
                await callback.message.answer_photo(photo=msg.media_id, caption=msg.text)
            case "document":
                await callback.message.answer_document(document=msg.media_id, caption=msg.text)
            case "mediaGroup":
                pass

    builder = InlineKeyboardBuilder()
    if consultation.chat_type in ["mainFirst", "mainRepeated"]:
        builder.button(text="Продолжить эту консультацию", callback_data=f"history_continue_{consult_id}")
    builder.button(text="Задать новый вопрос", callback_data=f"history_new_{consult_id}")
    builder.button(text="Назад", callback_data=f"history_doc_{consultation.doctor_id}_{consultation.specialty}")
    builder.adjust(1)

    await callback.message.answer("Действия с консультацией:", reply_markup=builder.as_markup())


# @router.message(F.text == 'История консультаций')
# async def message_historyOfConsultations(message: Message):
#     patient_id = message.from_user.id
#     specialties = await requestsSpecialty.get_specialties_by_patient(patient_id)
#
#     if not specialties:
#         await message.answer('У вас пока нет истории консультаций.')
#         return
#
#     # Формируем клавиатуру со специальностями
#     keyboard = await kbInline.getKeyboardSpecialtiesHistory(specialties)
#     await message.answer('Выберите интересующую вас специальность:', reply_markup=keyboard)


# @router.message(F.text == 'История консультаций')
# async def message_historyOfConsultations(message: Message):

# await message.answer('Выберите интересующие вас консультации', reply_markup=kbInline.typesHistoryConsultation)


@router.callback_query(F.data == 'ongoingConsultations')
async def callback_ongoingConsultations(callback: CallbackQuery):
    await logicConsultation.continueConsultation(callback)


# @router.callback_query(F.data == 'completedConsultations')
# async def callback_completedConsultations(callback: CallbackQuery):
#     patient_id = callback.from_user.id
#     consultations = await requestsHistoryConsultation.get_all_consultations_by_patient_id(patient_id)
#     if len(consultations) > 0:
#         await callback.message.edit_text('Выберите консультацию',
#                                          reply_markup=await kbInline.getKeyboardCompletedConsultations(consultations,
#                                                                                                        0))
#     else:
#         await callback.answer('Завершенных консультаций нет')
@router.callback_query(F.data.startswith('history_specialty_'))
async def callback_history_specialty(callback: CallbackQuery):
    specialty_id = int(callback.data.split('_')[2])
    patient_id = callback.from_user.id
    doctors = await requestsDoctor.get_doctors_by_specialty_id_and_patient(specialty_id, patient_id)
    if doctors:
        await callback.message.edit_text('Выберите врача',
                                         reply_markup=await kbInline.getKeyboardDoctorsHistory(doctors, specialty_id))
    else:
        await callback.answer('Вы пока не обращались к врачу этой специальности')


@router.callback_query(F.data.startswith('history_doctor_'))
async def callback_history_doctor(callback: CallbackQuery):
    doctor_id = int(callback.data.split('_')[2])
    specialty_id = int(callback.data.split('_')[3])
    patient_id = callback.from_user.id
    consultations = await requestsHistoryConsultation.get_consultations_by_patient_and_doctor(patient_id, doctor_id)
    if consultations:
        # формируем подписи консультаций с учётом 🔄
        consultation_titles = []
        for c in consultations:
            title = c.title
            if c.chat_type in ['mainFirst', 'mainRepeated']:  # типы, которые можно продолжить
                title = f'🔄 {title}'
            consultation_titles.append(
                {'id': c.id, 'title': title, 'isRepeated': c.chat_type in ['mainFirst', 'mainRepeated']})
        text = ("🔄- консультация, которую можно продолжить. "
                "Доктор увидит выбранный вами диалог, всю историю, рекомендации, а вы сможете дополнить её новыми деталями и изменениями в вашем самочувствии\n\n"
                "Выберите консультацию:")
        await callback.message.edit_text(text,
                                         reply_markup=await kbInline.getKeyboardConsultationsHistory(
                                             consultation_titles, doctor_id, specialty_id))
    else:
        await callback.answer('Нет консультаций с этим врачом')


@router.callback_query(F.data.startswith('history_consultation_'))
async def callback_history_consultation(callback: CallbackQuery):
    parts = callback.data.split('_')
    consultation_id = int(parts[2])
    doctor_id = int(parts[3])
    specialty_id = int(parts[4])
    consultation = await requestsHistoryConsultation.get_consultation(consultation_id)
    messages = await requestsHistoryMessage.get_all_messages_by_consultation_id(consultation_id)

    await callback.message.edit_text(f'<b>Консультация: {consultation.title}</b>\n\nИстория сообщений:',
                                     parse_mode='html')
    for message in messages:
        match message.media_type:
            case 'text':
                await callback.message.answer(message.text, parse_mode='html')
            case 'photo':
                await callback.message.answer_photo(photo=message.media_id, caption=message.text, parse_mode='html')
            case 'document':
                await callback.message.answer_document(document=message.media_id, caption=message.text,
                                                       parse_mode='html')
            case 'mediaGroup':
                mediaGroup = [InputMediaPhoto(media=photo, parse_mode='html') for photo in message.media_id.split(', ')]
                mediaGroup[0].caption = message.text
                await callback.message.answer_media_group(media=mediaGroup)
        await asyncio.sleep(0.5)

    # Кнопки действий: продолжить / новый вопрос / назад
    is_continuable = consultation.chat_type in ['mainFirst', 'mainRepeated']
    await callback.message.answer(
        'Выберите действие:',
        reply_markup=await kbInline.getKeyboardConsultationActions(consultation_id, doctor_id, is_continuable,
                                                                   specialty_id)
    )


@router.callback_query(F.data.startswith('completedConsultation_'))
async def callback_completedConsultation(callback: CallbackQuery):
    id_consultation = int(callback.data.split('_')[1])
    isRepeated = callback.data.split('_')[2] != '0'
    consultation = await requestsHistoryConsultation.get_consultation(id_consultation)
    specialty = await requestsSpecialty.get_specialty_by_name(consultation.specialty)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    doctor_id = consultation.doctor_id
    index = 0
    for i in range(len(doctors)):
        if doctors[i].user_id == doctor_id:
            index = i
    await callback.message.edit_text('Выберите действие',
                                     reply_markup=await kbInline.getKeyboardActionsCompletedConsultation(
                                         consultation.doctor_id, consultation.chat_type, id_consultation, isRepeated,
                                         index, specialty.id))


@router.callback_query(F.data.startswith('isStartAgain_'))
async def callback_isStartAgain(callback: CallbackQuery):
    id_consultation = int(callback.data.split('_')[1])
    isRepeated = callback.data.split('_')[2] != '0'
    consultation = await requestsHistoryConsultation.get_consultation(id_consultation)
    specialty = await requestsSpecialty.get_specialty_by_name(consultation.specialty)

    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    doctor_id = consultation.doctor_id
    index = 0
    for i in range(len(doctors)):
        if doctors[i].user_id == doctor_id:
            index = i

    doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)
    await callback.message.edit_text(f'''{doctor.full_name}

Тип: {type_consultation[consultation.chat_type]}
Стоимость: {int(await logicConsultation.getPrice(consultation.doctor_id, consultation.chat_type) * 1.2)} руб.

Вы уверены?''',
                                     reply_markup=await kbInline.getKeyboardStartAgainOrReturn(
                                         consultation.doctor_id,
                                         consultation.chat_type,
                                         isRepeated,
                                         specialty.id,
                                         id_consultation,
                                         index))


@router.callback_query(F.data.startswith('startAgainCompletedConsultation_'))
async def callback_startAgainCompletedConsultation(callback: CallbackQuery, state: FSMContext):
    chat_type = callback.data.split('_')[2]
    id_consultation = int(callback.data.split('_')[4])
    await logicConsultation.historyToMessageToSend(id_consultation)
    match chat_type:
        case 'justAsk':
            await logicConsultation.consultationJustAsk(callback, state)
        case 'decoding':
            await logicConsultation.consultationDecoding(callback, state)
        case 'mainRepeated' | 'mainFirst':
            await logicConsultation.startRepeatedConsultation(callback, state)
        case 'secondOpinion':
            await logicConsultation.consultationSecondOpinion(callback, state)


@router.callback_query(F.data.startswith('readCompletedConsultation_'))
async def callback_readCompletedConsultation(callback: CallbackQuery):
    id_consultation = int(callback.data.split('_')[1])
    consultation = await requestsHistoryConsultation.get_consultation(id_consultation)
    doctor_id = int(callback.data.split('_')[2])
    chat_type = callback.data.split('_')[3]
    isRepeated = callback.data.split('_')[4] != '0'

    specialty = await requestsSpecialty.get_specialty_by_name(consultation.specialty)
    doctors = await requestsDoctor.get_doctors_by_specialty(specialty.name)
    index = 0
    for i in range(len(doctors)):
        if doctors[i].user_id == doctor_id:
            index = i

    messages = await requestsHistoryMessage.get_all_messages_by_consultation_id(id_consultation)
    await callback.message.edit_text('<b>Начало консультации</b>', parse_mode='html')
    for message in messages:
        match message.media_type:
            case 'text':
                await callback.message.answer(message.text, parse_mode='html')
            case 'photo':
                await callback.message.answer_photo(photo=message.media_id, caption=message.text,
                                                    parse_mode='html')
            case 'document':
                await callback.message.answer_document(document=message.media_id, caption=message.text,
                                                       parse_mode='html')
            case 'mediaGroup':
                mediaGroup = [InputMediaPhoto(media=photo, parse_mode='html') for photo in message.media_id.split(', ')]
                mediaGroup[0].caption = message.text
                await callback.message.answer_media_group(media=mediaGroup)
        await asyncio.sleep(0.5)
    specialty = await requestsSpecialty.get_specialty_by_name(consultation.specialty)
    await callback.message.answer('<b>Конец консультации</b>', parse_mode='html',
                                  reply_markup=await kbInline.getKeyboardStartAgainOrReturn(doctor_id, chat_type,
                                                                                            isRepeated, specialty.id,
                                                                                            id_consultation, index))


@router.callback_query(F.data == 'returnToHistoryCompletedConsultations')
async def callback_returnToHistoryCompletedConsultations(callback: CallbackQuery):
    # await callback_completedConsultations(callback)
    pass


@router.callback_query(F.data.startswith("seeMessage_"))
async def callback_peek_new_message(callback: CallbackQuery, state: FSMContext):
    doctor_id, patient_id = map(int, callback.data.split("_")[1:3])

    consult_id = await requestsBundle.get_id_consultation(patient_id, doctor_id)
    if not consult_id:
        await callback.answer("Консультация не найдена.")
        return

    doctor = await requestsDoctor.get_doctor_by_user_id(doctor_id)
    last_msg = await requestsMessageToSend.get_last_message_for_patient(doctor_id, patient_id)
    if not last_msg:
        await callback.answer("Новых сообщений нет.")
        return

    header = f"<b>{doctor.full_name}</b>\n\n"
    if last_msg.media_type == "text":
        await callback.message.edit_text(
            header + (last_msg.text or ""),
            parse_mode="html",
            reply_markup=kbInline.kb_patient_peek_actions(consult_id, doctor_id)
        )
    elif last_msg.media_type == "photo":
        await callback.message.delete()
        await bot.send_photo(
            chat_id=patient_id,
            photo=last_msg.media_id,
            caption=header + (last_msg.text or ""),
            parse_mode="html",
            reply_markup=kbInline.kb_patient_peek_actions(consult_id, doctor_id)
        )
    elif last_msg.media_type == "document":
        await callback.message.delete()
        await bot.send_document(
            chat_id=patient_id,
            document=last_msg.media_id,
            caption=header + (last_msg.text or ""),
            parse_mode="html",
            reply_markup=kbInline.kb_patient_peek_actions(consult_id, doctor_id)
        )
    elif last_msg.media_type in ("mediaGroupPhoto", "mediaGroupDocument"):
        await callback.message.delete()
        parts = (last_msg.media_id or "").split(", ")
        if last_msg.media_type == "mediaGroupPhoto":
            media = [InputMediaPhoto(media=p) for p in parts]
            if last_msg.text or "":
                media[0].caption = header + last_msg.text
        else:
            media = [InputMediaDocument(media=p) for p in parts]
            if last_msg.text or "":
                media[-1].caption = header + last_msg.text

        messages = await bot.send_media_group(chat_id=patient_id, media=media)
        await bot.send_message(
            chat_id=patient_id,
            text="Действия:",
            reply_markup=kbInline.kb_patient_peek_actions(consult_id, doctor_id)
        )


@router.callback_query(F.data.startswith("replyDoctor_"))
async def callback_reply_doctor(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split("_")[1])
    patient_id = callback.from_user.id

    chat_type = await requestsBundle.get_chat_type(patient_id, doctor_id)
    if not chat_type:
        await callback.answer("Активной консультации не найдено.")
        return

    await requestsBundle.edit_is_open_dialog_patient(patient_id, doctor_id, True)

    await state.set_state(ChatPatient.openDialog)
    await state.update_data(doctor_id=doctor_id, chat_type=chat_type)

    await callback.message.answer(
        f"Вы открыли чат с доктором. Тип: {type_consultation[chat_type]}\nНапишите ваш ответ:",
        reply_markup=kbReply.kbPatientDialog
    )


@router.callback_query(F.data.startswith("viewConsult_"))
async def callback_view_consult(callback: CallbackQuery):
    patient_id = callback.from_user.id
    consult_id = int(callback.data.split("_")[1])

    messages = await requestsHistoryMessage.get_all_messages_by_consultation_id(consult_id)
    if not messages:
        await callback.answer("Переписка пуста.")
        return

    await callback.message.edit_text("<b>Переписка:</b>", parse_mode="html")

    for m in messages:
        if m.media_type == "text":
            await callback.message.answer(m.text, parse_mode="html")
        elif m.media_type == "photo":
            await callback.message.answer_photo(photo=m.media_id, caption=m.text or "", parse_mode="html")
        elif m.media_type == "document":
            await callback.message.answer_document(document=m.media_id, caption=m.text or "", parse_mode="html")
        elif m.media_type in ("mediaGroupPhoto", "mediaGroupDocument"):
            parts = (m.media_id or "").split(", ")
            if m.media_type == "mediaGroupPhoto":
                group = [InputMediaPhoto(media=p) for p in parts]
                if m.text or "":
                    group[0].caption = m.text
            else:
                group = [InputMediaDocument(media=p) for p in parts]
                if m.text or "":
                    group[-1].caption = m.text
            await callback.message.answer_media_group(media=group)

    if messages:
        doctor_id = messages[-1].doctor_id
    else:
        bundle = await requestsBundle.get_bundle(patient_id, doctor_id=None)
        doctor_id = bundle.doctor_id if bundle else 0

    await callback.message.answer(
        "Действия:",
        reply_markup=kbInline.kb_patient_consult_actions(consult_id, doctor_id)
    )


@router.callback_query(F.data.startswith("endConsult_"))
async def callback_end_consult(callback: CallbackQuery, state: FSMContext):
    _, consult_id, doctor_id = callback.data.split("_")
    doctor_id = int(doctor_id)
    patient_id = callback.from_user.id

    try:
        await requestsMessageToSend.delete_messages_to_send(doctor_id, patient_id)
    except:
        pass
    try:
        await requestsBundle.delete_bundle(patient_id, doctor_id)
    except:
        pass

    await state.clear()
    await callback.message.edit_text("Консультация завершена. Спасибо!")
