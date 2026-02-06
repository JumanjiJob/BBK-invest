"""
Скрипт для тестирования отправки заявок в Telegram.
"""
import sys
import os
import time
from pathlib import Path
import random

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.utils.telegram_helper import create_telegram_sender, create_notification_service
from backend.core.application_formatter import ApplicationFormatter


def generate_test_applications():
    """Генерирует тестовые заявки трех типов."""

    # Русские имена для теста
    russian_names = [
        "Иван", "Алексей", "Сергей", "Дмитрий", "Андрей",
        "Екатерина", "Мария", "Анна", "Ольга", "Наталья"
    ]

    russian_surnames = [
        "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов",
        "Иванова", "Петрова", "Сидорова", "Смирнова", "Кузнецова"
    ]

    companies = [
        "ООО 'ТехноПром'", "АО 'СтройГрад'", "ООО 'АгроХолдинг'",
        "ЗАО 'ФинансГрупп'", "ООО 'ЛогистикСервис'",
        "ИП Петров Игорь", "ИП Сидорова Анна", "ИП Кузнецов Алексей"
    ]

    car_brands = ["Toyota", "Kia", "Hyundai", "Skoda", "BMW", "Mercedes", "Audi", "Lexus"]
    car_models = ["Camry", "Sportage", "Tucson", "Octavia", "X5", "E-Class", "A6", "RX"]

    real_estate_types = ["квартира", "дом", "дача", "коммерческая недвижимость", "земельный участок"]

    test_applications = []

    # 10 заявок от физических лиц
    for i in range(1, 11):
        name = f"{random.choice(russian_names)} {random.choice(russian_surnames)}"
        car_brand = random.choice(car_brands)
        car_model = random.choice(car_models)
        year = random.randint(2015, 2023)

        test_applications.append({
            'type': 'individual',
            'data': {
                'name': name,
                'collateral': f"{car_brand} {car_model}, {year} год",
                'amount': random.randint(500000, 3000000),
                'purpose': random.choice(["развитие бизнеса", "покупка недвижимости", "ремонт", "образование", "лечение"]),
                'phone': f"89{random.randint(100000000, 999999999)}",
                'session_id': f"test_indiv_{i}"
            }
        })

    # 10 заявок от бизнеса
    for i in range(1, 11):
        company = random.choice(companies)
        collateral_types = [
            f"Недвижимость: {random.choice(real_estate_types)}, {random.randint(50, 500)} кв.м",
            f"Оборудование: станки, производственная линия {random.randint(2018, 2023)} г.в.",
            f"Транспорт: грузовой автомобиль {random.randint(2019, 2023)} г.в.",
            f"Товарный знак '{random.choice(['Техно', 'Агро', 'Строй', 'Фин'])}{random.randint(100, 999)}'"
        ]

        test_applications.append({
            'type': 'business',
            'data': {
                'company_name': company,
                'amount': random.randint(2000000, 15000000),
                'collateral': random.choice(collateral_types),
                'purpose': random.choice(["развитие производства", "пополнение оборотных средств", "закупка оборудования", "расширение бизнеса"]),
                'phone': f"89{random.randint(100000000, 999999999)}",
                'session_id': f"test_bus_{i}"
            }
        })

    # 10 заявок от инвесторов
    for i in range(1, 11):
        name = f"{random.choice(russian_names)} {random.choice(russian_surnames)}"

        test_applications.append({
            'type': 'investor',
            'data': {
                'name': name,
                'investment_amount': random.randint(1000000, 10000000),
                'term_months': random.choice([6, 12, 18, 24, 36, 48, 60]),
                'investment_goal': random.choice(["пассивный доход", "сохранение капитала", "диверсификация портфеля", "накопление на пенсию"]),
                'phone': f"89{random.randint(100000000, 999999999)}",
                'session_id': f"test_inv_{i}"
            }
        })

    return test_applications


