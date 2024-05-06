import aiohttp
from datetime import datetime
from wallet_info.BitcoinPriceFetcher import BitcoinPriceFetcher


class BitcoinInfoWallet:
    def __init__(self, bot, chat_id, bitcoin_address):
        self.bot = bot
        self.chat_id = chat_id
        self.bitcoin_address = bitcoin_address

    async def get_transaction_from_address(self):
        async with aiohttp.ClientSession() as session:
            api_url = f"https://blockchain.info/rawaddr/{self.bitcoin_address}"
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    btc_transactions = await self._filter_transactions(data.get("txs", []))
                    await self._handle_transaction_results(btc_transactions)
                else:
                    await self.bot.send_message(self.chat_id, "Failed to fetch transaction history")

    async def _filter_transactions(self, transactions):
        btc_transactions = []
        for tx in transactions:
            tx_date = datetime.fromtimestamp(tx['time']).strftime('%Y-%m-%d')
            if tx_date > '2023-11-30':
                btc_fetcher = BitcoinPriceFetcher()
                btc_price = await btc_fetcher.get_btc_price(tx['time'])
                btc_transaction = {
                    'date': tx_date,
                    'btc_price': btc_price,
                    'btc_amount': sum([output["value"] * 1e-8 for output in tx["out"] if
                                       "addr" in output and output["addr"] == self.bitcoin_address])
                }
                btc_transactions.append(btc_transaction)
        return btc_transactions

    async def _handle_transaction_results(self, btc_transactions):
        if btc_transactions:
            average_buy_price = await self._calculate_average_buy_price(btc_transactions)
            message = f"Средняя цена покупки: {average_buy_price}\n $"
        else:
            message = "Не найдено полученных транзакций"
        await self.bot.send_message(self.chat_id, message)


    async def _calculate_average_buy_price(self, btc_transactions):
        total_spent = 0
        total_btc_amount = 0
        for tx in btc_transactions:
            if tx['btc_amount'] > 0:
                total_spent += tx['btc_amount'] * float(tx['btc_price'])
                total_btc_amount += tx['btc_amount']
        if total_btc_amount > 0:
            return total_spent / total_btc_amount
        else:
            return "N/A"
