from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router()

from app.businessLogic.admin import logicEditDoctors
from app.businessLogic.admin.logicEditDoctors import Admin, AddDoctor, DeleteDoctor


@router.message(F.text == 'Врачи', Admin.admin)
async def message_editDoctors(message: Message):
    await logicEditDoctors.editDoctors(message)

@router.callback_query(F.data == 'addDoctor')
async def callback_addDoctor(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.addDoctor(callback, state)

@router.message(AddDoctor.user_id)
async def message_addDoctorUserID(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorUserID(message, state)

@router.message(AddDoctor.full_name)
async def message_addDoctorFullName(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorFullName(message, state)


@router.callback_query(F.data.startswith('country_'), AddDoctor.country)
async def callback_addDoctorCountry(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.addDoctorCountry(callback, state)

@router.callback_query(F.data.startswith('city_'), AddDoctor.city)
async def callback_addDoctorCity(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.addDoctorCity(callback, state)

@router.callback_query(F.data.startswith('specialty_'), AddDoctor.specialty)
async def callback_addDoctorSpecialty(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.addDoctorSpecialty(callback, state)

@router.callback_query(F.data == 'acceptSpecialties')
async def callback_acceptSpecialties(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.acceptSpecialties(callback, state)

@router.message(AddDoctor.work_experience)
async def message_addDoctorWorkExperience(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorWorkExperience(message, state)

@router.message(AddDoctor.education)
async def message_addDoctorEducation(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorEducation(message, state)

@router.message(AddDoctor.resume)
async def message_addDoctorResume(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorResume(message, state)

@router.callback_query(F.data == 'yesIsFaceToFace')
async def callback_yesIsFaceToFace(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.yesIsFaceToFace(callback, state)

@router.message(AddDoctor.data_face_to_face)
async def message_addDoctorDataFaceToFace(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorDataFaceToFace(message, state)

@router.callback_query(F.data == 'noIsFaceToFace')
async def callback_noIsFaceToFace(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.noIsFaceToFace(callback, state)

@router.message(F.photo, AddDoctor.photo)
async def message_addDoctorPhoto(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorPhoto(message, state)

@router.message(AddDoctor.price)
async def message_addDoctorPrice(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorPrice(message, state)

@router.message(AddDoctor.achievements)
async def message_addDoctorAchievements(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorAchievements(message, state)

@router.message(AddDoctor.social_networks)
async def message_addDoctorSocialNetworks(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorSocialNetworks(message, state)

@router.message(AddDoctor.about_me)
async def message_addDoctorAboutMe(message: Message, state: FSMContext):
    await logicEditDoctors.addDoctorAboutMe(message, state)



@router.callback_query(F.data == 'infoTrue')
async def callback_infoTrue(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.infoTrue(callback, state)

@router.callback_query(F.data == 'infoEdit')
async def callback_infoEdit(callback: CallbackQuery, state: FSMContext):
   await logicEditDoctors.infoEdit(callback, state)

@router.callback_query(F.data == 'infoDelete')
async def callback_infoDelete(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.infoDelete(callback, state)



@router.callback_query(F.data == 'deleteDoctor')
async def callback_deleteDoctor(callback: CallbackQuery, state: FSMContext):
    await logicEditDoctors.deleteDoctor(callback, state)

@router.message(DeleteDoctor.user_id)
async def message_deleteDoctorUserID(message: Message, state: FSMContext):
    await logicEditDoctors.deleteDoctorUserID(message, state)

