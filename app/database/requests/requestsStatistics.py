from sqlalchemy import select, update
from app.database.models import Statistics
from app.database.models import async_session


async def add_data(patient_id: int, doctor_id: int, type_of_consultation: str, specialty: str):
    async with async_session() as session:
        session.add(Statistics(patient_id=patient_id, doctor_id=doctor_id, type_of_consultation=type_of_consultation,
                               specialty=specialty))
        await session.commit()


async def delete_data(id: int):
    async with async_session() as session:
        record = await session.scalar(select(Statistics).where(Statistics.id == id))
        if record:
            await session.delete(record)
            await session.commit()
            return True
        return False


async def get_data_by_patient_id(patient_id: int):
    async with async_session() as session:
        records = await session.scalars(select(Statistics).where(Statistics.patient_id == patient_id))
        return records.all()


async def get_data_by_doctor_id(doctor_id: int):
    async with async_session() as session:
        records = await session.scalars(select(Statistics).where(Statistics.doctor_id == doctor_id))
        return records.all()


async def get_data_by_specialty(specialty: str):
    async with async_session() as session:
        records = await session.scalars(
            select(Statistics).where(Statistics.specialty == specialty).order_by(Statistics.specialty))
        return records.all()


async def get_data_by_type_of_consultation(type_of_consultation: str):
    async with async_session() as session:
        records = await session.scalars(
            select(Statistics).where(Statistics.type_of_consultation == type_of_consultation))
        return records.all()
