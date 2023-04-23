import requests
import json
from conf import money


# money = {
#     'рубль': 'RUB',
#     'евро': 'EUR',
#     'доллар': 'USD',
# }

class ConvertException(Exception):
    pass


class MoneyConverter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote == base:
            raise ConvertException('Нельзя обрабатывать одинаковые валюты.')

        try:
            quote_ticker = money[quote]
        except KeyError:
            raise ConvertException(f'Не удалось обработать валюту {quote}')

        try:
            base_ticker = money[base]
        except KeyError:
            raise ConvertException(f'Не удалось обработать валюту {base}')

        try:
            amount = float(amount)
        except ValueError:
            raise ConvertException(f'Не удалось обработать количественное значение.')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        total_base = json.loads(r.content)[money[base]]

        return total_base