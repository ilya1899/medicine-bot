from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()

type_consultation = {'justAsk': 'Просто спросить',
                     'decoding': 'Расшифровка анализов',
                     'secondOpinion': 'Второе мнение',
                     'mainFirst': 'Первичная консультация',
                     'mainRepeated': 'Повторная консультация'}

# admin_group_id = -1002299547910
admin_group_id = -1002561162159
#admin_group_id = -1441100175