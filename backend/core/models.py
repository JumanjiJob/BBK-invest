"""
Модели данных для ИИ-консультанта.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum

class UserType(str, Enum):
    """Типы пользователей."""
    INDIVIDUAL = "individual"  # Физическое лицо
    BUSINESS = "business"      # ЮЛ/ИП
    INVESTOR = "investor"      # Инвестор

class LoanPurpose(str, Enum):
    """Цели займа."""
    BUSINESS_DEVELOPMENT = "развитие бизнеса"
    PRODUCTION_DEVELOPMENT = "развитие производства"
    PERSONAL_NEEDS = "личные нужды"
    REAL_ESTATE = "недвижимость"
    OTHER = "другое"

class InvestmentGoal(str, Enum):
    """Цели инвестирования."""
    PASSIVE_INCOME = "пассивный доход"
    CAPITAL_PRESERVATION = "сохранение капитала"
    DIVERSIFICATION = "диверсификация"
    OTHER = "другое"

class BaseApplication(BaseModel):
    """Базовая модель заявки."""
    user_type: UserType
    phone: str
    created_at: Optional[str] = None

class IndividualApplication(BaseApplication):
    """Заявка от физического лица."""
    name: str
    collateral: str  # Залог (авто или недвижимость)
    amount: int
    purpose: LoanPurpose

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Сумма должна быть положительной')
        if v > 100_000_000:  # 100 млн руб лимит
            raise ValueError('Сумма слишком большая')
        return v

class BusinessApplication(BaseApplication):
    """Заявка от бизнеса (ЮЛ/ИП)."""
    company_name: str
    amount: int
    collateral: str  # Обеспечение
    purpose: LoanPurpose

class InvestorApplication(BaseApplication):
    """Заявка от инвестора."""
    name: str
    investment_amount: int
    term_months: int
    investment_goal: InvestmentGoal

    @validator('term_months')
    def validate_term(cls, v):
        if v < 1 or v > 120:  # От 1 месяца до 10 лет
            raise ValueError('Срок должен быть от 1 до 120 месяцев')
        return v

class DialogState(BaseModel):
    """Состояние диалога с пользователем."""
    session_id: str
    user_type: Optional[UserType] = None
    current_step: str = "start"
    collected_data: dict = {}
    completed: bool = False