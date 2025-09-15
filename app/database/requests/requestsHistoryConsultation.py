import logging

from sqlalchemy import select, update, desc

from app.database.models import HistoryConsultation, HistoryMessage, Bundle
from app.database.models import async_session

logger = logging.getLogger(__name__)


async def add_consultation(name: str, patient_id: int, doctor_id: int, chat_type: str, specialty: str):
    try:
        async with async_session() as session:
            session.add(HistoryConsultation(name=name, patient_id=patient_id, doctor_id=doctor_id, chat_type=chat_type,
                                            specialty=specialty))
            logger.info(
                f'Add {HistoryConsultation(name=name, patient_id=patient_id, doctor_id=doctor_id, chat_type=chat_type, specialty=specialty)}')
            await session.commit()
    except Exception as e:
        raise


async def delete_consultation(id: int):
    try:
        async with async_session() as session:
            consultation = await session.scalar(select(HistoryConsultation).where(HistoryConsultation.id == id))
            logger.info(f'Get consultation {consultation}')
            if consultation:
                await session.delete(consultation)
                logger.info(f'Delete consultation {consultation}')
                await session.commit()
                return True
            return False
    except Exception as e:
        raise


async def is_consultation(id: int):
    try:
        async with async_session() as session:
            consultation = await session.scalar(select(HistoryConsultation).where(HistoryConsultation.id == id))
            return consultation is not None
    except Exception as e:
        raise


async def get_consultation(id: int):
    try:
        async with async_session() as session:
            consultation = await session.scalar(select(HistoryConsultation).where(HistoryConsultation.id == id))
            return consultation
    except Exception as e:
        raise


async def get_all_consultations_by_patient_and_doctor_id(patient_id: int, doctor_id: int):
    async with async_session() as session:
        consultations = await session.scalars(select(HistoryConsultation)
                                              .where((HistoryConsultation.patient_id == patient_id) &
                                                     (HistoryConsultation.doctor_id == doctor_id))
                                              .order_by(HistoryConsultation.id))
        return consultations.all()


async def get_all_consultations_by_patient_doctor_id_and_type(patient_id: int, doctor_id: int, chat_type: str):
    async with async_session() as session:
        consultations = await session.scalars(select(HistoryConsultation)
                                              .where((HistoryConsultation.patient_id == patient_id) &
                                                     (HistoryConsultation.doctor_id == doctor_id) &
                                                     (HistoryConsultation.chat_type == chat_type))
                                              .order_by(HistoryConsultation.id))
        return consultations.all()


async def get_all_consultations_by_patient_id(patient_id: int):
    async with async_session() as session:
        consultations = await session.scalars(select(HistoryConsultation)
                                              .where(HistoryConsultation.patient_id == patient_id)
                                              .order_by(HistoryConsultation.id))
        return consultations.all()


async def get_last_id_consultation(patient_id: int):
    async with async_session() as session:
        consultations = (await session.scalars(select(HistoryConsultation)
                                               .where(HistoryConsultation.patient_id == patient_id)
                                               .order_by(HistoryConsultation.id))).all()
        return consultations[-1].id


async def get_messages_by_consultation_id(consultation_id: int):
    try:
        async with async_session() as session:
            messages = (await session.scalars(
                select(HistoryMessage)
                .where(HistoryMessage.id_consultation == consultation_id)
                .order_by(HistoryMessage.id)
            )).all()
            return messages if messages else []
    except Exception as e:
        print(f"Error in get_messages_by_consultation_id: {e}")
        return []


async def get_latest_consultation(doctor_id: int, patient_id: int):
    try:
        async with async_session() as session:
            result = await session.scalars(
                select(HistoryConsultation)
                .where(
                    HistoryConsultation.doctor_id == doctor_id,
                    HistoryConsultation.patient_id == patient_id
                )
                .order_by(desc(HistoryConsultation.id))
                .limit(1)
            )
            return result.first()
    except Exception as e:
        print(f"Error in get_latest_consultation: {e}")
        return None


async def get_consultation_messages(doctor_id: int, patient_id: int):
    try:
        consultation = await get_latest_consultation(doctor_id, patient_id)
        if not consultation:
            return []

        async with async_session() as session:
            result = await session.scalars(
                select(HistoryMessage)
                .where(HistoryMessage.id_consultation == consultation.id)
                .order_by(HistoryMessage.id.asc())
            )
            messages = result.all()
            return messages if messages else []
    except Exception as e:
        print(f"Error in get_consultation_messages: {e}")
        return []


async def close_consultation(doctor_id: int, patient_id: int):
    async with async_session() as session:
        await session.execute(
            update(Bundle)
            .where(Bundle.doctor_id == doctor_id, Bundle.patient_id == patient_id)
            .values(is_open_dialog_patient=False, is_open_dialog_doctor=False)
        )
        await session.commit()
        return True
