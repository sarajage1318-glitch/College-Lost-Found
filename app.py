from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from config import Config
from utils.db import get_db, close_db

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from mysql.connector import IntegrityError


# =========================================================
# FLASK APP CONFIGURATION
# =========================================================

app = Flask(__name__)
app.config.from_object(Config)

app.teardown_appcontext(close_db)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:

            flash(
                "Please fill in all required fields.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        hashed_password = generate_password_hash(password)

        db = get_db()

        cursor = db.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users
                (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    name,
                    email,
                    hashed_password,
                    "student"
                )
            )

            db.commit()

            flash(
                "Registration successful. Please log in.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except IntegrityError:

            db.rollback()

            flash(
                "Email already registered.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        finally:

            cursor.close()

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                password,
                role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()

        if user:

            try:

                password_valid = check_password_hash(
                    user["password"],
                    password
                )

            except ValueError:

                password_valid = False

            if password_valid:

                session.clear()

                session["user_id"] = user["user_id"]
                session["user_name"] = user["name"]
                session["role"] = user["role"]

                flash(
                    "Login successful.",
                    "success"
                )

                if user["role"] == "admin":

                    return redirect(
                        url_for("admin_dashboard")
                    )

                return redirect(
                    url_for("dashboard")
                )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# REPORT LOST ITEM
# =========================================================

@app.route(
    "/report-lost",
    methods=["GET", "POST"]
)
def report_lost():

    if "user_id" not in session:

        flash(
            "Please log in first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        item_name = request.form.get(
            "item_name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        date_reported = request.form.get(
            "date_reported",
            ""
        )

        if not item_name or not category or not location or not date_reported:

            flash(
                "Please fill in all required fields.",
                "error"
            )

            return redirect(
                url_for("report_lost")
            )

        db = get_db()

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO items
            (
                item_name,
                category,
                description,
                item_type,
                location,
                date_reported,
                reported_by,
                image_path,
                status
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                item_name,
                category,
                description,
                "Lost",
                location,
                date_reported,
                session["user_id"],
                None,
                "Lost"
            )
        )

        db.commit()

        cursor.close()

        flash(
            "Lost item reported successfully.",
            "success"
        )

        return redirect(
            url_for("items")
        )

    return render_template(
        "report-lost.html"
    )


# =========================================================
# REPORT FOUND ITEM
# =========================================================

@app.route(
    "/report-found",
    methods=["GET", "POST"]
)
def report_found():

    if "user_id" not in session:

        flash(
            "Please log in first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        item_name = request.form.get(
            "item_name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        date_reported = request.form.get(
            "date_reported",
            ""
        )

        if not item_name or not category or not location or not date_reported:

            flash(
                "Please fill in all required fields.",
                "error"
            )

            return redirect(
                url_for("report_found")
            )

        db = get_db()

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO items
            (
                item_name,
                category,
                description,
                item_type,
                location,
                date_reported,
                reported_by,
                image_path,
                status
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                item_name,
                category,
                description,
                "Found",
                location,
                date_reported,
                session["user_id"],
                None,
                "Found"
            )
        )

        db.commit()

        cursor.close()

        flash(
            "Found item reported successfully.",
            "success"
        )

        return redirect(
            url_for("items")
        )

    return render_template(
        "report-found.html"
    )


# =========================================================
# BROWSE ITEMS
# =========================================================

@app.route("/items")
def items():

    search = request.args.get(
        "search",
        ""
    ).strip()

    category = request.args.get(
        "category",
        ""
    ).strip()

    item_type = request.args.get(
        "item_type",
        ""
    ).strip()

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )

    query = """
        SELECT
            item_id,
            item_name,
            category,
            description,
            item_type,
            location,
            date_reported,
            reported_by,
            image_path,
            status
        FROM items
        WHERE 1=1
    """

    params = []

    if search:

        query += """
            AND (
                item_name LIKE %s
                OR description LIKE %s
                OR location LIKE %s
            )
        """

        search_value = "%" + search + "%"

        params.extend(
            [
                search_value,
                search_value,
                search_value
            ]
        )

    if category:

        query += """
            AND category = %s
        """

        params.append(category)

    if item_type:

        query += """
            AND item_type = %s
        """

        params.append(item_type)

    query += """
        ORDER BY item_id DESC
    """

    cursor.execute(
        query,
        params
    )

    items_list = cursor.fetchall()

    cursor.close()

    return render_template(
        "items.html",
        items=items_list,
        search=search,
        selected_category=category,
        selected_type=item_type
    )


