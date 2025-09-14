from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import requestsBundle, requestsDoctor
from config import type_consultation

regChooseGender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мужской', callback_data='regGender_male'),
     InlineKeyboardButton(text='Женский', callback_data='regGender_female')]
])


def kb_patient_new_msg(doctor_id: int, patient_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👀 Посмотреть", callback_data=f"seeMessage_{doctor_id}_{patient_id}")]
    ])


def kb_patient_peek_actions(consult_id: int, doctor_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Ответить", callback_data=f"replyDoctor_{doctor_id}")],
        [InlineKeyboardButton(text="🗂 Посмотреть консультацию", callback_data=f"viewConsult_{consult_id}")],
        [InlineKeyboardButton(text="⬅️ Закрыть", callback_data="closePeek")]
    ])


def kb_patient_consult_actions(consult_id: int, doctor_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Ответить", callback_data=f"replyDoctor_{doctor_id}")],
        [InlineKeyboardButton(text="✅ Завершить консультацию", callback_data=f"endConsult_{consult_id}_{doctor_id}")]
    ])


def notify_keyboard(doctor_id: int, patient_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👀 Посмотреть", callback_data=f"seeMessage_{doctor_id}_{patient_id}")]
    ])


def kb_doctor_reply_or_postpone(patient_id: int, consult_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Ответить", callback_data=f"doctorReply_{patient_id}_{consult_id}"),
                InlineKeyboardButton(text="Отложить консультацию",
                                     callback_data=f"doctorPostpone_{patient_id}_{consult_id}")
            ]
        ]
    )
    return kb


def kb_doctor_reply_or_view(patient_id: int, consult_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ответить",
                    callback_data=f"doctorReply_{patient_id}_{consult_id}"
                ),
                InlineKeyboardButton(
                    text="Посмотреть консультацию",
                    callback_data=f"doctorViewConsult_{patient_id}_{consult_id}"
                )
            ]
        ]
    )
    return kb


def kb_patient_conversation_nav(doctor_id: int, patient_id: int, page: int, total_pages: int) -> InlineKeyboardMarkup:
    prev_page = max(1, page - 1)
    next_page = min(total_pages, page + 1)
    buttons = []
    buttons.append([InlineKeyboardButton(text='⬅️', callback_data=f'convPatient_{doctor_id}_{patient_id}_{prev_page}'),
                    InlineKeyboardButton(text=f'{page} из {total_pages}', callback_data='tempButton'),
                    InlineKeyboardButton(text='➡️', callback_data=f'convPatient_{doctor_id}_{patient_id}_{next_page}')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def make_see_message_keyboard(doctor_id: int, patient_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"replyMessage_{doctor_id}_{patient_id}")],
        [InlineKeyboardButton(text="📂 Посмотреть консультацию",
                              callback_data=f"seeConsultation_{doctor_id}_{patient_id}")]
    ])


def make_consultation_keyboard(doctor_id: int, patient_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"replyMessage_{doctor_id}_{patient_id}")],
        [InlineKeyboardButton(text="✅ Завершить консультацию",
                              callback_data=f"endConsultation_{doctor_id}_{patient_id}")]
    ])


def see_message_keyboard(doctor_id: int, patient_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"replyMessage_{doctor_id}_{patient_id}")],
        [InlineKeyboardButton(text="📂 Посмотреть консультацию",
                              callback_data=f"seeConsultation_{doctor_id}_{patient_id}")]
    ])


def consultation_keyboard(doctor_id: int, patient_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"replyMessage_{doctor_id}_{patient_id}")],
        [InlineKeyboardButton(text="✅ Завершить консультацию",
                              callback_data=f"endConsultation_{doctor_id}_{patient_id}")]
    ])


async def getKeyboardCountryOrCity(place, callback):
    keyboard = InlineKeyboardBuilder()
    for i in range(len(place)):
        if i % 3 == 0:
            keyboard.row(InlineKeyboardButton(text=place[i].name, callback_data=callback + f'_{place[i].id}'))
        else:
            keyboard.add(InlineKeyboardButton(text=place[i].name, callback_data=callback + f'_{place[i].id}'))
    if callback.startswith('mailing'):
        keyboard.row(InlineKeyboardButton(text='Продолжить', callback_data=callback + 'Continue'))
    return keyboard.as_markup()


def listCrossToString(list, index):
    string = f'cross_{index}'
    for element in list:
        if element:
            string += '_yes'
        else:
            string += '_no'
    return string


def stringCrossToList(string):
    list = []
    for element in string.split('_'):
        if element == 'yes':
            list.append(True)
        else:
            list.append(False)
    return list


