import psycopg2
from psycopg2 import OperationalError
import config
from utils import log_msg


def execute_query(query, params=None, fetch_data=False):
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

    try:
        conn = psycopg2.connect(**config.DATABASE)
        cur = conn.cursor()
        # if params = None insert empty tuple
        cur.execute(query, params or ())

        if fetch_data:
            data = cur.fetchall()
            return data
        else:
            conn.commit()

    except OperationalError as e:
        print(f"The error '{e}' occurred")
    finally:
        if conn:
            cur.close()
            conn.close()


def delete_old_orders():
    delete_query = '''
    DELETE FROM orders
    WHERE Id IN (SELECT Id FROM orders ORDER BY Id LIMIT (SELECT COUNT(*) - 50 FROM orders)); '''

    execute_query(delete_query, params=None)
    log_msg('general', 'info', f" -> 20 old orders were deleted from DB.")
    print(f" -> 20 old orders were deleted from DB.")

    query = ''' SELECT orderId FROM orders ORDER BY orderId DESC LIMIT 1;'''
    last_order_id = execute_query(query, params=None, fetch_data=True)
    log_msg('general', 'info', f"Last order ID is {last_order_id[0][0]}")
    print(f"Last order ID is {last_order_id[0][0]}")


def add_order_to_db(order_id, total_to_pay, internalId, statusId, statusName, pharmacy):
    ''' Appends order info to the DB '''
    insert_query = '''
    INSERT INTO orders (orderId, statusId, statusName, total_to_pay, pharmacy, internalId)
    VALUES (%s, %s, %s, %s, %s, %s);
    '''
    params = (order_id, statusId, statusName,
              total_to_pay, pharmacy, internalId)

    execute_query(insert_query, params=params)
