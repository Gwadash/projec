import pymysql

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME =  ""

connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )

def create_tables(connection):
    try:
        with connection.cursor() as cursor:
            # SQL statement to create the 'adcons' table
            create_roles_table = '''
                CREATE TABLE IF NOT EXISTS  `roles` (
                `id` int NOT NULL AUTO_INCREMENT,
                `role_name` varchar(255) NOT NULL,
                PRIMARY KEY (`id`),
                UNIQUE KEY `role_name` (`role_name`)
                ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            '''

            create_user_roles_table = '''
                CREATE TABLE IF NOT EXISTS  `user_roles` (
                `user_id` int NOT NULL,
                `role_id` int NOT NULL,
                PRIMARY KEY (`user_id`,`role_id`),
                KEY `role_id` (`role_id`),
                CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
                CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            '''

            create_role_permissions_table = '''
                CREATE TABLE IF NOT EXISTS `role_permissions` (
                `role_id` int NOT NULL,
                `permission_id` int NOT NULL,
                PRIMARY KEY (`role_id`,`permission_id`),
                KEY `permission_id` (`permission_id`),
                CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
                CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            '''

            create_permissions_table = '''
                CREATE TABLE  IF NOT EXISTS `permissions` (
                `id` int NOT NULL AUTO_INCREMENT,
                `permission_name` varchar(255) NOT NULL,
                PRIMARY KEY (`id`),
                UNIQUE KEY `permission_name` (`permission_name`)
                ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            '''

            create_groups_table = '''
                CREATE TABLE IF NOT EXISTS `groups` (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            '''

            create_sites_table = '''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    value DOUBLE NOT NULL,
                    group_id BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_sites_group FOREIGN KEY (group_id) REFERENCES `groups`(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            '''

            create_user_groups_table = '''
                CREATE TABLE  IF NOT EXISTS `user_groups` (
                    user_id INT NOT NULL,
                    group_id BIGINT NOT NULL,
                    PRIMARY KEY (user_id, group_id),
                    CONSTRAINT fk_user_groups_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    CONSTRAINT fk_user_groups_group FOREIGN KEY (group_id) REFERENCES `groups`(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            '''

            create_users_table = '''
                CREATE TABLE IF NOT EXISTS `users` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `email` varchar(100) NOT NULL,
                `password` varchar(100) NOT NULL,
                `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            '''

            # Execute SQL commands to create the tables
            cursor.execute(create_users_table)
            cursor.execute(create_roles_table)
            cursor.execute(create_permissions_table)
            cursor.execute(create_role_permissions_table)
            cursor.execute(create_user_roles_table)
            cursor.execute(create_groups_table)
            cursor.execute(create_sites_table)
            cursor.execute(create_user_groups_table)

            groups = ["IR Obstacle Sensor", "LDR Light Sensor", "Soil Moisture Sensor", "Temperature Sensor"] #ADD A GROUP NAME

            cursor.executemany("INSERT INTO `groups` (name) VALUES (%s)", groups)

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
            
            # Commit the changes
            connection.commit()

            print("Tables and data created successfully!")

    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        connection.rollback()
    finally:
        connection.close()

# Run the function to create the tables
if __name__ == "__main__":
    create_tables(connection)