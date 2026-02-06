"""
Форматирование заявок для отправки в Telegram.
"""
from datetime import datetime
from typing import Dict, Any


class ApplicationFormatter:
    """Класс для форматирования заявок по трём шаблонам."""

    @staticmethod
    def format_individual_application(data: Dict[str, Any]) -> str:
        """Форматирование заявки от физического лица."""
        return (
            f"🆕 НОВАЯ ЗАЯВКА: Физическое лицо\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"────────────────\n"
            f"👤 Имя: {data.get('name', 'Не указано')}\n"
            f"🏠 Залог: {data.get('collateral', 'Не указано')}\n"
            f"💰 Сумма: {data.get('amount', 0):,} руб.\n"
            f"🎯 Цель займа: {data.get('purpose', 'Не указано')}\n"
            f"📞 Телефон: {data.get('phone', 'Не указано')}\n"
            f"────────────────\n"
            f"🔗 ID сессии: {data.get('session_id', 'Не указано')}"
        )

    @staticmethod
    def format_business_application(data: Dict[str, Any]) -> str:
        """Форматирование заявки от бизнеса."""
        return (
            f"🏢 НОВАЯ ЗАЯВКА: Бизнес\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"────────────────\n"
            f"🏛️ Компания: {data.get('company_name', 'Не указано')}\n"
            f"📝 Тип: Заемщик (бизнес)\n"
            f"💰 Сумма: {data.get('amount', 0):,} руб.\n"
            f"🔒 Обеспечение: {data.get('collateral', 'Не указано')}\n"
            f"🎯 Цель займа: {data.get('purpose', 'Не указано')}\n"
            f"📞 Телефон: {data.get('phone', 'Не указано')}\n"
            f"────────────────\n"
            f"🔗 ID сессии: {data.get('session_id', 'Не указано')}"
        )

    @staticmethod
    def format_investor_application(data: Dict[str, Any]) -> str:
        """Форматирование заявки от инвестора."""
        return (
            f"🤝 НОВАЯ ЗАЯВКА: Инвестор\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"────────────────\n"
            f"👤 Имя: {data.get('name', 'Не указано')}\n"
            f"📝 Тип: Инвестор\n"
            f"💰 Сумма для инвестирования: {data.get('investment_amount', 0):,} руб.\n"
            f"⏱️ Горизонт инвестирования: {data.get('term_months', 0)} месяцев\n"
            f"🎯 Цель: {data.get('investment_goal', 'Не указано')}\n"
            f"📞 Телефон: {data.get('phone', 'Не указано')}\n"
            f"────────────────\n"
            f"🔗 ID сессии: {data.get('session_id', 'Не указано')}"
        )

    @staticmethod
    def format_application(user_type: str, data: Dict[str, Any]) -> str:
        """Основной метод форматирования по типу пользователя."""
        if user_type == 'individual':
            return ApplicationFormatter.format_individual_application(data)
        elif user_type == 'business':
            return ApplicationFormatter.format_business_application(data)
        elif user_type == 'investor':
            return ApplicationFormatter.format_investor_application(data)
        else:
            raise ValueError(f"Неизвестный тип пользователя: {user_type}")

    @staticmethod
    def create_compact_format(user_type: str, data: Dict[str, Any]) -> str:
        """Создает компактный формат (как в ТЗ)."""
        if user_type == 'individual':
            return (
                f"Имя: {data.get('name')}\n"
                f"Залог: {data.get('collateral')}\n"
                f"Сумма: {data.get('amount')}\n"
                f"Цель займа: {data.get('purpose')}\n"
                f"Телефон: {data.get('phone')}"
            )
        elif user_type == 'business':
            return (
                f"Имя: {data.get('company_name')}\n"
                f"Тип: Заемщик (бизнес)\n"
                f"Сумма: {data.get('amount')}\n"
                f"Обеспечение: {data.get('collateral')}\n"
                f"Цель займа: {data.get('purpose')}\n"
                f"Телефон: {data.get('phone')}"
            )
        elif user_type == 'investor':
            return (
                f"Имя: {data.get('name')}\n"
                f"Тип: Инвестор\n"
                f"Сумма для инвестирования: {data.get('investment_amount')}\n"
                f"Горизонт инвестирования: {data.get('term_months')} месяцев\n"
                f"Цель: {data.get('investment_goal')}\n"
                f"Телефон: {data.get('phone')}"
            )