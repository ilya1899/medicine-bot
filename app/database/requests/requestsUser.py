from sqlalchemy import select, update

from app.database.models import async_session
from app.database.models import User, Doctor


async def add_user(user: User):
    async with async_session() as session:
        session.add(user)
        await session.commit()


async def edit_user(user: User):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.user_id == user.user_id).values(gender=user.gender, age=user.age,
                                                                                        country=user.country, city=user.city, full_name=user.full_name))
        await session.commit()
        return user.rowcount > 0


async def edit_user_gender(user_id: int, gender: str):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.user_id == user_id).values(gender=gender))
        await session.commit()
        return user.rowcount > 0


async def edit_user_age(user_id: int, age: int):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.user_id == user_id).values(age=age))
        await session.commit()
        return user.rowcount > 0


async def edit_user_country(user_id: int, country: str):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.user_id == user_id).values(country=country))
        await session.commit()
        return user.rowcount > 0


async def edit_user_city(user_id: int, city: str):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.user_id == user_id).values(city=city))
        await session.commit()
        return user.rowcount > 0


async def delete_user(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if user:
            await session.delete(user)
            await session.commit()
            return True
        return False


async def is_user(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        return user != None


async def get_user(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        return user


async def get_city(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if user:
            return user.city
        return ''


async def get_all_users():
    async with async_session() as session:
        users = await session.scalars(select(User))
        return users.all()


async def get_user_without_doctors():
    async with async_session() as session:
        users = (await session.scalars(select(User))).all()
        doctors = (await session.scalars(select(Doctor))).all()
        total_list = []
        for user in users:
            isDoctor = False
            for doctor in doctors:
                if user.user_id == doctor.user_id:
                    isDoctor = True
                    break
            if not isDoctor:
                total_list.append(user)

        return total_list


async def get_users_by_country(country: str):
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.country == country))
        return users.all()


async def get_users_by_city(city: str):
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.city == city))
        return users.all()

async def get_user_by_id(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalars().first()
