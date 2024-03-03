import pandas as pd
import time
from datetime import datetime
import utils
from database import execute_query, delete_old_orders
from woocomm import wc_get_orders, extract_order_data, update_order_statuses


def main():
    NUMBER_OF_ORDERS_TO_UPDATE = 30
    MAX_ORDERS_IN_DB = 70
    UPDATE_INTERVAL = 5

    while True:
        # Check time window for updates (8 AM to 5 PM)
        now = datetime.now()
        if 8 <= now.hour < 17 and now.weekday() < 7:

            # Fetch WooCommerce orders
            wc_orders_response = wc_get_orders(NUMBER_OF_ORDERS_TO_UPDATE)

            fetch_query = f''' SELECT * FROM orders ORDER BY id DESC; '''
            db_orders_data = execute_query(
                fetch_query, params=None, fetch_data=True)

            # Efficiently extract orderIds : statusIds from DB
            orders_db_dict = {i[1]: i[2] for i in db_orders_data}

            number_of_orders = len(orders_db_dict.keys())
            print(f"Number of orders in DB: {number_of_orders}")

            for wc_order in wc_orders_response.json()[::-1]:
                # Extract order data
                order_data = extract_order_data(wc_order)

                # Check if order already exists in DB
                if order_data['id'] not in orders_db_dict:
                    print(f"Order {order_data['id']} not found in DB, creating...")
                    utils.create_order(order_data)

            update_order_statuses(orders_db_dict, NUMBER_OF_ORDERS_TO_UPDATE)

            if number_of_orders > MAX_ORDERS_IN_DB:
                delete_old_orders()

            print(f"{now.strftime('%Y-%m-%d %H:%M')} OK! -> All orders up to date.")

        time.sleep(UPDATE_INTERVAL * 60)


if __name__ == "__main__":
    main()
