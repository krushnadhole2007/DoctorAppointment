from flask import Flask, render_template, request, redirect, session
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, template_folder="template", static_folder="static")

app.secret_key = "doctor_appointment_secret"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="DoctorAppointment",
        user="postgres",
        password="1234",
        port="5432"
    )


# =========================================================
# HOME / DASHBOARD
# =========================================================

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = get_db_connection()
        cur = conn.cursor()

        hashed_password = generate_password_hash(password)

        try:

            # -------------------------------------------------
            # INSERT USER
            # -------------------------------------------------

            cur.execute("""
                INSERT INTO users
                (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id;
            """, (
                name,
                email,
                hashed_password,
                role
            ))

            user_id = cur.fetchone()[0]

            # -------------------------------------------------
            # PATIENT
            # -------------------------------------------------

            if role == "patient":

                phone = request.form["phone"]
                dob = request.form["date_of_birth"]
                gender = request.form["gender"]

                cur.execute("""
                    INSERT INTO patients
                    (user_id, phone, date_of_birth, gender)
                    VALUES (%s, %s, %s, %s);
                """, (
                    user_id,
                    phone,
                    dob,
                    gender
                ))

            # -------------------------------------------------
            # DOCTOR
            # -------------------------------------------------

            elif role == "doctor":

                specialization = request.form["specialization"]
                phone = request.form["phone"]
                experience = request.form["experience"]

                cur.execute("""
                    INSERT INTO doctors
                    (user_id, specialization, phone, experience)
                    VALUES (%s, %s, %s, %s);
                """, (
                    user_id,
                    specialization,
                    phone,
                    experience
                ))

            conn.commit()

        except Exception as e:

            conn.rollback()

            cur.close()
            conn.close()

            return "Registration failed: " + str(e)

        cur.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                user_id,
                name,
                password,
                role
            FROM users
            WHERE email = %s;
        """, (email,))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:

            user_id = user[0]
            name = user[1]
            hashed_password = user[2]
            role = user[3]

            if check_password_hash(hashed_password, password):

                # -------------------------------------------------
                # CREATE SESSION
                # -------------------------------------------------

                session["user_id"] = user_id
                session["name"] = name
                session["role"] = role

                # -------------------------------------------------
                # PATIENT
                # -------------------------------------------------

                if role == "patient":
                    return redirect("/patient")

                # -------------------------------------------------
                # DOCTOR + ADMIN
                # SAME MAIN DASHBOARD
                # -------------------------------------------------

                elif role in ["doctor", "admin"]:
                    return redirect("/admin")

        return "Invalid email or password"

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# PATIENT DASHBOARD
# =========================================================

@app.route("/patient")
def patient_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "patient":
        return redirect("/login")

    return render_template(
        "patients.html",
        name=session["name"]
    )


# =========================================================
# DOCTOR DASHBOARD
# =========================================================

@app.route("/doctor")
def doctor_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") not in ["doctor", "admin"]:
        return redirect("/login")

    return render_template(
        "doctor.html",
        name=session["name"]
    )


# =========================================================
# ADMIN / DOCTOR DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    # Both doctor and admin can access this page
    if session.get("role") not in ["doctor", "admin"]:
        return redirect("/login")

    return render_template(
        "admin.html",
        name=session["name"],
        role=session["role"]
    )


# =========================================================
# SHOW ALL DOCTORS
# =========================================================

@app.route("/doctors")
def doctors():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            d.doctor_id,
            u.name,
            d.specialization,
            d.phone,
            d.experience
        FROM doctors d
        JOIN users u
            ON d.user_id = u.user_id
        ORDER BY u.name;
    """)

    doctors_list = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "doctors.html",
        doctors=doctors_list
    )


# =========================================================
# BOOK APPOINTMENT
# =========================================================

