import requests


def get_current_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["bitcoin"]["eur"]
    except requests.RequestException as e:
        logging.info(e)
        return None


def calculate_order_prices(current_price, percentages):
    return [round(current_price * (1 + p / 100), 1) for p in percentages]


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


def place_orders(order_prices):
    # Placeholder - Implement according to your exchange's API
    for price in order_prices:
        logging.info(f"Mock placing order at {price} USD for 0.01 BTC")
        num_orders = None
        # Replace with actual API call
        volume = euro_in / btc_price
        place_limit_buy_order(api, volume, price)


def main():
    current_price = get_current_price()
    logging.info(current_price)
    if current_price:
        percentages = [
            -2,
            -4,
            -6,
            -8,
            -10,
            -12,
            -14,
            -16,
            -18,
            -20,
        ]  # Define your percentages here
        order_prices = calculate_order_prices(current_price, percentages)
        logging.info(order_prices)
        place_orders(order_prices)
    else:
        logging.error("Failed to fetch current price.")


if __name__ == "__main__":
    main()
