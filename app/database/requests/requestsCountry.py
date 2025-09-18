from sqlalchemy import select, update
from app.database.models import Country
from app.database.models import async_session


async def add_country(name: str):
    async with async_session() as session:
        session.add(Country(name=name))
        await session.commit()


async def delete_country(name: str):
    async with async_session() as session:
        country = await session.scalar(select(Country).where(Country.name == name))
        if country:
            await session.delete(country)
            await session.commit()
            return True
        return False


async def get_name(id: int):
    async with async_session() as session:
        country = await session.scalar(select(Country).where(Country.id == id))
        if country:
            return country.name
        return ''


async def get_country_by_name(name: str):
    async with async_session() as session:
        country = await session.scalar(select(Country).where(Country.name == name))
        return country


async def get_country_by_id(id: int):
    async with async_session() as session:
        country = await session.scalar(select(Country).where(Country.id == id))
        return country


async def get_all_countries():
    async with async_session() as session:
        countries = await session.scalars(select(Country).order_by(Country.name))
        return countries.all()


async def is_country_by_name(name: str):
    async with async_session() as session:
        country = await session.scalar(select(Country).where(Country.name == name))
        return country is not None
