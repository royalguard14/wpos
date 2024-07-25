from flask import Flask, render_template, jsonify, request  # Import necessary Flask modules for web framework
import mysql.connector  # Import MySQL connector for database connection
from config import Config  # Import configuration settings
from datetime import datetime  # Import datetime module to handle date and time
app = Flask(__name__)  # Initialize Flask application
app.config.from_object(Config)  # Load configuration from Config object


def get_db_connection():
    # Function to establish a connection to the MySQL database using credentials from the app config
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

cart = []  # Initialize an empty cart list to hold cart items

@app.route('/')  # Define the route for the home page
def index():
    # Get database connection
    connection = get_db_connection()
    # Fetch products
    cursor = connection.cursor(dictionary=True)  # Create a cursor to execute queries
    cursor.execute("SELECT id, name, price FROM product")  # Execute query to fetch product details
    products = cursor.fetchall()  # Fetch all product records

    # Fetch customers
    cursor.execute("SELECT id, name FROM customer")  # Execute query to fetch customer details
    customers = cursor.fetchall()  # Fetch all customer records

    # Fetch employee 1
    cursor.execute("SELECT name FROM employee where id = 1")  # Execute query to fetch employee name with id 1
    employee_name = cursor.fetchone()['name']  # Fetch employee name

    cursor.close()  # Close the cursor
    connection.close()  # Close the database connection

    # Render the index.html template with products, cart, employee_name, and customers
    return render_template('index.html', products=products, cart=cart, employee_name=employee_name, customers=customers)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])  # Define the route for adding a product to the cart
def add_to_cart(product_id):
    connection = get_db_connection()  # Get database connection
    cursor = connection.cursor(dictionary=True)  # Create a cursor to execute queries
    cursor.execute("SELECT id, name, price FROM product WHERE id = %s", (product_id,))  # Execute query to fetch product details by id
    product = cursor.fetchone()  # Fetch product details
    cursor.close()  # Close the cursor
    connection.close()  # Close the database connection

    if product:
        for item in cart:
            if item['id'] == product_id:
                item['quantity'] += 1  # Increment quantity if product already in cart
                break
        else:
            cart.append({"id": product_id, "name": product['name'], "price": product['price'], "quantity": 1})  # Add new product to cart
    # Return updated cart and total price as JSON response
    return jsonify({"cart": cart, "total": sum(item['price'] * item['quantity'] for item in cart)})

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])  # Define the route for removing a product from the cart
def remove_from_cart(product_id):
    global cart  # Use the global cart variable
    for item in cart:
        if item['id'] == product_id:
            if item['quantity'] > 1:
                item['quantity'] -= 1  # Decrement quantity if more than one in cart
            else:
                cart.remove(item)  # Remove product from cart if only one left
            break
    # Return updated cart and total price as JSON response
    return jsonify({"cart": cart, "total": sum(item['price'] * item['quantity'] for item in cart)})

@app.route('/add_customer', methods=['POST'])  # Define the route for adding a new customer
def add_customer():
    name = request.form['name']  # Get customer name from form data
    address = request.form['address']  # Get customer address from form data
    phone = request.form['phone']  # Get customer phone from form data
    connection = get_db_connection()  # Get database connection
    cursor = connection.cursor(dictionary=True)  # Create a cursor to execute queries
    cursor.execute(
        "INSERT INTO customer (name, address, phoneNo) VALUES (%s, %s, %s)",
        (name, address, phone)  # Execute query to insert new customer
    )
    connection.commit()  # Commit the transaction
    customer_id = cursor.lastrowid  # Get the id of the newly inserted customer
    cursor.close()  # Close the cursor
    connection.close()  # Close the database connection

    # Return new customer details as JSON response
    return jsonify({"id": customer_id, "name": name})

@app.route('/process_payment', methods=['POST'])  # Define the route for processing a payment
def process_payment():
    customer_id = request.form.get('customer_id')  # Get customer id from form data
    if not customer_id:
        customer_id = 1  # Default to customer id 1 if not provided
    employee_id = 1  # Default employee id to 1
    payment_amount = float(request.form['payment_amount'])  # Get payment amount from form data
    connection = get_db_connection()  # Get database connection
    cursor = connection.cursor(dictionary=True)  # Create a cursor to execute queries
    try:
        # Check if customer exists
        cursor.execute("SELECT id FROM customer WHERE id = %s", (customer_id,))
        if cursor.fetchone() is None:
            return jsonify({"success": False, "message": "Customer ID does not exist."})
        # Check if employee exists
        cursor.execute("SELECT id FROM employee WHERE id = %s", (employee_id,))
        if cursor.fetchone() is None:
            return jsonify({"success": False, "message": "Employee ID does not exist."})
        # Insert into salestransaction
        cursor.execute(
            "INSERT INTO salestransaction (customerId, employeeId, transactionDate, totalAmount, paymentAmount) VALUES (%s, %s, %s, %s, %s)",
            (customer_id, employee_id, datetime.now(), sum(item['price'] * item['quantity'] for item in cart), payment_amount)
        )
        transaction_id = cursor.lastrowid  # Get the id of the newly inserted transaction
        # Insert into salestransactiondetails
        for item in cart:
            cursor.execute(
                "INSERT INTO salestransactiondetails (transactionId, productId, quantity, price) VALUES (%s, %s, %s, %s)",
                (transaction_id, item['id'], item['quantity'], item['price'])
            )
        connection.commit()  # Commit the transaction
        cart.clear()  # Clear the cart after processing the payment
        return jsonify({"success": True, "message": "Payment processed successfully."})
    except Exception as e:
        connection.rollback()  # Rollback transaction in case of error
        return jsonify({"success": False, "message": str(e)})  # Return error message as JSON response
    finally:
        cursor.close()  # Close the cursor
        connection.close()  # Close the database connection

if __name__ == '__main__':  # Run the application
    app.run(debug=True, port=1993)  # Start the Flask app with debugging enabled on port 1993
