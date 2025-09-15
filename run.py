import asyncio
import logging

import gspread
from aiogram.types import Update, ErrorEvent
from oauth2client.service_account import ServiceAccountCredentials

from app.database import models
from app.loader import dp, bot
from app.user import handlerCommand, handlerRegistration, handlerFAQ, handlerAboutUs, handlerSupportProject, \
    handlerConsultation, handlerReview, handlerCooperation, handlerHistory
from app.user.admin import handlerAdmin, handlerEditDoctors, handlerStatistics, handlerSpecialties, \
    handlerPhotoAndFile, handlerFeedback, handlerMailing, handlerLastMessage
from app.user.doctor import handlerDoctorConsultations, handlerPersonalAccount, handlerDoctor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding='utf-8'),
        logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('sheets.json', scope)
client = gspread.authorize(creds)


@dp.error()
async def global_error_handler(event: ErrorEvent):
    exception = event.exception
    update: Update = event.update
    logger.exception(f'Ошибка при обработке хэндлера: {exception}')

    try:
        if update.message:
            await update.message.answer(
                f'СООБЩЕНИЕ ДЛЯ ОТЛАДКИ!\n Отправьте это сообщение разработчикам\n Ошибка: {exception}')
        elif update.callback_query:
            await update.callback_query.message.answer(
                f'СООБЩЕНИЕ ДЛЯ ОТЛАДКИ!\n Отправьте это сообщение разработчикам\n Ошибка: {exception}')
    except Exception as e:
        logging.error(f"Не удалось отправить ошибку в чат: {e}")


async def main():
    logger.info('Starting bot...')

    await models.async_main()
    logger.info('Successful model init')
    # dp.message.outer_middleware(Middleware())
    # dp.callback_query.outer_middleware(Middleware())
    dp.include_routers(
        handlerCommand.router,
        # handlerUpload.router,
        handlerAdmin.router,
        handlerEditDoctors.router,
        handlerStatistics.router,
        handlerMailing.router,
        handlerLastMessage.router,
        handlerSpecialties.router,
        handlerFeedback.router,
        handlerPhotoAndFile.router,
        handlerDoctor.router,
        handlerPersonalAccount.router,
        handlerDoctorConsultations.router,
        handlerRegistration.router,
        handlerCooperation.router,
        handlerFAQ.router,
        handlerAboutUs.router,
        handlerSupportProject.router,
        handlerReview.router,
        handlerHistory.router,
        handlerConsultation.router,
    )

    logger.info('All routers connected')

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.warning(f'Error: {e}')
    except KeyboardInterrupt:
        print('Exit')
