"""
Резервная отправка заявок на email.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSender:
    """Класс для отправки уведомлений на email."""

    def __init__(self):
        # Импортируем здесь, чтобы избежать циклических импортов
        from backend.config import get_settings
        settings = get_settings()

        self.enabled = settings.email_enabled
        self.host = settings.email_host
        self.port = settings.email_port
        self.user = settings.email_user
        self.password = settings.email_password
        self.from_addr = settings.email_from
        self.to_addr = settings.email_to

        if self.enabled and not all([self.host, self.port, self.user, self.password]):
            logger.warning("Email включен, но не все настройки указаны")
            self.enabled = False

    def send_application(self, user_type: str, application_data: Dict[str, Any]) -> bool:
        """
        Отправляет заявку на email.

        Args:
            user_type: Тип пользователя ('individual', 'business', 'investor')
            application_data: Данные заявки

        Returns:
            bool: True если отправка успешна, False в противном случае
        """
        if not self.enabled:
            logger.debug("Email отключен, пропускаем отправку")
            return False

        try:
            from backend.core.application_formatter import ApplicationFormatter

            # Форматируем сообщение
            subject = f"Заявка от {user_type} - BBKinvest"
            plain_text = ApplicationFormatter.format_application(user_type, application_data)

            # Создаем email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_addr
            msg['To'] = self.to_addr

            # Добавляем текстовую версию
            text_part = MIMEText(plain_text, 'plain', 'utf-8')
            msg.attach(text_part)

            # Добавляем HTML версию
            html_content = self._create_html_email(user_type, application_data)
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # Отправляем
            return self._send_email(msg)

        except Exception as e:
            logger.error(f"Ошибка при создании email: {str(e)}", exc_info=True)
            return False

    def send_test_email(self) -> bool:
        """Отправляет тестовое письмо."""
        if not self.enabled:
            logger.warning("Email отключен")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Тестовое письмо от ИИ-консультанта BBKinvest"
            msg['From'] = self.from_addr
            msg['To'] = self.to_addr

            text = "Это тестовое письмо для проверки работы email уведомлений."
            text_part = MIMEText(text, 'plain', 'utf-8')
            msg.attach(text_part)

            return self._send_email(msg)
        except Exception as e:
            logger.error(f"Ошибка отправки тестового письма: {str(e)}")
            return False

    def _send_email(self, msg: MIMEMultipart) -> bool:
        """Отправляет email через SMTP."""
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)

            logger.info(f"Email успешно отправлен на {self.to_addr}")
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки email: {str(e)}")
            return False

    def _create_html_email(self, user_type: str, data: Dict[str, Any]) -> str:
        """Создает HTML версию письма."""
        colors = {
            'individual': "#4CAF50",
            'business': "#2196F3",
            'investor': "#9C27B0"
        }

        type_names = {
            'individual': "Физическое лицо",
            'business': "Бизнес",
            'investor': "Инвестор"
        }

        color = colors.get(user_type, "#607D8B")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .header {{ background-color: {color}; color: white; padding: 15px; border-radius: 5px 5px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .field {{ margin-bottom: 10px; }}
                .label {{ font-weight: bold; color: #555; }}
                .value {{ margin-left: 10px; }}
                .footer {{ margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 12px; color: #777; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🆕 Новая заявка: {type_names[user_type]}</h2>
                    <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="content">
        """

        # Добавляем поля в зависимости от типа
        if user_type == 'individual':
            fields = [
                ("👤 Имя", data.get('name')),
                ("🏠 Залог", data.get('collateral')),
                ("💰 Сумма", f"{data.get('amount', 0):,} руб."),
                ("🎯 Цель займа", data.get('purpose')),
                ("📞 Телефон", data.get('phone'))
            ]
        elif user_type == 'business':
            fields = [
                ("🏛️ Компания", data.get('company_name')),
                ("📝 Тип", "Заемщик (бизнес)"),
                ("💰 Сумма", f"{data.get('amount', 0):,} руб."),
                ("🔒 Обеспечение", data.get('collateral')),
                ("🎯 Цель займа", data.get('purpose')),
                ("📞 Телефон", data.get('phone'))
            ]
        elif user_type == 'investor':
            fields = [
                ("👤 Имя", data.get('name')),
                ("📝 Тип", "Инвестор"),
                ("💰 Сумма для инвестирования", f"{data.get('investment_amount', 0):,} руб."),
                ("⏱️ Горизонт инвестирования", f"{data.get('term_months', 0)} месяцев"),
                ("🎯 Цель", data.get('investment_goal')),
                ("📞 Телефон", data.get('phone'))
            ]

        for label, value in fields:
            html += f"""
                    <div class="field">
                        <span class="label">{label}:</span>
                        <span class="value">{value}</span>
                    </div>
            """

        html += f"""
                </div>
                <div class="footer">
                    <p>Это автоматическое уведомление от ИИ-консультанта BBKinvest</p>
                    <p>ID сессии: {data.get('session_id', 'Не указано')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html