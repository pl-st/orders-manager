""" Module that provides the main functionality of the RDS database. """

import psycopg2
from psycopg2 import OperationalError, DatabaseError
import config
from utils.log_msg import log_msg


def execute_query(query: str, params=None, fetch_data=False):
    ''' 
    Executes an SQL query and returns the result.
        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to pass to the query. Defaults to None.
            fetch_data (bool, optional): Whether to fetch the data from the query. Defaults to False.
        Returns: 
            The result of the query, either the number of rows affected or the fetched data.
        Raises: 
            OperationalError: If there is an error connecting to the database or executing the query.     
    '''

    with psycopg2.connect(**config.DATABASE) as conn:
        cur = conn.cursor()

        try:
            cur.execute(query, params or ())

            if fetch_data:
                data = cur.fetchall()
                return data
            else:
                conn.commit()
        except (OperationalError, DatabaseError) as e:
            print(f"An error occurred: {e}")


def delete_old_orders():
    """ Deletes old olders so database would be more managable. """
    
    delete_query = '''
    DELETE FROM orders
    WHERE Id IN (SELECT Id FROM orders ORDER BY Id LIMIT (SELECT COUNT(*) - 50 FROM orders)); '''

    execute_query(delete_query, params=None)
    log_msg('general', 'info', " -> 20 old orders were deleted from DB.")
    print(" -> 20 old orders were deleted from DB.")

    query = 'SELECT orderId FROM orders ORDER BY orderId DESC LIMIT 1;'
    last_order_id = execute_query(query, params=None, fetch_data=True)
    log_msg('general', 'info', f"Last order ID is {last_order_id[0][0]}")
    print(f"Last order ID is {last_order_id[0][0]}")


def add_order_to_db(params: tuple):
    ''' Appends an order to the database. '''

    insert_query = '''
    INSERT INTO orders (orderId, statusId, statusName, total_to_pay, pharmacy, internalId, customer_notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    '''

    execute_query(insert_query, params=params)
