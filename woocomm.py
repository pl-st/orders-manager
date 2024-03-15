""" WooCommerce helper functions can be found here. """

from datetime import datetime
import time
from woocommerce import API
import requests
from requests.auth import HTTPBasicAuth
from database import execute_query
import config
from utils.log_msg import log_msg


def define_wcapi(timeout_inp: int):
    """ Define WooCommerce API """

    wcapi = API(
        url="https://citadel.bg/",
        consumer_key="ck_2c9d6366a6d041353afb5694fd95557d801b4e48",
        consumer_secret="cs_e29a9eaecb06e20aad86a1e365a49bea0d027fc2",
        version="wc/v3",
        per_page=50,
        timeout=timeout_inp
    )
    return wcapi


def exponential_backoff(attempt: int):
    """ Exponential backoff with a maximum sleep of 1200 seconds (20 minutes) """
    return min(3 ** attempt, 1200)


def update_order_status_in_wc(order_id: int, actual_status_name: str) -> bool:
    """ Sends a PUT request to WooCommerce to update the order status to "completed".
    Args:
        order_id (str): Order ID in WooCommerce.
    Returns: 
        bool: True if the PUT request is successful, False otherwise. """

    # WooCommerce API client instance.
    wcapi = define_wcapi(timeout_inp=40)

    if actual_status_name in ['изпълнена', 'частично изпълнена', 'отказана']:
        data = {"status": "completed"}
        put_response = wcapi.put(f"orders/{order_id}", data)

        if put_response.status_code != 200:
            log_msg(
                'error', 'critical', f'ERROR! Check PUT response: {put_response.status_code}.\
                Order {str(order_id)} was NOT set to be completed in WC.')
            return False
    return True


def update_order_statuses(orders_db_dict: dict, number_of_orders_to_update: int) -> bool:
    ''' Update order status in RDS and make a PUT request to WooCommerce '''

    # Get request orders from Citadel: OrderID, InternalID, StatusID, and StatusName
    response_citadel = requests.get(
        f"http://{config.URL}:7779/api/orders/getOrderStatus",
        auth=HTTPBasicAuth(config.USERNAME, config.PASSWORD),
        timeout=120)

    if response_citadel.status_code != 200:
        log_msg('error', 'critical',
                f"Error in GET request to Citadel: {response_citadel.status_code}")
        return False

    # Process recent orders from Citadel
    for order_info in response_citadel.json()[-number_of_orders_to_update:]:
        order_id = order_info['orderId']

        # Check if order exists in the DB
        if order_id in orders_db_dict:
            actual_status_id = order_info['statusId']
            actual_status_name = order_info['statusName']
            actual_internal_id = order_info['internalId']

            # Update database if status has changed
            if orders_db_dict[order_id] != actual_status_id:

                update_order_status_in_wc(order_id, actual_status_name)

                # Define the update query
                update_query = '''
                UPDATE orders
                SET statusName = %s,
                    internalId = %s,
                    statusId = %s
                WHERE orderId = %s;
                '''

                params = (actual_status_name, actual_internal_id,
                          actual_status_id, order_id)
                execute_query(update_query, params=params)

                log_msg(
                    'general', 'info', f"Order {order_id} was set to be {actual_status_name}.")
                now = datetime.now()
                print(
                    f"{now.strftime('%Y-%m-%d %H:%M')} Order {order_id} ({actual_status_id})",
                    f"was set to be {actual_status_name}.")

    return True


def wc_get_orders(number_of_orders_to_update: int):
    """ Fetches a specified number of orders from WooCommerce using the REST API.
    Args:
        number_of_orders_to_update (int): Number of orders to retrieve.
    Returns:
        requests.Response or False:
            - The successful response object if orders are retrieved successfully.
            - False on failure after retry attempts. """

    wcapi = define_wcapi(40)

    for attempt in range(1, 8):
        try:
            wc_orders_response = wcapi.get(
                "orders", params={'orderby': 'date', 'per_page': number_of_orders_to_update})
            wc_orders_response.raise_for_status()  # Raise an HTTPError for bad responses
            return wc_orders_response

        except requests.RequestException as e:
            log_msg(
                'error', 'critical', f"Error WC GET orders response: {str(e)} at attempt {attempt}")
            sleep_duration = exponential_backoff(attempt)
            print(
                f"Script is asleep for {sleep_duration} seconds due to WC GET response error")
            time.sleep(sleep_duration)

    log_msg('error', 'critical',
            f"Failed to get orders after {attempt} attempts.")

    return False


def extract_order_data(single_order_response: dict) -> dict:
    ''' Returns single order data from WooCommerce '''

    billing_info = single_order_response['billing']
    # phone = billing_info['phone']
    
    if single_order_response['customer_note']:
        customer_name = billing_info['last_name'] + ' * Създ. бележка!'
    else:
        customer_name = billing_info['last_name']

    order_data = {
        "id": single_order_response['id'],
        "total": float(single_order_response['total']),
        "dateCreated": ' '.join(single_order_response['date_created'].split('T')),
        "customerName": customer_name,
        "customerEmail": billing_info['email'],
        "hasInvoice": 0,
        "items": [{"qty": item["quantity"], "sku": item["sku"], "price": item["total"]}
                  for item in single_order_response["line_items"]] , 
        "customer_notes" : single_order_response['customer_note']
    }

    return order_data