async def getKeyboardForContracts(list):
    keyboard = InlineKeyboardBuilder()
    for i in range(len(list)):
        if list[i]:
            keyboard.row(
                InlineKeyboardButton(text=f'{i + 1}. Даю согласие ✅', callback_data=listCrossToString(list, i)))
        else:
            keyboard.row(
                InlineKeyboardButton(text=f'{i + 1}. Даю согласие ❌', callback_data=listCrossToString(list, i)))

    return keyboard.as_markup()


def doctor_notify_keyboard(patient_id: int, consult_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👀 Посмотреть", callback_data=f"seePatientMessage_{patient_id}_{consult_id}")
    ]])


faqKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Срочно нужен врач! Что делать?', callback_data='faq_button_1')],
    [InlineKeyboardButton(text='Что важно знать?', callback_data='faq_button_2')],
    [InlineKeyboardButton(text='Как я могу помочь людям и/или проекту?', callback_data='faq_button_3')],
    [InlineKeyboardButton(text='Мои данные в безопасности?', callback_data='faq_button_4')],
    [InlineKeyboardButton(text='Как поддержать врача или проект?', callback_data='faq_button_5')],
    [InlineKeyboardButton(text='Как попасть на очный прием к врачу?', callback_data='faq_button_6')],
    [InlineKeyboardButton(text='Как связаться с поддержкой?', callback_data='faq_button_7')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToMenu')]
])

supportProject = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Поддержать проект', url='https://www.tbank.ru/cf/O75LoJrS1b')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToMenu')]
])


async def getKeyboardForFAQ(number):
    keyboard = InlineKeyboardBuilder()
    match number:
        case 1:
            keyboard.row(InlineKeyboardButton(text='Перейти в чат с врачами', url='https://t.me/FreeDocForEveryone'))
        case 5:
            keyboard.row(InlineKeyboardButton(text='Поддержать проект', url='https://www.tbank.ru/cf/O75LoJrS1b'))
        case 6:
            keyboard.row(InlineKeyboardButton(text='Записаться на очный прием', callback_data='makeAppointment'))
        case 7:
            keyboard.row(InlineKeyboardButton(text='Обратиться в поддержку', callback_data='connectAdminAppeal'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data='returnToFAQ'))
    return keyboard.as_markup()


continueOrNew = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продолжить', callback_data='continueConsultation')],
    [InlineKeyboardButton(text='Начать новую', callback_data='newConsultation')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToMenu')]
])


async def getKeyboardContinueConsultation(patient_id):
    keyboard = InlineKeyboardBuilder()
    bundles = await requestsBundle.get_bundles_by_patient_id(patient_id)
    for bundle in bundles:
        keyboard.row(InlineKeyboardButton(text=await requestsDoctor.get_full_name_by_user_id(bundle.doctor_id),
                                          callback_data=f'continueConsultation_{bundle.doctor_id}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data='returnToAskDoctor'))
    return keyboard.as_markup()


async def getKeyboardSpecialties(specialties, page, isAdd):
    keyboard = InlineKeyboardBuilder()
    totalList = specialties[page * 10:(page + 1) * 10]
    for i in range(len(totalList)):
        if i % 2 == 0:
            keyboard.row(
                InlineKeyboardButton(text=totalList[i].name, callback_data=f'specialty_{totalList[i].id}_{page}'))
        else:
            keyboard.add(
                InlineKeyboardButton(text=totalList[i].name, callback_data=f'specialty_{totalList[i].id}_{page}'))
    keyboard.row(InlineKeyboardButton(text='⬅️', callback_data=f'goBack_{page}'),
                 InlineKeyboardButton(
                     text=f'{page + 1} из {(len(specialties) // 10 + 1) if len(specialties) % 10 != 0 else (len(specialties) // 10)}',
                     callback_data='tempButton'),
                 InlineKeyboardButton(text='➡️', callback_data=f'goForward_{page}'))
    if isAdd:
        keyboard.row(InlineKeyboardButton(text='Готово', callback_data=f'acceptSpecialtiesPersonalAccount'))
    else:
        keyboard.row(InlineKeyboardButton(text='Назад', callback_data='returnToMenu'))
    return keyboard.as_markup()


async def getKeyboardDoctors(doctors, page, specialty):
    keyboard = InlineKeyboardBuilder()
    totalList = doctors[page * 5:(page + 1) * 5]
    for doctor in totalList:
        keyboard.row(InlineKeyboardButton(text=doctor.full_name, callback_data=f'doctor_{doctor.user_id}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='⬅️', callback_data=f'goBackDoctor_{page}_{specialty}'),
                 InlineKeyboardButton(
                     text=f'{page + 1} из {(len(doctors) // 5 + 1) if len(doctors) % 5 != 0 else (len(doctors) // 5)}',
                     callback_data='tempButton'),
                 InlineKeyboardButton(text='➡️', callback_data=f'goForwardDoctor_{page}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data='returnToAskDoctor'))
    return keyboard.as_markup()


editDoctors = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить', callback_data='addDoctor')],
    [InlineKeyboardButton(text='Удалить', callback_data='deleteDoctor')]
])

isFaceToFace = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yesIsFaceToFace')],
    [InlineKeyboardButton(text='Нет', callback_data='noIsFaceToFace')]
])

isInfoTrue = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Всё верно', callback_data='infoTrue')],
    [InlineKeyboardButton(text='Создать анкету заново', callback_data='infoEdit')],
    [InlineKeyboardButton(text='Удалить', callback_data='infoDelete')],
])


