from sqlalchemy import select

from app.database.models import async_session, Admin


async def add_admin(user_id: int):
    async with async_session() as session:
        session.add(Admin(user_id=user_id))
        await session.commit()


async def is_admin(user_id: int):
    async with async_session() as session:
        result = await session.scalar(select(Admin).where(Admin.user_id == user_id))
        return result is not None


async def delete_admin(user_id: int):
    async with async_session() as session:
        admin = await session.scalar(select(Admin).where(Admin.user_id == user_id))
        if admin:
            await session.delete(admin)
            await session.commit()
            return True
        return False
