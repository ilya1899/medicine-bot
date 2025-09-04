from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class EditUser(StatesGroup):
    setAge = State()
    setCountry = State()
    setCity = State()




from app.keyboards import kbInline
from app.database.requests import requestsUser, requestsCountry, requestsCity
from app.businessLogic import logicConsultation


async def regGender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data.split('_')[1]
    await state.update_data(gender=gender)
    await state.set_state(EditUser.setAge)
    await callback.message.edit_text('Укажите возраст')



async def regAge(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if 10 <= age <= 99:
            await state.update_data(age=age)
            countries = await requestsCountry.get_all_countries()
            await state.set_state(EditUser.setCountry)
            await message.answer('Выберите страну. Если Вашей страны нет в списке, Вы можете указать свой вариант.', reply_markup=await kbInline.getKeyboardCountryOrCity(countries, 'country'))
        else:
            await message.answer('Неверный возраст, необходимо написать число от 10 до 99. Попробуйте ещё раз.')
    except ValueError:
        await message.answer('Неверный формат, напишите число. Попробуйте ещё раз.')



async def regCountry(callback: CallbackQuery, state: FSMContext):
    country = await requestsCountry.get_country_by_id(int(callback.data.split('_')[1]))
    await state.update_data(country=country.name)

    cities = await requestsCity.get_all_cities_by_country_id(country.id)
    await state.set_state(EditUser.setCity)
    await callback.message.edit_text('Выберите город. Если Вашего города нет в списке, Вы можете указать свой вариант.', reply_markup=await kbInline.getKeyboardCountryOrCity(cities, 'city'))

async def regCountryOwn(message: Message, state: FSMContext):
    country = message.text
    await state.update_data(country=country)

    await state.set_state(EditUser.setCity)
    await message.answer('Укажите Ваш город.')


async def regCity(callback: CallbackQuery, state: FSMContext):
    city = await requestsCity.get_city_by_id(int(callback.data.split('_')[1]))
    await state.update_data(city=city.name)

    await callback.message.edit_text('''Продолжая пользоваться сервисом, вы подтверждаете, что ознакомились и даете согласие на обработку персональных данных, принимаете пользовательское соглашение и соглашаетесь с политикой конфиденциальности.

1. <b><a href="https://docs.google.com/document/d/1_9szCZrkTcqGgQtlt72eS5-qpspIjVu-Q9EUmXhxiu4/edit?tab=t.0">Согласие на обработку персональных данных</a></b>
2. <b><a href="https://docs.google.com/document/d/1G0vV1sS8sGMnsLdvxhQEJqIFlHV-DyxZMduO5DJdhYA/edit?tab=t.0#heading=h.fm4pd0evtapc">Пользовательское соглашение</a></b>
3. <b><a href="https://docs.google.com/document/d/1sveSZuZAzp5Wp4AnBXp2faUh1Zz6uPvS42Yq_NaflPg/edit?tab=t.0">Политика конфиденциальности</a></b>
''', reply_markup=await kbInline.getKeyboardForContracts([False, False, False]), parse_mode='html')

async def regCityOwn(message: Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)

    await message.answer('''Продолжая пользоваться сервисом, вы подтверждаете, что ознакомились и даете согласие на обработку персональных данных, принимаете пользовательское соглашение и соглашаетесь с политикой конфиденциальности.

1. <b><a href="https://docs.google.com/document/d/1_9szCZrkTcqGgQtlt72eS5-qpspIjVu-Q9EUmXhxiu4/edit?tab=t.0">Согласие на обработку персональных данных</a></b>
2. <b><a href="https://docs.google.com/document/d/1G0vV1sS8sGMnsLdvxhQEJqIFlHV-DyxZMduO5DJdhYA/edit?tab=t.0#heading=h.fm4pd0evtapc">Пользовательское соглашение</a></b>
3. <b><a href="https://docs.google.com/document/d/1sveSZuZAzp5Wp4AnBXp2faUh1Zz6uPvS42Yq_NaflPg/edit?tab=t.0">Политика конфиденциальности</a></b>
''', reply_markup=await kbInline.getKeyboardForContracts([False, False, False]), parse_mode='html')




async def cross(callback: CallbackQuery, state: FSMContext):
    string = callback.data.split('_')[2:]
    number = int(callback.data.split('_')[1])
    listCross = kbInline.stringCrossToList('_'.join(string))
    listCross[number] = not listCross[number]
    await callback.message.edit_text('''Продолжая пользоваться сервисом, вы подтверждаете, что ознакомились и даете согласие на обработку персональных данных, принимаете пользовательское соглашение и соглашаетесь с политикой конфиденциальности.

1. <b><a href="https://docs.google.com/document/d/1_9szCZrkTcqGgQtlt72eS5-qpspIjVu-Q9EUmXhxiu4/edit?tab=t.0">Согласие на обработку персональных данных</a></b>
2. <b><a href="https://docs.google.com/document/d/1G0vV1sS8sGMnsLdvxhQEJqIFlHV-DyxZMduO5DJdhYA/edit?tab=t.0#heading=h.fm4pd0evtapc">Пользовательское соглашение</a></b>
3. <b><a href="https://docs.google.com/document/d/1sveSZuZAzp5Wp4AnBXp2faUh1Zz6uPvS42Yq_NaflPg/edit?tab=t.0">Политика конфиденциальности</a></b>
''', reply_markup=await kbInline.getKeyboardForContracts(listCross), parse_mode='html')
    if listCross[0] and listCross[1] and listCross[2]:
        data = await state.get_data()
        await requestsUser.add_user(callback.from_user.id, data['gender'], data['age'], data['country'], data['city'])
        await logicConsultation.trueRegistration(callback, data['doctor_id'], data['index'], data['specialty'])





