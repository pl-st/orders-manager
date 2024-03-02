import requests
from requests.auth import HTTPBasicAuth
import time
import json
from database import add_order_to_db
import config
from . import log_msg


def create_order(order_data):
    """ Creates an order on Apteka Expert 2.0 and adds it to the database.
    Args:
        order_data:
            order_id (str): Order ID.
            total_to_pay (float): Total amount to pay.
            final_date_created (str): Date and time the order was created.
            customer_name (str): Customer name.
            items_list (list): List of items in the order.
            customer_email (str): Customer email address.
    Returns:
        bool: True if the order is created successfully, False otherwise. """

    main_url = config.URL
    url = f"http://{main_url}:7779/api/orders/order"

    headers = {"Content-Type": "application/json"}
    json_data = json.dumps(order_data)

    try:
        response = requests.post(url, headers=headers, data=json_data, auth=HTTPBasicAuth(
            config.USERNAME, config.PASSWORD), timeout=120)

        if response.status_code == 200:
            time.sleep(3)

            add_order_to_db(order_id, total_to_pay, internalId=0, statusId=0,
                            statusName='необработена', pharmacy=customer_name)

            msg = f"Invoice & Order were generated & added to DB -> Date: {final_date_created} ID: {order_id} Client: [{customer_name}] N_of_items: {len(items_list)} Total_value: {total_to_pay} BGN"

            print(msg)
            utils.log_msg('general', 'info', msg)
            return True
        else:
            utils.log_msg(
                'error', 'critical', f"Order {order_id} from {customer_name} has {response.text}. POST Request failed with status code {response.status_code}"
            )
            return False

    except requests.exceptions.RequestException as e:
        utils.log_msg(
            'error', 'critical', f"Order {order_id} from {customer_name} at a price of {total_to_pay} with {len(items_list)} items was NOT created! Request error: {str(e)}."
        )
        return False
