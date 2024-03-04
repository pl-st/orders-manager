""" By executing main() the main logic of the script can be run. """ 

import time
from datetime import datetime
from memory_profiler import profile
import utils
from database import execute_query, delete_old_orders
from woocomm import wc_get_orders, extract_order_data, update_order_statuses


@profile
def main():
    """ Main logic of the script thats fetching orders from 
    WooCommerce and generating invoices with request.post """

    number_of_orders_to_update = 35
    max_orders_in_db = 70
    update_interval = 5

    while True:
        # Check time window for updates (8 AM to 5 PM)
        now = datetime.now()
        if 8 <= now.hour < 30 and now.weekday() < 7:

            # Fetch WooCommerce orders
            wc_orders_response = wc_get_orders(number_of_orders_to_update)

            fetch_query = "SELECT orderId, statusId FROM orders ORDER BY id DESC;"
            db_orders_data = execute_query(
                fetch_query, params=None, fetch_data=True)

            # Extract orderIds : statusIds from DB
            orders_db_dict = {i[0]: i[1] for i in db_orders_data}

            number_of_orders = len(orders_db_dict.keys())
            print(f"Number of orders in DB: {number_of_orders}")

            for wc_order in wc_orders_response.json()[::-1]:
                # Extract order data
                order_data = extract_order_data(wc_order)

                # Check if order already exists in DB
                if order_data['id'] not in orders_db_dict:
                    print(
                        f"Order {order_data['id']} not found in DB, creating...")
                    utils.create_order(order_data)

            update_order_statuses(orders_db_dict, number_of_orders_to_update)

            if number_of_orders > max_orders_in_db:
                delete_old_orders()

            print(f"{now.strftime('%Y-%m-%d %H:%M')} OK! -> All orders up to date.")
        break
        time.sleep(update_interval * 60)


if __name__ == "__main__":
    main()
