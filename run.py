import asyncio
import logging

from aiogram import Bot, Dispatcher

from dotenv import load_dotenv
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(storage=storage)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('sheets.json', scope)
client = gspread.authorize(creds)

from app.database import models
# from app.middlewares.middlewares import Middleware

from app.user import handlerCommand, handlerRegistration, handlerFAQ, handlerAboutUs, handlerSupportProject, \
    handlerConsultation, handlerReview, handlerCooperation, handlerHistory

from app.user.doctor import handlerDoctorConsultations, handlerPersonalAccount, handlerDoctor
from app.user.admin import handlerAdmin, handlerEditDoctors, handlerStatistics, handlerSpecialties, \
    handlerPhotoAndFile, handlerFeedback, handlerMailing, handlerLastMessage


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
