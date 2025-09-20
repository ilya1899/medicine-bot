from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaDocument
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

from app.database.models import Doctor

router = Router()


class EditPersonalAccount(StatesGroup):
    full_name = State()
    country = State()
    city = State()
    specialty = State()
    work_experience = State()
    education = State()
    education_data = State()
    resume = State()
    photo = State()
    face_to_face = State()
    price_just_ask = State()
    price_decoding = State()
    price_main_first = State()
    price_main_repeated = State()
    price_second_opinion = State()
    achievements = State()
    is_social_networks = State()
    social_networks_telegram = State()
    social_networks_instagram = State()
    about_me = State()
    bank_details_russia = State()
    bank_details_abroad = State()


class EditPersonalAccountAdmin(StatesGroup):
    photo = State()
    education = State()
    reasonOfReject = State()


diplomasToSend = []

lock = asyncio.Lock()

from app.database.requests import requestsDoctor, requestsPreDoctor, requestsCountry, requestsSpecialty, requestsCity
from app.keyboards import kbInline, kbReply
from config_reader import config
from run import bot


@router.message(F.text == 'Личный кабинет')
async def message_personalAccount(message: Message):
    user_id = message.from_user.id
    if await requestsDoctor.is_doctor(user_id):
        await message.answer(
            'Вы можете изменить личный кабинет, после чего данные отправятся на проверку администрации. Результаты проверки придут Вам. После необходимых изменений нажмите на "Сохранить и отправить".',
            reply_markup=kbInline.continueToEditPersonalAccount)


