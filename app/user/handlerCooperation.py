import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from app.database.models import Doctor
from app.keyboards.kbInline import consent_keyboard, submitRequest1
from run import bot

router = Router()


class Request(StatesGroup):
    full_name = State()
    country = State()
    city = State()
    telegram = State()


class Connect(StatesGroup):
    help_patient = State()
    admin = State()
    answer_admin = State()
    represent = State()
    answer_represent = State()
    appeal = State()
    answer_appeal = State()
    answer_connect_admin = State()


photosToSend = []
lock = asyncio.Lock()

from app.keyboards import kbInline, kbReply
from app.database.requests import requestsDoctor
from config import admin_group_id


@router.message(F.text == 'Сотрудничество')
async def message_cooperation(message: Message):
    await message.answer('Выберите необходимый раздел', reply_markup=kbInline.cooperationCommand)


@router.callback_query(F.data == 'returnToCooperation')
async def callback_returnToCooperation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Выберите необходимый раздел', reply_markup=kbInline.cooperationCommand)


@router.callback_query(F.data == 'forDoctors')
async def callback_forDoctors(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('''Преимущества участия в сообществе

💙 Меняйте жизни к лучшему
Ваша помощь напрямую влияет на здоровье и благополучие людей.

💸 Зарабатывайте удаленно
Получайте дополнительный доход, консультируя онлайн в удобное время.

🤙🏻 Продвигайте свои услуги без вложений
Расширяйте клиентскую базу и повышайте свою репутацию.

📈 Увеличивайте поток пациентов
Привлекайте людей на очные консультации через доверие к сообществу.

📱 Растите аудиторию в соцсетях
Рекламируйте свои профессиональные профили среди целевой аудитории.

🤝 Расширяйте профессиональные связи
Знакомьтесь с коллегами, обменивайтесь опытом и находите партнёров.

🧠 Повышение квалификации и навыков
Получайте поддержку, советы и доступ к уникальным материалам от экспертов.

🌱 Раскройте свой потенциал
Реализуйте амбиции в медицине и создавайте значимые проекты.
''', reply_markup=submitRequest1)
    await state.clear()


@router.callback_query(F.data == "submitRequest1")
async def callback_submitRequest1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(license_accepted=False, privacy_accepted=False, personal_accepted=False)

    message_text = (
        '📋 <b>Для подачи заявки необходимо согласиться со всеми документами:</b>\n\n'

        '• <a href="https://docs.google.com/document/d/1_9szCZrkTcqGgQtlt72eS5-qpspIjVu-Q9EUmXhxiu4/edit?tab=t.0">'
        'Лицензионное соглашение</a>\n'

        '• <a href="https://docs.google.com/document/d/1_9szCZrkTcqGgQtlt72eS5-qpspIjVu-Q9EUmXhxiu4/edit?tab=t.0">'
        'Политика конфиденциальности</a>\n'

        '• <a href="https://docs.google.com/document/d/1_9szCZrkTcqGgQtlt72eS5-qpspIjVu-Q9EUmXhxiu4/edit?tab=t.0">'
        'Согласие на обработку персональных данных</a>\n\n'

        '📖 <i>Нажмите на ссылки чтобы открыть документы для чтения</i>\n'
        '✅ <i>После прочтения поставьте галочки согласия</i>'
    )

    await callback.message.edit_text(
        message_text,
        reply_markup=consent_keyboard({}),
        parse_mode='HTML',
        disable_web_page_preview=True
    )


@router.callback_query(F.data.startswith("toggle_"))
async def callback_toggleConsent(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data.setdefault("license_accepted", False)
    data.setdefault("privacy_accepted", False)
    data.setdefault("personal_accepted", False)

    if callback.data == "toggle_license":
        data["license_accepted"] = not data["license_accepted"]
    elif callback.data == "toggle_privacy":
        data["privacy_accepted"] = not data["privacy_accepted"]
    elif callback.data == "toggle_personal":
        data["personal_accepted"] = not data["personal_accepted"]

    await state.update_data(data)

    if data["license_accepted"] and data["privacy_accepted"] and data["personal_accepted"]:
        await state.set_state(Request.full_name)
        await callback.message.edit_text('✅ Все соглашения приняты!\n\nУкажите ФИО:')
    else:
        await callback.message.edit_reply_markup(reply_markup=consent_keyboard(data))

    await callback.answer()


@router.message(Request.full_name)
async def message_requestFullName(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Request.country)
    await message.answer('Укажите страну')


@router.message(Request.country)
async def message_requestCountry(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await state.set_state(Request.city)
    await message.answer('Укажите город')


@router.message(Request.city)
async def message_requestCity(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(Request.telegram)
    await message.answer('Укажите телеграм аккаунт для связи (пришлите ссылку или юзернейм)')


@router.message(Request.telegram)
async def message_requestTelegram(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    doctor = Doctor(
        user_id=user_id,
        full_name=data['full_name'],
        country=data['country'],
        city=data['city'],
        social_networks_telegram=message.text

    )
    await requestsDoctor.add_doctor(doctor)
    await state.clear()
    await message.answer(
        'Вы зарегистрированы! Заполните профиль врача в личном кабинете. Перейти в панель врача можно, написав команду /doctor',
        reply_markup=kbReply.kbDoctorMain)
    await bot.send_message(chat_id=admin_group_id, text=f'''Зарегистрировался новый доктор!

ID: {user_id}
ФИО: {data['full_name']}
Аккаунт: {message.text}
Страна: {data['country']}
Город: {data['city']}
''')


@router.callback_query(F.data == 'learnMoreAboutProject')
async def callback_learnMoreAboutProject(callback: CallbackQuery):
    await callback.message.edit_text('узнать подробнее о проекте', reply_markup=kbInline.learnMoreAboutProjectKeyboard)


@router.callback_query(F.data == 'advantagesOfParticipation')
async def callback_advantagesOfParticipation(callback: CallbackQuery):
    await callback.message.edit_text('преимущества участия в сообществе',
                                     reply_markup=kbInline.advantagesOfParticipationKeyboard)


@router.callback_query(F.data == 'helpPatient')
async def callback_helpPatient(callback: CallbackQuery):
    await callback.message.edit_text('''Ежедневно врачи принимают решения, от которых зависят жизни людей: работают сверхурочно, сталкиваются с болью, нехваткой времени и ресурсов. 
Они жертвуют личным временем, выдерживая груз ответственности и критику, но продолжают бороться за жизнь и здоровье каждого человека.

Врачи — живой пример того, что героизм — это не подвиги в кино, а осознанный выбор не пройти мимо чужой боли,именно поэтому многие наши специалисты делают некоторые консультации бесплатными-  🕊

 Вы тоже можете быть героем!


📢 Расскажите о нас в соц. сетях
Поделитесь информацией о сообществе — это поможет привлечь тех, кому нужна помощь 

🌟 Станьте амбассадором добра
Распространяйте истории, советы или успехи проекта — Ваша аудитория узнает о важной инициативе и Ваших добрых делах.

🤝🏻 Предложите сотрудничество
Ваши навыки, идеи или партнёрские программы могут стать ценным вкладом в развитие проекта!

💌 Поблагодарите врача или поддержите проект
Вы можете внести вклад в силы и ресурсы врачей, отправив любую сумму доктору в конце бесплатной консультации.

Даже без денег можно изменить чью-то жизнь к лучшему!
Спасибо, что разделяете наши ценности!
''', reply_markup=kbInline.supportProjectCooperation)


async def connectAdmin(message, state, text):
    patient_id = message.from_user.id
    data = await state.get_data()
    try:
        await bot.edit_message_text(chat_id=patient_id, message_id=data['id'], text=data['text'])
    except:
        pass

    if message.photo:
        photosToSend.append({'message': message, 'patient_id': patient_id})
        await asyncio.sleep(1)
        async with lock:
            photos = []
            photosToDelete = []
            for photo in photosToSend:
                if photo['patient_id'] == patient_id:
                    photos.append(photo['message'])
                    photosToDelete.append(photo)
            if photos:
                mediaGroup = [InputMediaPhoto(media=photo.photo[-1].file_id, parse_mode='html') for photo in photos]
                if photos[0].html_text != '':
                    mediaGroup[0].caption = photos[0].html_text

                if len(mediaGroup) > 1:
                    await bot.send_media_group(chat_id=admin_group_id, media=mediaGroup)
                    await bot.send_message(chat_id=admin_group_id, text='Выберите действие',
                                           reply_markup=await kbInline.getKeyboardAnswerConnectAdmin(patient_id))
                else:
                    await bot.send_photo(chat_id=admin_group_id, photo=message.photo[-1].file_id,
                                         caption=f'''{text} <code>{patient_id}</code>

{message.html_text}''', parse_mode='html', reply_markup=await kbInline.getKeyboardAnswerConnectAdmin(patient_id))

                for photo in photosToDelete:
                    photosToSend.remove(photo)

                await state.clear()
                await message.answer('Спасибо за обращение! Администратор скоро с Вами свяжется.',
                                     reply_markup=await kbReply.kbPatientMain(patient_id))
    else:
        await bot.send_message(chat_id=admin_group_id, text=f'''{text} <code>{patient_id}</code>

{message.html_text}''', parse_mode='html', reply_markup=await kbInline.getKeyboardAnswerConnectAdmin(patient_id))
        await state.clear()
        await message.answer('Спасибо за обращение! Администратор скоро с Вами свяжется.',
                             reply_markup=await kbReply.kbPatientMain(patient_id))


@router.callback_query(F.data.startswith('answerConnectAdmin_'))
async def callback_answerConnectAdmin(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Connect.answer_admin)
    await state.update_data(patient_id=int(callback.data.split('_')[1]))
    try:
        await callback.message.edit_text(callback.message.html_text, parse_mode='html')
    except:
        await callback.message.edit_caption(inline_message_id=str(callback.message.message_id),
                                            caption=callback.message.html_text, parse_mode='html')
    await callback.message.answer('Напишите ответ')


@router.message(Connect.answer_admin)
async def message_answerConnectAdmin(message: Message, state: FSMContext):
    data = await state.get_data()
    patient_id = data['patient_id']
    await bot.send_message(chat_id=patient_id, text=f'''<code>Администрация</code>

{message.html_text}''', parse_mode='html', reply_markup=kbInline.answerConnectAdmin)
    await message.answer('Сообщение отправлено')


@router.callback_query(F.data == 'connectAdmin')
async def callback_connectAdmin(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Connect.admin)
    message = await callback.message.edit_text(
        'Укажите ваш род деятельности, опишите ваше предложение о сотрудничестве и оставьте контакты для связи, с вами свяжется администратор.',
        reply_markup=kbInline.returnToCooperation)
    await state.update_data(id=message.message_id, text=message.text)


@router.message(Connect.admin)
async def message_connectAdmin(message: Message, state: FSMContext):
    await connectAdmin(message, state, 'Сотрудничество пользователя')


@router.callback_query(F.data == 'representProject')
async def callback_connectRepresent(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Connect.represent)
    message = await callback.message.edit_text(
        'Укажите название организации, опишите деятельность, прикрепите ссылку и опишите ваше предложение о сотрудничестве.',
        reply_markup=kbInline.returnToCooperation)
    await state.update_data(id=message.message_id, text=message.text)


@router.message(Connect.represent)
async def message_connectRepresent(message: Message, state: FSMContext):
    await connectAdmin(message, state, 'Представляю проект/организацию')


@router.callback_query(F.data == 'connectAdminAppeal')
async def callback_connectAdminAppeal(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Connect.appeal)
    message = await callback.message.edit_text('Опишите суть Вашего обращения, прикрепите скриншоты при необходимости.',
                                               reply_markup=kbInline.returnToFAQ)
    await state.update_data(id=message.message_id, text=message.text)


@router.message(Connect.appeal)
async def message_connectAdminAppeal(message: Message, state: FSMContext):
    await connectAdmin(message, state, 'Обращение пользователя')


@router.callback_query(F.data == 'answerConnectAdmin')
async def callback_answerConnectAdmin(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Connect.answer_connect_admin)
    message = await callback.message.edit_text('Напишите Ваш ответ', reply_markup=kbInline.returnToMenu)
    await state.update_data(id=message.message_id, text=message.text)


@router.message(Connect.answer_connect_admin)
async def message_answerConnectAdmin(message: Message, state: FSMContext):
    await connectAdmin(message, state, 'Ответ пользователя')