@app.route("/book/<int:doctor_id>", methods=["GET", "POST"])
def book_appointment(doctor_id):

    # -------------------------------------------------
    # ONLY PATIENTS CAN BOOK
    # -------------------------------------------------

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "patient":
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()

    # -------------------------------------------------
    # GET DOCTOR INFORMATION
    # -------------------------------------------------

    cur.execute("""
        SELECT
            d.doctor_id,
            u.name,
            d.specialization
        FROM doctors d
        JOIN users u
            ON d.user_id = u.user_id
        WHERE d.doctor_id = %s;
    """, (doctor_id,))

    doctor = cur.fetchone()

    if not doctor:

        cur.close()
        conn.close()

        return "Doctor not found"

    # -------------------------------------------------
    # POST REQUEST
    # -------------------------------------------------

    if request.method == "POST":

        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        reason = request.form["reason"]

        # -------------------------------------------------
        # FIND PATIENT
        # -------------------------------------------------

        cur.execute("""
            SELECT patient_id
            FROM patients
            WHERE user_id = %s;
        """, (session["user_id"],))

        patient = cur.fetchone()

        if not patient:

            cur.close()
            conn.close()

            return "Patient profile not found"

        patient_id = patient[0]

        # -------------------------------------------------
        # CHECK FOR APPOINTMENT CONFLICT
        # -------------------------------------------------

        cur.execute("""
            SELECT appointment_id
            FROM appointments
            WHERE doctor_id = %s
              AND appointment_date = %s
              AND appointment_time = %s
              AND status != 'cancelled';
        """, (
            doctor_id,
            appointment_date,
            appointment_time
        ))

        existing_appointment = cur.fetchone()

        if existing_appointment:

            cur.close()
            conn.close()

            return """
                <h2>Appointment Not Available</h2>

                <p>
                    This doctor is already booked at
                    the selected date and time.
                </p>

                <a href="/doctors">
                    Choose another time
                </a>
            """

        # -------------------------------------------------
        # INSERT APPOINTMENT
        # -------------------------------------------------

        try:

            cur.execute("""
                INSERT INTO appointments
                (
                    patient_id,
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    reason,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                reason,
                "pending"
            ))

            conn.commit()

        except Exception as e:

            conn.rollback()

            cur.close()
            conn.close()

            return "Appointment booking failed: " + str(e)

        cur.close()
        conn.close()

        return redirect("/appointments")

    # -------------------------------------------------
    # GET REQUEST
    # -------------------------------------------------

    cur.close()
    conn.close()

    return render_template(
        "book.html",
        doctor=doctor
    )


# =========================================================
# APPOINTMENTS
# =========================================================

@app.route("/appointments")
def appointments():

    # -------------------------------------------------
    # LOGIN CHECK
    # -------------------------------------------------

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()

    # =================================================
    # PATIENT APPOINTMENTS
    # =================================================

    if session.get("role") == "patient":

        cur.execute("""
            SELECT
                a.appointment_id,
                pu.name AS patient_name,
                du.name AS doctor_name,
                d.specialization,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status
            FROM appointments a

            JOIN patients p
                ON a.patient_id = p.patient_id

            JOIN users pu
                ON p.user_id = pu.user_id

            JOIN doctors d
                ON a.doctor_id = d.doctor_id

            JOIN users du
                ON d.user_id = du.user_id

            WHERE p.user_id = %s

            ORDER BY
                a.appointment_date,
                a.appointment_time;
        """, (session["user_id"],))

    # =================================================
    # DOCTOR / ADMIN APPOINTMENTS
    # =================================================

    elif session.get("role") in ["doctor", "admin"]:

        cur.execute("""
            SELECT
                a.appointment_id,
                pu.name AS patient_name,
                du.name AS doctor_name,
                d.specialization,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status
            FROM appointments a

            JOIN patients p
                ON a.patient_id = p.patient_id

            JOIN users pu
                ON p.user_id = pu.user_id

            JOIN doctors d
                ON a.doctor_id = d.doctor_id

            JOIN users du
                ON d.user_id = du.user_id

            ORDER BY
                a.appointment_date,
                a.appointment_time;
        """)

    else:

        cur.close()
        conn.close()

        return redirect("/login")

    appointments_list = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "appointments.html",
        appointments=appointments_list
    )


# =========================================================
# UPDATE APPOINTMENT STATUS
# =========================================================

@app.route("/update_status/<int:appointment_id>/<status>")
def update_status(appointment_id, status):

    # -------------------------------------------------
    # LOGIN CHECK
    # -------------------------------------------------

    if "user_id" not in session:
        return redirect("/login")

    # -------------------------------------------------
    # ONLY DOCTOR / ADMIN CAN CHANGE STATUS
    # -------------------------------------------------

    if session.get("role") not in ["doctor", "admin"]:
        return redirect("/login")

    # -------------------------------------------------
    # ALLOWED STATUSES
    # -------------------------------------------------

    allowed_statuses = [
        "pending",
        "confirmed",
        "completed",
        "cancelled"
    ]

    if status not in allowed_statuses:
        return "Invalid appointment status"

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            UPDATE appointments
            SET status = %s
            WHERE appointment_id = %s;
        """, (
            status,
            appointment_id
        ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        cur.close()
        conn.close()

        return "Status update failed: " + str(e)

    cur.close()
    conn.close()

    return redirect("/appointments")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)