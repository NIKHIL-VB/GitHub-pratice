from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps

app = Flask(__name__)

# Secret key is required for login sessions
app.secret_key = "plotease-secret-key-2026"

DATABASE = "bookings.db"


# =====================================
# ADMIN LOGIN DETAILS
# =====================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# =====================================
# DATABASE CONNECTION
# =====================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def create_database():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plot_id INTEGER NOT NULL,
            plot_name TEXT NOT NULL,
            location TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            booking_date TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


# =====================================
# ADMIN LOGIN PROTECTION
# =====================================

def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not session.get("admin_logged_in"):

            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return decorated_function


# =====================================
# PLOT DATA
# =====================================

plots = [
    {
        "id": 1,
        "name": "Green Valley Layout",
        "location": "Bengaluru",
        "size": "1200 sq.ft",
        "price": "₹18,00,000",
        "type": "Residential"
    },
    {
        "id": 2,
        "name": "Sunrise Residency",
        "location": "Mysuru",
        "size": "1500 sq.ft",
        "price": "₹22,00,000",
        "type": "Residential"
    },
    {
        "id": 3,
        "name": "Urban Heights",
        "location": "Hyderabad",
        "size": "1000 sq.ft",
        "price": "₹15,00,000",
        "type": "Commercial"
    }
]


# =====================================
# HOME PAGE
# =====================================

@app.route("/", methods=["GET"])
def home():

    search_location = request.args.get(
        "location",
        ""
    ).strip()

    search_type = request.args.get(
        "plot_type",
        ""
    ).strip()

    filtered_plots = []

    for plot in plots:

        location_matches = (
            search_location == ""
            or search_location.lower()
            in plot["location"].lower()
        )

        type_matches = (
            search_type == ""
            or search_type.lower()
            == plot["type"].lower()
        )

        if location_matches and type_matches:

            filtered_plots.append(plot)

    return render_template(
        "index.html",
        plots=filtered_plots,
        search_location=search_location,
        search_type=search_type
    )


# =====================================
# PLOT DETAILS
# =====================================

@app.route("/plot/<int:plot_id>")
def plot_details(plot_id):

    selected_plot = None

    for plot in plots:

        if plot["id"] == plot_id:

            selected_plot = plot

            break

    if selected_plot is None:

        return "Plot not found", 404

    return render_template(
        "plot_details.html",
        plot=selected_plot
    )


# =====================================
# BOOKING PAGE
# =====================================

@app.route(
    "/book/<int:plot_id>",
    methods=["GET", "POST"]
)
def book_plot(plot_id):

    selected_plot = None

    for plot in plots:

        if plot["id"] == plot_id:

            selected_plot = plot

            break

    if selected_plot is None:

        return "Plot not found", 404

    if request.method == "POST":

        customer_name = request.form.get(
            "customer_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        booking_date = request.form.get(
            "booking_date",
            ""
        ).strip()

        connection = get_db_connection()

        cursor = connection.execute("""
            INSERT INTO bookings (
                plot_id,
                plot_name,
                location,
                customer_name,
                email,
                phone,
                booking_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            selected_plot["id"],
            selected_plot["name"],
            selected_plot["location"],
            customer_name,
            email,
            phone,
            booking_date
        ))

        connection.commit()

        booking_id = cursor.lastrowid

        connection.close()

        return render_template(
            "booking_success.html",
            plot=selected_plot,
            booking_id=booking_id,
            customer_name=customer_name,
            email=email,
            phone=phone,
            booking_date=booking_date
        )

    return render_template(
        "booking.html",
        plot=selected_plot
    )


# =====================================
# ADMIN LOGIN
# =====================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if session.get("admin_logged_in"):

        return redirect(url_for("admin_bookings"))

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session["admin_logged_in"] = True

            session["admin_username"] = username

            return redirect(url_for("admin_bookings"))

        error = "Invalid username or password."

    return render_template(
        "admin_login.html",
        error=error
    )


# =====================================
# ADMIN DASHBOARD
# =====================================

@app.route("/admin/bookings")
@admin_required
def admin_bookings():

    connection = get_db_connection()

    bookings = connection.execute("""
        SELECT *
        FROM bookings
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "admin_bookings.html",
        bookings=bookings
    )


# =====================================
# ADMIN LOGOUT
# =====================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(url_for("home"))


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)