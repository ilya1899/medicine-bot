from sqlalchemy import select, update

from app.database.models import async_session
from app.database.models import PreDoctor


async def add_doctor(user_id: int, full_name: str, country: str, city: str, specialty: str, work_experience: int,
                     education_data: str, education: str, resume: str, is_face_to_face: str, data_face_to_face: str,
                     photo: str, price_just_ask: int, price_decoding: int, price_main_first: int,
                     price_main_repeated: int,
                     price_second_opinion: int,
                     achievements: str, is_social_networks: bool, social_networks_telegram: str,
                     social_networks_instagram: str, about_me: str, bank_details_russia: str, bank_details_abroad: str):
    async with async_session() as session:
        session.add(PreDoctor(user_id=user_id, full_name=full_name, country=country, city=city, specialty=specialty,
                              work_experience=work_experience, education_data=education_data, education=education,
                              resume=resume,
                              is_face_to_face=is_face_to_face, data_face_to_face=data_face_to_face, photo=photo,
                              price_just_ask=price_just_ask, price_decoding=price_decoding,
                              price_main_first=price_main_first,
                              price_main_repeated=price_main_repeated, price_second_opinion=price_second_opinion,
                              achievements=achievements,
                              is_social_networks=is_social_networks, social_networks_telegram=social_networks_telegram,
                              social_networks_instagram=social_networks_instagram, about_me=about_me,
                              bank_details_russia=bank_details_russia, bank_details_abroad=bank_details_abroad))
        await session.commit()


async def is_doctor(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(PreDoctor).where(PreDoctor.user_id == user_id))
        return doctor != None


async def delete_doctor(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(PreDoctor).where(PreDoctor.user_id == user_id))
        if doctor:
            await session.delete(doctor)
            await session.commit()
            return True
        return False


async def edit_full_name(doctor_id: int, full_name: str):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(full_name=full_name))
        await session.commit()
        return result.rowcount > 0


async def edit_country(doctor_id: int, country: str):
    async with async_session() as session:
        result = await session.execute(update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(country=country))
        await session.commit()
        return result.rowcount > 0


async def edit_city(doctor_id: int, city: str):
    async with async_session() as session:
        result = await session.execute(update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(city=city))
        await session.commit()
        return result.rowcount > 0


async def edit_specialty(doctor_id: int, specialty: str):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(specialty=specialty))
        await session.commit()
        return result.rowcount > 0


async def edit_work_experience(doctor_id: int, work_experience: int):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(work_experience=work_experience))
        await session.commit()
        return result.rowcount > 0


async def edit_education_data(doctor_id: int, education_data: str):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(education_data=education_data))
        await session.commit()
        return result.rowcount > 0


async def edit_education(doctor_id: int, education: str):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(education=education))
        await session.commit()
        return result.rowcount > 0


async def edit_resume(doctor_id: int, resume: str):
    async with async_session() as session:
        result = await session.execute(update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(resume=resume))
        await session.commit()
        return result.rowcount > 0


async def edit_is_face_to_face(doctor_id: int, is_face_to_face: bool):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(is_face_to_face=is_face_to_face))
        await session.commit()
        return result.rowcount > 0


async def edit_data_face_to_face(doctor_id: int, data_face_to_face: str):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(data_face_to_face=data_face_to_face))
        await session.commit()
        return result.rowcount > 0


async def edit_photo(doctor_id: int, photo: str):
    async with async_session() as session:
        result = await session.execute(update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(photo=photo))
        await session.commit()
        return result.rowcount > 0


async def edit_price_just_ask(doctor_id: int, price_just_ask: int):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(price_just_ask=price_just_ask))
        await session.commit()
        return result.rowcount > 0


async def edit_price_decoding(doctor_id: int, price_decoding: int):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(price_decoding=price_decoding))
        await session.commit()
        return result.rowcount > 0


async def edit_price_main_first(doctor_id: int, price_main_first: int):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(price_main_first=price_main_first))
        await session.commit()
        return result.rowcount > 0


async def edit_price_main_repeated(doctor_id: int, price_main_repeated: int):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(price_main_repeated=price_main_repeated))
        await session.commit()
        return result.rowcount > 0


async def edit_price_second_opinion(doctor_id: int, price_second_opinion: int):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(price_second_opinion=price_second_opinion))
        await session.commit()
        return result.rowcount > 0


async def edit_achievements(doctor_id: int, achievements: str):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(achievements=achievements))
        await session.commit()
        return result.rowcount > 0


async def edit_is_social_networks(doctor_id: int, is_social_networks: bool):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(is_social_networks=is_social_networks))
        await session.commit()
        return result.rowcount > 0


async def edit_social_networks_telegram(doctor_id: int, social_networks_telegram: str):
    async with async_session() as session:
        result = await session.execute(update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(
            social_networks_telegram=social_networks_telegram))
        await session.commit()
        return result.rowcount > 0


async def edit_social_networks_instagram(doctor_id: int, social_networks_instagram: str):
    async with async_session() as session:
        result = await session.execute(update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(
            social_networks_instagram=social_networks_instagram))
        await session.commit()
        return result.rowcount > 0


async def edit_about_me(doctor_id: int, about_me: str):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(about_me=about_me))
        await session.commit()
        return result.rowcount > 0


async def edit_bank_details_russia(doctor_id: int, bank_details_russia: str):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(bank_details_russia=bank_details_russia))
        await session.commit()
        return result.rowcount > 0


async def edit_bank_details_abroad(doctor_id: int, bank_details_abroad: str):
    async with async_session() as session:
        result = await session.execute(
            update(PreDoctor).where(PreDoctor.user_id == doctor_id).values(bank_details_abroad=bank_details_abroad))
        await session.commit()
        return result.rowcount > 0


async def get_doctors_by_specialty(specialty: str):
    async with async_session() as session:
        doctors = (await session.scalars(
            select(PreDoctor).where(PreDoctor.specialty.like(f'%{specialty}%')).order_by(PreDoctor.user_id))).all()
        return doctors


async def get_doctor_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(PreDoctor).where(PreDoctor.user_id == user_id))
        return doctor


async def get_open_dialog_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(PreDoctor).where(PreDoctor.user_id == user_id))
        return doctor.open_dialog
