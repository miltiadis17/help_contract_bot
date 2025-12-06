"""
Генератор договоров на основе шаблона DOCX
"""
import os
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from docxtpl import DocxTemplate

logger = logging.getLogger(__name__)

# Пути к файлам
BASE_DIR = Path(__file__).parent
TEMPLATE_PATH = BASE_DIR / "dogovor_template.docx"
OUTPUT_DIR = BASE_DIR / "generated_contracts"


async def generate_contract(data: Dict[str, Any]) -> str:
    """
    Генерирует договор на основе шаблона и данных пользователя

    Args:
        data: Словарь с данными для заполнения договора

    Returns:
        Путь к сгенерированному PDF-файлу

    Raises:
        FileNotFoundError: Если шаблон не найден
        Exception: При ошибках генерации или конвертации
    """
    # Проверяем наличие шаблона
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Шаблон договора не найден: {TEMPLATE_PATH}\n"
            "Пожалуйста, создайте файл dogovor_template.docx"
        )

    # Создаем директорию для выходных файлов
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Генерируем уникальное имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"contract_{timestamp}"
    docx_path = OUTPUT_DIR / f"{output_filename}.docx"
    pdf_path = OUTPUT_DIR / f"{output_filename}.pdf"

    try:
        # Загружаем шаблон
        logger.info(f"Загрузка шаблона: {TEMPLATE_PATH}")
        doc = DocxTemplate(TEMPLATE_PATH)

        # Подготавливаем контекст для шаблона
        context = prepare_context(data)

        # Рендерим документ
        logger.info("Рендеринг документа с данными")
        doc.render(context)

        # Сохраняем DOCX
        doc.save(str(docx_path))
        logger.info(f"DOCX сохранен: {docx_path}")

        # Конвертируем в PDF
        logger.info("Конвертация DOCX -> PDF")
        convert_to_pdf(str(docx_path), str(pdf_path))
        logger.info(f"PDF создан: {pdf_path}")

        return str(pdf_path)

    except Exception as e:
        logger.error(f"Ошибка при генерации договора: {e}")
        # Удаляем частично созданные файлы
        if docx_path.exists():
            docx_path.unlink()
        if pdf_path.exists():
            pdf_path.unlink()
        raise


def prepare_context(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Подготавливает контекст для шаблона договора

    Args:
        data: Исходные данные от пользователя

    Returns:
        Словарь с подготовленными данными для шаблона
    """

    def clean_value(value: Any) -> Any:
        """Очищает значение: если пустое или None, возвращает None, иначе строку"""
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return value if value else None
        return str(value) if value else None

    # Создаем контекст, где пустые значения = None (для условий в шаблоне)
    context = {
        # Данные заказчика
        "client_full_name": clean_value(data.get("client_full_name")),
        "client_passport_series": clean_value(data.get("client_passport_series")),
        "client_passport_number": clean_value(data.get("client_passport_number")),
        "client_passport_issued_by": clean_value(data.get("client_passport_issued_by")),
        "client_passport_issue_date": clean_value(data.get("client_passport_issue_date")),
        "client_birth_date": clean_value(data.get("client_birth_date")),
        "client_birth_place": clean_value(data.get("client_birth_place")),
        "client_address": clean_value(data.get("client_address")),
        "client_phone": clean_value(data.get("client_phone")),
        "client_email": clean_value(data.get("client_email")),
        "client_inn": clean_value(data.get("client_inn")),

        # Данные исполнителя
        "executor_full_name": clean_value(data.get("executor_full_name")),
        "executor_passport_series": clean_value(data.get("executor_passport_series")),
        "executor_passport_number": clean_value(data.get("executor_passport_number")),
        "executor_passport_issued_by": clean_value(data.get("executor_passport_issued_by")),
        "executor_passport_issue_date": clean_value(data.get("executor_passport_issue_date")),
        "executor_birth_date": clean_value(data.get("executor_birth_date")),
        "executor_birth_place": clean_value(data.get("executor_birth_place")),
        "executor_address": clean_value(data.get("executor_address")),
        "executor_phone": clean_value(data.get("executor_phone")),
        "executor_email": clean_value(data.get("executor_email")),
        "executor_inn": clean_value(data.get("executor_inn")),

        # Банковские реквизиты исполнителя
        "executor_bank_name": clean_value(data.get("executor_bank_name")),
        "executor_bank_account": clean_value(data.get("executor_bank_account")),
        "executor_bank_bik": clean_value(data.get("executor_bank_bik")),
        "executor_bank_corr_account": clean_value(data.get("executor_bank_corr_account")),

        # Данные договора
        "contract_subject": clean_value(data.get("contract_subject")),
        "contract_amount": clean_value(data.get("contract_amount")),
        "contract_deadline": clean_value(data.get("contract_deadline")),
        "contract_start_date": clean_value(data.get("contract_start_date")),
        "contract_payment_terms": clean_value(data.get("contract_payment_terms")),
        "contract_additional_terms": clean_value(data.get("contract_additional_terms")),

        # Системные данные (всегда присутствуют)
        "current_date": datetime.now().strftime("%d.%m.%Y"),
        "contract_number": datetime.now().strftime("%Y%m%d%H%M%S"),
    }

    return context


def convert_to_pdf(docx_path: str, pdf_path: str) -> None:
    """
    Конвертирует DOCX в PDF с помощью LibreOffice

    Args:
        docx_path: Путь к исходному DOCX файлу
        pdf_path: Путь для сохранения PDF файла

    Raises:
        FileNotFoundError: Если LibreOffice не установлен
        subprocess.CalledProcessError: При ошибке конвертации
    """
    # Проверяем наличие LibreOffice
    soffice_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
        "/usr/bin/soffice",  # Linux
        "/usr/bin/libreoffice",  # Linux alternative
        "soffice",  # Windows / PATH
    ]

    soffice_cmd = None
    for path in soffice_paths:
        if os.path.exists(path) or path == "soffice":
            soffice_cmd = path
            break

    if not soffice_cmd:
        raise FileNotFoundError(
            "LibreOffice не найден. Установите LibreOffice:\n"
            "macOS: brew install --cask libreoffice\n"
            "Ubuntu/Debian: sudo apt-get install libreoffice\n"
            "Windows: скачайте с https://www.libreoffice.org/"
        )

    # Получаем директорию для выходного файла
    output_dir = os.path.dirname(pdf_path)

    try:
        # Конвертируем DOCX в PDF
        # --headless: запуск без GUI
        # --convert-to pdf: формат конвертации
        # --outdir: директория для выходного файла
        cmd = [
            soffice_cmd,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_dir,
            docx_path
        ]

        logger.info(f"Выполнение команды: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )

        logger.info(f"LibreOffice stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"LibreOffice stderr: {result.stderr}")

        # Проверяем, что PDF создан
        if not os.path.exists(pdf_path):
            raise Exception(f"PDF файл не был создан: {pdf_path}")

        logger.info(f"Конвертация успешна: {pdf_path}")

    except subprocess.TimeoutExpired:
        raise Exception("Таймаут при конвертации DOCX в PDF")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Ошибка конвертации: {e.stderr}")
    except Exception as e:
        raise Exception(f"Неожиданная ошибка при конвертации: {str(e)}")
