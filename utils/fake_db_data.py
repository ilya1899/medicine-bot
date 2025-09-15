import asyncio
import sys
import random
import os

from dotenv import load_dotenv
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database.models import User, Doctor, Specialty, HistoryConsultation, HistoryMessage, City, Country

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

fake = Faker('ru_RU')


async def populate_database(user_ids=None, doctor_ids=None, n_users=5, n_doctors=3):
    engine = create_async_engine(os.getenv('SQLALCHEMY_URL'), echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    """
    user_ids: список конкретных user_id для User
    doctor_ids: список конкретных user_id для Doctor
    n_users: количество пользователей, если user_ids не переданы
    n_doctors: количество докторов, если doctor_ids не переданы
    """
    async with async_session() as session:
        country_objs = []
        countries = ['Россия', 'США', 'Германия', 'Франция']
        for country in countries:
            c = Country(name=country)
            session.add(c)
            country_objs.append(c)
        await session.commit()

        city_objs = []
        for country in country_objs:
            for _ in range(3):
                city = City(name=fake.city(), id_country=country.id)
                session.add(city)
                city_objs.append(city)
        await session.commit()

        specialties = ['Терапевт', 'Кардиолог', 'Педиатр', 'Невролог']
        specialty_objs = []
        for s in specialties:
            sp = Specialty(name=s)
            session.add(sp)
            specialty_objs.append(sp)
        await session.commit()

        users = []
        for i in range(max(n_users, len(user_ids) if user_ids else 0)):
            uid = None
            if user_ids and i < len(user_ids) and user_ids[i] is not None:
                uid = user_ids[i]
            else:
                uid = random.randint(1000, 9999)
            user = User(
                user_id=uid,
                gender=random.choice(['М', 'Ж']),
                age=random.randint(18, 80),
                country=random.choice(countries),
                city=random.choice(city_objs).name
            )
            session.add(user)
            users.append(user)
        await session.commit()

        doctors = []
        for i in range(max(n_doctors, len(doctor_ids) if doctor_ids else 0)):
            did = None
            if doctor_ids and i < len(doctor_ids) and doctor_ids[i] is not None:
                did = doctor_ids[i]
            else:
                did = random.randint(10000, 99999)
            doc = Doctor(
                user_id=did,
                full_name=fake.name(),
                country=random.choice(countries),
                city=random.choice(city_objs).name,
                specialty=random.choice(specialties),
                work_experience=random.randint(1, 30),
                education_data="ВУЗ",
                education="Медицина",
                resume=fake.text(max_nb_chars=200),
                is_face_to_face=True,
                data_face_to_face="Офис",
                price_just_ask=random.randint(500, 2000),
                price_decoding=random.randint(500, 2000),
                price_main_first=random.randint(500, 2000),
                price_main_repeated=random.randint(500, 2000),
                price_second_opinion=random.randint(500, 2000),
                achievements=fake.text(max_nb_chars=100),
                is_social_networks=True,
                social_networks_telegram=f"@{fake.user_name()}",
                social_networks_instagram=f"@{fake.user_name()}",
                about_me=fake.text(max_nb_chars=150),
                rating_all=random.uniform(3, 5),
                rating_1=random.uniform(3, 5),
                rating_2=random.uniform(3, 5),
                rating_3=random.uniform(3, 5),
                rating_4=random.uniform(3, 5),
                bank_details_russia="1234567890",
                bank_details_abroad="9876543210"
            )
            session.add(doc)
            doctors.append(doc)
        await session.commit()

        consultations = []
        for user in users:
            for _ in range(5):
                doc = random.choice(doctors)
                hc = HistoryConsultation(
                    name=fake.sentence(nb_words=3),
                    patient_id=user.user_id,
                    doctor_id=doc.user_id,
                    chat_type=random.choice(['justAsk', 'mainFirst', 'mainRepeated']),
                    specialty=doc.specialty
                )
                session.add(hc)
                consultations.append(hc)
        await session.commit()

        for hc in consultations:
            for _ in range(random.randint(1, 3)):
                hm = HistoryMessage(
                    id_consultation=hc.id,
                    patient_id=hc.patient_id,
                    doctor_id=hc.doctor_id,
                    who_write=random.choice(['patient', 'doctor']),
                    text=fake.text(max_nb_chars=100),
                    media_type='text',
                    media_id=''
                )
                session.add(hm)
        await session.commit()

        print("База данных успешно заполнена тестовыми данными!")


if __name__ == "__main__":
    asyncio.run(populate_database(user_ids=[1441100175], doctor_ids=[], n_users=5, n_doctors=3))