@router.callback_query(F.data == 'continueToEditPersonalAccount')
async def callback_continueToEditPersonalAccount(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await requestsPreDoctor.is_doctor(user_id):
        await copyToPreDoctor(await requestsDoctor.get_doctor_by_user_id(callback.from_user.id))
    await callback.message.edit_text('Выберите, что вы хотите изменить', reply_markup=kbInline.personalAccountEdit)


@router.callback_query(F.data == 'returnToDoctorMenu')
async def callback_returnToDoctorMenu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    if await requestsDoctor.is_doctor(user_id):
        await callback.message.edit_text('Выберите, что вы хотите изменить', reply_markup=kbInline.personalAccountEdit)


@router.callback_query(F.data == 'doctorPersonalInformation')
async def callback_doctorPersonalInformation(callback: CallbackQuery):
    await callback.message.edit_text('Выберите, что вы хотите изменить', reply_markup=kbInline.personalInformation)


@router.callback_query(F.data == 'doctorProfessionalInformation')
async def callback_doctorProfessionalInformation(callback: CallbackQuery):
    await callback.message.edit_text('Выберите, что вы хотите изменить', reply_markup=kbInline.professionalInformation)


async def copyToPreDoctor(doctor):
    await requestsPreDoctor.add_doctor(doctor.user_id, doctor.full_name, doctor.country, doctor.city, doctor.specialty,
                                       doctor.work_experience, doctor.education_data, doctor.education, doctor.resume,
                                       doctor.is_face_to_face,
                                       doctor.photo,
                                       doctor.data_face_to_face, doctor.price_just_ask,
                                       doctor.price_decoding, doctor.price_main_first, doctor.price_main_repeated,
                                       doctor.price_second_opinion,
                                       doctor.achievements, doctor.is_social_networks, doctor.social_networks_telegram,
                                       doctor.social_networks_instagram, doctor.about_me, doctor.bank_details_russia,
                                       doctor.bank_details_abroad)


async def copyToDoctor(doctor):
    if not await requestsDoctor.edit_doctor(doctor):
        await requestsDoctor.add_doctor(doctor)


async def editDoctorPersonalAccount(function, message, value, state, user_id, whereReturn):
    await state.clear()
    await function(user_id, value)
    match whereReturn:
        case 'personalInformation':
            await message.answer('Изменения сохранены', reply_markup=kbInline.personalInformation)
        case 'socialNetworks':
            await message.answer('Изменения сохранены', reply_markup=kbInline.socialNetworks)
        case 'professionalInformation':
            await message.answer('Изменения сохранены', reply_markup=kbInline.professionalInformation)
        case 'bankDetails':
            await message.answer('Изменения сохранены', reply_markup=kbInline.bankDetails)
        case 'consultationEdit':
            await message.answer('Изменения сохранены', reply_markup=kbInline.consultationEdit)


@router.callback_query(F.data == 'doctorEditFullName')
async def callback_doctorEditFullName(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.full_name)
    await callback.message.edit_text('Напишите ваше ФИО', reply_markup=kbInline.returnToPersonalInformation)


@router.message(EditPersonalAccount.full_name)
async def message_doctorEditFullName(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_full_name, message, message.text, state,
                                    message.from_user.id, 'personalInformation')


@router.callback_query(F.data == 'doctorEditCountry')
async def callback_doctorEditCountry(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.country)
    countries = await requestsCountry.get_all_countries()
    await callback.message.edit_text('Выберите страну или укажите свой вариант',
                                     reply_markup=await kbInline.getKeyboardCountryOrCity(countries, 'country'))


@router.callback_query(F.data.startswith('country_'), EditPersonalAccount.country)
async def callback_doctorEditCountry2(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split('_')[1])
    name = await requestsCountry.get_name(id)
    await callback.message.delete()
    await editDoctorPersonalAccount(requestsPreDoctor.edit_country, callback.message, name, state,
                                    callback.from_user.id, 'personalInformation')


@router.message(EditPersonalAccount.country)
async def message_doctorEditCountry2(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_country, message, message.text, state, message.from_user.id,
                                    'personalInformation')


@router.callback_query(F.data == 'doctorEditCity')
async def callback_doctorEditCity(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.city)
    doctor = await requestsPreDoctor.get_doctor_by_user_id(callback.from_user.id)
    country = await requestsCountry.get_country_by_name(doctor.country)
    if country:
        id_country = country.id
        cities = await requestsCity.get_all_cities_by_country_id(id_country)
        await callback.message.edit_text('Выберите город или укажите свой вариант',
                                         reply_markup=await kbInline.getKeyboardCountryOrCity(cities, 'city'))
    else:
        await callback.message.edit_text('Укажите свой город')


@router.callback_query(F.data.startswith('city_'), EditPersonalAccount.city)
async def callback_doctorEditCity2(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split('_')[1])
    name = await requestsCity.get_name(id)
    await callback.message.delete()
    await editDoctorPersonalAccount(requestsPreDoctor.edit_city, callback.message, name, state, callback.from_user.id,
                                    'personalInformation')


@router.message(EditPersonalAccount.city)
async def message_doctorEditCity2(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_city, message, message.text, state, message.from_user.id,
                                    'personalInformation')


@router.callback_query(F.data == 'doctorEditSpecialty')
async def callback_doctorEditSpecialty(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.specialty)
    specialties = await requestsSpecialty.get_all_specialties()
    id = await callback.message.edit_text(
        'Выберите одну или несколько специальностей. Если Вашей специльности нет в списке, введите название вручную.',
        reply_markup=await kbInline.getKeyboardSpecialties(specialties, 0, True))
    await state.update_data(id=id.message_id)


async def editSpecialties(function, state, specialty, page):
    specialties = await requestsSpecialty.get_all_specialties()
    data = await state.get_data()
    try:
        listSpecialties = data['specialties']
    except:
        listSpecialties = []
    if specialty not in listSpecialties:
        listSpecialties.append(specialty)
    else:
        listSpecialties.remove(specialty)

    if listSpecialties != []:
        strAll = 'Выбрано: '
        for i in listSpecialties:
            strAll += i + '\n'
        id = await function(strAll, reply_markup=await kbInline.getKeyboardSpecialties(specialties, page, True))
    else:
        id = await function('Специальности не выбраны',
                            reply_markup=await kbInline.getKeyboardSpecialties(specialties, page, True))
    await state.update_data(specialties=listSpecialties, id=id.message_id)


@router.callback_query(F.data.startswith('specialty_'), EditPersonalAccount.specialty)
async def callback_doctorEditSpecialty2(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split('_')[1])
    specialty = (await requestsSpecialty.get_specialty_by_id(id)).name
    page = int(callback.data.split('_')[2])
    await editSpecialties(callback.message.edit_text, state, specialty, page)


@router.message(EditPersonalAccount.specialty)
async def message_doctorEditSpecialty2(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['id'])
    await editSpecialties(message.answer, state, message.text, 0)


@router.callback_query(F.data == 'acceptSpecialtiesPersonalAccount', EditPersonalAccount.specialty)
async def callback_doctorEditAcceptSpecialties(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        listSpecialties = data['specialties']
        if listSpecialties != []:
            await callback.message.delete()
            await editDoctorPersonalAccount(requestsPreDoctor.edit_specialty, callback.message,
                                            ', '.join(listSpecialties), state, callback.from_user.id,
                                            'professionalInformation')
    except:
        await callback.answer('Выберите хотя бы одну специальность')


@router.callback_query(F.data == 'doctorEditWorkExperience')
async def callback_doctorEditWorkExperience(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.work_experience)
    await callback.message.edit_text('Напишите опыт работы в годах',
                                     reply_markup=kbInline.returnToProfessionalInformation)


@router.message(EditPersonalAccount.work_experience)
async def message_doctorEditWorkExperience(message: Message, state: FSMContext):
    try:
        work_experience = int(message.text)
        await editDoctorPersonalAccount(requestsPreDoctor.edit_work_experience, message, work_experience, state,
                                        message.from_user.id, 'professionalInformation')
    except:
        await message.answer('Неверный формат ввода. Напишите целое число, обозначающее опыт работы в годах',
                             reply_markup=kbInline.returnToProfessionalInformation)


@router.callback_query(F.data == 'doctorEditEducationData')
async def callback_doctorEditEducationData(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.education_data)
    await callback.message.edit_text('Укажите Ваше образование в формате ВУЗ-специальность',
                                     reply_markup=kbInline.returnToProfessionalInformation)


@router.message(EditPersonalAccount.education_data)
async def message_doctorEditEducationData(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_education_data, message, message.text, state,
                                    message.from_user.id, 'professionalInformation')


@router.callback_query(F.data == 'doctorEditEducation')
async def callback_doctorEditEducation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.education)
    await callback.message.edit_text(
        'Загрузите документы об образовании. После проверки документов и наложения на них водяных знаков, эта информация будет видна в профиле.',
        reply_markup=kbInline.returnToProfessionalInformation)


@router.message(EditPersonalAccount.education)
async def message_doctorEditEducation(message: Message, state: FSMContext):
    doctor_id = message.from_user.id
    if message.document or message.photo:
        diplomasToSend.append({'message': message, 'doctor_id': doctor_id})
        await asyncio.sleep(1)
        async with lock:
            files = []
            for file in diplomasToSend:
                if file['doctor_id'] == doctor_id:
                    files.append(file)
            if files:
                try:
                    await editDoctorPersonalAccount(requestsPreDoctor.edit_education, message,
                                                    ', '.join([file['message'].document.file_id for file in files]),
                                                    state, message.from_user.id, 'professionalInformation')
                except:
                    await editDoctorPersonalAccount(requestsPreDoctor.edit_education, message,
                                                    ', '.join([file['message'].photo[-1].file_id for file in files]),
                                                    state, message.from_user.id, 'professionalInformation')
                for file in files:
                    diplomasToSend.remove(file)


@router.callback_query(F.data == 'doctorEditResume')
async def callback_doctorProfessionalInterest(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.resume)
    await callback.message.edit_text('''В этом разделе укажите:
•	Чем вы в рамках информационных услуг можете помочь человеку
•	Лечением каких заболеваний и состояний вы занимаетесь в повседневной жизни 
•	Опишите свой подход к пациентам:
[Пример: "Объясняю сложное простыми словами", "Не люблю запугивать, я мягкий человек..."]  

Совет: выделяйте текст в абзацы, используйте смайлики, чтобы акцентировать внимание на важных деталях.
''', reply_markup=kbInline.returnToProfessionalInformation)


@router.message(EditPersonalAccount.resume)
async def message_doctorProfessionalInterest(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_resume, message, message.text, state, message.from_user.id,
                                    'professionalInformation')


@router.callback_query(F.data == 'doctorEditFaceToFace')
async def callback_doctorEditFaceToFace(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.face_to_face)
    await callback.message.edit_text('Ведете ли вы платный прием (не по ОМС)?', reply_markup=kbInline.yesOrNoCMI)


@router.callback_query(F.data == 'yesCMI', EditPersonalAccount.face_to_face)
async def callback_yesCMI(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cmi=True)
    await callback.message.edit_text('''Укажите данные в следующем формате:

Название медицинского учреждения
Адрес клиники
Способ записи на прием
Дни и время приема
Стоимость приема

Если Вы ведете прием в нескольких клиниках, укажите их данные ниже в таком же формате.''')


@router.callback_query(F.data == 'noCMI', EditPersonalAccount.face_to_face)
async def callback_noCMI(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cmi=False)
    await callback.message.edit_text('Напишите название медицинского учреждения, в котором Вы ведете прием.')


@router.message(EditPersonalAccount.face_to_face)
async def message_dataFaceToFace(message: Message, state: FSMContext):
    data = await state.get_data()
    await editDoctorPersonalAccount(requestsPreDoctor.edit_is_face_to_face, message, True, state, message.from_user.id,
                                    'consultationEdit')
    if data['cmi']:
        await requestsPreDoctor.edit_data_face_to_face(message.from_user.id, message.text)
    else:
        await requestsPreDoctor.edit_data_face_to_face(message.from_user.id, message.text +
                                                       '\n\nВрач работает в данном медицинском учреждении и ведет прием только по ОМС. Попасть к нему на прием можно только прикрепившись к этой медицинской клинике.')


@router.callback_query(F.data == 'doctorEditPhoto')
async def callback_doctorEditPhoto(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.photo)
    await callback.message.edit_text('Отправьте фотографию', reply_markup=kbInline.returnToPersonalInformation)


@router.message(F.photo, EditPersonalAccount.photo)
async def message_doctorEditPhoto(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_photo, message, message.photo[-1].file_id, state,
                                    message.from_user.id, 'personalInformation')


@router.callback_query(F.data.startswith('doctorEditPricePaid_'))
async def callback_doctorEditPricePaid(callback: CallbackQuery, state: FSMContext):
    type = callback.data.split('_')[1]
    match type:
        case 'justAsk':
            await state.set_state(EditPersonalAccount.price_just_ask)
        case 'decoding':
            await state.set_state(EditPersonalAccount.price_decoding)
        case 'mainFirst':
            await state.set_state(EditPersonalAccount.price_main_first)
        case 'mainRepeated':
            await state.set_state(EditPersonalAccount.price_main_repeated)
        case 'secondOpinion':
            await state.set_state(EditPersonalAccount.price_second_opinion)
    await callback.message.edit_text('Напишите стоимость консультации', reply_markup=kbInline.returnToConsultationEdit)


@router.callback_query(F.data.startswith('doctorEditPriceFree_'))
async def callback_doctorEditPriceFree(callback: CallbackQuery, state: FSMContext):
    type = callback.data.split('_')[1]
    await callback.message.delete()
    match type:
        case 'justAsk':
            await editDoctorPersonalAccount(requestsPreDoctor.edit_price_just_ask, callback.message, 0, state,
                                            callback.from_user.id, 'consultationEdit')
        case 'decoding':
            await editDoctorPersonalAccount(requestsPreDoctor.edit_price_decoding, callback.message, 0, state,
                                            callback.from_user.id, 'consultationEdit')
        case 'mainFirst':
            await editDoctorPersonalAccount(requestsPreDoctor.edit_price_main_first, callback.message, 0, state,
                                            callback.from_user.id, 'consultationEdit')
        case 'mainRepeated':
            await editDoctorPersonalAccount(requestsPreDoctor.edit_price_main_repeated, callback.message, 0, state,
                                            callback.from_user.id, 'consultationEdit')
        case 'secondOpinion':
            await editDoctorPersonalAccount(requestsPreDoctor.edit_price_second_opinion, callback.message, 0, state,
                                            callback.from_user.id, 'consultationEdit')


@router.callback_query(F.data == 'doctorEditPrice')
async def callback_doctorEditPrice(callback: CallbackQuery):
    await callback.message.edit_text('Выберите консультацию', reply_markup=kbInline.consultationEdit)


@router.callback_query(F.data == 'doctorEditPriceJustAsk')
async def callback_doctorEditPriceJustAsk(callback: CallbackQuery):
    await callback.message.edit_text('Выберите вариант',
                                     reply_markup=await kbInline.getKeyboardConsultationEdit('justAsk'))


@router.message(EditPersonalAccount.price_just_ask)
async def message_doctorEditPriceJustAsk(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await editDoctorPersonalAccount(requestsPreDoctor.edit_price_just_ask, message, price, state,
                                        message.from_user.id, 'consultationEdit')
    except:
        await message.answer('Неверный формат. Напишите стоимость консультаций в виде целого числа рублей.',
                             reply_markup=kbInline.returnToConsultationEdit)


@router.callback_query(F.data == 'doctorEditPriceDecoding')
async def callback_doctorEditPriceDecoding(callback: CallbackQuery):
    await callback.message.edit_text('Выберите вариант',
                                     reply_markup=await kbInline.getKeyboardConsultationEdit('decoding'))


@router.message(EditPersonalAccount.price_decoding)
async def message_doctorEditPriceDecoding(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await editDoctorPersonalAccount(requestsPreDoctor.edit_price_decoding, message, price, state,
                                        message.from_user.id, 'consultationEdit')
    except:
        await message.answer('Неверный формат. Напишите стоимость консультаций в виде целого числа рублей.',
                             reply_markup=kbInline.returnToConsultationEdit)


@router.callback_query(F.data == 'doctorEditPriceMainFirst')
async def callback_doctorEditPriceMain(callback: CallbackQuery):
    await callback.message.edit_text('Выберите вариант',
                                     reply_markup=await kbInline.getKeyboardConsultationEdit('mainFirst'))


@router.message(EditPersonalAccount.price_main_first)
async def message_doctorEditPriceMainFirst(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await editDoctorPersonalAccount(requestsPreDoctor.edit_price_main_first, message, price, state,
                                        message.from_user.id, 'consultationEdit')
    except:
        await message.answer('Неверный формат. Напишите стоимость консультаций в виде целого числа рублей.',
                             reply_markup=kbInline.returnToConsultationEdit)


@router.callback_query(F.data == 'doctorEditPriceMainRepeated')
async def callback_doctorEditPriceMainRepeated(callback: CallbackQuery):
    await callback.message.edit_text('Выберите вариант',
                                     reply_markup=await kbInline.getKeyboardConsultationEdit('mainRepeated'))


@router.message(EditPersonalAccount.price_main_repeated)
async def message_doctorEditPriceMainRepeated(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await editDoctorPersonalAccount(requestsPreDoctor.edit_price_main_repeated, message, price, state,
                                        message.from_user.id, 'consultationEdit')
    except:
        await message.answer('Неверный формат. Напишите стоимость консультаций в виде целого числа рублей.',
                             reply_markup=kbInline.returnToConsultationEdit)


@router.callback_query(F.data == 'doctorEditSecondOpinion')
async def callback_doctorEditSecondOpinion(callback: CallbackQuery):
    await callback.message.edit_text(
        'Этот вид консультации создан для специалистов, которые в своей практике просматривают КТ, МРТ.',
        reply_markup=kbInline.secondOpinionCommands)


@router.callback_query(F.data == 'doctorNotEditSecondOpinion')
async def callback_doctorNotEditSecondOpinion(callback: CallbackQuery):
    await callback.message.edit_text('Вы отключили данный вид консультации', reply_markup=kbInline.consultationEdit)


@router.callback_query(F.data == 'doctorEditPriceSecondOpinion')
async def callback_doctorEditPriceSecondOpinion(callback: CallbackQuery):
    await callback.message.edit_text('Выберите вариант',
                                     reply_markup=await kbInline.getKeyboardConsultationEdit('secondOpinion'))


@router.message(EditPersonalAccount.price_second_opinion)
async def message_doctorEditPriceSecondOpinion(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await editDoctorPersonalAccount(requestsPreDoctor.edit_price_second_opinion, message, price, state,
                                        message.from_user.id, 'consultationEdit')
    except:
        await message.answer('Неверный формат. Напишите стоимость консультаций в виде целого числа рублей.',
                             reply_markup=kbInline.returnToConsultationEdit)


@router.callback_query(F.data == 'doctorEditAchievements')
async def callback_doctorEditAchievements(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.achievements)
    await callback.message.edit_text(
        'Укажите Ваши заслуги: в каких научных сообществах состоите, имеете ли ученую степень, знание английского, являетесь ли автором научных статей и т.д.',
        reply_markup=kbInline.returnToProfessionalInformation)


@router.message(EditPersonalAccount.achievements)
async def message_doctorEditAchievements(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_achievements, message, message.text, state,
                                    message.from_user.id, 'professionalInformation')


@router.callback_query(F.data == 'doctorEditSocialNetworks')
async def callback_doctorEditSocialNetworks(callback: CallbackQuery):
    await callback.message.edit_text('Ведете ли вы профессиональные соц. сети/блог?',
                                     reply_markup=kbInline.isSocialNetworks)


@router.callback_query(F.data == 'yesSocialNetworks')
async def callback_yesSocialNetworks(callback: CallbackQuery):
    await callback.message.edit_text('Выберите, что Вы хотите изменить', reply_markup=kbInline.socialNetworks)


@router.callback_query(F.data == 'doctorEditSocialNetworksTelegram')
async def callback_doctorEditSocialNetworksTelegram(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.social_networks_telegram)
    await callback.message.edit_text('Укажите ссылку на аккаунт')


@router.message(EditPersonalAccount.social_networks_telegram)
async def message_doctorEditSocialNetworksTelegram(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_social_networks_telegram, message, message.text, state,
                                    message.from_user.id, 'socialNetworks')


@router.callback_query(F.data == 'doctorEditSocialNetworksInstagram')
async def callback_doctorEditSocialNetworksInstagram(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.social_networks_instagram)
    await callback.message.edit_text('Укажите ссылку на аккаунт')


@router.message(EditPersonalAccount.social_networks_instagram)
async def message_doctorEditSocialNetworksInstagram(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_social_networks_instagram, message, message.text, state,
                                    message.from_user.id, 'socialNetworks')


@router.callback_query(F.data == 'doctorEditAboutMe')
async def callback_doctorEditAboutMe(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.about_me)
    await callback.message.edit_text('Напишите о себе', reply_markup=kbInline.returnToPersonalInformation)


@router.message(EditPersonalAccount.about_me)
async def message_doctorEditResume(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_about_me, message, message.text, state, message.from_user.id,
                                    'personalInformation')


@router.callback_query(F.data == 'doctorEditBankDetails')
async def callback_doctorEditBankDetails(callback: CallbackQuery):
    await callback.message.edit_text('Выберите, что вы хотите изменить', reply_markup=kbInline.bankDetails)


@router.callback_query(F.data == 'doctorEditBankDetailsRussia')
async def callback_doctorEditBankDetailsRussia(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.bank_details_russia)
    await callback.message.edit_text('Укажите номер карты МИР', reply_markup=kbInline.returnToBankDetails)


@router.message(EditPersonalAccount.bank_details_russia)
async def message_doctorEditBankDetailsRussia(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_bank_details_russia, message, message.text, state,
                                    message.from_user.id, 'bankDetails')


@router.callback_query(F.data == 'doctorEditBankDetailsAbroad')
async def callback_doctorEditBankDetailsAbroad(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditPersonalAccount.bank_details_abroad)
    await callback.message.edit_text('Укажите название банка и номер карты VISA / MASTERCARD',
                                     reply_markup=kbInline.returnToBankDetails)


@router.message(EditPersonalAccount.bank_details_abroad)
async def message_doctorEditBankDetailsAbroad(message: Message, state: FSMContext):
    await editDoctorPersonalAccount(requestsPreDoctor.edit_bank_details_abroad, message, message.text, state,
                                    message.from_user.id, 'bankDetails')


async def sendProfileDoctor(doctor: Doctor):
    if doctor.is_social_networks:
        socialNetworks = f'''Социальные сети: Да
Telegram: {doctor.social_networks_telegram}
Instagram: {doctor.social_networks_instagram}'''
    else:
        socialNetworks = 'Социальные сети: Нет'

    messages = []

    try:
        if doctor.photo and doctor.photo.strip():
            messages.append(await bot.send_photo(
                chat_id=config.ADMIN_GROUP_ID.get_secret_value(),
                photo=doctor.photo
            ))
    except Exception as e:
        print(e)

    if doctor.education and doctor.education.strip():
        education_files = doctor.education.split(', ')

        first_file = education_files[0]
        try:
            file_info = await bot.get_file(first_file)
            file_extension = file_info.file_path.split('.')[-1].lower() if file_info.file_path else ''

            is_document = (
                    file_info.file_path and
                    (file_info.file_path.startswith('documents/') or
                     file_extension in ['pdf', 'doc', 'docx', 'txt', 'zip', 'rar'])
            )

            if is_document:
                mediaGroup = [InputMediaDocument(media=file_id) for file_id in education_files]
            else:
                mediaGroup = [InputMediaPhoto(media=file_id) for file_id in education_files]

            mediaGroup[-1].caption = f'''id врача: {doctor.user_id}
ФИО: {doctor.full_name}
Страна: {doctor.country}
Город: {doctor.city}
Специальность: {doctor.specialty}
Опыт работы: {doctor.work_experience}
Резюме: {doctor.resume}
Очный прием: {doctor.data_face_to_face if doctor.is_face_to_face else 'нет'}
Стоимость:
1. просто спросить {doctor.price_just_ask}
2. расшифровка анализов {doctor.price_decoding}
3. первичная консультация: {doctor.price_main_first}
4. повторная консультация: {doctor.price_main_repeated}
5. второе мнение: {doctor.price_second_opinion}
Образование: {doctor.education_data}
Достижения: {doctor.achievements}
{socialNetworks}
О себе: {doctor.about_me}
МИР: {doctor.bank_details_russia}
VISA / MASTERCARD: {doctor.bank_details_abroad}'''
            mediaGroup[-1].parse_mode = 'HTML'

            media_messages = await bot.send_media_group(
                chat_id=config.ADMIN_GROUP_ID.get_secret_value(),
                media=mediaGroup
            )
            messages.extend(media_messages)

        except Exception as e:
            await bot.send_message(
                chat_id=config.ADMIN_GROUP_ID.get_secret_value(),
                text=f"Ошибка загрузки файлов образования: {e}"
            )
    else:
        text_message = f'''id врача: {doctor.user_id}
ФИО: {doctor.full_name}
Страна: {doctor.country}
Город: {doctor.city}
Специальность: {doctor.specialty}
Опыт работы: {doctor.work_experience}
Резюме: {doctor.resume}
Очный прием: {doctor.data_face_to_face if doctor.is_face_to_face else 'нет'}
Стоимость:
1. просто спросить {doctor.price_just_ask}
2. расшифровка анализов {doctor.price_decoding}
3. первичная консультация: {doctor.price_main_first}
4. повторная консультация: {doctor.price_main_repeated}
5. второе мнение: {doctor.price_second_opinion}
Образование: {doctor.education_data}
Достижения: {doctor.achievements}
{socialNetworks}
О себе: {doctor.about_me}
МИР: {doctor.bank_details_russia}
VISA / MASTERCARD: {doctor.bank_details_abroad}'''

        messages.append(await bot.send_message(
            chat_id=config.ADMIN_GROUP_ID.get_secret_value(),
            text=text_message,
            parse_mode='HTML'
        ))

    ids = ', '.join([str(message.message_id) for message in messages])
    print(ids)
    await bot.send_message(
        chat_id=int(config.ADMIN_GROUP_ID.get_secret_value()),
        text='Выберите действие',
        reply_markup=kbInline.acceptPersonalAccount(doctor.user_id, ids)
    )


@router.callback_query(F.data == 'publishPersonalAccount')
async def callback_publishPersonalAccount(callback: CallbackQuery):
    await callback.message.edit_text(
        'Перед отправкой заявки на публикацию, убедитесь, что вы заполнили все разделы анкеты. После проверки администратором анкеты будет опубликована.',
        reply_markup=kbInline.acceptAndSendPersonalAccount)


@router.callback_query(F.data == 'acceptAndSendPersonalAccount')
async def callback_acceptAndSendPersonalAccount(callback: CallbackQuery):
    user_id = callback.from_user.id
    doctor = await requestsPreDoctor.get_doctor_by_user_id(user_id)
    await sendProfileDoctor(doctor)
    await callback.message.edit_text('После проверки администрацией анкета будет обновлена')


@router.callback_query(F.data.startswith('acceptPersonalAccount_'))
async def callback_acceptPersonalAccount(callback: CallbackQuery):
    doctor_id = int(callback.data.split('_')[1])
    await copyToDoctor(await requestsPreDoctor.get_doctor_by_user_id(doctor_id))
    await requestsPreDoctor.delete_doctor(doctor_id)
    await callback.message.edit_text('<b>Изменения сохранены</b>', parse_mode='html')
    await bot.send_message(chat_id=doctor_id, text='''<code>Администрация</code>

Ваша заявка одобрена и опубликована.''', parse_mode='html', reply_markup=kbReply.kbDoctorMain)
    await bot.send_message(chat_id=doctor_id, text='''
Добро пожаловать в сообщество «Врач для каждого». Теперь вы можете проводить консультации на платформе.
Вам открыт доступ в закрытый чат врачей нашего сообщества 👇
''', parse_mode='html', reply_markup=kbInline.chatWithDoctors)


@router.callback_query(F.data.startswith('rejectPersonalAccount_'))
async def callback_rejectPersonalAccount(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split('_')[1])
    await state.set_state(EditPersonalAccountAdmin.reasonOfReject)
    id = (await callback.message.edit_text('Укажите причину отказа')).message_id
    await state.update_data(doctor_id=doctor_id, id=id)


@router.message(EditPersonalAccountAdmin.reasonOfReject)
async def message_rejectPersonalAccount(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.send_message(chat_id=data['doctor_id'], text=f'''<code>Администрация</code>

Отказано в изменении личного кабинета

<i>{message.html_text}</i>
''', parse_mode='html')
    await bot.delete_message(chat_id=config.ADMIN_GROUP_ID.get_secret_value(), message_id=data['id'])
    await message.answer('Сообщение об отказе отправлено пользователю')


@router.callback_query(F.data.startswith('newPhotoPersonalAccount_'))
async def callback_newPhotoPersonalAccount(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split('_')[1])
    ids = callback.data.split('_')[2].split(', ')
    await state.set_state(EditPersonalAccountAdmin.photo)
    await state.update_data(doctor_id=doctor_id, ids=ids)
    await callback.message.edit_text('Отправьте новую фотографию')


@router.message(EditPersonalAccountAdmin.photo)
async def message_newPhotoPersonalAccount(message: Message, state: FSMContext):
    data = await state.get_data()
    doctor_id = data['doctor_id']
    await bot.delete_messages(chat_id=config.ADMIN_GROUP_ID.get_secret_value(), message_ids=data['ids'])
    await requestsPreDoctor.edit_photo(doctor_id, message.photo[-1].file_id)
    doctor = await requestsPreDoctor.get_doctor_by_user_id(doctor_id)
    await sendProfileDoctor(doctor)


@router.callback_query(F.data.startswith('newEducationPersonalAccount_'))
async def callback_newEducationPersonalAccount(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split('_')[1])
    ids = callback.data.split('_')[2].split(', ')
    await state.set_state(EditPersonalAccountAdmin.education)
    await state.update_data(doctor_id=doctor_id, ids=ids)
    await callback.message.edit_text('Отправьте новые документы об образовании')


@router.message(EditPersonalAccountAdmin.education)
async def message_newPhotoPersonalAccount(message: Message, state: FSMContext):
    data = await state.get_data()
    admin_id = message.from_user.id
    doctor_id = data['doctor_id']
    if message.photo:
        diplomasToSend.append({'message': message, 'admin_id': admin_id})
        await asyncio.sleep(1)
        async with lock:
            photos = []
            for photo in diplomasToSend:
                if photo['admin_id'] == admin_id:
                    photos.append(photo)
            if photos:
                await requestsPreDoctor.edit_education(doctor_id,
                                                       ', '.join(
                                                           [photo['message'].photo[-1].file_id for photo in photos]))
                for photo in photos:
                    diplomasToSend.remove(photo)

                await bot.delete_messages(chat_id=config.ADMIN_GROUP_ID.get_secret_value(), message_ids=data['ids'])
                doctor = await requestsPreDoctor.get_doctor_by_user_id(doctor_id)
                await sendProfileDoctor(doctor)
