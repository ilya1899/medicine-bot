from sqlalchemy import select, update

from app.database.models import async_session, Doctor


async def add_doctor(user_id: int, full_name: str, country: str, city: str, specialty: str, work_experience: int,
                     education_data: str, education: str, resume: str, is_face_to_face: bool, data_face_to_face: str,
                     price_just_ask: int, price_decoding: int, price_main_first: int,
                     price_main_repeated: int, price_second_opinion: int, achievements: str, is_social_networks: bool,
                     social_networks_telegram: str, social_networks_instagram: str, about_me: str,
                     bank_details_russia: str, bank_details_abroad: str):
    async with async_session() as session:

        session.add(Doctor(user_id=user_id, full_name=full_name, country=country, city=city, specialty=specialty,
                           work_experience=work_experience, education_data=education_data, education=education,
                           resume=resume,
                           is_face_to_face=is_face_to_face, data_face_to_face=data_face_to_face,
                           price_just_ask=price_just_ask, price_decoding=price_decoding,
                           price_main_first=price_main_first,
                           price_main_repeated=price_main_repeated, price_second_opinion=price_second_opinion,
                           achievements=achievements,
                           is_social_networks=is_social_networks, social_networks_telegram=social_networks_telegram,
                           social_networks_instagram=social_networks_instagram, about_me=about_me, rating_all=0,
                           rating_1=0, rating_2=0, rating_3=0, rating_4=0, bank_details_russia=bank_details_russia,
                           bank_details_abroad=bank_details_abroad))
        await session.commit()


async def is_doctor(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        return doctor is not None


async def is_open_dialog(doctor_id: int, patient_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == doctor_id))
        return doctor.open_dialog == patient_id


async def delete_doctor(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        if doctor:
            await session.delete(doctor)
            await session.commit()
            return True
        return False


async def edit_doctor(user_id: int, full_name: str, country: str, city: str, specialty: str, work_experience: int,
                      education_data: str, education: str, resume: str, is_face_to_face: bool, data_face_to_face: str,
                       price_just_ask: int, price_decoding: int, price_main_first: int,
                      price_main_repeated: int, price_second_opinion: int,
                      achievements: str, is_social_networks: bool, social_networks_telegram: str,
                      social_networks_instagram: str, about_me: str, bank_details_russia: str,
                      bank_details_abroad: str):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == user_id).values(full_name=full_name, country=country,
                                                                   city=city, specialty=specialty,
                                                                   work_experience=work_experience,
                                                                   education_data=education_data, education=education,
                                                                   resume=resume,
                                                                   is_face_to_face=is_face_to_face,
                                                                   data_face_to_face=data_face_to_face,
                                                                   price_just_ask=price_just_ask,
                                                                   price_decoding=price_decoding,
                                                                   price_main_first=price_main_first,
                                                                   price_main_repeated=price_main_repeated,
                                                                   price_second_opinion=price_second_opinion,
                                                                   achievements=achievements,
                                                                   is_social_networks=is_social_networks,
                                                                   social_networks_telegram=social_networks_telegram,
                                                                   social_networks_instagram=social_networks_instagram,
                                                                   about_me=about_me,
                                                                   bank_details_russia=bank_details_russia,
                                                                   bank_details_abroad=bank_details_abroad))
        await session.commit()
        return result.rowcount > 0


async def edit_open_dialog(doctor_id: int, patient_id: int):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(open_dialog=patient_id))
        await session.commit()
        return result.rowcount > 0


async def edit_full_name(doctor_id: int, full_name: str):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(full_name=full_name))
        await session.commit()
        return result.rowcount > 0


async def edit_country(doctor_id: int, country: str):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(country=country))
        await session.commit()
        return result.rowcount > 0


async def edit_city(doctor_id: int, city: str):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(city=city))
        await session.commit()
        return result.rowcount > 0


async def edit_specialty(doctor_id: int, specialty: str):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(specialty=specialty))
        await session.commit()
        return result.rowcount > 0


async def edit_work_experience(doctor_id: int, work_experience: int):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(work_experience=work_experience))
        await session.commit()
        return result.rowcount > 0


async def edit_education_data(doctor_id: int, education_data: str):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(education_data=education_data))
        await session.commit()
        return result.rowcount > 0


async def edit_education(doctor_id: int, education: str):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(education=education))
        await session.commit()
        return result.rowcount > 0


async def edit_resume(doctor_id: int, resume: str):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(resume=resume))
        await session.commit()
        return result.rowcount > 0


async def edit_is_face_to_face(doctor_id: int, is_face_to_face: bool):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(is_face_to_face=is_face_to_face))
        await session.commit()
        return result.rowcount > 0


