from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

button_quit = InlineKeyboardButton(text="cancel", callback_data="quit")
keyboard_quit = InlineKeyboardMarkup(inline_keyboard=[[button_quit]])