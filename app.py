
from cs50 import SQL
from flask import Flask, flash, redirect, request, render_template, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import pytz

from helpers import login_required

app = Flask(__name__)

#Add loop control extension to Jinja
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Set the session lifetime (in seconds)
app.config['PERMANENT_SESSION_LIFETIME'] = 10800 # 3 hours

# Initialize the Flask-Session extension
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Ensure that the client always fetches a fresh copy of the content from the server and doesn't use a cached version
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Register administrator
@app.route("/register_admin", methods=["GET", "POST"])
def register_admin():

    rows = db.execute(
        "SELECT * FROM users WHERE permission = 'admin';"
    )

    if len(rows) != 0:
        return render_template("info.html")

    """Register administrator"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("You must provide a username")
            return render_template("register_admin.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("You must provide a password")
            return render_template("register_admin.html")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            flash("You must provide a password confirmation")
            return render_template("register_admin.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username doesn't exists and password confirmation is correct
        if len(rows) != 0:
            flash("Username already exists")
            return render_template("register_admin.html")

        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Password doesn't match with confirmation")
            return render_template("register_admin.html")

        # Hash user's password
        password_hash = generate_password_hash(request.form.get("password"))

        # Inserts user into database
        db.execute(
            "INSERT INTO users (username, hash, permission) VALUES (?, ?, ?);",
            request.form.get("username"),
            password_hash,
            "admin"
        )

        # Query database for new user entry
        new_user_entry = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Log new user in
        session["user_id"] = new_user_entry[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register_admin.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("You must provide a username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("You must provide a password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():

    # Specify the time zone you want to work with
    my_timezone = pytz.timezone('America/Fortaleza')

    # Get the current time in the specified time zone
    current_date = datetime.now(my_timezone).date()
    # current_date -= timedelta(days=1) # Remove later

    # Get current week day
    current_day_of_week = current_date.weekday()

    # Current week dates
    dates_current_week = []

    # Get days before current day
    if current_day_of_week == 0:
        dates_current_week.append(current_date)

    if current_day_of_week > 0:
        for i in range(current_day_of_week, 0, -1):
            day_before = (current_date - timedelta(days=i))
            dates_current_week.append(day_before)

    # Get days ahead current day
    if current_day_of_week <= 5:
        for i in range(1, 6 - current_day_of_week):
            day_ahead = current_date + timedelta(days=i)
            dates_current_week.append(day_ahead)
        dates_current_week.append(current_date)

    this_week_orders = []

    for i in range(6):
        day_orders = db.execute(
            "SELECT orders.id, customers.name, customers.neighborhood, orders.amount FROM orders INNER JOIN customers ON orders.customer_id=customers.id WHERE orders.execution_date = ?;", dates_current_week[i]
        )
        for j in range(len(day_orders)):
            order_services = db.execute(
                "SELECT service, quantity FROM services_ordered WHERE order_id = ?;", day_orders[j]["id"]
            )
            day_orders[j]["services"] = []
            for service in order_services:
                day_orders[j]["services"].append({'service': service["service"], 'quantity': service["quantity"]})

        this_week_orders.append(day_orders)

    # Next week dates
    dates_next_week = []

    for date in dates_current_week:
        dates_next_week.append(date + timedelta(days=7))

    # Get next week orders day by day
    next_week_orders = []

    for i in range(6):
        day_orders = db.execute(
            "SELECT orders.id, customers.name, customers.neighborhood, orders.amount FROM orders INNER JOIN customers ON orders.customer_id=customers.id WHERE orders.execution_date = ?;", dates_next_week[i]
        )
        for j in range(len(day_orders)):
            order_services = db.execute(
                "SELECT service, quantity FROM services_ordered WHERE order_id = ?;", day_orders[j]["id"]
            )
            day_orders[j]["services"] = []
            for service in order_services:
                day_orders[j]["services"].append({'service': service["service"], 'quantity': service["quantity"]})

        next_week_orders.append(day_orders)

    return render_template("index.html", this_week_orders=this_week_orders, dates_current_week=dates_current_week, next_week_orders=next_week_orders, dates_next_week=dates_next_week)


@app.route("/orders", methods=["GET", "POST"])
@login_required
def orders():

    order_status = [
        "Scheduled",
        "Done",
        "Canceled"
    ]

    payment_types = [
        "Cash",
        "Credit Card",
        "Debit Card",
        "Transfer",
        "Uninformed"
    ]

    payment_status = [
        "Paid",
        "Not paid"
    ]

    # Search for technician
    technicians_search = db.execute(
        "SELECT name FROM staff WHERE role = 'Technician';"
    )

    technicians = []
    for row in technicians_search:
        technicians.append(row["name"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure a customers name was submitted
        if not request.form.get("name"):
            flash("You must provide a username")
            return redirect("/orders")

        # Ensure a scheduling date was submitted
        elif not request.form.get("date"):
            flash("You must provide a scheduling date")
            return redirect("/orders")

        # Ensure a service item was submitted
        elif not request.form.get("service"):
            flash("You must provide at least a service item")
            return redirect("/orders")

        # Query database for customer
        rows = db.execute(
            "SELECT * FROM customers WHERE name = ?", request.form.get("name")
        )

        # Ensure customer is registered
        if len(rows) != 1:
            flash("Customer not registered")
            return redirect("/orders")

        # Set the date of the service ordering
        timestamp = datetime.now()

        # Insert new order into database
        db.execute(
            "INSERT INTO orders (customer_id, register_date, execution_date, time, amount, discount, status, payment, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
            request.form.get("customer_id"),
            timestamp,
            request.form.get("date"),
            request.form.get("time"),
            int(request.form.get("total")),
            0 if request.form.get("total_discount") == '' else int(request.form.get("total_discount")),
            "Scheduled",
            request.form.get("payment_type"),
            "Not paid"
        )

        # Search for id of recently added order
        order_id = db.execute(
            "SELECT id FROM orders ORDER BY id DESC LIMIT 1;"
        )

        # Insert distinct services from the new order into database
        for i in range(len(request.form.getlist("service"))):
            db.execute(
                "INSERT INTO services_ordered (order_id, service, quantity, price_un, discount_un) VALUES (?, ?, ?, ?, ?);",
                order_id[0]["id"],
                request.form.getlist("service")[i],
                int(request.form.getlist("quantity")[i]),
                int(request.form.getlist("price_un")[i]),
                int(request.form.getlist("discount_un")[i]) if request.form.getlist("discount_un")[i] != '' else '',
            )

        return redirect("/orders")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        orders = db.execute(
            "SELECT orders.id, customers.name, orders.execution_date, customers.address, customers.address_number, customers.neighborhood, orders.amount, orders.status, orders.payment_status, orders.technician FROM orders INNER JOIN customers ON orders.customer_id=customers.id ORDER BY orders.id DESC;"
        )
        print(technicians)
        return render_template("orders.html", order_status=order_status, payment_status=payment_status, payment_types=payment_types, technicians=technicians, orders=orders)


@app.route("/orders/edit=<order_id>", methods=["GET", "POST"])
@login_required
def edit_order(order_id):

    payment_types = [
        "Cash",
        "Credit Card",
        "Debit Card",
        "Transfer",
        "Uninformed"
    ]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure a scheduling date was submitted
        if not request.form.get("date"):
            flash("You must provide a scheduling date")
            return redirect("/orders")

        # Ensure a service item was submitted
        elif not request.form.get("service"):
            flash("You must provide at least a service item")
            return redirect("/orders")

        # Remove all the service order items from the database
        db.execute(
            "DELETE FROM services_ordered WHERE order_id = ?;", order_id
        )

        # Update order entry for general informations
        db.execute(
            "UPDATE orders SET execution_date = ?, time = ?, amount = ?, discount = ?, payment = ? WHERE id = ?;",
            request.form.get("date"),
            request.form.get("time"),
            int(request.form.get("total")),
            int(request.form.get("total_discount")),
            request.form.get("payment_type"),
            order_id
        )

        # Insert distinct services from the updated order into database
        for i in range(len(request.form.getlist("service"))):
            db.execute(
                "INSERT INTO services_ordered (order_id, service, quantity, price_un, discount_un) VALUES (?, ?, ?, ?, ?);",
                order_id,
                request.form.getlist("service")[i],
                int(request.form.getlist("quantity")[i]),
                int(request.form.getlist("price_un")[i]),
                int(request.form.getlist("discount_un")[i]) if request.form.getlist("discount_un")[i] != '' else '',
            )

        flash("Order successfully updated!")

        return redirect("/orders")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        order = db.execute(
            "SELECT orders.id, customers.name, orders.execution_date, orders.time, orders.status, orders.discount, orders.amount, orders.payment, orders.payment_status, orders.technician FROM orders INNER JOIN customers ON orders.customer_id=customers.id WHERE orders.id = ?;",
            order_id
        )
        order_services = db.execute(
            "SELECT id, service, quantity, price_un, discount_un FROM services_ordered WHERE order_id = ?;", order_id
        )

        order[0]["services"] = []
        for service in order_services:
            service["subtotal"] = (service["price_un"] * service["quantity"]) - (0 if service["discount_un"] == '' else service["discount_un"])
            order[0]["services"].append(service)

        payment_types.remove(order[0]["payment"])
        print(order)
        print("------")
        print(order_services)
        return render_template("edit_order.html", order=order[0], payment_types=payment_types)


@app.route("/orders/remove=<order_id>")
@login_required
def remove_order(order_id):

    # Remove all the service order items from the database
    db.execute(
        "DELETE FROM services_ordered WHERE order_id = ?;", order_id
    )

    # Delete order from database
    db.execute(
        "DELETE FROM orders WHERE id = ?;", order_id
    )

    flash("Order successfully removed")
    return redirect("/orders")


@app.route("/orders/change_status")
@login_required
def change_order_status():

    order_id = request.args.get("order_id")
    status = request.args.get("status")

    # Update order status
    db.execute(
        "UPDATE orders SET status = ? WHERE id = ?;", status, order_id
    )

    flash("Order status successfully updated")
    return redirect("/orders")


@app.route("/orders/change_payment_status")
@login_required
def change_payment_status():

    order_id = request.args.get("order_id")
    payment_status = request.args.get("payment_status")

    # Update payment status
    db.execute(
        "UPDATE orders SET payment_status = ? WHERE id = ?;", payment_status, order_id
    )

    flash("Payment status successfully updated")
    return redirect("/orders")


@app.route("/orders/change_technician")
@login_required
def change_technician():

    order_id = request.args.get("order_id")
    technician = request.args.get("technician")

    # Update payment status
    db.execute(
        "UPDATE orders SET technician = ? WHERE id = ?;", technician, order_id
    )

    flash("Order technician successfully updated")
    return redirect("/orders")


@app.route("/customers", methods=["GET", "POST"])
@login_required
def customers():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure a name was submitted
        if not request.form.get("name"):
            flash("You must provide a name")
            return render_template("customers.html")

        # Ensure a phone was submitted
        elif not request.form.get("phone"):
            flash("You must provide a phone number")
            return render_template("customers.html")

        # Query database for phone number
        rows = db.execute(
            "SELECT * FROM customers WHERE phone = ?", request.form.get("phone")
        )

        # Ensure new user's phone number isn't already registered
        if len(rows) != 0:
            flash("Phone number is already registered")
            return render_template("customers.html")

        # Inserts new customer into database
        db.execute(
            "INSERT INTO customers (name, phone, phone2, address, address_number, address_complement, neighborhood, city) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
            request.form.get("name"),
            request.form.get("phone"),
            request.form.get("phone2"),
            request.form.get("address"),
            request.form.get("address_number"),
            request.form.get("complement"),
            request.form.get("neighborhood"),
            request.form.get("city")
        )

        # Redirect user to customers page
        flash(f'{request.form.get("name")} successfully registered')
        return redirect("/customers")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Selects all customers from database
        customers = db.execute("SELECT * FROM customers;")
        # Return rendered customers table in the page
        return render_template("customers.html", customers=customers)


@app.route("/customers/edit=<customer_id>", methods=["GET", "POST"])
@login_required
def edit_customer(customer_id):

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure a name was submitted
        if not request.form.get("name"):
            flash("You must provide a name")
            return redirect("/customers")

        # Ensure a phone was submitted
        elif not request.form.get("phone"):
            flash("You must provide a phone number")
            return redirect("/customers")

        # Query database for phone number
        rows = db.execute(
            "SELECT * FROM customers WHERE phone = ? AND NOT id = ?;",
             request.form.get("phone"),
             customer_id
        )

        # Ensure new user's phone number isn't already registered
        if len(rows) != 0:
            flash("Phone number is already registered")
            return redirect("/customers")

        # Standardize service description
        standardized_name = request.form.get("name").title()

        # Update customer entry
        db.execute(
            "UPDATE customers SET name = ?, phone = ?, phone2 = ?, address = ?, address_number = ?, address_complement = ?, neighborhood = ?, city = ? WHERE id = ?;",
            standardized_name,
            request.form.get("phone"),
            request.form.get("phone2"),
            request.form.get("address"),
            request.form.get("address_number"),
            request.form.get("complement"),
            request.form.get("neighborhood"),
            request.form.get("city"),
            customer_id
        )

        flash(f"Customer #{customer_id} registry successfully updated!")

        return redirect("/customers")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        customer = db.execute(
            "SELECT * FROM customers WHERE id = ?;",
            customer_id
        )
        return render_template("edit_customer.html", customer=customer[0])


@app.route("/customers/remove=<customer_id>")
@login_required
def remove_customer(customer_id):

    # Delete customer from database
    db.execute(
        "DELETE FROM customers WHERE id = ?;", customer_id
    )

    flash(f"Customer {customer_id} successfully removed")
    return redirect("/customers")


# API for searching customers for ajax feature
@app.route("/customer_search")
@login_required
def customer_search():
    customer = request.args.get("customer")

    if customer:
        customers = db.execute("SELECT id, name FROM customers WHERE name LIKE ? LIMIT 10", customer + "%")
    else:
        customers = []

    return jsonify(customers)


# API for searching services for ajax feature
@app.route("/service_search")
@login_required
def service_search():
    service = request.args.get("service")

    if service:
        services = db.execute("SELECT * FROM services WHERE description LIKE ? LIMIT 10", "%" + service + "%")
    else:
        services = []

    return jsonify(services)


@app.route("/services", methods=["GET", "POST"])
@login_required
def services():

    service_types = [
        "Upholstery",
        "Rug",
        "Baby",
        "Others"
    ]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure a description was submitted
        if not request.form.get("description"):
            flash("You must provide a service description")
            return redirect("/services")

        # Ensure a type was submitted
        elif not request.form.get("type") or request.form.get("type") not in service_types:
            flash("You must provide a service type")
            return redirect("/services")

        # Ensure a price was submitted
        elif not request.form.get("price"):
            flash("You must provide a price")
            return redirect("/services")

        # Standardize service description
        service_description = request.form.get("description").title()

        # Query database for service description
        rows = db.execute(
            "SELECT * FROM services WHERE description = ?", service_description
        )

        # Ensure new services's description isn't already registered
        if len(rows) != 0:
            flash("Service is already registered")
            return render_template("services.html")

        # Inserts new service into database
        db.execute(
            "INSERT INTO services (type, description, price) VALUES (?, ?, ?);",
            request.form.get("type"),
            service_description,
            request.form.get("price")
        )

        # Redirect user to customers page
        flash(f'New service successfully registered')
        return redirect("/services")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Selects all customers from database
        services = db.execute("SELECT * FROM services;")

        # Return rendered services table in the page
        return render_template("services.html", services=services, service_types=service_types)


@app.route("/services/edit=<service_id>", methods=["GET", "POST"])
@login_required
def edit_service(service_id):

    service_types = [
        "Upholstery",
        "Rug",
        "Baby",
        "Others"
    ]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure a description was submitted
        if not request.form.get("description"):
            flash("You must provide a service description")
            return redirect("/services")

        # Ensure a type was submitted
        elif not request.form.get("type") or request.form.get("type") not in service_types:
            flash("You must provide a service type")
            return redirect("/services")

        # Ensure a price was submitted
        elif not request.form.get("price"):
            flash("You must provide a price")
            return redirect("/services")

        # Standardize service description
        service_description = request.form.get("description").title()

        # Update service entry
        db.execute(
            "UPDATE services SET type = ?, description = ?, price = ? WHERE id = ?;",
            request.form.get("type"),
            service_description,
            request.form.get("price"),
            service_id
        )

        flash("Service successfully updated!")

        return redirect("/services")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        service = db.execute(
            "SELECT * FROM services WHERE id = ?;",
            service_id
        )
        return render_template("edit_service.html", service=service[0], service_types=service_types)


@app.route("/services/remove=<service_id>")
@login_required
def remove_service(service_id):

    # Delete service from database
    db.execute(
        "DELETE FROM services WHERE id = ?;", service_id
    )

    flash("Service successfully removed")
    return redirect("/services")


@app.route("/staff", methods=["GET", "POST"])
@login_required
def staff():

    roles = [
        "Technician",
        "Manager",
    ]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure a name was submitted
        if not request.form.get("name"):
            flash("You must provide a name")
            return redirect("/staff")

        # Ensure a role was submitted
        elif not request.form.get("role") or request.form.get("role") not in roles:
            flash("You must provide a role")
            return redirect("/staff")

        # Standardize name
        standardized_name = request.form.get("name").title()

        # Query database for name
        rows = db.execute(
            "SELECT * FROM staff WHERE name = ?", standardized_name
        )

        # Ensure name isn't already registered
        if len(rows) != 0:
            flash(f"{standardized_name} is already registered")
            return redirect("/staff")

        # Inserts new service into database
        db.execute(
            "INSERT INTO staff (name, role) VALUES (?, ?);",
            standardized_name,
            request.form.get("role")
        )

        # Redirect user to customers page
        flash(f'New staff member successfully registered')
        return redirect("/staff")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Selects all customers from database
        staff = db.execute("SELECT * FROM staff;")

        # Return rendered services table in the page
        return render_template("staff.html", staff=staff, roles=roles)


@app.route("/staff/edit=<person_id>", methods=["GET", "POST"])
@login_required
def edit_staff(person_id):

    roles = [
        "Technician",
        "Manager",
    ]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure a name was submitted
        if not request.form.get("name"):
            flash("You must provide a name")
            return redirect("/staff")

        # Ensure a role was submitted
        elif not request.form.get("role") or request.form.get("role") not in roles:
            flash("You must provide a role")
            return redirect("/staff")

        # Standardize name
        standardized_name = request.form.get("name").title()

        # Query database for name
        rows = db.execute(
            "SELECT * FROM staff WHERE name = ? AND NOT id = ?;",
             standardized_name,
             person_id
        )

        # Ensure name isn't already registered
        if len(rows) != 0:
            flash(f"{standardized_name} is already registered as a staff member")
            return redirect("/staff")

        # Update staff member entry
        db.execute(
            "UPDATE staff SET name = ?, role = ? WHERE id = ?;",
            request.form.get("name"),
            request.form.get("role"),
            person_id
        )

        flash("Staff member successfully updated!")

        return redirect("/staff")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        staff_member = db.execute(
            "SELECT * FROM staff WHERE id = ?;",
            person_id
        )
        return render_template("edit_staff.html", staff_member=staff_member[0], roles=roles)


@app.route("/staff/remove=<person_id>")
@login_required
def remove_staff(person_id):

    # Delete service from database
    db.execute(
        "DELETE FROM staff WHERE id = ?;", person_id
    )

    flash("Staff member successfully removed")
    return redirect("/staff")