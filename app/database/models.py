from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from dataclasses import dataclass

from dotenv import load_dotenv
import os

load_dotenv()
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'))

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

@dataclass
class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column()
    gender: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()
    country: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()


class Doctor(Base):
    __tablename__ = 'doctors'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    specialty: Mapped[str] = mapped_column()
    work_experience: Mapped[int] = mapped_column()
    education_data: Mapped[str] = mapped_column()
    education: Mapped[str] = mapped_column()
    resume = mapped_column(Text)
    is_face_to_face: Mapped[bool] = mapped_column()
    data_face_to_face: Mapped[str] = mapped_column()
    photo: Mapped[str] = mapped_column()
    price_just_ask: Mapped[int] = mapped_column()
    price_decoding: Mapped[int] = mapped_column()
    price_main_first: Mapped[int] = mapped_column()
    price_main_repeated: Mapped[int] = mapped_column()
    price_second_opinion: Mapped[int] = mapped_column()
    achievements: Mapped[str] = mapped_column()
    is_social_networks: Mapped[bool] = mapped_column()
    social_networks_telegram: Mapped[str] = mapped_column()
    social_networks_instagram: Mapped[str] = mapped_column()
    about_me = mapped_column(Text)
    rating_all: Mapped[float] = mapped_column()
    rating_1: Mapped[float] = mapped_column()
    rating_2: Mapped[float] = mapped_column()
    rating_3: Mapped[float] = mapped_column()
    rating_4: Mapped[float] = mapped_column()
    bank_details_russia: Mapped[str] = mapped_column()
    bank_details_abroad: Mapped[str] = mapped_column()


class PreDoctor(Base):
    __tablename__ = 'pre_doctors'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    specialty: Mapped[str] = mapped_column()
    work_experience: Mapped[int] = mapped_column()
    education_data: Mapped[str] = mapped_column()
    education: Mapped[str] = mapped_column()
    resume = mapped_column(Text)
    is_face_to_face: Mapped[bool] = mapped_column()
    data_face_to_face: Mapped[str] = mapped_column()
    photo: Mapped[str] = mapped_column()
    price_just_ask: Mapped[int] = mapped_column()
    price_decoding: Mapped[int] = mapped_column()
    price_main_first: Mapped[int] = mapped_column()
    price_main_repeated: Mapped[int] = mapped_column()
    price_second_opinion: Mapped[int] = mapped_column()
    achievements: Mapped[str] = mapped_column()
    is_social_networks: Mapped[bool] = mapped_column()
    social_networks_telegram: Mapped[str] = mapped_column()
    social_networks_instagram: Mapped[str] = mapped_column()
    about_me = mapped_column(Text)
    bank_details_russia: Mapped[str] = mapped_column()
    bank_details_abroad: Mapped[str] = mapped_column()


class Review(Base):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(primary_key=True)

    doctor_id: Mapped[int] = mapped_column(BigInteger)
    patient_id: Mapped[int] = mapped_column(BigInteger)
    stars_1: Mapped[int] = mapped_column()
    stars_2: Mapped[int] = mapped_column()
    stars_3: Mapped[int] = mapped_column()
    stars_4: Mapped[int] = mapped_column()
    review: Mapped[str] = mapped_column()


class Statistics(Base):
    __tablename__ = 'statistics'
    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(BigInteger)
    doctor_id: Mapped[int] = mapped_column(BigInteger)
    type_of_consultation: Mapped[str] = mapped_column()
    specialty: Mapped[str] = mapped_column()


# третья нормальная форма почитать
# создать файлы для проксирования requests


class Admin(Base):
    __tablename__ = 'admins'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class MessageToSend(Base):
    __tablename__ = 'messages_to_send'
    id: Mapped[int] = mapped_column(primary_key=True)

    user_1_id: Mapped[int] = mapped_column(BigInteger)
    user_2_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[str] = mapped_column()
    media_type: Mapped[str] = mapped_column()
    media_id: Mapped[str] = mapped_column()

    is_first_message: Mapped[bool] = mapped_column()


class MessageToRepeat(Base):
    __tablename__ = 'messages_to_repeat'
    id: Mapped[int] = mapped_column(primary_key=True)

    user_1_id: Mapped[int] = mapped_column(BigInteger)
    user_2_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[str] = mapped_column()
    media_type: Mapped[str] = mapped_column()
    media_id: Mapped[str] = mapped_column()


class Bundle(Base):
    __tablename__ = 'bundles'
    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(BigInteger)
    doctor_id: Mapped[int] = mapped_column(BigInteger)
    is_open_dialog_patient: Mapped[bool] = mapped_column()
    is_open_dialog_doctor: Mapped[bool] = mapped_column()
    chat_type: Mapped[str] = mapped_column()

    id_consultation: Mapped[int] = mapped_column()


class Country(Base):
    __tablename__ = 'countries'
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()


class City(Base):
    __tablename__ = 'cities'
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    id_country: Mapped[int] = mapped_column()


class Specialty(Base):
    __tablename__ = 'specialties'
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()


class HistoryConsultation(Base):
    __tablename__ = 'history_of_consultations'
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    patient_id: Mapped[int] = mapped_column(BigInteger)
    doctor_id: Mapped[int] = mapped_column(BigInteger)
    chat_type: Mapped[str] = mapped_column()
    specialty: Mapped[str] = mapped_column()


class HistoryMessage(Base):
    __tablename__ = 'history_of_messages'
    id: Mapped[int] = mapped_column(primary_key=True)

    id_consultation: Mapped[int] = mapped_column()
    patient_id: Mapped[int] = mapped_column(BigInteger)
    doctor_id: Mapped[int] = mapped_column(BigInteger)
    who_write: Mapped[str] = mapped_column()
    text = mapped_column(Text)
    media_type: Mapped[str] = mapped_column()
    media_id: Mapped[str] = mapped_column()


class PhotoAndFile(Base):
    __tablename__ = 'photos_and_files'
    id: Mapped[int] = mapped_column(primary_key=True)

    media_id: Mapped[str] = mapped_column()
    function: Mapped[str] = mapped_column()


class LastMessage(Base):
    __tablename__ = 'last_messages'
    id: Mapped[int] = mapped_column(primary_key=True)

    text = mapped_column(Text)
    function: Mapped[str] = mapped_column()


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
