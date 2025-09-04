import aiogram
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext



router = Router()


class StatisticsOne(StatesGroup):
    doctor = State()



from app.businessLogic.admin.logicAdmin import Admin
from app.keyboards import kbReply, kbInline
from app.database.requests import requestsStatistics, requestsSpecialty


@router.message(F.text == 'Статистика', Admin.admin)
async def message_statistics(message: Message):
    await message.answer('Выберите параметр', reply_markup=kbInline.statisticsParameters)


@router.callback_query(F.data == 'statisticsTypeConsultations')
async def callback_statisticsTypeConsultation(callback: CallbackQuery):
    await callback.message.edit_text('Выберите диапазон', reply_markup=await kbInline.statisticsPeople('typeConsultations'))

@router.callback_query(F.data == 'statisticsSpecialty')
async def callback_statisticsTypeConsultation(callback: CallbackQuery):
    await callback.message.edit_text('Выберите диапазон', reply_markup=await kbInline.statisticsPeople('specialty'))


@router.callback_query(F.data.startswith('statisticsAll_'))
async def callback_statisticsAll(callback: CallbackQuery):
    parameter = callback.data.split('_')[1]
    match parameter:
        case 'typeConsultations':
            await callback.message.delete()
            await callback.message.answer(f'''<b>Количество выборов консультаций:</b>

Просто спросить: {len(await requestsStatistics.get_data_by_type_of_consultation('justAsk'))}
Расшифровка анализов: {len(await requestsStatistics.get_data_by_type_of_consultation('decoding'))}
Обычная консультация: {len(await requestsStatistics.get_data_by_type_of_consultation('main'))}
Второе мнение: {len(await requestsStatistics.get_data_by_type_of_consultation('secondOpinion'))}
Очный прием: {len(await requestsStatistics.get_data_by_type_of_consultation('faceToFace'))}
''', parse_mode='html', reply_markup=kbReply.kbAdminMain)
        case 'specialty':
            specialties = await requestsSpecialty.get_all_specialties()
            strAll = '<b>Количество выборов специальностей:</b>\n\n'
            for specialty in specialties:
                strAll += specialty.name + ': ' + str(len(await requestsStatistics.get_data_by_specialty(specialty.name))) + '\n'
            await callback.message.delete()
            await callback.message.answer(strAll, parse_mode='html', reply_markup=kbReply.kbAdminMain)


@router.callback_query(F.data.startswith('statisticsOneDoctor_'))
async def callback_statisticsOneDoctor(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StatisticsOne.doctor)
    await state.update_data(parameter=callback.data.split('_')[1])
    await callback.message.edit_text('Введите ID доктора')


def getStatistisc(parameter, value, data):
    counter = 0
    match parameter:
        case 'typeConsultations':
            for oneData in data:
                if oneData.type_of_consultation == value:
                    counter += 1
        case 'specialty':
            for oneData in data:
                if oneData.specialty == value:
                    counter += 1
    return counter


@router.message(StatisticsOne.doctor)
async def message_statisticsOneDoctor(message: Message, state: FSMContext):
    data = await state.get_data()
    parameter = data['parameter']
    await state.clear()
    await state.set_state(Admin.admin)
    try:
        doctor_id = int(message.text)
        statistics = await requestsStatistics.get_data_by_doctor_id(doctor_id)
        match parameter:
            case 'typeConsultations':
                await message.answer(f'''<b>Количество выборов консультаций:</b>

Просто спросить: {getStatistisc(parameter, 'justAsk', statistics)}
Расшифровка анализов: {getStatistisc(parameter, 'decoding', statistics)}
Обычная консультация: {getStatistisc(parameter, 'main', statistics)}
Второе мнение: {getStatistisc(parameter, 'secondOpinion', statistics)}
Очный прием: {getStatistisc(parameter, 'faceToFace', statistics)}
''', parse_mode='html', reply_markup=kbReply.kbAdminMain)
            case 'specialty':
                specialties = await requestsSpecialty.get_all_specialties()
                strAll = '<b>Количество выборов специальностей:</b>\n\n'
                for specialty in specialties:
                    strAll += specialty.name + ': ' + str(getStatistisc(parameter, specialty.name, statistics)) + '\n'
                await message.answer(strAll, parse_mode='html', reply_markup=kbReply.kbAdminMain)
    except:
        await message.answer('Произошла ошибка', reply_markup=kbReply.kbAdminMain)












