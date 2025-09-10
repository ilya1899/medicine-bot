from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.database.requests import requestsHistoryMessage

router = Router()

from app.businessLogic import logicConsultation
from app.businessLogic.logicConsultation import AttachFile, ChatPatient, Payment, FailedConsultation


@router.message(F.text == 'Задать вопрос врачу')
async def message_askDoctor(message: Message):
    await logicConsultation.askDoctorMessage(message)


@router.callback_query(F.data == 'returnToAskDoctor')
async def callback_continueOrNew(callback: CallbackQuery):
    await logicConsultation.askDoctorCallback(callback)


@router.callback_query(F.data == 'newConsultation')
async def callback_newConsultation(callback: CallbackQuery):
    await logicConsultation.newConsultation(callback)


@router.callback_query(F.data == 'continueConsultation')
async def callback_continueConsultation(callback: CallbackQuery):
    await logicConsultation.continueConsultation(callback)


@router.callback_query(F.data.startswith('continueConsultation_'))
async def callback_continueConsultationDoctor(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.continueConsultationDoctor(callback, state)


@router.callback_query(F.data.startswith('goBack_'))
async def callback_goBack(callback: CallbackQuery):
    await logicConsultation.goBack(callback)


@router.callback_query(F.data.startswith('goForward_'))
async def callback_goBack(callback: CallbackQuery):
    await logicConsultation.goForward(callback)


@router.callback_query(F.data.startswith('specialty_'))
async def callback_specialty(callback: CallbackQuery):
    await logicConsultation.specialty(callback)


@router.callback_query(F.data.startswith('goBackDoctor_'))
async def callback_goBackDoctor(callback: CallbackQuery):
    await logicConsultation.goBackDoctor(callback)


@router.callback_query(F.data.startswith('goForwardDoctor_'))
async def callback_goForwardDoctor(callback: CallbackQuery):
    await logicConsultation.goForwardDoctor(callback)


@router.callback_query(F.data.startswith('doctor_'))
async def callback_openDoctorInfo(callback: CallbackQuery):
    await logicConsultation.openDoctorInfo(callback)


@router.callback_query(F.data.startswith('goBackDoctorInfo_'))
async def callback_goBackDoctorInfo(callback: CallbackQuery):
    await logicConsultation.goBackDoctorInfo(callback)


@router.callback_query(F.data.startswith('goForwardDoctorInfo_'))
async def callback_goForwardDoctorInfo(callback: CallbackQuery):
    await logicConsultation.goForwardDoctorInfo(callback)


@router.callback_query(F.data.startswith('moreInfo_'))
async def callback_moreInfo(callback: CallbackQuery):
    await logicConsultation.moreInfo(callback)


@router.callback_query(F.data.startswith('resume_'))
async def callback_resume(callback: CallbackQuery):
    await logicConsultation.resume(callback)


@router.callback_query(F.data.startswith('education_'))
async def callback_education(callback: CallbackQuery):
    await logicConsultation.education(callback)


@router.callback_query(F.data.startswith('socialNetworks_'))
async def callback_socialNetworks(callback: CallbackQuery):
    await logicConsultation.socialNetworks(callback)


@router.callback_query(F.data.startswith('openReviews_'))
async def callback_openReviews(callback: CallbackQuery):
    await logicConsultation.openReviews(callback)


@router.callback_query(F.data.startswith('goBackReview_'))
async def callback_openReviews(callback: CallbackQuery):
    await logicConsultation.goBackReview(callback)


@router.callback_query(F.data.startswith('goForwardReview_'))
async def callback_openReviews(callback: CallbackQuery):
    await logicConsultation.goForwardReview(callback)


@router.callback_query(F.data.startswith('returnToDoctorInfo_'))
async def callback_returnToDoctorInfo(callback: CallbackQuery):
    await logicConsultation.returnToDoctorInfo(callback)


@router.callback_query(F.data.startswith('returnToAcceptDoctor_'))
async def callback_returnToAcceptDoctor(callback: CallbackQuery):
    await logicConsultation.acceptDoctor(callback)


@router.callback_query(F.data.startswith('acceptDoctor_'))
async def callback_acceptDoctor(callback: CallbackQuery):
    await logicConsultation.acceptDoctor(callback)


@router.callback_query(F.data.startswith('infoAboutConsultation_'))
async def callback_infoAboutConsultation(callback: CallbackQuery):
    await logicConsultation.infoAboutConsultation(callback)


@router.message(Payment.receipt)
async def callback_truePayment(message: Message, state: FSMContext):
    await logicConsultation.consultationTruePayment(message, state)


@router.callback_query(F.data.startswith('acceptPayment_'))
async def callback_acceptPayment(callback: CallbackQuery):
    await logicConsultation.consultationAcceptPayment(callback)


@router.callback_query(F.data.startswith('rejectPayment_'))
async def callback_rejectPayment(callback: CallbackQuery):
    await logicConsultation.consultationRejectPayment(callback)


# @router.callback_query(F.data.startswith('longSendMessage_'))
# async def callback_longSendMessage(callback: CallbackQuery, state: FSMContext):
#     await logicConsultation.consultationLongSendMessage(callback, state)

# @router.callback_query(F.data.startswith('sendNotTrue_'))
# async def callback_sendNotTrue(callback: CallbackQuery):
#     await logicConsultation.isSendFirstMessage(callback)


@router.callback_query(F.data.startswith('failedConsultation_'))
async def callback_failedConsultation(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.failedConsultation(callback, state)


@router.message(FailedConsultation.text)
async def message_failedConsultatation(message: Message, state: FSMContext):
    await logicConsultation.failedConsultatationMessage(message, state)


@router.callback_query(F.data.startswith('consultationJustAsk_'))
async def callback_consultationJustAsk(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationJustAsk(callback, state)


@router.callback_query(F.data.startswith('consultationJustAskOffer_'))
async def callback_consultationJustAsk(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationJustAskOffer(callback, state)


@router.message(AttachFile.justAsk_name)
async def message_consultationJustAskName(message: Message, state: FSMContext):
    await logicConsultation.consultationJustAskName(message, state)


@router.message(AttachFile.photoJustAsk)
async def message_attachFileJustAskPhoto(message: Message, state: FSMContext):
    await logicConsultation.getDataForAttachFile(message, state, 'JustAsk')


@router.callback_query(F.data.startswith('sendJustAsk_'))
async def callback_sendJustAsk(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.sendFirstMessage(callback, 'justAsk', state)


@router.callback_query(F.data.startswith('writeAgainJustAsk_'))
async def callback_writeAgainJustAsk(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.writeAgainJustAsk(callback, state)


@router.callback_query(F.data.startswith('consultationDecoding_'))
async def callback_consultatioDecoding(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationDecoding(callback, state)


@router.callback_query(F.data.startswith('consultationDecodingOffer_'))
async def callback_consultatioDecodingOffer(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationDecodingOffer(callback, state)


@router.message(AttachFile.decoding_name)
async def message_consultationDecondingName(message: Message, state: FSMContext):
    await logicConsultation.consultationDecodingName(message, state)


@router.message(AttachFile.photoDecoding)
async def message_attachFileDecodingPhoto(message: Message, state: FSMContext):
    await logicConsultation.getDataForAttachFile(message, state, 'Decoding')


@router.callback_query(F.data.startswith('sendDecoding_'))
async def callback_sendDecoding(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.sendFirstMessage(callback, 'decoding', state)


@router.callback_query(F.data.startswith('writeAgainDecoding_'))
async def callback_writeAgainDecoding(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.writeAgainDecoding(callback, state)


@router.callback_query(F.data.startswith('consultationMain_'))
async def callback_consultationMain(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationMain(callback, state)


@router.callback_query(F.data.startswith('consultationMainFirstOffer_'))
async def callback_consultationMainFirstOffer(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationMainFirstOffer(callback, state)


@router.callback_query(F.data.startswith('firstConsultation_'))
async def callback_firstConsulationName(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.firstConsultationName(callback, state)


@router.message(AttachFile.main_first_name)
async def message_firstConsultation(message: Message, state: FSMContext):
    await logicConsultation.firstConsultation(message, state)


@router.message(AttachFile.main_first)
async def message_textConsultationMain(message: Message, state: FSMContext):
    await logicConsultation.getDataForAttachFile(message, state, 'MainFirst')


@router.callback_query(F.data.startswith('sendMainFirst_'))
async def callback_sendMainFirst(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.sendFirstMessage(callback, 'mainFirst', state)


@router.callback_query(F.data.startswith('writeAgainMainFirst_'))
async def callback_writeAgainMainFirst(callback: CallbackQuery):
    await logicConsultation.writeAgainFirstConsultation(callback)


@router.callback_query(F.data.startswith('repeatedConsultation_'))
async def callback_repeatedConsulation(callback: CallbackQuery):
    await logicConsultation.repeatedConsultation(callback)


@router.callback_query(F.data.startswith('consultationMainRepeatedOffer_'))
async def callback_consultationMainRepeatedOffer(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationMainRepeatedOffer(callback, state)


@router.message(AttachFile.main_repeated)
async def message_textConsultationMain(message: Message, state: FSMContext):
    await logicConsultation.getDataForAttachFile(message, state, 'MainRepeated')


@router.callback_query(F.data.startswith('sendMainRepeated_'))
async def callback_sendMainRepeated(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.sendFirstMessage(callback, 'mainRepeated', state)


@router.callback_query(F.data.startswith('writeAgainMainRepeated_'))
async def callback_writeAgainMainRepeated(callback: CallbackQuery):
    await logicConsultation.writeAgainRepeatedConsultation(callback)


@router.callback_query(F.data.startswith('returnToHistoryRepeatedConsultations_'))
async def callback_returnToHistoryRepeatedConsultations(callback: CallbackQuery):
    await logicConsultation.repeatedConsultation(callback)


@router.callback_query(F.data.startswith('consultationSecondOpinion_'))
async def callback_consultationSecondOpinion(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationSecondOpinion(callback, state)


@router.callback_query(F.data.startswith('consultationSecondOpinionOffer_'))
async def callback_consultationSecondOpinionOffer(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationSecondOpinionOffer(callback, state)


@router.message(AttachFile.secondOpinion_name)
async def message_consultationDecondingName(message: Message, state: FSMContext):
    await logicConsultation.consultationSecondOpinionName(message, state)


@router.message(AttachFile.secondOpinion)
async def message_attachFileSecondOpinion(message: Message, state: FSMContext):
    await logicConsultation.consultationSecondOpinionLink1(message, state)


@router.message(AttachFile.secondOpinion_link)
async def message_consultationSecondOpinionLink(message: Message, state: FSMContext):
    await logicConsultation.consultationSecondOpinionLink2(message, state)


@router.callback_query(F.data.startswith('sendSecondOpinion_'))
async def callback_sendSecondOpinion(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.sendFirstMessage(callback, 'secondOpinion', state)


@router.callback_query(F.data.startswith('writeAgainSecondOpinion_'))
async def callback_writeAgainSecondOpinion(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.writeAgainSecondOpinion(callback, state)


@router.callback_query(F.data.startswith('consultationFaceToFace_'))
async def callback_consultationFaceToFace(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.consultationFaceToFace(callback, state)


@router.callback_query(F.data.startswith('returnToMenu_'))
async def callback_returnToMenu(callback: CallbackQuery):
    await logicConsultation.returnToMenu(callback)


@router.message(F.text == 'Завершить консультацию', ChatPatient.openDialog)
async def message_endDialogPatient(message: Message):
    await logicConsultation.endDialogPatient(message)


@router.callback_query(F.data == 'endConsultation', ChatPatient.openDialog)
async def callback_endConsultation(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.endConsultation(callback, state)


@router.callback_query(F.data == 'endNotConsultation', ChatPatient.openDialog)
async def callback_endNotConsultation(callback: CallbackQuery):
    await logicConsultation.endNotConsultation(callback)


@router.message(F.text == 'Свернуть диалог', ChatPatient.openDialog)
async def message_closeDialogPatient(message: Message):
    await logicConsultation.closeDialogPatient(message)


@router.callback_query(F.data == 'yesCloseDialogPatient', ChatPatient.openDialog)
async def callback_yesCloseDialog(callback: CallbackQuery, state: FSMContext):
    await logicConsultation.yesCloseDialogPatient(callback, state)


@router.callback_query(F.data == 'notCloseDialogPatient', ChatPatient.openDialog)
async def callback_notCloseDialog(callback: CallbackQuery):
    await logicConsultation.notCloseDialog(callback)


@router.callback_query(F.data == 'deleteMessage', ChatPatient.openDialog)
async def callback_deleteMessage(callback: CallbackQuery):
    await logicConsultation.deleteMessage(callback)


@router.callback_query(F.data.startswith('sendMessage'), ChatPatient.openDialog)
async def callback_sendMessage(callback: CallbackQuery):
    await logicConsultation.sendMessage(callback)


@router.message(ChatPatient.openDialog)
async def message_openDialogPatient(message: Message, state: FSMContext):
    await logicConsultation.openDialogPatient(message, state)

@router.callback_query(F.data.startswith("seePatientMessage_"))
async def callback_see_patient_message(callback: CallbackQuery):
    _, patient_id, consult_id = callback.data.split("_")
    await logicConsultation.show_patient_message(callback, int(patient_id), int(consult_id))


@router.callback_query(F.data.startswith('convPatient_'))
async def callback_conv_patient(callback: CallbackQuery):
    _, doctor_id, patient_id, page = callback.data.split('_')
    doctor_id = int(doctor_id)
    patient_id = int(patient_id)
    page = int(page)
    await logicConsultation.show_patient_conversation_paginated(callback.message, doctor_id, patient_id, page)
