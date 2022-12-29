import logging

from dotenv import load_dotenv
import os

import telegram
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, JobQueue

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
load_dotenv()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"User {update.effective_user.name} triggered 'start' at "
          f"{update.message.chat.type} chat {update.message.chat.id}")

    reply_text = ''
    if update.message.chat.type == telegram.Chat.PRIVATE:
        reply_text = f"Привет, меня зовут {update.get_bot().name}!\n" \
                     f'Я ботик, созданный Алексашкой для группы "Чат игнорщиков и вечно занятого Влада".\n' \
                     f'Я сделан с любовью, по крайней мере мне так сказал создатель 🤔'
    elif update.message.chat.type == telegram.Chat.GROUP or update.message.chat.type == telegram.Chat.SUPERGROUP:
        reply_text = f"Всем привет, меня зовут {update.get_bot().name}!\n" \
                     f'Я ботик, созданный Алексашкой, спасибо, что пригласили меня в ' \
                     f'"{update.message.chat.title.title()}" 🥰'
    else:
        reply_text = f"Привет, меня зовут {update.get_bot().name}!\n" \
                     f'Что я тут делаю? 🤔'

    await update.message.reply_text(reply_text)


def help_back(update: Update) -> str:
    if hasattr(update, "effective_user"):
        user_name = update.effective_user.name
    else:
        user_name = update.from_user.name

    print(f"User {user_name} triggered 'help' at "
          f"{update.message.chat.type} chat {update.message.chat.id}")

    reply_text = ''

    if update.message.chat.type == telegram.Chat.PRIVATE:
        reply_text = f"Добавь меня в чат, я могу много интересного!\n" \
                     f'Ну, пока что нет, но папа сказал, что я расту... вроде как.\n' \
                     f'Можешь посмотреть ниже, что именно я могу:'
    elif update.message.chat.type == telegram.Chat.GROUP or update.message.chat.type == telegram.Chat.SUPERGROUP:
        reply_text = f"Я рад быть в этом чатике, в долгу не останусь, я могу много интересного!\n" \
                     f'Ну, пока что нет, но папа сказал, что я расту... вроде как.\n' \
                     f'Можешь посмотреть ниже, что именно я могу:'
    return reply_text


def join_data(d_type: str, data: str) -> str:
    return d_type + ', ' + data


def parse_data(data: str) -> list[str, str]:
    return data.split(', ', 1)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    reply_text = help_back(update)

    keyboard = [
        [InlineKeyboardButton("Доброе утро!", callback_data=join_data('help', "morning"))],
        [InlineKeyboardButton("С Днюхой!", callback_data=join_data('help', "b-day"))],
        [InlineKeyboardButton("Закончить", callback_data=join_data('help', "end"))],
    ]
    if not edit:
        await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.edit_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def inline_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    print(f"User {update.effective_user.name} triggered '{query.data}' at "
          f"{query.message.chat.type} chat {query.message.chat.id}")

    d_type, data = parse_data(query.data)

    keyboard = []
    reply_text = ''

    if d_type == 'help':
        if data == "morning":
            reply_text = f"<b><u>Доброе утро/Спокойной ночи</u></b>\n" \
                         f'Я могу(смогу) присылать сообщения, как <i>"Доброе утро"</i> и <i>"Спокойной ночи"</i>' \
                         f'каждый день в определённое время. Это можно будет отключить и настроить в разделе ' \
                         f'<u>"Доброе утро"</u>, если прописать команду <u>"/options"</u> или на кнопке снизу!'
            keyboard = [
                [InlineKeyboardButton("Настроить", callback_data=join_data('options', "morning"))],
                [InlineKeyboardButton("Назад", callback_data=join_data('help', "help"))],
            ]


        elif data == 'b-day':
            reply_text = f"<b><u>С Днюхой</u></b>\n" \
                         f'Я могу(смогу) присылать сообщения, как <i>"Давайте поздравим ......"</i> ' \
                         f'на дни рождения. Это можно будет отключить и настроить в разделе ' \
                         f'<u>"С Днюхой"</u>, если прописать команду <u>"/options"</u> или на кнопке снизу!'
            keyboard = [
                [InlineKeyboardButton("Настроить", callback_data=join_data('options', "b-day"))],
                [InlineKeyboardButton("Назад", callback_data=join_data('help', "help"))],
            ]


        elif data == 'help':
            await help_command(query, context, edit=True)

        elif data == 'end':
            reply_text = f"Хорошо, ещё поговорим!\n" \
                         f"Если что-то нужно будет, просто напиши <u>'/help'</u>"

    elif d_type == 'options':
        reply_text = f"Хорошо, ещё поговорим!\n" \
                     f"Если что-то нужно будет, просто напиши <u>'/help'</u>"

    await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"An error occurred at update {update}. Cause of error was {context.error}")

def main() -> None:
    application = Application.builder().token("5614824616:AAFTDG7Ls2ZeL4J-2GVgC1TGbSIJ5gePZbU").build()

    # Commands
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))

    # Keyboard
    application.add_handler(CallbackQueryHandler(inline_keyboard))

    # Error
    application.add_error_handler(error_handler)



    application.run_polling()


if __name__ == "__main__":
    main()
