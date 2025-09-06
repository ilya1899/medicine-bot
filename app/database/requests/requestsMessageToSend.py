from sqlalchemy import select, update

from app.database.models import async_session
from app.database.models import MessageToSend


async def add_message_to_send(user_1_id: int, user_2_id: int, text: str, media_type: str, media_id: str,
                              is_first_message: bool):
    async with async_session() as session:
        session.add(MessageToSend(user_1_id=user_1_id, user_2_id=user_2_id, text=text, media_type=media_type,
                                  media_id=media_id, is_first_message=is_first_message))
        await session.commit()


async def delete_message_to_send_by_id(id: int):
    async with async_session() as session:
        message = await session.scalar(select(MessageToSend).where(MessageToSend.id == id))
        if message:
            await session.delete(message)
            await session.commit()
            return True
        return False


async def delete_messages_to_send(user_1_id: int, user_2_id: int):
    async with async_session() as session:
        messages = await session.scalars(select(MessageToSend).where((MessageToSend.user_1_id == user_1_id) &
                                                                     (MessageToSend.user_2_id == user_2_id)))
        if messages:
            messages = messages.all()
            for message in messages:
                if not message.is_first_message:
                    await session.delete(message)
            await session.commit()
            return True
        return False


async def delete_first_message(user_1_id: int, user_2_id: int):
    async with async_session() as session:
        messages = await session.scalars(select(MessageToSend).where((MessageToSend.user_1_id == user_1_id) &
                                                                     (MessageToSend.user_2_id == user_2_id)))
        if messages:
            messages = messages.all()
            for message in messages:
                if message.is_first_message:
                    await session.delete(message)
            await session.commit()
            return True
        return False


async def is_message_to_send(user_1_id: int, user_2_id: int):
    async with async_session() as session:
        message = await session.scalar(select(MessageToSend).where((MessageToSend.user_1_id == user_1_id) &
                                                                   (MessageToSend.user_2_id == user_2_id)))
        return message != None


async def is_message_to_send_by_id(id: int):
    async with async_session() as session:
        message = await session.scalar(select(MessageToSend).where(MessageToSend.id == id))
        return message != None


async def get_message_to_send_by_id(id: int):
    async with async_session() as session:
        message = await session.scalar(select(MessageToSend).where(MessageToSend.id == id))
        return message


async def get_id_last_message_to_send(user_1_id: int, user_2_id: int):
    async with async_session() as session:
        messages = (await session.scalars(select(MessageToSend).where((MessageToSend.user_1_id == user_1_id) &
                                                                      (MessageToSend.user_2_id == user_2_id)))).all()
        return messages[-1].id


async def get_messages_to_send(user_1_id: int, user_2_id: int):
    async with async_session() as session:
        messages = (await session.scalars(select(MessageToSend).where((MessageToSend.user_1_id == user_1_id) &
                                                                      (MessageToSend.user_2_id == user_2_id)))).all()
        return messages


async def get_first_message_to_send(user_1_id: int, user_2_id: int):
    async with async_session() as session:
        messages = (await session.scalars(select(MessageToSend)
                                          .where((MessageToSend.user_1_id == user_1_id) &
                                                 (MessageToSend.user_2_id == user_2_id))
                                          .order_by(MessageToSend.id))).all()
        return messages[0]


async def get_last_message_for_patient(doctor_id: int, patient_id: int):
    async with async_session() as session:
        res = await session.scalars(
            select(MessageToSend)
            .where(MessageToSend.user_1_id == doctor_id, MessageToSend.user_2_id == patient_id)
            .order_by(MessageToSend.id.desc())
            .limit(1)
        )
        return res.first()
