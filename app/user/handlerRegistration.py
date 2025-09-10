from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router()

from app.businessLogic import logicRegistration
from app.businessLogic.logicRegistration import EditUser

@router.message(EditUser.setFullName)
async def regFullName(message: Message, state: FSMContext):
    await logicRegistration.regFullName(message, state)

@router.callback_query(F.data.startswith('regGender_'))
async def callback_regGender(callback: CallbackQuery, state: FSMContext):
    await logicRegistration.regGender(callback, state)


@router.message(EditUser.setAge)
async def message_regAge(message: Message, state: FSMContext):
    await logicRegistration.regAge(message, state)


@router.callback_query(F.data.startswith('country_'))
async def callback_regCountry(callback: CallbackQuery, state: FSMContext):
    await logicRegistration.regCountry(callback, state)


@router.message(EditUser.setCountry)
async def message_regCountryOwn(message: Message, state: FSMContext):
    await logicRegistration.regCountryOwn(message, state)


@router.callback_query(F.data.startswith('city_'))
async def callback_regCity(callback: CallbackQuery, state: FSMContext):
    await logicRegistration.regCity(callback, state)


@router.message(EditUser.setCity)
async def message_regCityOwn(message: Message, state: FSMContext):
    await logicRegistration.regCityOwn(message, state)


@router.callback_query(F.data.startswith('cross_'))
async def callback_cross(callback: CallbackQuery, state: FSMContext):
    await logicRegistration.cross(callback, state)
