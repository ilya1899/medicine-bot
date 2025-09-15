from dataclasses import dataclass

from sqlalchemy import BigInteger, Text
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config_reader import config

engine = create_async_engine(url=config.DB_URL.get_secret_value())

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

    def __repr__(self):
        return f"User(id={self.user_id}, name={self.full_name}, age={self.age}, gender={self.gender}, city={self.city})"


@dataclass
class Doctor(Base):
    __tablename__ = 'doctors'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(default="")
    country: Mapped[str] = mapped_column(default="")
    city: Mapped[str] = mapped_column(default="")
    specialty: Mapped[str] = mapped_column(default="")
    work_experience: Mapped[int] = mapped_column(default=0)
    education_data: Mapped[str] = mapped_column(default="")
    education: Mapped[str] = mapped_column(default="")
    resume: Mapped[str] = mapped_column(Text, default="")
    is_face_to_face: Mapped[bool] = mapped_column(default=False)
    data_face_to_face: Mapped[str] = mapped_column(default="")
    photo: Mapped[str] = mapped_column(default="")
    price_just_ask: Mapped[int] = mapped_column(default=0)
    price_decoding: Mapped[int] = mapped_column(default=0)
    price_main_first: Mapped[int] = mapped_column(default=0)
    price_main_repeated: Mapped[int] = mapped_column(default=0)
    price_second_opinion: Mapped[int] = mapped_column(default=0)
    achievements: Mapped[str] = mapped_column(default="")
    is_social_networks: Mapped[bool] = mapped_column(default=False)
    social_networks_telegram: Mapped[str] = mapped_column(default="")
    social_networks_instagram: Mapped[str] = mapped_column(default="")
    about_me: Mapped[str] = mapped_column(Text, default="")
    rating_all: Mapped[float] = mapped_column(default=0.0)
    rating_1: Mapped[float] = mapped_column(default=0.0)
    rating_2: Mapped[float] = mapped_column(default=0.0)
    rating_3: Mapped[float] = mapped_column(default=0.0)
    rating_4: Mapped[float] = mapped_column(default=0.0)
    bank_details_russia: Mapped[str] = mapped_column(default="")
    bank_details_abroad: Mapped[str] = mapped_column(default="")

    def __repr__(self):
        return f"Doctor(id={self.user_id}, name={self.full_name}, specialty={self.specialty}, city={self.city})"


@dataclass
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

    def __repr__(self):
        return f"PreDoctor(id={self.user_id}, name={self.full_name}, specialty={self.specialty})"


@dataclass
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

    def __repr__(self):
        return f"Review(id={self.id}, doctor_id={self.doctor_id}, patient_id={self.patient_id})"


@dataclass
class Statistics(Base):
    __tablename__ = 'statistics'
    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(BigInteger)
    doctor_id: Mapped[int] = mapped_column(BigInteger)
    type_of_consultation: Mapped[str] = mapped_column()
    specialty: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"Statistics(id={self.id}, doctor_id={self.doctor_id}, patient_id={self.patient_id})"


@dataclass
class Admin(Base):
    __tablename__ = 'admins'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    def __repr__(self):
        return f"Admin(user_id={self.user_id})"


@dataclass
class MessageToSend(Base):
    __tablename__ = 'messages_to_send'
    id: Mapped[int] = mapped_column(primary_key=True)

    user_1_id: Mapped[int] = mapped_column(BigInteger)
    user_2_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[str] = mapped_column()
    media_type: Mapped[str] = mapped_column()
    media_id: Mapped[str] = mapped_column()

    is_first_message: Mapped[bool] = mapped_column()

    def __repr__(self):
        return f"MessageToSend(id={self.id}, from={self.user_1_id}, to={self.user_2_id})"


@dataclass
class MessageToRepeat(Base):
    __tablename__ = 'messages_to_repeat'
    id: Mapped[int] = mapped_column(primary_key=True)

    user_1_id: Mapped[int] = mapped_column(BigInteger)
    user_2_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[str] = mapped_column()
    media_type: Mapped[str] = mapped_column()
    media_id: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"MessageToRepeat(id={self.id}, from={self.user_1_id}, to={self.user_2_id})"


@dataclass
class Bundle(Base):
    __tablename__ = 'bundles'
    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(BigInteger)
    doctor_id: Mapped[int] = mapped_column(BigInteger)
    is_open_dialog_patient: Mapped[bool] = mapped_column()
    is_open_dialog_doctor: Mapped[bool] = mapped_column()
    chat_type: Mapped[str] = mapped_column()

    id_consultation: Mapped[int] = mapped_column()

    def __repr__(self):
        return f"Bundle(id={self.id}, patient={self.patient_id}, doctor={self.doctor_id})"


@dataclass
class Country(Base):
    __tablename__ = 'countries'
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"Country(id={self.id}, name={self.name})"


@dataclass
class City(Base):
    __tablename__ = 'cities'
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    id_country: Mapped[int] = mapped_column()

    def __repr__(self):
        return f"City(id={self.id}, name={self.name}, country_id={self.id_country})"


@dataclass
class Specialty(Base):
    __tablename__ = 'specialties'
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"Specialty(id={self.id}, name={self.name})"


@dataclass
class HistoryConsultation(Base):
    __tablename__ = 'history_of_consultations'
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    patient_id: Mapped[int] = mapped_column(BigInteger)
    doctor_id: Mapped[int] = mapped_column(BigInteger)
    chat_type: Mapped[str] = mapped_column()
    specialty: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"HistoryConsultation(id={self.id}, patient={self.patient_id}, doctor={self.doctor_id})"


@dataclass
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

    def __repr__(self):
        return f"HistoryMessage(id={self.id}, consult={self.id_consultation}, writer={self.who_write})"


@dataclass
class PhotoAndFile(Base):
    __tablename__ = 'photos_and_files'
    id: Mapped[int] = mapped_column(primary_key=True)

    media_id: Mapped[str] = mapped_column()
    function: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"PhotoAndFile(id={self.id}, function={self.function})"


@dataclass
class LastMessage(Base):
    __tablename__ = 'last_messages'
    id: Mapped[int] = mapped_column(primary_key=True)

    text = mapped_column(Text)
    function: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"LastMessage(id={self.id}, function={self.function})"


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