async def getKeyboardDoctorsInfo(page, index, doctors, specialty):
    keyboard = InlineKeyboardBuilder()
    match page:
        case 1:
            keyboard.row(InlineKeyboardButton(text='⬅️', callback_data=f'goBackDoctorInfo_{index}_{specialty}'),
                         InlineKeyboardButton(text=f'{index + 1} из {len(doctors)}', callback_data='tempButton'),
                         InlineKeyboardButton(text=f'➡️', callback_data=f'goForwardDoctorInfo_{index}_{specialty}'))
            keyboard.row(InlineKeyboardButton(text='Выбрать врача ✅',
                                              callback_data=f'acceptDoctor_{doctors[index].user_id}_{index}_{specialty}'))
            keyboard.row(InlineKeyboardButton(text='Резюме', callback_data=f'resume_{index}_{specialty}'),
                         InlineKeyboardButton(text='Отзывы',
                                              callback_data=f'openReviews_{doctors[index].user_id}_{index}_{specialty}_0'))
            keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'specialty_{specialty}_{page}'))
        case 2:
            pass
    return keyboard.as_markup()


async def getKeyboardResume(index, specialty, doctors):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Дипломы', callback_data=f'education_{index}_{specialty}'),
                 InlineKeyboardButton(text='В свободное время я...', callback_data=f'moreInfo_{index}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='Социальные сети', callback_data=f'socialNetworks_{index}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='Выбрать врача ✅',
                                      callback_data=f'acceptDoctor_{doctors[index].user_id}_{index}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'returnToDoctorInfo_{index}_{specialty}_-1'))
    return keyboard.as_markup()


async def getKeyboardReviews(doctor_id, index, specialty, index_review, all_pages):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='⬅️', callback_data=f'goBackReview_{doctor_id}_{index}_{specialty}_{index_review}'),
        InlineKeyboardButton(text=f'{index_review} из {all_pages}', callback_data='tempButton'),
        InlineKeyboardButton(text='➡️',
                             callback_data=f'goForwardReview_{doctor_id}_{index}_{specialty}_{index_review}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'returnToDoctorInfo_{index}_{specialty}_-1'))
    return keyboard.as_markup()


async def returnToDoctorInfo(index, specialty, id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'returnToDoctorInfo_{index}_{specialty}_{id}'))
    return keyboard.as_markup()


async def returnToResume(index, specialty, id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'resume_{index}_{specialty}_{id}'))
    return keyboard.as_markup()


async def returnToConsultations(doctor_id, index, id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'acceptDoctor_{doctor_id}_{index}_{id}'))
    return keyboard.as_markup()


