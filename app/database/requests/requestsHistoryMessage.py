from sqlalchemy import select, update, desc

from app.database.models import HistoryMessage, HistoryConsultation, User
from app.database.models import async_session


async def add_message(id_consultation: int, patient_id: int, doctor_id: int, who_write: str, text: str,
                      media_type: str, media_id: str):
    async with async_session() as session:
        session.add(HistoryMessage(id_consultation=id_consultation, patient_id=patient_id, doctor_id=doctor_id,
                                   who_write=who_write, text=text, media_type=media_type, media_id=media_id))
        await session.commit()


async def delete_message(id: int):
    async with async_session() as session:
        message = await session.scalar(select(HistoryMessage).where(HistoryMessage.id == id))
        if message:
            await session.delete(message)
            await session.commit()
            return True
        return False


async def get_message(id: int):
    async with async_session() as session:
        message = await session.scalar(select(HistoryMessage).where(HistoryMessage.id == id))
        return message


async def get_all_messages_by_consultation_id(id_consultation: int):
    async with async_session() as session:
        messages = await session.scalars(select(HistoryMessage)
                                         .where(HistoryMessage.id_consultation == id_consultation)
                                         .order_by(HistoryMessage.id))
        return messages.all()


async def get_last_message_for_patient(doctor_id: int, patient_id: int):
    async with async_session() as session:
        result = await session.scalars(
            select(HistoryMessage)
            .join(HistoryConsultation, HistoryMessage.id_consultation == HistoryConsultation.id)
            .where(
                HistoryConsultation.doctor_id == doctor_id,
                HistoryConsultation.patient_id == patient_id
            )
            .order_by(desc(HistoryMessage.id))
            .limit(1)
        )
        return result.first()


async def get_last_consultation_id(patient_id: int, doctor_id: int) -> int | None:
    async with async_session() as session:
        result = await session.scalars(
            select(HistoryConsultation.id)
            .where(
                HistoryConsultation.patient_id == patient_id,
                HistoryConsultation.doctor_id == doctor_id
            )
            .order_by(desc(HistoryConsultation.id))
            .limit(1)
        )
        return result.first()


async def get_patient_info(patient_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == patient_id)
        )
        return result.scalar()

async def get_messages_by_consultation_id(consultation_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(HistoryMessage)
            .where(HistoryMessage.id_consultation == consultation_id)
            .order_by(HistoryMessage.id.asc())
        )
        return result.scalars().all()