def main():
    """Основная функция тестирования."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ОТПРАВКИ ЗАЯВОК В TELEGRAM")
    print("=" * 60)

    # Создаем экземпляры
    telegram_sender = create_telegram_sender()
    notification_service = create_notification_service()

    # Проверяем подключение
    print("\n🔍 Проверка подключения к Telegram...")
    bot_info = telegram_sender.get_bot_info()

    if bot_info and bot_info.get('ok'):
        bot = bot_info['result']
        print(f"✅ Бот подключен: @{bot.get('username')} ({bot.get('first_name')})")
    else:
        print("❌ Ошибка подключения к Telegram")
        return

    # Генерируем тестовые заявки
    print(f"\n📊 Генерация тестовых заявок...")
    test_apps = generate_test_applications()

    print(f"  Всего заявок: {len(test_apps)}")
    print(f"    • Физические лица: 10")
    print(f"    • Бизнес: 10")
    print(f"    • Инвесторы: 10")

    # Подтверждение
    print("\n⚠️  ВНИМАНИЕ: Будет отправлено 30 тестовых заявок в Telegram!")
    response = input("  Продолжить? (да/нет): ").strip().lower()

    if response not in ['да', 'д', 'yes', 'y']:
        print("❌ Тестирование отменено")
        return

    # Отправляем заявки
    print(f"\n🚀 Начинаем отправку заявок...")
    print("-" * 60)

    results = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'by_type': {
            'individual': {'total': 0, 'success': 0},
            'business': {'total': 0, 'success': 0},
            'investor': {'total': 0, 'success': 0}
        }
    }

    for i, app in enumerate(test_apps, 1):
        app_type = app['type']
        data = app['data']

        print(f"\n[{i:2d}/{len(test_apps)}] Отправка: {app_type}")

        # Показываем краткую информацию о заявке
        if app_type == 'individual':
            print(f"   👤 {data['name']} | 💰 {data['amount']:,} руб. | 🏠 {data['collateral'][:30]}...")
        elif app_type == 'business':
            print(f"   🏢 {data['company_name'][:30]}... | 💰 {data['amount']:,} руб.")
        elif app_type == 'investor':
            print(f"   👤 {data['name']} | 💰 {data['investment_amount']:,} руб. | ⏱️ {data['term_months']} мес.")

        # Отправляем через notification service
        success = notification_service.send_application_notification(app_type, data)

        # Обновляем статистику
        results['total'] += 1
        results['by_type'][app_type]['total'] += 1

        if success:
            results['success'] += 1
            results['by_type'][app_type]['success'] += 1
            print(f"   ✅ Успешно отправлено")
        else:
            results['failed'] += 1
            print(f"   ❌ Ошибка отправки")

        # Пауза между отправками, чтобы не спамить
        if i < len(test_apps):
            time.sleep(2)  # 1 секунда между сообщениями

    # Выводим результаты
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)

    print(f"\n📊 Общая статистика:")
    print(f"  Всего отправлено: {results['total']}")
    print(f"  Успешно: {results['success']} ({results['success']/results['total']*100:.1f}%)")
    print(f"  С ошибками: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")

    print(f"\n📈 По типам заявок:")
    for app_type, stats in results['by_type'].items():
        if stats['total'] > 0:
            success_rate = stats['success'] / stats['total'] * 100
            type_name = {
                'individual': 'Физ. лица',
                'business': 'Бизнес',
                'investor': 'Инвесторы'
            }.get(app_type, app_type)

            print(f"  {type_name}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")

    # Критерий успеха (из ТЗ)
    print(f"\n🎯 Критерии приемки из ТЗ:")
    print(f"  - Все три типа заявок передаются в Telegram")
    print(f"  - Форматы соответствуют требованиям")
    print(f"  - Отправка 10 заявок каждого типа")

    # Проверяем критерии
    criteria_met = True
    issues = []

    if results['total'] != 30:
        criteria_met = False
        issues.append(f"Отправлено {results['total']} вместо 30 заявок")

    for app_type, stats in results['by_type'].items():
        if stats['total'] != 10:
            criteria_met = False
            issues.append(f"Для типа '{app_type}': {stats['total']} вместо 10 заявок")

    if results['failed'] > 0:
        criteria_met = False
        issues.append(f"{results['failed']} заявок не доставлено")

    print(f"\n{'='*60}")
    if criteria_met:
        print("✅ ВСЕ КРИТЕРИИ ЭТАПА 2 ВЫПОЛНЕНЫ!")
        print("   Этап 2 завершен успешно!")
    else:
        print("⚠️  НЕ ВСЕ КРИТЕРИИ ВЫПОЛНЕНЫ:")
        for issue in issues:
            print(f"   • {issue}")

    # Предлагаем проверить вручную
    print(f"\n📱 Проверьте Telegram-чат:")
    print(f"   Должно прийти 30 сообщений с заявками")
    print(f"   Форматы должны соответствовать ТЗ")

    # Сохраняем лог в файл
    log_file = "telegram_test_results.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("Результаты тестирования Telegram API\n")
        f.write("=" * 50 + "\n")
        f.write(f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Всего отправлено: {results['total']}\n")
        f.write(f"Успешно: {results['success']}\n")
        f.write(f"С ошибками: {results['failed']}\n\n")

        for app_type, stats in results['by_type'].items():
            f.write(f"{app_type}: {stats['success']}/{stats['total']}\n")

    print(f"\n📝 Лог сохранен в файл: {log_file}")


if __name__ == "__main__":
    main()