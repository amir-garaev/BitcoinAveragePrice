import asyncio
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup


class BitcoinPriceFetcher:
    async def get_btc_price(self, timestamp):
        date = self._format_timestamp(timestamp)
        formatted_date = self._format_date(date)
        url = self._construct_url(date)

        attempts = 5
        delay_seconds = 2
        for _ in range(attempts):
            response = await self._fetch_url(url)
            if response is not None:
                rate = self._parse_response(response, formatted_date)
                if rate is not None:
                    return rate
            await asyncio.sleep(delay_seconds)

        return None

    async def _fetch_url(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return None
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return None

    def _format_timestamp(self, timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    def _format_date(self, date):
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        return date_obj.strftime("%d.%m.%Y")

    def _construct_url(self, date):
        year, month, _ = date.split('-')
        return f"https://www.calc.ru/grafik-Bitcoin-k-dollaru-za-{year}-{month}.html"

    def _parse_response(self, response_text, formatted_date):
        soup = BeautifulSoup(response_text, "html.parser")
        table_rows = soup.find_all("tr")
        for row in table_rows:
            cells = row.find_all("td")
            if len(cells) == 2:
                cell_date = cells[0].text.strip()
                rate_parts = cells[1].text.strip().split()
                rate = ''.join(rate_parts[:2])
                if cell_date and rate and not re.search('[а-яА-Я]', cell_date) and not re.search('[а-яА-Я]',rate):
                    if cell_date == formatted_date:
                        return rate
        return None