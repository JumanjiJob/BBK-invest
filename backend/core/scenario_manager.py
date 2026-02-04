"""
Управление логикой трёх сценариев.
"""
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from .models import UserType, LoanPurpose, InvestmentGoal
from .validators import validators


class DialogStep(str, Enum):
    """Шаги диалога."""
    WELCOME = "welcome"
    ASK_LOAN_OR_INVEST = "ask_loan_or_invest"
    ASK_INDIVIDUAL_OR_BUSINESS = "ask_individual_or_business"

    # Физическое лицо
    INDIVIDUAL_ASK_NAME = "individual_ask_name"
    INDIVIDUAL_ASK_COLLATERAL = "individual_ask_collateral"
    INDIVIDUAL_ASK_AMOUNT = "individual_ask_amount"
    INDIVIDUAL_ASK_PURPOSE = "individual_ask_purpose"
    INDIVIDUAL_ASK_PHONE = "individual_ask_phone"
    INDIVIDUAL_CONFIRM = "individual_confirm"

    # Бизнес
    BUSINESS_ASK_COMPANY_NAME = "business_ask_company_name"
    BUSINESS_ASK_AMOUNT = "business_ask_amount"
    BUSINESS_ASK_COLLATERAL = "business_ask_collateral"
    BUSINESS_ASK_PURPOSE = "business_ask_purpose"
    BUSINESS_ASK_PHONE = "business_ask_phone"
    BUSINESS_CONFIRM = "business_confirm"

    # Инвестор
    INVESTOR_ASK_NAME = "investor_ask_name"
    INVESTOR_ASK_AMOUNT = "investor_ask_amount"
    INVESTOR_ASK_TERM = "investor_ask_term"
    INVESTOR_ASK_GOAL = "investor_ask_goal"
    INVESTOR_ASK_PHONE = "investor_ask_phone"
    INVESTOR_CONFIRM = "investor_confirm"

    COMPLETED = "completed"
    ERROR = "error"


