""" Creates an order invoice in "Apteka Expert 2.0" and adds it to the database. """

import time
import json
import requests
from requests.auth import HTTPBasicAuth
from database import add_order_to_db
import config
from utils.log_msg import log_msg


def create_order(order_data: dict) -> bool:
    """ Creates an order on Apteka Expert 2.0 and adds it to the database.
    Args:
        order_data:
            id: Order ID.
            total_to_pay (float): Total amount to pay.
            final_date_created (str): Date and time the order was created.
            customer_name (str): Customer name.
            items_list (list): List of items in the order.
            customer_email (str): Customer email address.
            customer_notes (str): Additional notes
    Returns:
        bool: True if the order is created successfully, False otherwise. """

    main_url = config.URL
    url = f"http://{main_url}:7779/api/orders/order"

    headers = {"Content-Type": "application/json"}
    json_data = json.dumps(order_data)
    
    customer_notes = 0 if not order_data['customer_notes'] else 1
    
    try:
        response = requests.post(url, headers=headers, data=json_data, auth=HTTPBasicAuth(
            config.USERNAME, config.PASSWORD), timeout=120)

        if response.status_code == 200:
            time.sleep(3)

            params = (order_data['id'], 0, 'необработена',
                      order_data['total'], order_data['customerName'], 0, customer_notes)

            add_order_to_db(params)

            msg = [f"Invoice & Order were generated & added to DB ->",
                f"Date: {order_data['dateCreated']} ID: {order_data['id']}",
                f"Client: [{order_data['customerName']}]",
                f"Items: {len(order_data['items'])} Total: {order_data['total']} BGN",
                f"Customer notes: {customer_notes}"]

            print(msg)
            # Print customer_notes for future debugging if needed. Delete this print otherwise!
            print(f" ---- {order_data['customer_notes']} ---- ")
            log_msg('general', 'info', msg)
            return True

        log_msg(
            'error', 'critical', 
            (f"Order {order_data['id']} from {order_data['customerName']} has" ,
            f"{response.text}. POST Request failed with status code {response.status_code}")
        )
        return False

    except requests.exceptions.RequestException as e:
        log_msg(
            'error', 'critical', 
            (f"Order {order_data['id']} from {order_data['customerName']}" ,
            f"at a price of {order_data['total']} with {len(order_data['items'])}",
            f"items was NOT created! Request error: {str(e)}.")
        )
        print("Msg has been logged!")
        return False
