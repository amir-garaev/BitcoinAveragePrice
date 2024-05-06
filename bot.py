import asyncio
import logging
import sys
from datetime import datetime

from config import API_TOKEN, bitcoin_address_regex
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import re
from aiogram.fsm.context import FSMContext
from keyboard import keyboard_quit
from state import DateInput
from wallet_info.BitcoinInfoWallet import BitcoinInfoWallet
from wallet_info.BitcoinPriceFetcher import BitcoinPriceFetcher

TOKEN = API_TOKEN

dp = Dispatcher()
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# average_price - Средняя цена
# price_on_date - цену Bitcoin по дате

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Я бот для анализа истории транзакций Bitcoin.\n\n"
        "Чтобы получить среднюю цену покупки Bitcoin, отправьте мне свой адрес Bitcoin формата bc1...\n"
        "Я проанализирую историю транзакций по этому адресу и вычислю среднюю цену покупки в момент покупки.\n\n"
        "Подробнее про среднюю цену покупки: /average_price\n"
        "Узнать цену в определенный день: /price_on_date\n"
    )


@dp.message(Command("average_price"))
async def average_price_command(message: Message) -> None:
    average_price_text = (
        "Средняя цена покупки Bitcoin - это средневзвешенная цена, по которой вы приобретали биткоины "
        "с учетом различных курсов и объемов покупки.\n\n"
        "Формула для вычисления средней цены покупки выглядит следующим образом:\n\n"
        "Средняя цена покупки = (Сумма всех покупок * Курс всех покупок) / Общий объем покупок\n\n"
        "Это позволяет узнать среднюю цену покупки, учитывая все ваши предыдущие покупки биткоина."
    )

    await message.answer(average_price_text)

@dp.message(Command("price_on_date"))
async def command_check_price_bitcoin_datetime(message: Message, state: FSMContext) -> None:
    await bot.send_message(
        message.chat.id,
            "Введите дату в формате ДД.ММ.ГГГГ (например, 01.12.2024).\n"
            "Мы покажем цену Bitcoin на эту дату.",
        reply_markup=keyboard_quit
    )

    await state.set_state(DateInput.waiting_for_date)


@dp.message(DateInput.waiting_for_date)
async def handle_date_input(message: Message, state: FSMContext) -> None:
    datetime_str = message.text.strip()
    try:
        timestamp = datetime.strptime(datetime_str, "%d.%m.%Y").timestamp()
    except ValueError:
        await bot.send_message(message.chat.id, "Введите дату в формате ДД.ММ.ГГГГ (например, 01.12.2024):", reply_markup=keyboard_quit)
        return

    bitcoin_fetcher = BitcoinPriceFetcher()
    price = await bitcoin_fetcher.get_btc_price(timestamp)
    await message.answer(f"Цена Bitcoin на {datetime_str}: {price} $")

    await state.clear()


@dp.callback_query(lambda c: c.data.startswith('quit'))
async def quit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    message = await bot.send_message(chat_id=call.message.chat.id, text="Поиск цены Bitcoin по дате отменен")
    await asyncio.sleep(2)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=message.message_id)


@dp.message()
async def check_average_price_bitcoin(message: Message) -> None:
    bitcoin_address = message.text
    bitcoin_address_bool = re.search(bitcoin_address_regex, bitcoin_address)

    if bitcoin_address_bool:
        message_new_address = await bot.send_message(
            message.chat.id,
            "Обнаружен Bitcoin адрес!",
            reply_to_message_id=message.message_id
        )

        message_please_wait = await bot.send_message(
            message.chat.id,
            "Пожалуйста, подождите, пока вычисляется средняя цена покупки Bitcoin...",
            reply_to_message_id=message.message_id
        )

        btc_history = BitcoinInfoWallet(bot, message.chat.id, bitcoin_address)
        await btc_history.get_transaction_from_address()

        await bot.delete_message(chat_id=message.chat.id, message_id=message_new_address.message_id)
        await bot.delete_message(chat_id=message.chat.id, message_id=message_please_wait.message_id)
    else:
        await bot.send_message(
            message.chat.id,
            'К сожалению, введенный кошелек некорректен. Пример корректного кошелька: bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq.'
        )



async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())