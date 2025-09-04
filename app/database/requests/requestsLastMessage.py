from sqlalchemy import select, update

from app.database.models import LastMessage
from app.database.models import async_session



async def add_last_message(text: str, function: str):
    async with async_session() as session:
        session.add(LastMessage(text=text, function=function))
        await session.commit()


async def delete_last_message(id: int):
    async with async_session() as session:
        result = await session.scalar(select(LastMessage).where(LastMessage.id == id))
        if result:
            await session.delete(result)
            await session.commit()
            return True
        return False


async def delete_last_message_by_function(function: str):
    async with async_session() as session:
        result = await session.scalar(select(LastMessage).where(LastMessage.function == function))
        if result:
            await session.delete(result)
            await session.commit()
            return True
        return False

async def edit_last_message_by_function(text:str, function: str):
    async with async_session() as session:
        result = await session.execute(update(LastMessage).where(LastMessage.function == function).values(text=text))
        return result.rowcount > 0


async def is_last_message_by_function(function: str):
    async with async_session() as session:
        result = await session.scalar(select(LastMessage).where(LastMessage.function == function))
        return result != None


async def get_last_message_by_function(function: str):
    async with async_session() as session:
        result = await session.scalar(select(LastMessage).where(LastMessage.function == function))
        return result










