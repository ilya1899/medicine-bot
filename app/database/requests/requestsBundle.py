from sqlalchemy import select, update

from app.database.models import async_session
from app.database.models import Bundle


async def add_bundle(patient_id: int, doctor_id: int, chat_type: str, id_consultation: int):
    async with async_session() as session:
        session.add(Bundle(patient_id=patient_id, doctor_id=doctor_id, is_open_dialog_patient=False,
                           is_open_dialog_doctor=False, chat_type=chat_type, id_consultation=id_consultation))
        await session.commit()


async def delete_bundle(patient_id: int, doctor_id: int):
    async with async_session() as session:
        bundle = await session.scalar(select(Bundle).where((Bundle.patient_id == patient_id) &
                                                           (Bundle.doctor_id == doctor_id)))
        if bundle:
            await session.delete(bundle)
            await session.commit()
            return True
        return False


async def edit_is_open_dialog_patient(patient_id: int, doctor_id: int, is_open_dialog_patient: bool):
    async with async_session() as session:
        result = await session.execute(update(Bundle).where((Bundle.patient_id == patient_id) &
                                                            (Bundle.doctor_id == doctor_id)).values(
            is_open_dialog_patient=is_open_dialog_patient))

        await session.commit()
        return result.rowcount > 0


async def edit_is_open_dialog_doctor(patient_id: int, doctor_id: int, is_open_dialog_doctor: bool):
    async with async_session() as session:
        result = await session.execute(update(Bundle).where((Bundle.patient_id == patient_id) &
                                                            (Bundle.doctor_id == doctor_id)).values(
            is_open_dialog_doctor=is_open_dialog_doctor))

        await session.commit()
        return result.rowcount > 0


async def is_open_dialog_patient(patient_id: int, doctor_id: int):
    async with async_session() as session:
        bundle = await session.scalar(select(Bundle).where((Bundle.patient_id == patient_id) &
                                                           (Bundle.doctor_id == doctor_id)))
        return bundle.is_open_dialog_patient


async def is_open_dialog_doctor(patient_id: int, doctor_id: int):
    async with async_session() as session:
        bundle = await session.scalar(select(Bundle).where((Bundle.patient_id == patient_id) &
                                                           (Bundle.doctor_id == doctor_id)))
        return bundle.is_open_dialog_doctor


async def is_bundle(patient_id: int, doctor_id: int):
    async with async_session() as session:
        bundle = await session.scalar(select(Bundle).where((Bundle.patient_id == patient_id) &
                                                           (Bundle.doctor_id == doctor_id)))
        return bundle != None


async def is_bundle_by_patient_id(patient_id: int):
    async with async_session() as session:
        bundle = await session.scalar(select(Bundle).where(Bundle.patient_id == patient_id))
        return bundle != None


async def get_bundles_by_doctor_id(doctor_id: int):
    async with async_session() as session:
        bundles = (await session.scalars(select(Bundle).where(Bundle.doctor_id == doctor_id))).all()
        return bundles


async def get_bundles_by_patient_id(patient_id: int):
    async with async_session() as session:
        bundles = (await session.scalars(select(Bundle).where(Bundle.patient_id == patient_id))).all()
        return bundles


async def get_chat_type(patient_id: int, doctor_id: int):
    async with async_session() as session:
        bundle = await session.scalar(select(Bundle).where((Bundle.patient_id == patient_id) &
                                                           (Bundle.doctor_id == doctor_id)))
        if bundle:
            return bundle.chat_type
        return ''


async def get_id_consultation(patient_id: int, doctor_id: int):
    async with async_session() as session:
        bundle = await session.scalar(select(Bundle).where((Bundle.patient_id == patient_id) &
                                                           (Bundle.doctor_id == doctor_id)))
        if bundle:
            return bundle.id_consultation
        return ''


async def is_dialog_open_for_patient(patient_id: int, doctor_id: int) -> bool:
    async with async_session() as session:
        bundle = await session.scalar(
            select(Bundle).where(Bundle.patient_id == patient_id, Bundle.doctor_id == doctor_id)
        )
        return bundle and bundle.is_open_dialog_patient


async def get_last_bundle_by_doctor(doctor_id: int):
    async with async_session() as session:
        res = await session.scalars(
            select(Bundle).where(Bundle.doctor_id == doctor_id).order_by(Bundle.id.desc())
        )
        return res.first()


async def get_bundle(patient_id: int, doctor_id: int):
    async with async_session() as session:
        return await session.scalar(
            select(Bundle).where(Bundle.patient_id == patient_id, Bundle.doctor_id == doctor_id)
        )
