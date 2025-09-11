from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.requests import requestsPhotoAndFile
from app.keyboards import kbReply


async def start(message: Message, state: FSMContext):
    await state.clear()
    photo = (await requestsPhotoAndFile.get_photo_or_file_by_function('start')).media_id
    await message.answer(text='''Врач для каждого / Doc for everyone»- место, где собрались доктора и специалисты по здоровью со всего мира. Нас объединяет простая, но важная мечта: сделать медицину доступной каждому, где бы вы ни жили, во что верили и какими бы средствами ни располагали.

Вместе мы верим, что расстояние между врачом и вами можно сократить до одного сообщения. И даже маленький шаг — например, рассказать о нас друзьям или добавить близких в наши чаты — может однажды стать большим спасением. 💙

Быть здоровым - право каждого!


Мы сочетаем экспертный подход с человечностью — здесь вы можете:
▪️ Выбрать профильного врача и обсудить с ним волнующие вопросы
▪️ Посмотреть историю консультаций и продолжить уже завершенную консультацию при необходимости.
▪️ Обсудить ваше состояние анонимно — врач не видит ваше ФИО, а только пол, возраст и суть вашего обращения
''', reply_markup=await kbReply.kbPatientMain(message.from_user.id))


async def returnToMenu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('Вы вернулись в главное меню',
                                  reply_markup=await kbReply.kbPatientMain(callback.from_user.id))


async def unknown_message(message: Message, state: FSMContext):
    """Обработчик для неизвестных сообщений"""
    await state.clear()
    await message.answer(
        '❌ Что-то пошло не так. Пожалуйста, используйте кнопки меню для навигации.',
        reply_markup=await kbReply.kbPatientMain(message.from_user.id)
    )


async def unknown_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик для неизвестных callback запросов"""
    await state.clear()
    await callback.answer('❌ Что-то пошло не так. Пожалуйста, используйте кнопки меню для навигации.')
    await callback.message.answer(
        '❌ Что-то пошло не так. Пожалуйста, используйте кнопки меню для навигации.',
        reply_markup=await kbReply.kbPatientMain(callback.from_user.id)
    )


async def unknown_command(message: Message, state: FSMContext):
    """Обработчик для неизвестных команд"""
    await state.clear()
    await message.answer(
        '❌ Неизвестная команда. Пожалуйста, используйте кнопки меню для навигации.',
        reply_markup=await kbReply.kbPatientMain(message.from_user.id)
    )