async def getKeyboardConsultation(doctor_id, index, specialty, isInfo):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Правила консультаций',
                                      callback_data=f'infoAboutConsultation_{doctor_id}_{index}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='Просто спросить',
                                      callback_data=f'consultationJustAskOffer_{doctor_id}_{index}_{specialty}'),
                 InlineKeyboardButton(text='Расшифровка анализов',
                                      callback_data=f'consultationDecodingOffer_{doctor_id}_{index}_{specialty}')),
    keyboard.row(
        InlineKeyboardButton(text='Консультация ✅', callback_data=f'consultationMain_{doctor_id}_{index}_{specialty}'),
        InlineKeyboardButton(text='Экстренный случай 🆘', url='https://t.me/FreeDocForEveryone')),
    keyboard.row(InlineKeyboardButton(text='Второе мнение',
                                      callback_data=f'consultationSecondOpinionOffer_{doctor_id}_{index}_{specialty}'),
                 InlineKeyboardButton(text='Очный прием',
                                      callback_data=f'consultationFaceToFace_{doctor_id}_{index}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'returnToDoctorInfo_{index}_{specialty}'))
    return keyboard.as_markup()


async def getKeyboardOffer(doctor_id, index, id, chat_type):
    keyboard = InlineKeyboardBuilder()
    if chat_type in ['JustAsk', 'Decoding', 'SecondOpinion']:
        keyboard.row(
            InlineKeyboardButton(text='Соглашаюсь', callback_data=f'consultation{chat_type}_{doctor_id}_{index}_{id}'))
    elif chat_type == 'MainFirst':
        keyboard.row(
            InlineKeyboardButton(text='Соглашаюсь', callback_data=f'firstConsultation_{doctor_id}_{index}_{id}'))
    else:
        keyboard.row(
            InlineKeyboardButton(text='Соглашаюсь', callback_data=f'repeatedConsultation_{doctor_id}_{index}_{id}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'returnToAcceptDoctor_{doctor_id}_{index}_{id}'))
    return keyboard.as_markup()


async def getKeyboardFirstMessageSend(doctor_id, consultation, specialty, id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='Отправить', callback_data=f'send{consultation}_{doctor_id}_{id}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='Заполнить заново',
                                      callback_data=f'writeAgain{consultation}_{doctor_id}_{id}_{specialty}'))
    return keyboard.as_markup()


def consent_keyboard(state_data: dict) -> InlineKeyboardMarkup:
    license_mark = "✅" if state_data.get("license_accepted") else "☐"
    privacy_mark = "✅" if state_data.get("privacy_accepted") else "☐"
    personal_mark = "✅" if state_data.get("personal_accepted") else "☐"

    buttons = [
        [InlineKeyboardButton(text=f"{license_mark} Лицензионное соглашение", callback_data="toggle_license")],
        [InlineKeyboardButton(text=f"{privacy_mark} Политика конфиденциальности", callback_data="toggle_privacy")],
        [InlineKeyboardButton(text=f"{personal_mark} Согласие на обработку персональных данных",
                              callback_data="toggle_personal")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def getKeyboardFirstMessageSendTrueOrFalse(doctor_id, consultation, id, specialty):
    keyboard = InlineKeyboardBuilder()
    if consultation == 'JustAsk':
        keyboard.row(InlineKeyboardButton(text='Да', callback_data=f'send{consultation}_{doctor_id}_{id}_{specialty}'))
    else:
        keyboard.row(
            InlineKeyboardButton(text='Отправить', callback_data=f'send{consultation}_{doctor_id}_{id}_{specialty}'))
    keyboard.row(
        InlineKeyboardButton(text='Назад', callback_data=f'sendNotTrue_{consultation}_{doctor_id}_{id}_{specialty}'))
    return keyboard.as_markup()


async def getKeyboardLongSendMessage(doctor_id, chat_type, id, specialty):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='Начать', callback_data=f'longSendMessage_{doctor_id}_{chat_type}_{id}_{specialty}'))
    return keyboard.as_markup()


returnToMenu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='returnToMenu')]
])


async def getKeyboardAcceptPayment(user_id, doctor_id, consultation, id, specialty):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Подтвердить',
                                      callback_data=f'acceptPayment_{consultation}_{user_id}_{doctor_id}_{id}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='Отказать', callback_data=f'rejectPayment_{user_id}'))
    return keyboard.as_markup()


async def getKeyboardPatients(bundles):
    keyboard = InlineKeyboardBuilder()
    for bundle in bundles:
        keyboard.row(
            InlineKeyboardButton(text=str(bundle.patient_id), callback_data=f'dialogDoctor_{bundle.patient_id}'))
    return keyboard.as_markup()


async def getKeyboardFirstOrSecondConsultation(doctor_id, index, id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Первичная консультация',
                                      callback_data=f'consultationMainFirstOffer_{doctor_id}_{index}_{id}'))
    keyboard.row(InlineKeyboardButton(text='Повторная консультация',
                                      callback_data=f'consultationMainRepeatedOffer_{doctor_id}_{index}_{id}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'returnToAcceptDoctor_{doctor_id}_{index}_{id}'))
    return keyboard.as_markup()


async def getKeyboardFailedConsultation(doctor_id, specialty, chat_type):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Связаться с администратором',
                                      callback_data=f'failedConsultation_{doctor_id}_{specialty}_{chat_type}'))
    return keyboard.as_markup()


continueToEditPersonalAccount = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продолжить', callback_data='continueToEditPersonalAccount')]
])

