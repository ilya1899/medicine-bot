import asyncio

from aiogram import F, Router
from aiogram.types import Message, FSInputFile
import pandas as pd

from sqlalchemy import text
import os

router = Router()

from app.database.models import async_session
from app.businessLogic.admin.logicAdmin import Admin


async def fetch_table_data(session, table_name):
    # Выполняем асинхронный запрос для получения данных из таблицы
    result = await session.execute(text(f"SELECT * FROM {table_name}"))
    return result.fetchall(), result.keys()

async def export_to_excel():
    async with async_session() as session:
        result = await session.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        )
        tables = result.scalars().all()

        if not tables:
            raise ValueError("Нет таблиц для экспорта.")

        db_name = 'medicine_db'
        excel_file_path = f"{db_name}.xlsx"

        # Используем ExcelWriter вне цикла, чтобы избежать создания нескольких файлов
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            for table_name in tables:
                # Получаем данные и ключи (имена колонок)
                data, columns = await fetch_table_data(session, table_name)
                # Создаем DataFrame
                df = pd.DataFrame(data, columns=columns)
                # Записываем DataFrame на отдельный лист в Excel
                df.to_excel(writer, sheet_name=table_name, index=False)

        return excel_file_path





@router.message(F.text == '/export', Admin.admin)
async def message_upload(message: Message):

    await message.answer('Начинаю выгрузку...')

    excel_file_path = await export_to_excel()

    await message.answer('Выгрузка завершена, отправляю файл...')

    input_file = FSInputFile(excel_file_path)

    await message.answer_document(input_file)

    os.remove(excel_file_path)





