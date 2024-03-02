Orders Manager 

This project is a Python script that automates the process of updating a local PostgreSQL database with new orders from a WooCommerce store. The script is designed to run continuously and check for new orders at regular intervals, ensuring that the local database remains up-to-date with the latest order data from the WooCommerce store.

Functionality

The script performs the following functions:

    Fetch WooCommerce orders: The script connects to a WooCommerce store using the woocommerce Python package and fetches the most recent orders that have not yet been processed by the script.
    Update a PostgreSQL RDS: The script updates a local PostgreSQL database with the new order data. It does this by connecting to the database using the psycopg2 Python package and executing SQL queries to insert the new orders into the database.
    Generate an invoice: The script sends a POST request to an inventory management software to generate an invoice for each new order. This is done using the requests Python package.
    Delete old orders: If the number of orders in the database exceeds 70, the script will delete the oldest orders to keep the database size manageable.

Architecture

    The script is organized into several modules, each with a specific function. The main module, main.py, contains the main loop of the script, which runs indefinitely and checks for new orders at regular intervals. The database.py module contains functions for connecting to and querying the PostgreSQL database. The woocommerce.py module contains functions for connecting to and fetching data from the WooCommerce store. The utils.py module contains utility functions used throughout the script such as logging messages.


Requirements

    Python 3.x
    The following Python packages: pandas, psycopg2, requests, and datetime

Usage

The script will run indefinitely, checking for new orders every 5 minutes during the hours of 8 AM to 5 PM on weekdays. It will log messages to the console to indicate when it is running and when it has successfully updated the database.
