from sqlalchemy import select

from app.database.models import async_session
from app.database.models import MessageToRepeat


async def add_message_to_repeat(user_1_id: int, user_2_id: int, text: str, media_type: str, media_id: str):
    async with async_session() as session:
        session.add(MessageToRepeat(user_1_id=user_1_id, user_2_id=user_2_id, text=text, media_type=media_type,
                                    media_id=media_id))
        await session.commit()


async def delete_message_to_repeat_by_id(id: int):
    async with async_session() as session:
        message = await session.scalar(select(MessageToRepeat).where(MessageToRepeat.id == id))
        if message:
            await session.delete(message)
            await session.commit()
            return True
        return False


async def delete_messages_to_repeat(user_1_id: int, user_2_id: int):
    async with async_session() as session:
        messages = await session.scalars(select(MessageToRepeat).where((MessageToRepeat.user_1_id == user_1_id) &
                                                                       (MessageToRepeat.user_2_id == user_2_id)))
        if messages:
            messages = messages.all()
            for message in messages:
                await session.delete(message)
            await session.commit()
            return True
        return False


async def is_message_to_repeat(user_1_id: int, user_2_id: int):
    async with async_session() as session:
        message = await session.scalar(select(MessageToRepeat).where((MessageToRepeat.user_1_id == user_1_id) &
                                                                     (MessageToRepeat.user_2_id == user_2_id)))
        return message != None


async def is_message_to_repeat_by_id(id: int):
    async with async_session() as session:
        message = await session.scalar(select(MessageToRepeat).where(MessageToRepeat.id == id))
        return message != None


async def get_message_to_repeat_by_id(id: int):
    async with async_session() as session:
        message = await session.scalar(select(MessageToRepeat).where(MessageToRepeat.id == id))
        return message


async def get_id_last_message_to_repeat(user_1_id: int, user_2_id: int):
    async with async_session() as session:
        messages = (await session.scalars(select(MessageToRepeat).where((MessageToRepeat.user_1_id == user_1_id) &
                                                                        (
                                                                                MessageToRepeat.user_2_id == user_2_id)))).all()
        return messages[-1].id
