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

from config import (
    TEMPLATE_PATH,
    OUTPUT_DIR,
    PDF_CONVERSION_TIMEOUT,
    PDF_CONVERSION_RETRIES,
    LIBREOFFICE_PATHS,
)
from exceptions import (
    TemplateNotFoundError,
    PDFConversionError,
    LibreOfficeNotFoundError,
    PDFConversionTimeoutError,
)
from validators import sanitize_text

logger = logging.getLogger(__name__)


async def generate_contract(data: Dict[str, Any]) -> str:
    """
    Генерирует договор на основе шаблона и данных пользователя

    Args:
        data: Словарь с данными для заполнения договора

    Returns:
        Путь к сгенерированному PDF-файлу

    Raises:
        TemplateNotFoundError: Если шаблон не найден
        PDFConversionError: При ошибках конвертации в PDF
    """
    # Проверяем наличие шаблона
    if not TEMPLATE_PATH.exists():
        logger.error(f"Шаблон не найден: {TEMPLATE_PATH}")
        raise TemplateNotFoundError(f"Шаблон договора не найден: {TEMPLATE_PATH}")

    # Создаем директорию для выходных файлов
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Генерируем уникальное имя файла с user_id для безопасности
    user_id = data.get("user_id", "unknown")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_filename = f"contract_{user_id}_{timestamp}"
    docx_path = OUTPUT_DIR / f"{output_filename}.docx"
    pdf_path = OUTPUT_DIR / f"{output_filename}.pdf"

    try:
        # Загружаем шаблон
        logger.info(f"Генерация договора для пользователя {user_id}")
        doc = DocxTemplate(TEMPLATE_PATH)

        # Подготавливаем контекст для шаблона
        context = prepare_context(data)

        # Рендерим документ
        logger.info("Рендеринг документа с данными")
        doc.render(context)

        # Сохраняем DOCX
        doc.save(str(docx_path))
        logger.info(f"DOCX сохранен: {docx_path}")

        # Конвертируем в PDF с retry логикой
        logger.info("Конвертация DOCX -> PDF")
        convert_to_pdf_with_retry(str(docx_path), str(pdf_path))
        logger.info(f"PDF создан успешно: {pdf_path}")

        return str(pdf_path)

    except (TemplateNotFoundError, PDFConversionError, LibreOfficeNotFoundError):
        # Пробрасываем кастомные исключения
        _cleanup_files(docx_path, pdf_path)
        raise
    except Exception as e:
        # Неожиданная ошибка
        logger.error(f"Неожиданная ошибка при генерации договора: {e}", exc_info=True)
        _cleanup_files(docx_path, pdf_path)
        raise PDFConversionError(f"Ошибка при генерации договора: {str(e)}")


def _cleanup_files(*file_paths: Path) -> None:
    """Удаляет временные файлы"""
    for file_path in file_paths:
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Удален временный файл: {file_path}")
        except Exception as e:
            logger.warning(f"Не удалось удалить файл {file_path}: {e}")


def prepare_context(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Подготавливает контекст для шаблона договора

    Args:
        data: Исходные данные от пользователя

    Returns:
        Словарь с подготовленными данными для шаблона
    """

    def clean_value(value: Any) -> Any:
        """Очищает и санитизирует значение"""
        if value is None:
            return None
        if isinstance(value, str):
            # Санитизация для защиты от инъекций
            value = sanitize_text(value)
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


def find_libreoffice() -> str:
    """
    Находит LibreOffice в системе

    Returns:
        Путь к исполняемому файлу LibreOffice

    Raises:
        LibreOfficeNotFoundError: Если LibreOffice не найден
    """
    for path in LIBREOFFICE_PATHS:
        if os.path.exists(path) or path == "soffice":
            logger.debug(f"LibreOffice найден: {path}")
            return path

    raise LibreOfficeNotFoundError(
        "LibreOffice не найден. Установите LibreOffice:\n"
        "macOS: brew install --cask libreoffice\n"
        "Ubuntu/Debian: sudo apt-get install libreoffice\n"
        "Windows: скачайте с https://www.libreoffice.org/"
    )


def convert_to_pdf(docx_path: str, pdf_path: str) -> None:
    """
    Конвертирует DOCX в PDF с помощью LibreOffice

    Args:
        docx_path: Путь к исходному DOCX файлу
        pdf_path: Путь для сохранения PDF файла

    Raises:
        LibreOfficeNotFoundError: Если LibreOffice не установлен
        PDFConversionTimeoutError: При таймауте конвертации
        PDFConversionError: При ошибке конвертации
    """
    soffice_cmd = find_libreoffice()
    output_dir = os.path.dirname(pdf_path)

    cmd = [
        soffice_cmd,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_dir,
        docx_path
    ]

    logger.debug(f"Команда конвертации: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=PDF_CONVERSION_TIMEOUT,
            check=True
        )

        logger.debug(f"LibreOffice stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"LibreOffice stderr: {result.stderr}")

        # Проверяем, что PDF создан
        if not os.path.exists(pdf_path):
            raise PDFConversionError(f"PDF файл не был создан: {pdf_path}")

        logger.info(f"Конвертация успешна: {pdf_path}")

    except subprocess.TimeoutExpired:
        logger.error(f"Таймаут конвертации ({PDF_CONVERSION_TIMEOUT}s)")
        raise PDFConversionTimeoutError(
            f"Превышен таймаут конвертации ({PDF_CONVERSION_TIMEOUT} секунд)"
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка LibreOffice: {e.stderr}")
        raise PDFConversionError(f"Ошибка конвертации LibreOffice: {e.stderr}")


def convert_to_pdf_with_retry(docx_path: str, pdf_path: str) -> None:
    """
    Конвертирует DOCX в PDF с повторными попытками

    Args:
        docx_path: Путь к DOCX файлу
        pdf_path: Путь для PDF файла

    Raises:
        PDFConversionError: Если все попытки неудачны
    """
    last_error = None

    for attempt in range(1, PDF_CONVERSION_RETRIES + 1):
        try:
            logger.info(f"Попытка конвертации {attempt}/{PDF_CONVERSION_RETRIES}")
            convert_to_pdf(docx_path, pdf_path)
            return  # Успешная конвертация
        except PDFConversionTimeoutError as e:
            last_error = e
            logger.warning(f"Попытка {attempt} не удалась (таймаут)")
            if attempt < PDF_CONVERSION_RETRIES:
                logger.info("Повторная попытка...")
        except (PDFConversionError, LibreOfficeNotFoundError) as e:
            # Эти ошибки не имеет смысла повторять
            raise

    # Все попытки исчерпаны
    logger.error(f"Все {PDF_CONVERSION_RETRIES} попытки конвертации не удались")
    raise PDFConversionError(f"Не удалось сконвертировать PDF после {PDF_CONVERSION_RETRIES} попыток: {last_error}")
