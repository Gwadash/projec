from flask import render_template, request, redirect, flash, Blueprint, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .functions import *


main_bp = Blueprint("main", __name__)

@main_bp.route('register', methods=['POST', 'GET'])
def register():
    groups = []
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * from `groups`;")
        groups = cursor.fetchall()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        role = request.form["role"]
        group_id = request.form["group"]

        if not username or not password or not role:
            flash("Please fill out all fields")
            return redirect("/register")

        hashed_pw = generate_password_hash(password)
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id from users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash("Username already exists!")
                    return redirect("/register") 
                cursor.execute('INSERT INTO users (username, password) values (%s, %s)', (username, hashed_pw))

                user_id = cursor.lastrowid
                if role == 'Admin':
                    values = [(user_id, group.get('id')) for group in groups]
                    cursor.executemany("INSERT INTO user_groups (user_id, group_id) VALUES (%s, %s)", values)
                else:
                    cursor.execute("INSERT INTO user_groups (user_id, group_id) VALUES (%s, %s)", (user_id, group_id))
                conn.commit()
                flash("User registered successfully!")
                print(username, password,role, group_id)
                return redirect("/register")
        except Exception as E:
            print(E, 'Error')
            flash("Username already exists.", E)
            return redirect("/register")
        finally:
            conn.rollback()

    return render_template("register.html", groups=groups)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * from users where username = %s", (username,))
                user =cursor.fetchone()

                if not user or not check_password_hash(user.get("password"), password):
                    flash("Invalid email or password!")
                    return redirect("/login") 
                session["username"] = username
                flash("Login successful!")
                return redirect("/dashboard") 
        except Exception as E:
            flash("Something went wrong.")
            return redirect('/login')
        finally:
            conn.close()

    return render_template("login.html")

@main_bp.route("/dashboard")
def dashboard():
    if "username" in session:
        # Get sensor data
        return render_template("dashboard.html", username=session["username"])
    else:
        flash("Please log in to view your dashboard.")
        return redirect("/login")
    
@main_bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("You’ve been logged out.")
    return redirect("/login")

@main_bp.route('/setup_roles_permissions', methods=['GET'])
def setup_roles_and_permissions():
    conn = get_connection()
    cursor = conn.cursor()

    roles = ['Admin', 'User']
    permissions = ['admin_access', 'view_content']

    # Insert roles
    for role in roles:
        cursor.execute("INSERT INTO roles (role_name) VALUES (%s) ON DUPLICATE KEY UPDATE role_name = role_name", (role,))

    # Insert permissions
    for permission in permissions:
        cursor.execute("INSERT INTO permissions (permission_name) VALUES (%s) ON DUPLICATE KEY UPDATE permission_name = permission_name", (permission,))

    # Assign permissions to roles
    cursor.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES ((SELECT id FROM roles WHERE role_name = 'Admin'), (SELECT id FROM permissions WHERE permission_name = 'admin_access'))")
    cursor.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES ((SELECT id FROM roles WHERE role_name = 'User'), (SELECT id FROM permissions WHERE permission_name = 'view_content'))")

    conn.commit()
    return jsonify({"message": "Roles and permissions setup complete!"})

@main_bp.route('/sensor_data')
def sensor_data():
    try:
        if "username" in session:
            user = get_user(session.get("username"))
            user_id = user.get('id') # or however you're identifying the user
            data = get_user_sensor_data(user_id)
            return jsonify(data)
        else:
            flash("Please log in to view your dashboard.")
            return redirect("/login")
    except Exception as E:
        return  jsonify("sello") 
    
@main_bp.route('/sensor-data', methods=['POST'])
def sensor():
    data = request.json
    value = data.get('value')
    name = data.get('name')
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # 1. Get group_id from groups table where name = name
        cursor.execute("SELECT id FROM `groups` WHERE name = %s", (name,))
        result = cursor.fetchone()

        if not result:
            return {"status": "error", "message": f"Group '{name}' not found."}, 404

        group_id = result.get("id") #

        # 2. Insert value into sensor_data with group_id
        cursor.execute(
            "INSERT INTO sensor_data (name, group_id, value) VALUES (%s, %s, %s)",
            (name, group_id, value)
        )
        connection.commit()

        cursor.close()
        connection.close()

        return {"status": "ok"}, 200

    except Exception as e:
        print(f"Error saving data to MySQL: {e}")
        return {"status": "error", "message": str(e)}, 500
