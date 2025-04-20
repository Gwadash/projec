import pymysql

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Rotondwa2@"
DB_NAME =  "flask_app"

def get_connection():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

    return connection
    
def assign_role_to_user(user_id, role_name, connection):
    # Check if the role exists
    try:
        with connection.cursor() as cursor:
            # Check if the role exists in the 'roles' table
            cursor.execute("SELECT id FROM roles WHERE role_name = %s", (role_name,))
            role = cursor.fetchone()
            if not role:
                raise Exception("Role does not exist.")

            role_id = role['id']

            # Check if the user already has a role assigned in 'user_roles'
            cursor.execute("SELECT * FROM user_roles WHERE user_id = %s", (user_id,))
            existing_role = cursor.fetchone()

            if existing_role:
                # Update the existing role
                cursor.execute("UPDATE user_roles SET role_id = %s WHERE user_id = %s", (role_id, user_id))
            else:
                # Insert a new role assignment
                cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, role_id))

            connection.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
        return False

def get_user(username: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * from users WHERE username = %s", (username))
            user = cursor.fetchone()
            if user:
                return user
            else:
                return None
    except Exception as E:
        print(E, "Error")
        raise E
    finally:
        conn.close()

def get_user_sensor_data(user_id: int):
    if not user_id:
        return None

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.*
                FROM sensor_data s
                JOIN `groups` g ON s.group_id = g.id
                JOIN user_groups ug ON g.id = ug.group_id
                JOIN (
                    SELECT group_id, MAX(created_at) AS latest_time
                    FROM sensor_data
                    GROUP BY group_id
                ) latest ON latest.group_id = s.group_id AND latest.latest_time = s.created_at
                WHERE ug.user_id = %s
            """, (user_id,))

            sensors = cursor.fetchall() 
        return {"sensors": [{"id": row.get('id'), "value": row.get('value'), "name": row.get('name'), "create_at": row.get("created_at")} for row in sensors]}

    except Exception as e:
        print("error", e)
        return None

    finally:
        conn.close()