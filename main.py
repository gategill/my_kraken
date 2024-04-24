import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
import numpy as np
import time
from dotenv import load_dotenv
import os
import logging
from pprint import pprint

load_dotenv()  # take environment variables from .env.


def place_limit_buy_order(api, volume, price):
    """
    Place a limit buy order on Kraken.

    :param volume: Volume of the asset to buy.
    :param price: Price at which to buy the asset.
    """
    try:
        order = api.query_private(
            "AddOrder",
            {
                "pair": "XBTEUR",
                "type": "buy",
                "ordertype": "limit",
                "price": price,
                "volume": volume,
                "validate": False,  # Set to False to actually place the order. True is for validation only.
            },
        )
        logging.info(order)
        if order["error"]:
            logging.error(f"Error placing order: {order['error']}")
        else:
            logging.info("Order placed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def main():

    # Initialize Kraken API
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")

    api = krakenex.API(key=API_KEY, secret=API_SECRET)
    kraken = KrakenAPI(api)

    # Example usage
    try:
        balance = api.query_private("Balance")
        euro_balance = balance["result"].get(
            "ZEUR", "Balance not available"
        )  # Checking for Euro balance
        logging.info(f"Your Euro balance is: {euro_balance}")

        balance = api.query_private("Balance")
        bitcoin_balance = balance["result"].get(
            "XXBT", "Balance not available"
        )  # Use 'XBT' if 'XXBT' does not work
        logging.info(f"Your Bitcoin balance is: {bitcoin_balance}")

        place_limit_buy_order(api, 0.001, 20000)

        past_orders = api.query_private("OpenOrders")
        logging.info("Your open orders:")
        for order_id, order_info in past_orders["result"]["open"].items():
            logging.info(f"OrderID = {order_id}")
            pprint(order_info)
            break

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    # while True:
    #     # Fetch historical data
    #     ohlc, last = kraken.get_ohlc_data('XXBTZUSD', interval=60)

    #     # Calculate RSI
    #     rsi = calculate_rsi(ohlc['close'])

    #     # Check RSI condition
    #     if rsi[-1] < 20:
    #         buy_bitcoin(amount=0.01) # Specify your amount

    #     # Sleep for a certain amount of time before next check
    #     time.sleep(3600) # 1 hour


if __name__ == "__main__":
    main()
