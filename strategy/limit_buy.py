import time
import os
import logging
from pprint import pprint
from typing import Union, List

from dotenv import load_dotenv
import requests
import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
import numpy as np

load_dotenv()  # take environment variables from .env.


def cancel_all_open_orders() -> None:
    logging.info("Deleting Open Orders")
    # Initialize the Kraken API client
    k = krakenex.API()

    # Load API key and secret from environment variables for security
    k.key = os.getenv("API_KEY")
    k.secret = os.getenv("API_SECRET")

    try:
        # Use the CancelAll endpoint to cancel all open orders
        response = k.query_private("CancelAll")

        if response["error"]:
            logging.warning(f"Error canceling orders: {response['error']}")
        else:
            # The response includes a count of how many orders were canceled
            logging.debug(
                f"Successfully canceled {response['result']['count']} orders."
            )
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def get_current_price() -> Union[float, None]:
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        current_price = int(data["bitcoin"]["eur"])
        logging.info(f"Current BTC price €{current_price}")

        return current_price
    except requests.RequestException as e:
        logging.error(e)
        return None


def distribute_buy_orders(
    n_orders: int, min_percentage: float, max_percentage: float
) -> None:
    logging.info(f"Placing {n_orders} orders")
    euro_balance = get_euro_balance()
    current_btc_price = get_current_price()

    # Calculate the amount of Euro to allocate per order
    euro_per_order = euro_balance / n_orders
    logging.info(f"Euro per order €{euro_per_order}")
    min_euro_amount = 30
    if euro_per_order < min_euro_amount:
        raise Exception(
            "Sorry, the euro order amount is less than the min euro amount. Try lowering N, the number of orders"
        )

    # Generate percentages using numpy.linspace
    percentages = np.linspace(min_percentage, max_percentage, n_orders)
    for percentage in percentages:
        # Calculate the target buy price based on the current price and percentage
        logging.info(f"Percentage is {percentage}%")
        target_price = int(current_btc_price * (1 + percentage / 100))
        logging.info(f"Target price is {target_price} euro")

        # Calculate the volume of BTC to buy with the allocated Euro per order at the target price
        volume = euro_per_order / target_price

        # Place the limit buy order
        create_limit_buy_order(btc_price=target_price, volume_btc=volume)


def get_euro_balance() -> float:
    logging.debug("Getting Euro balance")

    # Initialize Kraken API
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")

    api = krakenex.API(key=API_KEY, secret=API_SECRET)
    kraken = KrakenAPI(api)

    try:
        balance = api.query_private("Balance")
        euro_balance = balance["result"].get(
            "ZEUR", "Balance not available"
        )  # Checking for Euro balance
        logging.info(f"Your Euro balance is €{euro_balance}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    return float(euro_balance)


def create_limit_buy_order(btc_price: float, volume_btc: float) -> None:
    # Placeholder: Implement the logic to place a limit buy order
    order_price = round(btc_price * volume_btc)
    logging.debug(
        f"Placing order: Buy {volume_btc:.6f} BTC at €{btc_price:.2f} at {order_price=}"
    )

    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")

    api = krakenex.API(key=API_KEY, secret=API_SECRET)
    kraken = KrakenAPI(api)

    try:
        order = api.query_private(
            "AddOrder",
            {
                "pair": "XBTEUR",
                "type": "buy",
                "ordertype": "limit",
                "price": btc_price,
                "volume": volume_btc,
                "validate": True,  # Set to False to actually place the order. True is for validation only.
            },
        )

        if order["error"]:
            logging.error(f"Error placing order: {order['error']}")
        else:
            logging.info(
                f"Order placed successfully - {order['result']['descr']['order']}"
            )
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def distribute_buy_orders_by_btc_volume(
    btc_volume: float, percent_step: float, percent_discount: float
) -> None:
    """
    Distributes buy orders for Bitcoin at different price levels but with a fixed volume for each order.

    This function calculates and places multiple limit buy orders for Bitcoin, each with the same fixed volume but at different price levels. The price levels are determined by applying a percentage step and discount to the current BTC price.

    Parameters:
        btc_volume (float): The fixed volume of Bitcoin to be purchased for each order.
        percent_step (float): The percentage step between each buy order's price level. A negative value indicates a decrease in price levels, while a positive value indicates an increase.
        percent_discount (float): The percentage discount from the current BTC price at which to start placing orders. A negative value indicates a discount, while a positive value indicates a premium.

    Returns:
        None

    Example:
        distribute_buy_orders_by_btc_volume(0.001, -1, -5)

        This example places limit buy orders for Bitcoin with a fixed volume of 0.001 BTC each, starting at a price level 5% below the current BTC price and decreasing by 1% for each subsequent order.
    """

    logging.info("Placing orders")

    # Get account balance
    account_balance = get_euro_balance()

    # Get current BTC price
    btc_price = get_current_price()

    # Calculate the starting price for placing orders
    start_price = btc_price * (1 + percent_discount / 100)

    total_cost = 0
    n_orders = 0

    while True:
        # Calculate the price for the current order
        order_price = round(start_price * (1 + percent_step / 100) ** n_orders)
        # Calculate the cost of the current order
        order_cost = round(btc_volume * order_price)

        # Stop if total cost exceeds account balance or order price exceeds current price
        if order_cost > account_balance:
            logging.info("Funds depleted. Breaking")
            break
        if order_price > btc_price:
            logging.info(
                f"Ups, something went wrong, order_price > btc_price, {order_price} > {btc_price}"
            )
            break

        # Increment total cost and order count
        total_cost += order_cost
        n_orders += 1
        # Reduce the balance
        account_balance -= order_cost
        account_balance = round(account_balance)

        # Place the limit buy order
        create_limit_buy_order(btc_price=order_price, volume_btc=btc_volume)


    logging.info(f"Placed {n_orders} orders")
    logging.info(f"Total cost €{total_cost}")
    logging.info(f"Estimated balance €{account_balance}")

    new_balance = get_euro_balance()

def main() -> None:
    # Cancels all existing orders and places distributed limit buy orders
    cancel_all_open_orders()
    distribute_buy_orders(n_orders=20, min_percentage=-1, max_percentage=-15)


def main2() -> None:
    # Cancels all existing orders and places distributed limit buy orders
    #cancel_all_open_orders()
    distribute_buy_orders_by_btc_volume(
        btc_volume=0.001, percent_step=-1, percent_discount=-5
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main2()