personalAccountEdit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Правила и инструкции',
                          url='https://docs.google.com/document/d/1R15i4TFkP1x1Nu__-JCMmrOURf-luepC9GpcfXyZmvo/edit?tab=t.0#heading=h.mv6yaftne5ew')],
    [InlineKeyboardButton(text='Личная информация', callback_data='doctorPersonalInformation')],
    [InlineKeyboardButton(text='Профессиональная информация', callback_data='doctorProfessionalInformation')],
    [InlineKeyboardButton(text='Консультации', callback_data='doctorEditPrice')],
    [InlineKeyboardButton(text='Опубликовать', callback_data='publishPersonalAccount')],
])

acceptAndSendPersonalAccount = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить на проверку', callback_data='acceptAndSendPersonalAccount')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToDoctorMenu')]
])

personalInformation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ФИО', callback_data='doctorEditFullName'),
     InlineKeyboardButton(text='Фото', callback_data='doctorEditPhoto')],
    [InlineKeyboardButton(text='Страна', callback_data='doctorEditCountry'),
     InlineKeyboardButton(text='Город', callback_data='doctorEditCity')],
    [InlineKeyboardButton(text='О себе', callback_data='doctorEditAboutMe'),
     InlineKeyboardButton(text='Банковские реквизиты', callback_data='doctorEditBankDetails')],
    [InlineKeyboardButton(text='Социальные сети', callback_data='doctorEditSocialNetworks')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToDoctorMenu')]
])

isSocialNetworks = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yesSocialNetworks')],
    [InlineKeyboardButton(text='Нет', callback_data='doctorPersonalInformation')],
    [InlineKeyboardButton(text='Назад', callback_data='doctorPersonalInformation')]
])

socialNetworks = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Telegram', callback_data='doctorEditSocialNetworksTelegram')],
    [InlineKeyboardButton(text='Instagram', callback_data='doctorEditSocialNetworksInstagram')],
    [InlineKeyboardButton(text='Назад', callback_data='doctorPersonalInformation')]
])

professionalInformation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Специальность', callback_data='doctorEditSpecialty'),
     InlineKeyboardButton(text='Опыт работы', callback_data='doctorEditWorkExperience')],
    [InlineKeyboardButton(text='Образование', callback_data='doctorEditEducationData'),
     InlineKeyboardButton(text='Документы об образовании', callback_data='doctorEditEducation')],
    [InlineKeyboardButton(text='Резюме', callback_data='doctorEditResume'),
     InlineKeyboardButton(text='Достижения', callback_data='doctorEditAchievements')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToDoctorMenu')]
])

bankDetails = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='МИР', callback_data='doctorEditBankDetailsRussia'),
     InlineKeyboardButton(text='VISA / MASTERCARD', callback_data='doctorEditBankDetailsAbroad')],
    [InlineKeyboardButton(text='Назад', callback_data='doctorPersonalInformation')]
])

consultationEdit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Просто спросить', callback_data='doctorEditPriceJustAsk'),
     InlineKeyboardButton(text='Расшифровка анализов', callback_data='doctorEditPriceDecoding')],
    [InlineKeyboardButton(text='Первичная консультация', callback_data='doctorEditPriceMainFirst'),
     InlineKeyboardButton(text='Повторная консультация', callback_data='doctorEditPriceMainRepeated')],
    [InlineKeyboardButton(text='Второе мнение', callback_data='doctorEditSecondOpinion'),
     InlineKeyboardButton(text='Очный прием', callback_data='doctorEditFaceToFace')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToDoctorMenu')]
])

secondOpinionCommands = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Это про меня', callback_data='doctorEditPriceSecondOpinion')],
    [InlineKeyboardButton(text='Не про меня', callback_data='doctorNotEditSecondOpinion')]
])

returnToPersonalInformation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='doctorPersonalInformation')]
])

returnToSocialNetworks = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='doctorEditSocialNetworks')]
])

returnToBankDetails = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='doctorEditBankDetails')]
])

returnToProfessionalInformation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='doctorProfessionalInformation')]
])

returnToConsultationEdit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='doctorEditPrice')]
])


async def getKeyboardConsultationEdit(type):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Платно', callback_data=f'doctorEditPricePaid_{type}'),
                 InlineKeyboardButton(text='Бесплатно', callback_data=f'doctorEditPriceFree_{type}'))
    return keyboard.as_markup()


returnToDoctorMenu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='returnToDoctorMenu')]
])

yesOrNoCMI = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yesCMI'), InlineKeyboardButton(text='Нет', callback_data='noCMI')],
    [InlineKeyboardButton(text='Назад', callback_data='doctorEditPrice')]
])


