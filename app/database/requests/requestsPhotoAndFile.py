from sqlalchemy import select, update

from app.database.models import PhotoAndFile
from app.database.models import async_session



async def add_photo_or_file(media_id: str, function: str):
    async with async_session() as session:
        session.add(PhotoAndFile(media_id=media_id, function=function))
        await session.commit()


async def delete_photo_or_file(id: int):
    async with async_session() as session:
        result = await session.scalar(select(PhotoAndFile).where(PhotoAndFile.id == id))
        if result:
            await session.delete(result)
            await session.commit()
            return True
        return False


async def delete_photo_or_file_by_function(function: str):
    async with async_session() as session:
        result = await session.scalar(select(PhotoAndFile).where(PhotoAndFile.function == function))
        if result:
            await session.delete(result)
            await session.commit()
            return True
        return False


async def is_photo_or_file_by_function(function: str):
    async with async_session() as session:
        result = await session.scalar(select(PhotoAndFile).where(PhotoAndFile.function == function))
        return result != None


async def get_photo_or_file_by_function(function: str):
    async with async_session() as session:
        result = await session.scalar(select(PhotoAndFile).where(PhotoAndFile.function == function))
        return PhotoAndFile()










