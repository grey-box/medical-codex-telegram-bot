from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, \
    ConversationHandler
import requests

from config import FUZZY_MATCH_API, TRANSLATE_API, LANGUAGE_API, TELEGRAM_TOKEN
from schemas import FuzzyQuery

# Define conversation states
SELECTING_SOURCE, SELECTING_DESTINATION, AWAITING_QUERY, AWAITING_SELECTION = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    languages = requests.get(LANGUAGE_API).json()
    keyboard = [[InlineKeyboardButton(lang['name'], callback_data=f"source_{lang['code']}") for lang in languages]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome! Please select the source language:', reply_markup=reply_markup)
    return SELECTING_SOURCE


async def select_source_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['source_lang'] = query.data.split('_')[1]

    languages = requests.get(LANGUAGE_API).json()
    keyboard = [[InlineKeyboardButton(lang['name'], callback_data=f"dest_{lang['code']}") for lang in languages]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Now, please select the destination language:', reply_markup=reply_markup)
    return SELECTING_DESTINATION


async def select_destination_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['dest_lang'] = query.data.split('_')[1]
    await query.edit_message_text('Please enter a word or phrase to search or translate:')
    return AWAITING_QUERY


async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_text = update.message.text
    query = FuzzyQuery(query=query_text,
                       source_language=context.user_data['source_lang'],
                       threshold=80,
                       nb_max_results=5)
    fuzzy_matches = requests.post(FUZZY_MATCH_API, json=query.model_dump()).json()

    if not fuzzy_matches:
        await update.message.reply_text("No matches found.")
        return ConversationHandler.END

    keyboard = []
    for match in fuzzy_matches[:5]:
        keyboard.append([InlineKeyboardButton(f"{match['word']} ({match['score']})",
                                              callback_data=f"translate_{match['id']}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a match to translate:", reply_markup=reply_markup)
    return AWAITING_SELECTION


async def handle_translation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    word_id = query.data.split('_')[1]
    translation = requests.get(f"{TRANSLATE_API}?id={word_id}&target_lang={context.user_data['dest_lang']}").json()

    if translation:
        await query.edit_message_text(f"Translation: {translation['translated_text']}")
    else:
        await query.edit_message_text("Sorry, translation not available.")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_SOURCE: [CallbackQueryHandler(select_source_language, pattern=r"^source_")],
            SELECTING_DESTINATION: [CallbackQueryHandler(select_destination_language, pattern=r"^dest_")],
            AWAITING_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query)],
            AWAITING_SELECTION: [CallbackQueryHandler(handle_translation, pattern=r"^translate_")]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