async def acceptPersonalAccount(user_id, ids):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='Загрузить новое фото', callback_data=f'newPhotoPersonalAccount_{user_id}_{ids}'))
    keyboard.row(InlineKeyboardButton(text='Загрузить документы об образовании',
                                      callback_data=f'newEducationPersonalAccount_{user_id}_{ids}'))
    keyboard.row(InlineKeyboardButton(text='Принять', callback_data=f'acceptPersonalAccount_{user_id}'))
    keyboard.row(InlineKeyboardButton(text='Отказать', callback_data=f'rejectPersonalAccount_{user_id}'))
    return keyboard.as_markup()


async def leaveReview(doctor_id, chat_type):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Оценить врача', callback_data=f'leaveReview_{doctor_id}_{chat_type}'))
    return keyboard.as_markup()


notLeaveReview = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оставить отзыв', callback_data='leaveReview')],
    [InlineKeyboardButton(text='Не оставлять отзыв', callback_data='notLeaveReview')]
])


async def keyboardStars(doctor_id, number_of_review, chat_type):
    keyboard = InlineKeyboardBuilder()
    stars = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    for i in range(5):
        keyboard.add(InlineKeyboardButton(text=stars[i],
                                          callback_data=f'star_{i + 1}_{doctor_id}_{number_of_review}_{chat_type}'))
    return keyboard.as_markup()


cooperationCommand = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Для врачей', callback_data='forDoctors')],
    [InlineKeyboardButton(text='Представляю проект/организацию', callback_data='representProject')],
    [InlineKeyboardButton(text='Я пациент и хочу помочь', callback_data='helpPatient')],
    [InlineKeyboardButton(text='Связаться с администратором', callback_data='connectAdmin')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToMenu')]
])

supportProjectCooperation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Поддержать проект', url='https://www.tbank.ru/cf/O75LoJrS1b')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToCooperation')]
])


async def getKeyboardAnswerConnectAdmin(patient_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Ответить', callback_data=f'answerConnectAdmin_{patient_id}'))
    return keyboard.as_markup()


answerConnectAdmin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ответить', callback_data='answerConnectAdmin')],
    [InlineKeyboardButton(text='Завершить', callback_data='returnToMenu')]
])

submitRequest1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Узнать подробнее о проекте', callback_data='learnMoreAboutProject')],
    [InlineKeyboardButton(text='Преимущества участия в сообществе', callback_data='advantagesOfParticipation')],
    [InlineKeyboardButton(text='Подать заявку ✅', callback_data='submitRequest1')],
    [InlineKeyboardButton(text='Связаться с администратором', callback_data='connectAdmin')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToCooperation')]
])

learnMoreAboutProjectKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Преимущества участия в сообществе', callback_data='advantagesOfParticipation')],
    [InlineKeyboardButton(text='Назад', callback_data='forDoctors')]
])

advantagesOfParticipationKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подать заявку ✅', callback_data='submitRequest1')],
    [InlineKeyboardButton(text='Назад', callback_data='forDoctors')]
])

returnToCooperation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='returnToCooperation')]
])

returnToForDoctors = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='forDoctors')]
])

returnToFAQ = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='returnToFAQ')]
])

submitRequest2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтверждаю', callback_data='submitRequest2')]
])

specialtiesCommand = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить', callback_data='addSpecialty')]
])

returnToAdminMenu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='returnToAdminMenu')]
])


async def getKeyboardSee(patient_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Посмотреть', callback_data=f'seeNewConsultation_{patient_id}'))
    return keyboard.as_markup()


async def getKeyboardStartOrBack(patient_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Начать', callback_data=f'startNewConsultation_{patient_id}'))
    keyboard.row(InlineKeyboardButton(text='Ответить позже', callback_data=f'backNewConsultation_{patient_id}'))
    return keyboard.as_markup()


endConsultation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data=f'endConsultation')],
    [InlineKeyboardButton(text='Назад', callback_data='endNotConsultation')]
])


async def sendOrDelete(message_id, user_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Отправить', callback_data=f'sendMessage_{message_id}_{user_id}'))
    keyboard.row(InlineKeyboardButton(text='Удалить', callback_data='deleteMessage'))
    return keyboard.as_markup()


aboutUs = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Чат с врачами - экстренный случай', url='https://t.me/+HM3oO_s3kCkyMGJi')],
    [InlineKeyboardButton(text='Telegram-канал', url='https://t.me/+2jKuYkBQPO8xODFi'),
     InlineKeyboardButton(text='Instagram', url='https://www.instagram.com/docforeveryone')],
    [InlineKeyboardButton(text='Международный чат', url='https://t.me/+c2E9Vtiw155iNzgy'),
     InlineKeyboardButton(text='Российский чат', url='https://t.me/+egwFXps4_38zZDIy')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToMenu')]
])