# =========================================================
# ITEM DETAILS
# =========================================================

@app.route("/item/<int:item_id>")
def item_details(item_id):

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            i.*,
            u.name AS reporter_name
        FROM items i
        JOIN users u
            ON i.reported_by = u.user_id
        WHERE i.item_id = %s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    cursor.close()

    if not item:

        flash(
            "Item not found.",
            "error"
        )

        return redirect(
            url_for("items")
        )

    return render_template(
        "item.html",
        item=item
    )


# =========================================================
# CLAIM ITEM
# =========================================================

@app.route(
    "/claim/<int:item_id>",
    methods=["GET", "POST"]
)
def claim_item(item_id):

    if "user_id" not in session:

        flash(
            "Please log in first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )

    # Check item

    cursor.execute(
        """
        SELECT
            item_id,
            item_name,
            status
        FROM items
        WHERE item_id = %s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    if not item:

        cursor.close()

        flash(
            "Item not found.",
            "error"
        )

        return redirect(
            url_for("items")
        )

    if request.method == "POST":

        reason = request.form.get(
            "reason",
            ""
        ).strip()

        proof = request.form.get(
            "proof",
            ""
        ).strip()

        if not reason:

            cursor.close()

            flash(
                "Please provide a reason for your claim.",
                "error"
            )

            return redirect(
                url_for(
                    "claim_item",
                    item_id=item_id
                )
            )

        # Prevent duplicate claim
        cursor.execute(
            """
            SELECT request_id
            FROM claim_requests
            WHERE item_id = %s
            AND student_id = %s
            AND status IN ('Pending', 'Approved')
            """,
            (
                item_id,
                session["user_id"]
            )
        )

        existing_claim = cursor.fetchone()

        if existing_claim:

            cursor.close()

            flash(
                "You have already submitted a claim for this item.",
                "error"
            )

            return redirect(
                url_for(
                    "item_details",
                    item_id=item_id
                )
            )

        cursor.execute(
            """
            INSERT INTO claim_requests
            (
                item_id,
                student_id,
                reason,
                proof,
                request_date,
                status
            )
            VALUES
            (%s, %s, %s, %s, CURDATE(), %s)
            """,
            (
                item_id,
                session["user_id"],
                reason,
                proof if proof else None,
                "Pending"
            )
        )

        cursor.execute(
            """
            UPDATE items
            SET status = 'Claim Pending'
            WHERE item_id = %s
            """,
            (item_id,)
        )

        db.commit()

        cursor.close()

        flash(
            "Claim request submitted successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    cursor.close()

    return render_template(
        "claim.html",
        item=item
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        flash(
            "Please log in first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )

    # Student's reported items

    cursor.execute(
        """
        SELECT
            item_id,
            item_name,
            category,
            description,
            item_type,
            location,
            date_reported,
            status
        FROM items
        WHERE reported_by = %s
        ORDER BY item_id DESC
        """,
        (session["user_id"],)
    )

    my_items = cursor.fetchall()


    # Student's claims

    cursor.execute(
        """
        SELECT
            c.request_id,
            c.item_id,
            c.reason,
            c.proof,
            c.request_date,
            c.status,
            i.item_name
        FROM claim_requests c
        JOIN items i
            ON c.item_id = i.item_id
        WHERE c.student_id = %s
        ORDER BY c.request_id DESC
        """,
        (session["user_id"],)
    )

    my_claims = cursor.fetchall()

    cursor.close()

    return render_template(
        "dashboard.html",
        my_items=my_items,
        my_claims=my_claims
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    # Check login

    if "user_id" not in session:

        flash(
            "Please log in first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # Check admin role

    if session.get("role") != "admin":

        flash(
            "Administrator access is required.",
            "error"
        )

        return redirect(
            url_for("home")
        )

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )


    # -----------------------------------------------------
    # ALL REPORTED ITEMS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            i.item_id,
            i.item_name,
            i.category,
            i.item_type,
            i.location,
            i.date_reported,
            i.status,
            u.name AS reporter_name
        FROM items i
        JOIN users u
            ON i.reported_by = u.user_id
        ORDER BY i.item_id DESC
        """
    )

    all_items = cursor.fetchall()


    # -----------------------------------------------------
    # ALL CLAIM REQUESTS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            c.request_id,
            c.item_id,
            c.student_id,
            c.reason,
            c.proof,
            c.request_date,
            c.status,

            i.item_name,

            u.name AS student_name,
            u.email AS student_email

        FROM claim_requests c

        JOIN items i
            ON c.item_id = i.item_id

        JOIN users u
            ON c.student_id = u.user_id

        ORDER BY c.request_id DESC
        """
    )

    claims = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin.html",
        all_items=all_items,
        claims=claims
    )


# =========================================================
# APPROVE CLAIM
# =========================================================

@app.route(
    "/admin/claim/<int:request_id>/approve",
    methods=["POST"]
)
def approve_claim(request_id):

    if session.get("role") != "admin":

        flash(
            "Administrator access required.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )

    # Find item connected to claim

    cursor.execute(
        """
        SELECT
            item_id
        FROM claim_requests
        WHERE request_id = %s
        """,
        (request_id,)
    )

    claim = cursor.fetchone()

    if not claim:

        cursor.close()

        flash(
            "Claim request not found.",
            "error"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    item_id = claim["item_id"]


    # Approve selected claim

    cursor.execute(
        """
        UPDATE claim_requests
        SET status = 'Approved'
        WHERE request_id = %s
        """,
        (request_id,)
    )


    # Reject other pending claims
    # for the same item

    cursor.execute(
        """
        UPDATE claim_requests
        SET status = 'Rejected'
        WHERE item_id = %s
        AND request_id != %s
        AND status = 'Pending'
        """,
        (
            item_id,
            request_id
        )
    )


    # Update item

    cursor.execute(
        """
        UPDATE items
        SET status = 'Claim Approved'
        WHERE item_id = %s
        """,
        (item_id,)
    )

    db.commit()

    cursor.close()

    flash(
        "Claim approved successfully.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# REJECT CLAIM
# =========================================================

@app.route(
    "/admin/claim/<int:request_id>/reject",
    methods=["POST"]
)
def reject_claim(request_id):

    if session.get("role") != "admin":

        flash(
            "Administrator access required.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    db = get_db()

    cursor = db.cursor(
        dictionary=True
    )

    # Find item

    cursor.execute(
        """
        SELECT
            item_id
        FROM claim_requests
        WHERE request_id = %s
        """,
        (request_id,)
    )

    claim = cursor.fetchone()

    if not claim:

        cursor.close()

        flash(
            "Claim request not found.",
            "error"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    item_id = claim["item_id"]


    # Reject claim

    cursor.execute(
        """
        UPDATE claim_requests
        SET status = 'Rejected'
        WHERE request_id = %s
        """,
        (request_id,)
    )


    # Check whether another pending claim exists

    cursor.execute(
        """
        SELECT request_id
        FROM claim_requests
        WHERE item_id = %s
        AND status = 'Pending'
        """,
        (item_id,)
    )

    pending_claim = cursor.fetchone()


    # If no other pending claim exists,
    # change item back to Found

    if not pending_claim:

        cursor.execute(
            """
            UPDATE items
            SET status = 'Found'
            WHERE item_id = %s
            """,
            (item_id,)
        )

    db.commit()

    cursor.close()

    flash(
        "Claim rejected successfully.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# MARK ITEM AS RETURNED
# =========================================================

@app.route(
    "/admin/item/<int:item_id>/returned",
    methods=["POST"]
)
def mark_returned(item_id):

    if session.get("role") != "admin":

        flash(
            "Administrator access required.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE items
        SET status = 'Returned'
        WHERE item_id = %s
        """,
        (item_id,)
    )

    db.commit()

    cursor.close()

    flash(
        "Item marked as returned.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=False)