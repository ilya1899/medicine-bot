from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

router = Router()

from app.database.requests import requestsDoctor, requestsUser, requestsCountry, requestsCity
from app.keyboards import kbInline


@router.callback_query(F.data == 'makeAppointment')
async def callback_makeAppointment(callback: CallbackQuery):
    patient_id = callback.from_user.id
    city = await requestsUser.get_city(patient_id)
    if city:
        await callback.message.edit_text(f'Вы ищете специалиста в своем городе? ({city})',
                                         reply_markup=kbInline.makeAppointment)
    else:
        await callback_noMyCity(callback)


@router.callback_query(F.data == 'noMyCity')
async def callback_noMyCity(callback: CallbackQuery):
    doctors = await requestsDoctor.get_doctors_by_face_to_face()
    countries = [await requestsCountry.get_country_by_name(doctor.country) for doctor in doctors]
    await callback.message.edit_text('Выберите страну',
                                     reply_markup=await kbInline.getKeyboardCountryOrCity(countries,
                                                                                          'makeAppointmentCountry'))


@router.callback_query(F.data.startswith('makeAppointmentCountry_'))
async def callback_makeAppointmentCountry(callback: CallbackQuery):
    doctors = await requestsDoctor.get_doctors_by_face_to_face()
    country_id = int(callback.data.split('_')[1])
    citiesBefore = await requestsCity.get_all_cities_by_country_id(country_id)
    cities = []
    for doctor in doctors:
        for city in citiesBefore:
            if doctor.city == city.name:
                cities.append(city)
    if cities:
        await callback.message.edit_text('Выберите город',
                                         reply_markup=await kbInline.getKeyboardCountryOrCity(callback,
                                                                                              'makeAppointmentCity'))
    else:
        await callback.message.edit_text('Города с врачами, принимающими очно, не найдены',
                                         reply_markup=await kbInline.getKeyboardForFAQ(6))
