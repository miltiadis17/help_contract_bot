"""
FSM States для бота генерации договоров
"""
from aiogram.fsm.state import State, StatesGroup


class ContractStates(StatesGroup):
    """Состояния для процесса создания договора"""

    # Выбор полей для заполнения
    selecting_fields = State()

    # Сбор данных заказчика
    client_full_name = State()
    client_passport_series = State()
    client_passport_number = State()
    client_passport_issued_by = State()
    client_passport_issue_date = State()
    client_birth_date = State()
    client_birth_place = State()
    client_address = State()
    client_phone = State()
    client_email = State()
    client_inn = State()

    # Сбор данных исполнителя
    executor_full_name = State()
    executor_passport_series = State()
    executor_passport_number = State()
    executor_passport_issued_by = State()
    executor_passport_issue_date = State()
    executor_birth_date = State()
    executor_birth_place = State()
    executor_address = State()
    executor_phone = State()
    executor_email = State()
    executor_inn = State()

    # Данные договора
    contract_subject = State()
    contract_amount = State()
    contract_deadline = State()
    contract_start_date = State()
    contract_payment_terms = State()
    contract_additional_terms = State()

    # Банковские реквизиты
    executor_bank_name = State()
    executor_bank_account = State()
    executor_bank_bik = State()
    executor_bank_corr_account = State()

    # Предпросмотр и подтверждение
    preview = State()
    editing_field = State()
