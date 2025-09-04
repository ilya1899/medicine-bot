from sqlalchemy import select, update
from app.database.models import City
from app.database.models import async_session




async def add_city(name: str, id_country: int):
    async with async_session() as session:
        session.add(City(name=name, id_country=id_country))
        await session.commit()


async def delete_city(id: int):
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.id == id))
        if city:
            await session.delete(city)
            await session.commit()
            return True
        return False





async def is_city_by_name(name: str):
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.name == name))
        return city != None





async def get_name(id: int):
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.id == id))
        if city:
            return city.name
        return ''


async def get_city_by_name(name: str):
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.name == name))
        return city

async def get_city_by_id(id: int):
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.id == id))
        return city


async def get_all_cities():
    async with async_session() as session:
        cities = await session.scalars(select(City).order_by(City.name))
        return cities.all()


async def get_all_cities_by_country_id(id_country: int):
    async with async_session() as session:
        cities = await session.scalars(select(City).where(City.id_country == id_country).order_by(City.name))
        return cities.all()

















