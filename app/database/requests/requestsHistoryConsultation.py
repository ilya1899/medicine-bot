from sqlalchemy import select, update

from app.database.models import HistoryConsultation, HistoryMessage
from app.database.models import async_session


async def add_consultation(name: str, patient_id: int, doctor_id: int, chat_type: str, specialty: str):
    async with async_session() as session:
        session.add(HistoryConsultation(name=name, patient_id=patient_id, doctor_id=doctor_id, chat_type=chat_type,
                                        specialty=specialty))
        await session.commit()


async def delete_consultation(id: int):
    async with async_session() as session:
        consultation = await session.scalar(select(HistoryConsultation).where(HistoryConsultation.id == id))
        if consultation:
            await session.delete(consultation)
            await session.commit()
            return True
        return False


async def is_consultation(id: int):
    async with async_session() as session:
        consultation = await session.scalar(select(HistoryConsultation).where(HistoryConsultation.id == id))
        return consultation != None


async def get_consultation(id: int):
    async with async_session() as session:
        consultation = await session.scalar(select(HistoryConsultation).where(HistoryConsultation.id == id))
        return consultation


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
    async with async_session() as session:
        messages = (await session.scalars(
            select(HistoryMessage)
            .where(HistoryMessage.id_consultation == consultation_id)
            .order_by(HistoryMessage.id)
        )).all()
        return messages
