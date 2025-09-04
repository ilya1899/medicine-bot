from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext



router = Router()

class WriteMailingMessage(StatesGroup):
    text = State()
    button_text = State()
    button_url = State()
    countries = State()
    cities = State()




from app.database.requests import requestsUser, requestsCountry, requestsCity
from app.keyboards import kbReply, kbInline
from app.businessLogic.admin.logicAdmin import Admin
from run import bot


@router.message(F.text == 'Рассылка', Admin.admin)
async def message_mailing(message: Message):
    await message.answer('Выберите область действия', reply_markup=kbInline.mailingCommand)


@router.callback_query(F.data == 'mailingAllUsers')
async def callback_mailingAllUsers(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WriteMailingMessage.text)
    await state.update_data(type='all')
    await callback.message.edit_text('Напишите текст сообщения')


async def mailingPlace(callback, state, requests, function, text):
    data = await state.get_data()
    place = await requests.get_name(int(callback.data.split('_')[1]))
    places = data['places']
    if place not in places:
        places.append(place)
        await state.update_data(places=places)
        await callback.message.edit_text('\n'.join(places),
                                         reply_markup=await kbInline.getKeyboardCountryOrCity(await function(),
                                                                                              text))
    else:
        if len(places) > 1:
            places.remove(place)
            await state.update_data(places=places)
            await callback.message.edit_text('\n'.join(places),
                                             reply_markup=await kbInline.getKeyboardCountryOrCity(await function(),
                                                                                                  text))
        else:
            await state.update_data(places=[])
            await callback.message.edit_text('Ничего не выбрано',
                                             reply_markup=await kbInline.getKeyboardCountryOrCity(await function(),
                                                                                                  text))


@router.callback_query(F.data == 'mailingCountries')
async def callback_mailingCountries(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WriteMailingMessage.countries)
    await state.update_data(places=[])
    await callback.message.edit_text('Выберите страны для рассылки',
                                     reply_markup=await kbInline.getKeyboardCountryOrCity(await requestsCountry.get_all_countries(),
                                                                                          'mailingCountry'))

@router.callback_query(F.data.startswith('mailingCountry_'))
async def callback_mailingCountry(callback: CallbackQuery, state: FSMContext):
    await mailingPlace(callback, state, requestsCountry, requestsCountry.get_all_countries, 'mailingCountry')

@router.callback_query(F.data == 'mailingCountryContinue')
async def callback_mailingCountryContinue(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['places']:
        await state.set_state(WriteMailingMessage.text)
        await state.update_data(type='countries')
        await callback.message.edit_text('Напишите текст сообщения')
    else:
        await callback.answer('Выберите хотя бы одну страну!')



@router.callback_query(F.data == 'mailingCities')
async def callback_mailingCities(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WriteMailingMessage.cities)
    await state.update_data(places=[])
    await callback.message.edit_text('Выберите города для рассылки',
                                     reply_markup=await kbInline.getKeyboardCountryOrCity(await requestsCity.get_all_cities(),
                                                                                          'mailingCity'))

@router.callback_query(F.data.startswith('mailingCity_'))
async def callback_mailingCity(callback: CallbackQuery, state: FSMContext):
    await mailingPlace(callback, state, requestsCity, requestsCity.get_all_cities, 'mailingCity')

@router.callback_query(F.data == 'mailingCityContinue')
async def callback_mailingCityContinue(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['places']:
        await state.set_state(WriteMailingMessage.text)
        await state.update_data(type='cities')
        await callback.message.edit_text('Напишите текст сообщения')
    else:
        await callback.answer('Выберите хотя бы один город!')


@router.message(WriteMailingMessage.text)
async def message_mailingText(message: Message, state: FSMContext):
    await state.update_data(text=message.html_text)
    await message.answer('Добавлять кнопку?', reply_markup=kbInline.addButtonToMailinMessage)

@router.callback_query(F.data == 'mailingAddButton')
async def callback_mailingAddButton(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WriteMailingMessage.button_text)
    await callback.message.edit_text('Напишите текст кнпоки')

@router.message(WriteMailingMessage.button_text)
async def message_mailingButtonText(message: Message, state: FSMContext):
    await state.set_state(WriteMailingMessage.button_url)
    await state.update_data(button_text=message.text)
    await message.answer('Напишите URL-ссылку для кнопки (обязательно проверьте ее корректность)')

@router.message(WriteMailingMessage.button_url)
async def message_mailingButtonURL(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        id = await message.answer(data['text'],
                             reply_markup=await kbInline.getKeyboardMailingButton(data['button_text'], message.text),
                             parse_mode='html')
        await state.update_data(id=id.message_id, button_url=message.text)
        await message.answer('Все ли верно?', reply_markup=kbInline.mailingSend)
    except:
        await message.answer('Неверный URL-адрес, попробуйте снова', reply_markup=kbInline.returnToAdminMenu)


@router.callback_query(F.data == 'mailingNotAddButton')
async def callback_mailingNotAddButton(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = await callback.message.edit_text(data['text'], parse_mode='html')
    await state.update_data(id=id.message_id)
    await callback.message.answer('Все ли верно?', reply_markup=kbInline.mailingSend)



@router.callback_query(F.data == 'mailingSend')
async def callback_mailingSend(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=callback.from_user.id, message_id=data['id'])
    listMailing = []
    match data['type']:
        case 'all':
            listMailing = await requestsUser.get_user_without_doctors()
        case 'countries':
            for country in data['places']:
                listMailing.extend(await requestsUser.get_users_by_country(country))
        case 'cities':
            for city in data['places']:
                listMailing.extend(await requestsUser.get_users_by_city(city))

    if data.get('button_text'):
        for user in listMailing:
            try:
              await bot.send_message(chat_id=user.user_id,
                                   text=data['text'],
                                   reply_markup=await kbInline.getKeyboardMailingButton(data['button_text'],
                                                                                        data['button_url']))
            except:
                pass
    else:
        for user in listMailing:
            try:
                await bot.send_message(chat_id=user.user_id,
                                   text=data['text'])
            except:
                pass

    await callback.message.delete()
    await callback.message.answer('Рассылка завершена', reply_markup=kbReply.kbAdminMain)






