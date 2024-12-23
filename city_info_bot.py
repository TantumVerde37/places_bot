import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from mock_yandex_api import MockYandexAPI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Состояния разговора
WAITING_FOR_CITY = 1
WAITING_FOR_CITY_WEATHER = 2
WAITING_FOR_CITY_TRANSPORT = 3
WAITING_FOR_CITY_SIGHTS = 4
WAITING_FOR_CITY_HISTORY = 5
WAITING_FOR_CITY_EVENTS = 6

# Инициализация API
yandex_api = MockYandexAPI()

# Создание основной клавиатуры
def get_base_keyboard():
    keyboard = [
        [KeyboardButton("🏠 Главное меню")],
        [KeyboardButton("🔍 Найти город"), KeyboardButton("🌤 Погода и время")],
        [KeyboardButton("🚇 Транспорт"), KeyboardButton("🏛 Достопримечательности")],
        [KeyboardButton("📜 История города"), KeyboardButton("🎭 Мероприятия")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Я бот для получения информации о городах.\n'
        'Нажмите "🔍 Найти город" для получения информации о городе.',
        reply_markup=get_base_keyboard()
    )
    return ConversationHandler.END

async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🏠 Главное меню":
        return await start(update, context)
    elif text == "🔍 Найти город":
        return await info_command(update, context)
    elif text == "🌤 Погода и время":
        return await weather_command(update, context)
    elif text == "🚇 Транспорт":
        return await transport_command(update, context)
    elif text == "🏛 Достопримечательности":
        return await sights_command(update, context)
    elif text == "📜 История города":
        return await history_command(update, context)
    elif text == "🎭 Мероприятия":
        return await events_command(update, context)
    else:
        await update.message.reply_text(
            'Пожалуйста, используйте кнопки меню.',
            reply_markup=get_base_keyboard()
        )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Пожалуйста, введите название города:',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )
    return WAITING_FOR_CITY

async def process_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    city_data = yandex_api.get_city_info(city)

    if not city_data:
        await update.message.reply_text(
            f'Извините, информация о городе "{city}" не найдена.',
            reply_markup=get_base_keyboard()
        )
        return ConversationHandler.END

    # Формирование ответного сообщения
    response = f"🏙 Информация о городе {city.title()}:\n\n"
    
    response += "🏛 Достопримечательности:\n"
    for sight in city_data["достопримечательности"]:
        response += f"• {sight}\n"
    
    response += "\n🍽 Рестораны:\n"
    for restaurant in city_data["рестораны"]:
        response += f"• {restaurant}\n"
    
    response += f"\n🌤 Погода:\n"
    response += f"• Температура: {city_data['погода']['температура']}°C\n"
    response += f"• {city_data['погода']['описание']}"

    await update.message.reply_text(
        response,
        reply_markup=get_base_keyboard()
    )
    return ConversationHandler.END

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Пожалуйста, введите название города для получения информации о погоде и времени:',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )
    return WAITING_FOR_CITY_WEATHER

async def process_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    weather_data = yandex_api.get_weather_and_time(city)

    if not weather_data:
        await update.message.reply_text(
            f'Извините, информация о городе "{city}" не найдена.',
            reply_markup=get_base_keyboard()
        )
        return ConversationHandler.END

    response = f"🏙 {city.title()}\n\n"
    response += f"📅 Дата: {weather_data['дата']}\n"
    response += f"🕐 Время: {weather_data['время']}\n\n"
    response += f"🌤 Погода:\n"
    response += f"• Температура: {weather_data['погода']['температура']}°C\n"
    response += f"• {weather_data['погода']['описание']}"

    await update.message.reply_text(
        response,
        reply_markup=get_base_keyboard()
    )
    return ConversationHandler.END

async def transport_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Пожалуйста, введите название города для получения информации о транспорте:',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )
    return WAITING_FOR_CITY_TRANSPORT

async def process_transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    transport_data = yandex_api.get_transport_info(city)

    if not transport_data:
        await update.message.reply_text(
            f'Извините, информация о транспорте в городе "{city}" не найдена.',
            reply_markup=get_base_keyboard()
        )
        return ConversationHandler.END

    response = f"🏙 Транспорт в городе {city.title()}:\n\n"
    
    response += "🚇 Метро:\n"
    for info in transport_data["метро"]:
        response += f"• {info}\n"
    
    response += "\n🚌 Автобусы:\n"
    for info in transport_data["автобусы"]:
        response += f"• {info}\n"
    
    response += "\n🚕 Такси:\n"
    for company in transport_data["такси"]:
        response += f"• {company}\n"

    await update.message.reply_text(
        response,
        reply_markup=get_base_keyboard()
    )
    return ConversationHandler.END

async def sights_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Пожалуйста, введите название города для получения информации о достопримечательностях:',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )
    return WAITING_FOR_CITY_SIGHTS

async def process_sights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    sights_data = yandex_api.get_sights_info(city)

    if not sights_data:
        await update.message.reply_text(
            f'Извините, информация о достопримечательностях города "{city}" не найдена.',
            reply_markup=get_base_keyboard()
        )
        return ConversationHandler.END

    response = f"🏛 Достопримечательности города {city.title()}:\n\n"
    
    for sight in sights_data["достопримечательности"]:
        response += f"🏛 {sight['название']}\n"
        response += f"📝 {sight['описание']}\n"
        response += f"📍 {sight['адрес']}\n"
        response += f"🕒 Время работы: {sight['время_работы']}\n"
        response += f"💰 Стоимость: {sight['вход']}\n\n"

    await update.message.reply_text(
        response,
        reply_markup=get_base_keyboard()
    )
    return ConversationHandler.END

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Пожалуйста, введите название города для получения исторической информации:',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )
    return WAITING_FOR_CITY_HISTORY

async def process_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    history_data = yandex_api.get_history_info(city)

    if not history_data:
        await update.message.reply_text(
            f'Извините, историческая информация о городе "{city}" не найдена.',
            reply_markup=get_base_keyboard()
        )
        return ConversationHandler.END

    response = f"📜 История города {city.title()}\n\n"
    response += f"🏛 Основан в {history_data['основание']}\n"
    response += f"👑 Основатель: {history_data['основатель']}\n\n"
    
    response += "📖 Краткая история:\n"
    for fact in history_data['краткая_история']:
        response += f"• {fact}\n"
    
    response += "\n🎯 Интересные факты:\n"
    for fact in history_data['интересные_факты']:
        response += f"• {fact}\n"

    await update.message.reply_text(
        response,
        reply_markup=get_base_keyboard()
    )
    return ConversationHandler.END

async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Пожалуйста, введите название города для получения информации о мероприятиях:',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )
    return WAITING_FOR_CITY_EVENTS

async def process_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    events_data = yandex_api.get_events_info(city)

    if not events_data:
        await update.message.reply_text(
            f'Извините, информация о мероприятиях в городе "{city}" не найдена.',
            reply_markup=get_base_keyboard()
        )
        return ConversationHandler.END

    response = f"🎭 Мероприятия в городе {city.title()}\n\n"
    
    response += "🎵 Концерты:\n"
    for event in events_data['концерты']:
        response += f"• {event['название']}\n"
        response += f"  📍 {event['место']}\n"
        response += f"  📅 {event['дата']}\n"
        response += f"  💰 {event['цена']}\n\n"
    
    response += "🎨 Выставки:\n"
    for event in events_data['выставки']:
        response += f"• {event['название']}\n"
        response += f"  📍 {event['место']}\n"
        response += f"  📅 {event['дата']}\n"
        response += f"  💰 {event['цена']}\n\n"
    
    response += "🎭 Театр:\n"
    for event in events_data['театр']:
        response += f"• {event['название']}\n"
        response += f"  📍 {event['место']}\n"
        response += f"  📅 {event['дата']}\n"
        response += f"  💰 {event['цена']}\n\n"

    await update.message.reply_text(
        response,
        reply_markup=get_base_keyboard()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Поиск информации отменен.',
        reply_markup=get_base_keyboard()
    )
    return ConversationHandler.END

def main():
    application = Application.builder().token('7223528820:AAHbmSni787ovnHws_U9YTaOFhb6AkvCqoY').build()

    # Обновляем обработчик разговора
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('info', info_command),
            CommandHandler('weather', weather_command),
            CommandHandler('transport', transport_command),
            CommandHandler('sights', sights_command),
            CommandHandler('history', history_command),
            CommandHandler('events', events_command),
            MessageHandler(filters.Regex('^🔍 Найти город$'), info_command),
            MessageHandler(filters.Regex('^🌤 Погода и время$'), weather_command),
            MessageHandler(filters.Regex('^🚇 Транспорт$'), transport_command),
            MessageHandler(filters.Regex('^🏛 Достопримечательности$'), sights_command),
            MessageHandler(filters.Regex('^📜 История города$'), history_command),
            MessageHandler(filters.Regex('^🎭 Мероприятия$'), events_command)
        ],
        states={
            WAITING_FOR_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_city)],
            WAITING_FOR_CITY_WEATHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_weather)],
            WAITING_FOR_CITY_TRANSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_transport)],
            WAITING_FOR_CITY_SIGHTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_sights)],
            WAITING_FOR_CITY_HISTORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_history)],
            WAITING_FOR_CITY_EVENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_events)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex('^❌ Отмена$'), cancel)
        ]
    )

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    
    # Обработчик для кнопок и всех остальных сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_button_press
    ))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main() 