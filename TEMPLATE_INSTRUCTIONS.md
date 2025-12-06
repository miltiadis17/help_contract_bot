# Инструкция по созданию шаблона договора с условными блоками

## Проблема и решение

**Проблема:** Если пользователь не заполнил поле (например, ИНН), в договоре появляется "ИНН: " с пустым значением.

**Решение:** Используйте условные блоки Jinja2 в шаблоне `dogovor_template.docx`, чтобы скрывать строки с незаполненными полями.

---

## Синтаксис условных блоков в DOCX

В шаблоне используйте Jinja2-синтаксис:

```
{% if variable_name %}
Текст, который будет показан только если поле заполнено: {{ variable_name }}
{% endif %}
```

### Примеры использования:

#### 1. Простое условие (одна строка)
```
{% if client_inn %}ИНН: {{ client_inn }}{% endif %}
```

#### 2. Многострочное условие
```
{% if client_email %}
Email: {{ client_email }}
{% endif %}
```

#### 3. Комбинированное условие (несколько полей в одной строке)
```
{% if client_passport_series and client_passport_number %}
Паспорт: серия {{ client_passport_series }} № {{ client_passport_number }}
{% endif %}
```

#### 4. Условие "ИЛИ" (показать если хотя бы одно поле заполнено)
```
{% if client_phone or client_email %}
Контакты:
{% if client_phone %}Телефон: {{ client_phone }}{% endif %}
{% if client_email %}Email: {{ client_email }}{% endif %}
{% endif %}
```

---

## Полный пример шаблона договора

Создайте файл **dogovor_template.docx** в Microsoft Word или LibreOffice Writer:

---

**ДОГОВОР ОКАЗАНИЯ УСЛУГ**

№ {{ contract_number }} от {{ current_date }}

г. _______________

---

### 1. СТОРОНЫ ДОГОВОРА

**Заказчик:**

ФИО: {{ client_full_name }}

{% if client_passport_series and client_passport_number %}Паспорт: серия {{ client_passport_series }} № {{ client_passport_number }}{% endif %}

{% if client_passport_issued_by %}Выдан: {{ client_passport_issued_by }}{% if client_passport_issue_date %}, {{ client_passport_issue_date }}{% endif %}{% endif %}

{% if client_birth_date %}Дата рождения: {{ client_birth_date }}{% endif %}

{% if client_birth_place %}Место рождения: {{ client_birth_place }}{% endif %}

{% if client_address %}Адрес регистрации: {{ client_address }}{% endif %}

{% if client_phone %}Телефон: {{ client_phone }}{% endif %}

{% if client_email %}Email: {{ client_email }}{% endif %}

{% if client_inn %}ИНН: {{ client_inn }}{% endif %}

именуемый в дальнейшем "Заказчик", с одной стороны, и

---

**Исполнитель:**

ФИО: {{ executor_full_name }}

{% if executor_passport_series and executor_passport_number %}Паспорт: серия {{ executor_passport_series }} № {{ executor_passport_number }}{% endif %}

{% if executor_passport_issued_by %}Выдан: {{ executor_passport_issued_by }}{% if executor_passport_issue_date %}, {{ executor_passport_issue_date }}{% endif %}{% endif %}

{% if executor_birth_date %}Дата рождения: {{ executor_birth_date }}{% endif %}

{% if executor_birth_place %}Место рождения: {{ executor_birth_place }}{% endif %}

{% if executor_address %}Адрес регистрации: {{ executor_address }}{% endif %}

{% if executor_phone %}Телефон: {{ executor_phone }}{% endif %}

{% if executor_email %}Email: {{ executor_email }}{% endif %}

{% if executor_inn %}ИНН: {{ executor_inn }}{% endif %}

именуемый в дальнейшем "Исполнитель", с другой стороны, совместно именуемые "Стороны", заключили настоящий договор о нижеследующем:

---

### 2. ПРЕДМЕТ ДОГОВОРА

2.1. Исполнитель обязуется оказать услуги:

{{ contract_subject }}

2.2. Заказчик обязуется принять и оплатить оказанные услуги в порядке и на условиях, предусмотренных настоящим Договором.

---

### 3. СТОИМОСТЬ УСЛУГ И ПОРЯДОК РАСЧЕТОВ

{% if contract_amount %}3.1. Стоимость услуг по настоящему Договору составляет: **{{ contract_amount }}**{% endif %}

{% if contract_payment_terms %}
3.2. Порядок оплаты:

{{ contract_payment_terms }}
{% endif %}

3.3. Оплата производится путем перечисления денежных средств на расчетный счет Исполнителя.

---

### 4. СРОКИ ВЫПОЛНЕНИЯ РАБОТ

{% if contract_start_date %}4.1. Договор вступает в силу с: {{ contract_start_date }}{% endif %}

{% if contract_deadline %}4.2. Срок оказания услуг: {{ contract_deadline }}{% endif %}

---

### 5. ПРАВА И ОБЯЗАННОСТИ СТОРОН

5.1. Исполнитель обязуется:
- Оказать услуги качественно и в установленные сроки
- Обеспечить конфиденциальность полученной информации

5.2. Заказчик обязуется:
- Своевременно оплатить услуги
- Предоставить необходимую информацию для выполнения услуг

---

### 6. ОТВЕТСТВЕННОСТЬ СТОРОН

