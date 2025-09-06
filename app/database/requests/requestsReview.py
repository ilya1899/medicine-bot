from sqlalchemy import select, update
from app.database.models import Review
from app.database.models import async_session


async def add_review(patient_id: int, doctor_id: int, stars_1: int, stars_2: int, stars_3: int, stars_4: int,
                     review: str):
    async with async_session() as session:
        session.add(Review(patient_id=patient_id, doctor_id=doctor_id, stars_1=stars_1, stars_2=stars_2,
                           stars_3=stars_3, stars_4=stars_4, review=review))
        await session.commit()


async def edit_review(patient_id: int, doctor_id: int, review: str):
    async with async_session() as session:
        result = await session.scalar(update(Review)
                                      .where((Review.patient_id == patient_id) &
                                             (Review.doctor_id == doctor_id))
                                      .values(review=review))
        return result.rowcount > 0


async def delete_review(id: int):
    async with async_session() as session:
        review = await session.scalar(select(Review).where(Review.id == id))
        if review:
            await session.delete(review)
            await session.commit()
            return True
        return False


async def is_review(patient_id: int, doctor_id: int):
    async with async_session() as session:
        review = await session.scalar(select(Review).where((Review.patient_id == patient_id) &
                                                           (Review.doctor_id == doctor_id)))
        return review != None


async def is_reviews_by_doctor_id(doctor_id: int):
    async with async_session() as session:
        review = await session.scalar(select(Review).where(Review.doctor_id == doctor_id))
        return review != None


async def is_reviews_with_text_by_doctor_id(doctor_id: int):
    async with async_session() as session:
        review = await session.scalar(select(Review).where((Review.doctor_id == doctor_id) &
                                                           (Review.review != '')))
        return review != None


async def get_review(patient_id: int, doctor_id: int):
    async with async_session() as session:
        review = await session.scalar(select(Review).where((Review.patient_id == patient_id) &
                                                           (Review.doctor_id == doctor_id)))
        return review


async def get_number_of_reviews_by_doctor_by(doctor_id: int):
    async with async_session() as session:
        reviews = await session.scalars(select(Review).where(Review.doctor_id == doctor_id))
        return len(reviews.all())


async def get_reviews_by_doctor_id(doctor_id: int):
    async with async_session() as session:
        reviews = await session.scalars(select(Review).where(Review.doctor_id == doctor_id))
        return reviews.all()


async def get_reviews_by_doctor_id_with_text(doctor_id: int):
    async with async_session() as session:
        reviews = await session.scalars(select(Review).where((Review.doctor_id == doctor_id) &
                                                             (Review.review != '')).order_by(Review.id.desc()))
        return reviews.all()


async def get_number_of_reviews_by_doctor_id(doctor_id: int):
    async with async_session() as session:
        reviews = await session.scalars(select(Review).where(Review.doctor_id == doctor_id))
        return len(reviews.all())
