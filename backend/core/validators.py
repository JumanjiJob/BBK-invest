"""
Валидация данных для всех сценариев.
"""
import re
from typing import Tuple, Optional


class DataValidators:
    """Класс валидаторов для проверки введённых данных."""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Валидация российского номера телефона."""
        # Убираем все нецифровые символы
        digits = re.sub(r'\D', '', phone)

        # Проверяем длину (10-11 цифр)
        if len(digits) not in [10, 11]:
            return False, "Номер должен содержать 10-11 цифр"

        # Проверяем начало номера
        if not (digits.startswith('7') or digits.startswith('8') or
                (len(digits) == 10 and digits.startswith('9'))):
            return False, "Номер должен начинаться с 7, 8 или 9"

        return True, digits[-10:]  # Возвращаем 10 цифр без кода страны

    @staticmethod
    def validate_amount(amount_str: str, min_amount: int = 10000,
                        max_amount: int = 100000000) -> Tuple[bool, Optional[int]]:
        """Валидация суммы."""
        try:
            # Убираем пробелы и нецифровые символы, кроме точки/запятой
            clean_str = re.sub(r'[^\d,.]', '', amount_str)
            clean_str = clean_str.replace(',', '.')

            amount = int(float(clean_str))

            if amount < min_amount:
                return False, f"Минимальная сумма: {min_amount:,} руб."

            if amount > max_amount:
                return False, f"Максимальная сумма: {max_amount:,} руб."

            return True, amount

        except (ValueError, AttributeError):
            return False, "Введите корректную сумму (только цифры)"

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """Валидация имени."""
        name = name.strip()

        if len(name) < 2:
            return False, "Имя должно содержать минимум 2 символа"

        if len(name) > 100:
            return False, "Имя слишком длинное (макс. 100 символов)"

        # Проверяем на наличие только допустимых символов
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', name):
            return False, "Имя содержит недопустимые символы"

        return True, name

    @staticmethod
    def validate_term_months(term_str: str) -> Tuple[bool, Optional[int]]:
        """Валидация срока в месяцах."""
        try:
            term = int(term_str)

            if term < 1:
                return False, "Срок должен быть не менее 1 месяца"

            if term > 120:
                return False, "Максимальный срок: 120 месяцев (10 лет)"

            return True, term

        except ValueError:
            return False, "Введите корректное число месяцев"

    @staticmethod
    def validate_company_name(company_name: str) -> Tuple[bool, str]:
        """Валидация названия компании."""
        company_name = company_name.strip()

        if len(company_name) < 2:
            return False, "Название должно содержать минимум 2 символа"

        # Для ИП проверяем наличие префикса
        if company_name.lower().startswith('ип '):
            # Извлекаем ФИО после "ИП "
            fio = company_name[3:].strip()
            if len(fio.split()) < 2:
                return False, "Для ИП укажите ФИО полностью после 'ИП'"

        return True, company_name


validators = DataValidators()