class ScenarioManager:
    """Управление логикой трёх сценариев."""

    # Тексты вопросов
    MESSAGES = {
        DialogStep.WELCOME: "Здравствуйте! Я ИИ-консультант BBKinvest. Чем могу помочь?",
        DialogStep.ASK_LOAN_OR_INVEST: "Вы рассматриваете получение займа или хотите инвестировать?",
        DialogStep.ASK_INDIVIDUAL_OR_BUSINESS: "Займ оформляется на физическое лицо или на бизнес (ЮЛ/ИП)?",

        # Физическое лицо
        DialogStep.INDIVIDUAL_ASK_NAME: "Консультирую по займам под залог автомобиля или недвижимости. Для оформления заявки потребуется несколько данных.\n\nВведите ваше имя:",
        DialogStep.INDIVIDUAL_ASK_COLLATERAL: "Укажите залог: марку, модель и год выпуска авто или описание недвижимости.\nПример: Kia Sportage, 2021 год",
        DialogStep.INDIVIDUAL_ASK_AMOUNT: "Желаемая сумма займа (в рублях):",
        DialogStep.INDIVIDUAL_ASK_PURPOSE: "Цель займа:\n(например: развитие бизнеса, личные нужды, недвижимость)",
        DialogStep.INDIVIDUAL_ASK_PHONE: "Введите номер телефона для связи:",
        DialogStep.INDIVIDUAL_CONFIRM: "Спасибо! Проверьте данные:\n\nИмя: {name}\nЗалог: {collateral}\nСумма: {amount:,} руб.\nЦель: {purpose}\nТелефон: {phone}\n\nВсё верно?",

        # Бизнес
        DialogStep.BUSINESS_ASK_COMPANY_NAME: "Консультирую по займам для юридических лиц и ИП. Уточните, какое обеспечение имеется:\n\n• Недвижимость (офис, склад, производство)\n• Движимое имущество (оборудование, транспорт, техника)\n• Интеллектуальная собственность (патенты, товарные знаки)\n\nУкажите полное название компании или ФИО с указанием 'ИП':\nПримеры:\n- Для ООО: 'ООО «ТехноПром»'\n- Для ИП: 'ИП Иванов Игорь'",
        DialogStep.BUSINESS_ASK_AMOUNT: "Желаемая сумма займа (в рублях):",
        DialogStep.BUSINESS_ASK_COLLATERAL: "Опишите обеспечение подробно (можно несколько видов):\nПример: Станки (оборудование 2023 г.), товарный знак 'Марка'",
        DialogStep.BUSINESS_ASK_PURPOSE: "Цель займа:",
        DialogStep.BUSINESS_ASK_PHONE: "Контактный телефон для связи:",
        DialogStep.BUSINESS_CONFIRM: "Проверьте данные:\n\nКомпания: {company_name}\nСумма: {amount:,} руб.\nОбеспечение: {collateral}\nЦель: {purpose}\nТелефон: {phone}\n\nВсё верно?",

        # Инвестор
        DialogStep.INVESTOR_ASK_NAME: "Консультирую по инвестиционным продуктам под обеспечение залогового имущества. Для подбора варианта потребуется информация.\n\nВведите ваше имя:",
        DialogStep.INVESTOR_ASK_AMOUNT: "Сумма для инвестирования (в рублях):",
        DialogStep.INVESTOR_ASK_TERM: "Горизонт инвестирования (в месяцах):",
        DialogStep.INVESTOR_ASK_GOAL: "Цель инвестирования:\n(например: пассивный доход, сохранение капитала, диверсификация)",
        DialogStep.INVESTOR_ASK_PHONE: "Контактный телефон для связи:",
        DialogStep.INVESTOR_CONFIRM: "Проверьте данные:\n\nИмя: {name}\nСумма: {investment_amount:,} руб.\nСрок: {term_months} мес.\nЦель: {investment_goal}\nТелефон: {phone}\n\nВсё верно?",

        DialogStep.COMPLETED: "Заявка отправлена! Специалист свяжется с вами в ближайшее время. Спасибо!",
    }

    # Варианты ответов для кнопок
    OPTIONS = {
        DialogStep.ASK_LOAN_OR_INVEST: ["Займ", "Инвестировать"],
        DialogStep.ASK_INDIVIDUAL_OR_BUSINESS: ["Физическое лицо", "Бизнес"],
        DialogStep.INDIVIDUAL_CONFIRM: ["Да, отправить заявку", "Нет, исправить"],
        DialogStep.BUSINESS_CONFIRM: ["Да, отправить", "Нет, исправить"],
        DialogStep.INVESTOR_CONFIRM: ["Да, отправить", "Нет, исправить"],
    }

    def get_next_step(self, current_step: DialogStep, user_input: str,
                      session_data: Dict[str, Any]) -> Tuple[DialogStep, Dict[str, Any]]:
        """Определяет следующий шаг на основе текущего и ввода пользователя."""

        # Логика приветствия
        if current_step == DialogStep.WELCOME:
            return DialogStep.ASK_LOAN_OR_INVEST, {}

        # Определение типа услуги
        if current_step == DialogStep.ASK_LOAN_OR_INVEST:
            user_input_lower = user_input.lower()
            if "займ" in user_input_lower or "кредит" in user_input_lower:
                session_data["service_type"] = "loan"
                return DialogStep.ASK_INDIVIDUAL_OR_BUSINESS, {}
            elif "инвест" in user_input_lower:
                session_data["service_type"] = "invest"
                session_data["user_type"] = UserType.INVESTOR
                return DialogStep.INVESTOR_ASK_NAME, {}

        # Определение типа заемщика
        if current_step == DialogStep.ASK_INDIVIDUAL_OR_BUSINESS:
            user_input_lower = user_input.lower()
            if "физ" in user_input_lower or "лич" in user_input_lower:
                session_data["user_type"] = UserType.INDIVIDUAL
                return DialogStep.INDIVIDUAL_ASK_NAME, {}
            elif "биз" in user_input_lower or "юр" in user_input_lower or "ип" in user_input_lower:
                session_data["user_type"] = UserType.BUSINESS
                return DialogStep.BUSINESS_ASK_COMPANY_NAME, {}

        # Обработка сценариев
        if session_data.get("user_type") == UserType.INDIVIDUAL:
            return self._handle_individual_scenario(current_step, user_input, session_data)
        elif session_data.get("user_type") == UserType.BUSINESS:
            return self._handle_business_scenario(current_step, user_input, session_data)
        elif session_data.get("user_type") == UserType.INVESTOR:
            return self._handle_investor_scenario(current_step, user_input, session_data)

        return DialogStep.ERROR, {"error": "Неизвестный сценарий"}

    def _handle_individual_scenario(self, current_step: DialogStep, user_input: str,
                                    session_data: Dict[str, Any]) -> Tuple[DialogStep, Dict[str, Any]]:
        """Обработка сценария физического лица."""

        steps = [
            (DialogStep.INDIVIDUAL_ASK_NAME, "name", validators.validate_name),
            (DialogStep.INDIVIDUAL_ASK_COLLATERAL, "collateral", None),
            (DialogStep.INDIVIDUAL_ASK_AMOUNT, "amount", validators.validate_amount),
            (DialogStep.INDIVIDUAL_ASK_PURPOSE, "purpose", None),
            (DialogStep.INDIVIDUAL_ASK_PHONE, "phone", validators.validate_phone),
        ]

        for step, field, validator in steps:
            if current_step == step:
                if validator:
                    is_valid, result = validator(user_input)
                    if not is_valid:
                        return current_step, {"error": result}
                    session_data[field] = result
                else:
                    session_data[field] = user_input.strip()

                # Получаем следующий шаг
                next_step_index = steps.index((step, field, validator)) + 1
                if next_step_index < len(steps):
                    return steps[next_step_index][0], {}
                else:
                    # Все данные собраны, переходим к подтверждению
                    return DialogStep.INDIVIDUAL_CONFIRM, {}

        # Обработка подтверждения
        if current_step == DialogStep.INDIVIDUAL_CONFIRM:
            if "да" in user_input.lower() or "отправ" in user_input.lower():
                return DialogStep.COMPLETED, session_data
            else:
                # Возвращаем к редактированию (можно усложнить логику выбора поля)
                return DialogStep.INDIVIDUAL_ASK_NAME, {"reset": True}

        return DialogStep.ERROR, {"error": "Неизвестный шаг в сценарии физлица"}

    def _handle_business_scenario(self, current_step: DialogStep, user_input: str,
                                  session_data: Dict[str, Any]) -> Tuple[DialogStep, Dict[str, Any]]:
        """Обработка сценария бизнеса."""

        steps = [
            (DialogStep.BUSINESS_ASK_COMPANY_NAME, "company_name", validators.validate_company_name),
            (DialogStep.BUSINESS_ASK_AMOUNT, "amount", validators.validate_amount),
            (DialogStep.BUSINESS_ASK_COLLATERAL, "collateral", None),
            (DialogStep.BUSINESS_ASK_PURPOSE, "purpose", None),
            (DialogStep.BUSINESS_ASK_PHONE, "phone", validators.validate_phone),
        ]

        for step, field, validator in steps:
            if current_step == step:
                if validator:
                    is_valid, result = validator(user_input)
                    if not is_valid:
                        return current_step, {"error": result}
                    session_data[field] = result
                else:
                    session_data[field] = user_input.strip()

                next_step_index = steps.index((step, field, validator)) + 1
                if next_step_index < len(steps):
                    return steps[next_step_index][0], {}
                else:
                    return DialogStep.BUSINESS_CONFIRM, {}

        if current_step == DialogStep.BUSINESS_CONFIRM:
            if "да" in user_input.lower() or "отправ" in user_input.lower():
                return DialogStep.COMPLETED, session_data
            else:
                return DialogStep.BUSINESS_ASK_COMPANY_NAME, {"reset": True}

        return DialogStep.ERROR, {"error": "Неизвестный шаг в сценарии бизнеса"}

    def _handle_investor_scenario(self, current_step: DialogStep, user_input: str,
                                  session_data: Dict[str, Any]) -> Tuple[DialogStep, Dict[str, Any]]:
        """Обработка сценария инвестора."""

        steps = [
            (DialogStep.INVESTOR_ASK_NAME, "name", validators.validate_name),
            (DialogStep.INVESTOR_ASK_AMOUNT, "investment_amount", validators.validate_amount),
            (DialogStep.INVESTOR_ASK_TERM, "term_months", validators.validate_term_months),
            (DialogStep.INVESTOR_ASK_GOAL, "investment_goal", None),
            (DialogStep.INVESTOR_ASK_PHONE, "phone", validators.validate_phone),
        ]

        for step, field, validator in steps:
            if current_step == step:
                if validator:
                    is_valid, result = validator(user_input)
                    if not is_valid:
                        return current_step, {"error": result}
                    session_data[field] = result
                else:
                    session_data[field] = user_input.strip()

                next_step_index = steps.index((step, field, validator)) + 1
                if next_step_index < len(steps):
                    return steps[next_step_index][0], {}
                else:
                    return DialogStep.INVESTOR_CONFIRM, {}

        if current_step == DialogStep.INVESTOR_CONFIRM:
            if "да" in user_input.lower() or "отправ" in user_input.lower():
                return DialogStep.COMPLETED, session_data
            else:
                return DialogStep.INVESTOR_ASK_NAME, {"reset": True}

        return DialogStep.ERROR, {"error": "Неизвестный шаг в сценарии инвестора"}

    def get_message(self, step: DialogStep, data: Dict[str, Any] = None) -> str:
        """Получает текст сообщения для шага."""
        message_template = self.MESSAGES.get(step, "Извините, произошла ошибка.")

        if data and "{" in message_template:
            try:
                return message_template.format(**data)
            except KeyError:
                return message_template

        return message_template

    def get_options(self, step: DialogStep) -> List[str]:
        """Получает варианты ответов для шага."""
        return self.OPTIONS.get(step, [])


scenario_manager = ScenarioManager()