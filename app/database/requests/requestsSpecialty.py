from typing import List

from sqlalchemy import select
from app.database.models import Specialty, HistoryConsultation
from app.database.models import async_session


async def add_specialty(name: str):
    async with async_session() as session:
        session.add(Specialty(name=name))
        await session.commit()


async def delete_specialty(name: str):
    async with async_session() as session:
        specialty = await session.scalar(select(Specialty).where(Specialty.name == name))
        if specialty:
            await session.delete(specialty)
            await session.commit()
            return True
        return False


async def get_specialty_by_id(id: int):
    async with async_session() as session:
        specialty = await session.scalar(select(Specialty).where(Specialty.id == id))
        return specialty


async def get_specialty_by_name(name: str):
    async with async_session() as session:
        specialty = await session.scalar(select(Specialty).where(Specialty.name == name))
        return specialty


async def get_all_specialties():
    async with async_session() as session:
        specialties = await session.scalars(select(Specialty).order_by(Specialty.name))
        return specialties.all()


async def is_specialty_by_name(name: str):
    async with async_session() as session:
        specialty = await session.scalar(select(Specialty).where(Specialty.name == name))
        return specialty != None


async def get_specialties_by_patient(patient_id: int) -> List[Specialty]:
    async with async_session() as session:
        result = await session.scalars(
            select(Specialty)
            .join(HistoryConsultation, HistoryConsultation.specialty == Specialty.name)
            .where(HistoryConsultation.patient_id == patient_id)
            .distinct()
            .order_by(Specialty.name)
        )
        return result.all()