typesHistoryConsultation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Активные', callback_data='ongoingConsultations')],
    [InlineKeyboardButton(text='Завершенные', callback_data='completedConsultations')],
    [InlineKeyboardButton(text='Назад', callback_data='returnToMenu')]
])


async def getKeyboardRepeatedConsultations(consultations, isRepeated, doctor_id, index, id):
    keyboard = InlineKeyboardBuilder()
    for consultation in consultations:
        keyboard.row(InlineKeyboardButton(text=f'{consultation.name}',
                                          callback_data=f'completedConsultation_{consultation.id}_{isRepeated}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'consultationMain_{doctor_id}_{index}_{id}'))
    return keyboard.as_markup()


async def getKeyboardCompletedConsultations(consultations, isRepeated):
    keyboard = InlineKeyboardBuilder()
    for consultation in consultations:
        name = await requestsDoctor.get_full_name_by_user_id(consultation.doctor_id)
        keyboard.row(InlineKeyboardButton(text=f'{name} - {type_consultation[consultation.chat_type]}',
                                          callback_data=f'completedConsultation_{consultation.id}_{isRepeated}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data='completedConsultations'))
    return keyboard.as_markup()


async def getKeyboardActionsCompletedConsultation(doctor_id, chat_type, id_consultation, isRepeated, index, specialty):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Продолжить эту консультацию',
                                      callback_data=f'isStartAgain_{id_consultation}_{isRepeated}'))
    keyboard.row(
        InlineKeyboardButton(text='Задать новый вопрос', callback_data=f'acceptDoctor_{doctor_id}_{index}_{specialty}'))
    keyboard.row(InlineKeyboardButton(text='Прочитать',
                                      callback_data=f'readCompletedConsultation_{id_consultation}_{doctor_id}_{chat_type}_{isRepeated}'))
    return keyboard.as_markup()


async def getKeyboardStartAgainOrReturn(doctor_id, chat_type, isRepeated, specialty, id_consultation, index):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Продолжить эту консультацию',
                                      callback_data=f'startAgainCompletedConsultation_{doctor_id}_{chat_type}_{specialty}_{id_consultation}'))
    keyboard.row(
        InlineKeyboardButton(text='Задать новый вопрос', callback_data=f'acceptDoctor_{doctor_id}_{index}_{specialty}'))
    if isRepeated:
        keyboard.row(
            InlineKeyboardButton(text='Назад', callback_data=f'returnToHistoryRepeatedConsultations_{doctor_id}'))
    else:
        keyboard.row(InlineKeyboardButton(text='Назад', callback_data='returnToHistoryCompletedConsultations'))
    return keyboard.as_markup()


whatsEditPhotoAndFile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Стартовое изображение', callback_data='editPhotoStart')]
])


async def getKeyboardSupportDoctor(doctor_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Отблагодарить врача', callback_data=f'supportDoctor_{doctor_id}'))
    keyboard.row(InlineKeyboardButton(text='Поддержать проект', url='https://www.tbank.ru/cf/O75LoJrS1b'))
    keyboard.row(InlineKeyboardButton(text='Завершить', callback_data='lastMessageReview'))
    return keyboard.as_markup()


async def returnToSupportDoctor(doctor_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'returnToSupportDoctor_{doctor_id}'))
    return keyboard.as_markup()


statisticsParameters = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Тип консультаций', callback_data='statisticsTypeConsultations')],
    [InlineKeyboardButton(text='Специальность', callback_data='statisticsSpecialty')]
])


async def statisticsPeople(parameter):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Все пользователи', callback_data=f'statisticsAll_{parameter}'))
    keyboard.row(InlineKeyboardButton(text='Конкретный врач', callback_data=f'statisticsOneDoctor_{parameter}'))
    return keyboard.as_markup()


chatWithDoctors = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Закрытый чат врачей', url='https://t.me/+CJlRD6f0gzA3Yzcy')]
])

makeAppointment = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yesMyCity')],
    [InlineKeyboardButton(text='Нет, выбрать другой', callback_data='noMyCity')]
])


async def getKeyboardAllDoctors(doctors, callback):
    keyboard = InlineKeyboardBuilder()
    for doctor in doctors:
        keyboard.row(InlineKeyboardButton(text=doctor.full_name, callback_data=callback + f'_{doctor.user_id}'))
    if callback == 'feedbackAdmin':
        keyboard.row(InlineKeyboardButton(text='Назад', callback_data='returnToAdminMenu'))
    return keyboard.as_markup()