6.1. За неисполнение или ненадлежащее исполнение обязательств по настоящему Договору Стороны несут ответственность в соответствии с действующим законодательством Российской Федерации.

6.2. Все споры решаются путем переговоров, а при недостижении согласия – в судебном порядке.

---

{% if executor_bank_name or executor_bank_account or executor_bank_bik or executor_bank_corr_account %}
### 7. БАНКОВСКИЕ РЕКВИЗИТЫ ИСПОЛНИТЕЛЯ

Получатель: {{ executor_full_name }}

{% if executor_bank_name %}Банк: {{ executor_bank_name }}{% endif %}

{% if executor_bank_account %}Расчетный счет: {{ executor_bank_account }}{% endif %}

{% if executor_bank_bik %}БИК: {{ executor_bank_bik }}{% endif %}

{% if executor_bank_corr_account %}Корреспондентский счет: {{ executor_bank_corr_account }}{% endif %}

---
{% endif %}

{% if contract_additional_terms %}
### 8. ДОПОЛНИТЕЛЬНЫЕ УСЛОВИЯ

{{ contract_additional_terms }}

---
{% endif %}

### 9. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

9.1. Настоящий Договор составлен в двух экземплярах, имеющих одинаковую юридическую силу, по одному для каждой из Сторон.

9.2. Изменения и дополнения к Договору действительны при условии, если они совершены в письменной форме и подписаны уполномоченными представителями Сторон.

---

### ПОДПИСИ СТОРОН:

**Заказчик:**

_____________________  / {{ client_full_name }} /

Дата: __________________


**Исполнитель:**

_____________________  / {{ executor_full_name }} /

Дата: __________________

---

## Как создать шаблон в Word/LibreOffice

### Шаг 1: Создание файла
1. Откройте Microsoft Word или LibreOffice Writer
2. Создайте новый документ

### Шаг 2: Вставка текста с условиями
1. Скопируйте текст выше
2. Вставьте в документ
3. **ВАЖНО:** Убедитесь, что весь Jinja2-синтаксис (`{% if %}`, `{{ }}`) сохранился корректно

### Шаг 3: Форматирование
- Настройте шрифты, отступы, выравнивание по вашему усмотрению
- Сделайте заголовки жирными
- Добавьте нумерацию разделов

### Шаг 4: Проверка синтаксиса
Убедитесь, что:
- Все условные блоки имеют закрывающий `{% endif %}`
- Переменные правильно указаны: `{{ variable_name }}`
- Нет лишних пробелов внутри `{{ }}`

### Шаг 5: Сохранение
1. Сохраните файл как **dogovor_template.docx**
2. Поместите файл в корневую папку проекта `help_contract_bot/`

---

## Важные моменты

### ✅ Правильно:
```
{% if client_inn %}ИНН: {{ client_inn }}{% endif %}
```

### ❌ Неправильно:
```
ИНН: {{ client_inn }}  ← Будет показывать "ИНН: " даже если поле пустое
```

---

## Тестирование шаблона

После создания шаблона:

1. Запустите бота: `python main.py`
2. Выберите минимальный набор полей
3. Заполните только обязательные поля
4. Проверьте, что в PDF нет пустых строк типа "ИНН: " или "Email: "

---

## Дополнительные примеры условий

### Показать блок только если ВСЕ поля заполнены:
```
{% if executor_bank_name and executor_bank_account and executor_bank_bik %}
Банковские реквизиты:
Банк: {{ executor_bank_name }}
Счет: {{ executor_bank_account }}
БИК: {{ executor_bank_bik }}
{% endif %}
```

### Показать одно из двух:
```
{% if contract_payment_terms %}
{{ contract_payment_terms }}
{% else %}
Оплата по факту выполнения работ
{% endif %}
```

### Условие с проверкой на несколько значений:
```
{% if client_phone or client_email %}
Контактная информация:
{% if client_phone %}Телефон: {{ client_phone }}{% endif %}
{% if client_email %}Email: {{ client_email }}{% endif %}
{% endif %}
```

---

## Список всех доступных переменных

### Заказчик:
- `client_full_name`
- `client_passport_series`
- `client_passport_number`
- `client_passport_issued_by`
- `client_passport_issue_date`
- `client_birth_date`
- `client_birth_place`
- `client_address`
- `client_phone`
- `client_email`
- `client_inn`

### Исполнитель:
- `executor_full_name`
- `executor_passport_series`
- `executor_passport_number`
- `executor_passport_issued_by`
- `executor_passport_issue_date`
- `executor_birth_date`
- `executor_birth_place`
- `executor_address`
- `executor_phone`
- `executor_email`
- `executor_inn`

### Договор:
- `contract_subject`
- `contract_amount`
- `contract_deadline`
- `contract_start_date`
- `contract_payment_terms`
- `contract_additional_terms`

### Банковские реквизиты:
- `executor_bank_name`
- `executor_bank_account`
- `executor_bank_bik`
- `executor_bank_corr_account`

### Системные (всегда доступны):
- `current_date` - текущая дата в формате ДД.ММ.ГГГГ
- `contract_number` - уникальный номер договора

---

## Поддержка

Если шаблон не работает:
1. Проверьте, что все `{% if %}` имеют соответствующий `{% endif %}`
2. Убедитесь, что имена переменных написаны правильно
3. Посмотрите логи в `bot.log` для диагностики ошибок
