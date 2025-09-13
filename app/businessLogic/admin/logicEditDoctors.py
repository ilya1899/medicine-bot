from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class AddDoctor(StatesGroup):
    user_id = State()
    full_name = State()
    country = State()
    city = State()
    specialty = State()
    work_experience = State()
    education = State()
    resume = State()
    data_face_to_face = State()
    photo = State()
    price = State()
    achievements = State()
    social_networks = State()
    about_me = State()


class DeleteDoctor(StatesGroup):
    user_id = State()


from app.database.requests import requestsUser, requestsDoctor, requestsCountry, requestsCity, requestsSpecialty
from app.user.admin.handlerAdmin import Admin
from app.keyboards import kbInline, kbReply
from run import bot


async def editDoctors(message: Message):
    await message.answer('Выберите действие', reply_markup=kbInline.editDoctors)


async def addDoctor(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddDoctor.user_id)
    await callback.message.edit_text('Напишите ID пользователя')


async def addDoctorUserID(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        if await requestsUser.is_user(user_id):
            if not await requestsDoctor.is_doctor(user_id):
                await state.update_data(user_id=user_id)
                await state.set_state(AddDoctor.full_name)
                await message.answer('Напишите ФИО врача')
            else:
                await state.set_state(Admin.admin)
                await message.answer('Анкета врача уже создана', reply_markup=kbReply.kbAdminMain)
        else:
            await message.answer('Пользователь не найден, попробуйте снова')
    except:
        await message.answer('Неправильный формат записи. Попробуйте снова.')


async def addDoctorFullName(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(AddDoctor.country)
    countries = await requestsCountry.get_all_countries()
    await message.answer('Выберите страну и город',
                         reply_markup=await kbInline.getKeyboardCountryOrCity(countries, 'country'))


async def addDoctorCountry(callback: CallbackQuery, state: FSMContext):
    countries = await requestsCountry.get_all_countries()
    for country in countries:
        if country.callback == callback.data:
            await state.update_data(country=country.name)
    await state.set_state(AddDoctor.city)
    cities = await requestsCity.get_all_cities()
    await callback.message.edit_text('Выберите страну и город',
                                     reply_markup=await kbInline.getKeyboardCountryOrCity(cities, 'city'))


async def addDoctorCity(callback: CallbackQuery, state: FSMContext):
    cities = await requestsCity.get_all_cities()
    for city in cities:
        if city.callback == callback.data:
            await state.update_data(city=city.name)
    await state.set_state(AddDoctor.specialty)
    specialties = await requestsSpecialty.get_all_specialties()
    await callback.message.edit_text('Выберите одну или несколько специальностей',
                                     reply_markup=await kbInline.getKeyboardSpecialties(specialties, 0, True))


async def addDoctorSpecialty(callback: CallbackQuery, state: FSMContext):
    specialty = int(callback.data.split('_')[1])
    page = int(callback.data.split('_')[2])
    specialties = await requestsSpecialty.get_all_specialties()
    try:
        data = await state.get_data()
        listSpecialties = data['specialty']
        strAll = ''
        if specialty not in listSpecialties:
            for i in listSpecialties:
                strAll += f'{specialties[i].name}, '
            strAll += specialties[specialty].name
            listSpecialties.append(specialty)
            await callback.message.edit_text(f'Выбрано: {strAll}',
                                             reply_markup=await kbInline.getKeyboardSpecialties(specialties, page,
                                                                                                True))
        else:
            listSpecialties.remove(specialty)
            if listSpecialties:
                for i in listSpecialties:
                    strAll += f', {specialties[i].name}'
                strAll = strAll[2:]
                await callback.message.edit_text(f'Выбрано: {strAll}',
                                                 reply_markup=await kbInline.getKeyboardSpecialties(specialties, page,
                                                                                                    True))
            else:
                await callback.message.edit_text('Не выбраны',
                                                 reply_markup=await kbInline.getKeyboardSpecialties(specialties, page,
                                                                                                    True))

    except:
        listSpecialties = [specialty]
        await callback.message.edit_text(f'Выбрано: {specialties[specialty].name}',
                                         reply_markup=await kbInline.getKeyboardSpecialties(specialties, page, True))
    await state.update_data(specialty=listSpecialties)


async def acceptSpecialties(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        listSpecialties = data['specialty']
        await state.set_state(AddDoctor.work_experience)
        await callback.message.edit_text('Напишите опыт работы в годах')
    except:
        await callback.answer('Выберите минимум одну специальность')


async def addDoctorWorkExperience(message: Message, state: FSMContext):
    try:
        experience = int(message.text)
        await state.update_data(work_experience=experience)
        await state.set_state(AddDoctor.education)
        await message.answer('Напишите информацию об образовании')
    except:
        await message.answer('Неверный формат, попробуйте снова')


async def addDoctorEducation(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(AddDoctor.resume)
    await message.answer('Напишите резюме')


async def addDoctorResume(message: Message, state: FSMContext):
    await state.update_data(resume=message.text)
    await message.answer('Осуществляется ли очный прием?', reply_markup=kbInline.isFaceToFace)


async def yesIsFaceToFace(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddDoctor.data_face_to_face)
    await callback.message.edit_text('Напишите данные об очном приеме')


async def addDoctorDataFaceToFace(message: Message, state: FSMContext):
    await state.update_data(data_face_to_face=message.text)
    await state.set_state(AddDoctor.photo)
    await message.answer('Отправьте фотографию')


async def noIsFaceToFace(callback: CallbackQuery, state: FSMContext):
    await state.update_data(data_face_to_face='')
    await state.set_state(AddDoctor.photo)
    await callback.message.edit_text('Отправьте фотографию')


async def addDoctorPhoto(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(AddDoctor.price)
    await message.answer('Напишите стоимость консультации')


async def addDoctorPrice(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await state.set_state(AddDoctor.achievements)
        await message.answer('Напишите достижения')
    except:
        await message.answer('Неверный формат, попробуйте снова')


async def addDoctorAchievements(message: Message, state: FSMContext):
    await state.update_data(achievements=message.text)
    await state.set_state(AddDoctor.social_networks)
    await message.answer('Отправьте ссылки на социальные сети')


async def addDoctorSocialNetworks(message: Message, state: FSMContext):
    await state.update_data(social_networks=message.text)
    await state.set_state(AddDoctor.about_me)
    await message.answer('Напишите о вас')


async def addDoctorAboutMe(message: Message, state: FSMContext):
    await state.update_data(resume=message.text)
    data = await state.get_data()
    specialties = await requestsSpecialty.get_all_specialties()
    face_to_face = f'''да
<b>Данные об очном приеме:</b> {data['data_face_to_face']}''' if data['data_face_to_face'] != '' else 'нет'
    await message.answer_photo(photo=data['photo'], caption=f'''<b>ФИО:</b> {data['full_name']}
<b>Страна:</b> {data['country']}
<b>Город:</b> {data['city']}
<b>Специальность/ти:</b> {', '.join([specialties[x].name for x in data['specialty']])}
<b>Опыт работы:</b> {data['work_experience']}
<b>Образование:</b> {data['education']}
<b>Резюме:</b> {data['resume']}
<b>Осуществляется ли очный прием:</b> {face_to_face}
<b>Стоимость консультации:</b> {data['price']}
<b>Достижения:</b> {data['achievements']}
<b>Соц. сети:</b> {data['social_networks']}
<b>О себе:</b> {data['about_me']}
''', reply_markup=kbInline.isInfoTrue, parse_mode='html')


async def infoTrue(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await requestsDoctor.add_doctor(data['user_id'], data['full_name'], data['country'], data['city'],
                                    ', '.join([str(x) for x in data['specialty']]),
                                    data['work_experience'], '', data['education'], data['resume'],
                                    data['data_face_to_face'] != '', data['data_face_to_face'], data['photo'],
                                    data['price'], data['price'], data['achievements'], data['social_networks'],
                                    data['about_me'], data['bank_details_russia'], data['bank_details_abroad'], '', '',
                                    '', '', '')
    await state.clear()
    await state.set_state(Admin.admin)
    await callback.message.delete()
    await bot.send_message(chat_id=data['user_id'],
                           text='Ваша анкета врача успешно создана! Для продолжения работы нажмите на /start')
    await callback.message.answer('Анкета успешно создана!', reply_markup=kbReply.kbAdminMain)


async def infoEdit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Admin.admin)
    await addDoctor(callback, state)


async def infoDelete(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Admin.admin)
    await callback.message.delete()
    await callback.message.answer('Анкета удалена', reply_markup=kbReply.kbAdminMain)


async def deleteDoctor(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DeleteDoctor.user_id)
    await callback.message.edit_text('Напишите ID доктора')


async def deleteDoctorUserID(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        if await requestsDoctor.is_doctor(user_id):
            await state.clear()
            await state.set_state(Admin.admin)
            await requestsDoctor.delete_doctor(user_id)
            await message.answer('Анкета доктора удалена', reply_markup=kbReply.kbAdminMain)
        else:
            await message.answer('Доктор не найден, попробуйте снова')
    except:
        await message.answer('Неверный формат, попробуйте снова')