async def getKeyboardFeedbackAdmin(index, length, id, doctor_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='⬅️', callback_data=f'goBackFeedbackAdmin_{index}_{doctor_id}'),
                 InlineKeyboardButton(text=f'{index + 1} из {length}', callback_data='tempButton'),
                 InlineKeyboardButton(text='➡️', callback_data=f'goForwardFeedbackAdmin_{index}_{doctor_id}'))
    if id != -1:
        keyboard.row(InlineKeyboardButton(text='Удалить', callback_data=f'deleteReview_{id}_{index}_{doctor_id}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'returnToFeedbackAdmin'))
    return keyboard.as_markup()


async def getKeyboardDeleteReview(index, id, doctor_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Да, удалить', callback_data=f'yesDeleteReview_{id}_{index}_{doctor_id}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'noDeleteReview_{index}_{doctor_id}'))
    return keyboard.as_markup()


mailingCommand = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Всем пользователям', callback_data='mailingAllUsers')],
    [InlineKeyboardButton(text='Отдельным странам', callback_data='mailingCountries')],
    [InlineKeyboardButton(text='Отдельным городам', callback_data='mailingCities')]
])

addButtonToMailinMessage = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить', callback_data='mailingAddButton')],
    [InlineKeyboardButton(text='Не добавлять', callback_data='mailingNotAddButton')]
])


async def getKeyboardMailingButton(text, url):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=text, url=url))
    return keyboard.as_markup()


mailingSend = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить', callback_data='mailingSend')],
    [InlineKeyboardButton(text='В главное меню', callback_data='returnToAdminMenu')]
])

closeDialogPatient = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Свернуть', callback_data='yesCloseDialogPatient')],
    [InlineKeyboardButton(text='Назад', callback_data='notCloseDialogPatient')]
])

closeDialogDoctor = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отложить консультацию', callback_data='yesCloseDialogDoctor')],
    [InlineKeyboardButton(text='Вернуться', callback_data='notCloseDialogDoctor')]
])

whatsEditLastMessage = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Завершение отзыва', callback_data='editTextLastMessageReview')],
    [InlineKeyboardButton(text='Перед консультацией', callback_data='editTextLastMessageBeforeConsultations')]
])


# --- Уровень 1: специальности ---
async def getKeyboardSpecialtiesHistory(specialties: list) -> InlineKeyboardMarkup:
    keyboard_buttons = [
        [InlineKeyboardButton(text=spec.name, callback_data=f"historySpecialty_{spec.id}")]
        for spec in specialties
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


# --- Уровень 2: врачи ---
async def getKeyboardDoctorsHistory(doctors: list, specialty_id: int) -> InlineKeyboardMarkup:
    keyboard_buttons = [
        [InlineKeyboardButton(text=doc.full_name, callback_data=f"historyDoctor_{specialty_id}_{doc.user_id}")]
        for doc in doctors
    ]
    keyboard_buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="returnToHistorySpecialties")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


# --- Уровень 3: консультации ---
async def getKeyboardConsultationsHistory(consultations: list) -> InlineKeyboardMarkup:
    keyboard_buttons = []
    for c in consultations:
        text = f"🔄 {c.name}" if c.chat_type in ["mainFirst", "mainRepeated"] else c.name
        keyboard_buttons.append([InlineKeyboardButton(text=text, callback_data=f"historyConsultation_{c.id}")])
    keyboard_buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="returnToHistoryDoctors")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


# --- Кнопки действий на уровне консультации ---
async def getKeyboardConsultationActions(consultation_id: int, doctor_id: int, chat_type: str) -> InlineKeyboardMarkup:
    keyboard_buttons = []
    if chat_type in ["mainFirst", "mainRepeated"]:
        keyboard_buttons.append([InlineKeyboardButton(text="🔄 Продолжить эту консультацию",
                                                      callback_data=f"startAgainConsultation_{consultation_id}")])
    keyboard_buttons.append(
        [InlineKeyboardButton(text="✉ Задать новый вопрос", callback_data=f"newQuestion_{doctor_id}")])
    keyboard_buttons.append(
        [InlineKeyboardButton(text="⬅ Назад", callback_data=f"returnToHistoryConsultations_{doctor_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


# --- Кнопки выбора между завершенными и текущими консультациями ---
async def typesHistoryConsultation() -> InlineKeyboardMarkup:
    keyboard_buttons = [
        [InlineKeyboardButton(text="Текущие", callback_data="ongoingConsultations"),
         InlineKeyboardButton(text="Завершенные", callback_data="completedConsultations")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
