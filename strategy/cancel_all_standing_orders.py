import krakenex
import os

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


def cancel_all_open_orders():
    # Initialize the Kraken API client
    k = krakenex.API()

    # Load API key and secret from environment variables for security
    k.key = os.getenv("API_KEY")
    k.secret = os.getenv("API_SECRET")

    try:
        # Use the CancelAll endpoint to cancel all open orders
        response = k.query_private("CancelAll")

        if response["error"]:
            logging.warning("Error canceling orders:", response["error"])
        else:
            # The response includes a count of how many orders were canceled
            logging.info(f"Successfully canceled {response['result']['count']} orders.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    cancel_all_open_orders()
