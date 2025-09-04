from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.database.requests import requestsDoctor

async def kbPatientMain(user_id):
    if await requestsDoctor.is_doctor(user_id):
        kbPatientMain = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='О нас'), KeyboardButton(text='Задать вопрос врачу')],
            [KeyboardButton(text='Частые вопросы'), KeyboardButton(text='История консультаций')],
            [KeyboardButton(text='Сотрудничество'), KeyboardButton(text='Поддержать проект')],
            [KeyboardButton(text='Перейти в кабинет врача')]
        ], resize_keyboard=True, one_time_keyboard=True)
    else:
        kbPatientMain = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='О нас'), KeyboardButton(text='Задать вопрос врачу')],
            [KeyboardButton(text='Частые вопросы'), KeyboardButton(text='История консультаций')],
            [KeyboardButton(text='Сотрудничество'), KeyboardButton(text='Поддержать проект')]
        ], resize_keyboard=True, one_time_keyboard=True)
    return kbPatientMain



kbPatientDialog = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Свернуть диалог')],
    [KeyboardButton(text='Завершить консультацию')]
], resize_keyboard=True, one_time_keyboard=True)

kbDoctorMain = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Консультации'), KeyboardButton(text='Личный кабинет')],
    [KeyboardButton(text='Перейти в аккаунт пользователя')]
], resize_keyboard=True, one_time_keyboard=True)

kbDoctorDialog1 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Свернуть диалог')]
], resize_keyboard=True)

kbDoctorDialog2 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Свернуть диалог')],
    [KeyboardButton(text='Завершить консультацию')]
], resize_keyboard=True)



kbAdminMain = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отзывы'), KeyboardButton(text='Рассылка')],
    [KeyboardButton(text='Обратная связь'), KeyboardButton(text='Статистика')],
    [KeyboardButton(text='Специальности'), KeyboardButton(text='Изменить фото/файл')],
    [KeyboardButton(text='Изменить текст')],
    [KeyboardButton(text='На главную')]
], resize_keyboard=True, one_time_keyboard=True)

# KeyboardButton(text='Сотрудничество') KeyboardButton(text='Текст консультаций')

# , KeyboardButton(text='Врачи')