async def edit_data_face_to_face(doctor_id: int, data_face_to_face: str):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(data_face_to_face=data_face_to_face))
        await session.commit()
        return result.rowcount > 0


async def edit_photo(doctor_id: int, photo: str):
    async with async_session() as session:
        # result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(photo=photo))
        #  await session.commit()
        # return result.rowcount > 0
        return True


async def edit_price_just_ask(doctor_id: int, price_just_ak: int):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(price_just_ak=price_just_ak))
        await session.commit()
        return result.rowcount > 0


async def edit_price_decoding(doctor_id: int, price_decoding: int):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(price_decoding=price_decoding))
        await session.commit()
        return result.rowcount > 0


async def edit_price_main_first(doctor_id: int, price_main_first: int):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(price_main_first=price_main_first))
        await session.commit()
        return result.rowcount > 0


async def edit_price_main_repeated(doctor_id: int, price_main_repeated: int):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(price_main_repeated=price_main_repeated))
        await session.commit()
        return result.rowcount > 0


async def edit_price_second_opinion(doctor_id: int, price_second_opinion: int):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(price_second_opinion=price_second_opinion))
        await session.commit()
        return result.rowcount > 0


async def edit_achievements(doctor_id: int, achievements: str):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(achievements=achievements))
        await session.commit()
        return result.rowcount > 0


async def edit_is_social_networks(doctor_id: int, is_social_networks: bool):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(is_social_networks=is_social_networks))
        await session.commit()
        return result.rowcount > 0


async def edit_social_networks_telegram(doctor_id: int, social_networks_telegram: str):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(social_networks_telegram=social_networks_telegram))
        await session.commit()
        return result.rowcount > 0


async def edit_social_networks_instagram(doctor_id: int, social_networks_instagram: str):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(
            social_networks_instagram=social_networks_instagram))
        await session.commit()
        return result.rowcount > 0


async def edit_about_me(doctor_id: int, about_me: str):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(about_me=about_me))
        await session.commit()
        return result.rowcount > 0


async def edit_rating_all(doctor_id: int, rating: float):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(rating_all=rating))
        await session.commit()
        return result.rowcount > 0


async def edit_rating_1(doctor_id: int, rating: float):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(rating_1=rating))
        await session.commit()
        return result.rowcount > 0


async def edit_rating_2(doctor_id: int, rating: float):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(rating_2=rating))
        await session.commit()
        return result.rowcount > 0


async def edit_rating_3(doctor_id: int, rating: float):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(rating_3=rating))
        await session.commit()
        return result.rowcount > 0


async def edit_rating_4(doctor_id: int, rating: float):
    async with async_session() as session:
        result = await session.execute(update(Doctor).where(Doctor.user_id == doctor_id).values(rating_4=rating))
        await session.commit()
        return result.rowcount > 0


async def edit_bank_details_russia(doctor_id: int, bank_details_russia: str):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(bank_details_russia=bank_details_russia))
        await session.commit()
        return result.rowcount > 0


async def edit_bank_details_abroad(doctor_id: int, bank_details_abroad: str):
    async with async_session() as session:
        result = await session.execute(
            update(Doctor).where(Doctor.user_id == doctor_id).values(bank_details_abroad=bank_details_abroad))
        await session.commit()
        return result.rowcount > 0


async def get_doctors_by_specialty(specialty: str):
    async with async_session() as session:
        doctors = (await session.scalars(select(Doctor)
                                         .where(Doctor.specialty.ilike(f'%{specialty}%'))
                                         .order_by(Doctor.user_id))).all()
        return doctors


async def get_doctors_by_face_to_face():
    async with async_session() as session:
        doctors = await session.scalars(select(Doctor).where(Doctor.is_face_to_face == True).order_by(Doctor.user_id))
        return doctors.all()


async def get_doctor_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        return doctor


async def get_open_dialog_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        return doctor.open_dialog


async def get_price_just_ask_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        if doctor:
            return doctor.price_just_ask
        return 0


async def get_price_decoding_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        if doctor:
            return doctor.price_decoding
        return 0


async def get_price_main_first_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        if doctor:
            return doctor.price_main_first
        return 0


async def get_price_main_repeated_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        if doctor:
            return doctor.price_main_repeated
        return 0


async def get_price_second_opinion_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        if doctor:
            return doctor.price_second_opinion
        return 0


async def get_full_name_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        if doctor:
            return doctor.full_name
        return ''


async def get_bank_details_russia_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        if doctor:
            return doctor.bank_details_russia
        return ''


async def get_bank_details_abroad_by_user_id(user_id: int):
    async with async_session() as session:
        doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user_id))
        if doctor:
            return doctor.bank_details_abroad
        return ''


async def get_all_doctors():
    async with async_session() as session:
        doctors = await session.scalars(select(Doctor))
        return doctors.all()
