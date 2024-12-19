import psycopg2
from werkzeug.security import generate_password_hash


class DatabaseManager:

    @staticmethod
    def connect():
        conn = psycopg2.connect(
            host='localhost',
            database='airport',
            user='airport_user',
            password='pass1234'
        )
        return conn, conn.cursor()

    @staticmethod
    def create_tables_and_admin():
        conn, cur = DatabaseManager.connect()
        
        cur.execute('DROP TABLE IF EXISTS users CASCADE;')
        cur.execute('DROP TABLE IF EXISTS company_infos CASCADE;')
        cur.execute('DROP TABLE IF EXISTS planes CASCADE;')
        cur.execute('DROP TABLE IF EXISTS baskets CASCADE;')
        cur.execute('DROP TABLE IF EXISTS services CASCADE;')
        cur.execute('DROP TABLE IF EXISTS baskets_services CASCADE;')
        cur.execute('DROP TABLE IF EXISTS orders CASCADE;')

        cur.execute(
            """
            CREATE TABLE users (
                id serial PRIMARY KEY,
                login VARCHAR(50) NOT NULL,
                email VARCHAR(100),
                password VARCHAR(300) NOT NULL,
                is_company BOOLEAN DEFAULT true
            );
            """
        )

        cur.execute(
            f"""
            INSERT INTO users (login, password, is_company) VALUES ('admin', '{generate_password_hash('admin')}', false);
            """
        )

        cur.execute(
            """
            CREATE TABLE company_infos (
                id serial PRIMARY KEY,
                name VARCHAR(100),
                country VARCHAR(100),
                user_id INTEGER,
                money FLOAT DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE baskets (
                id serial PRIMARY KEY,
                sum_price INTEGER DEFAULT 0
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE planes (
                id serial PRIMARY KEY,
                name VARCHAR(50),
                company_id INTEGER,
                basket_id INTEGER,
                FOREIGN KEY (company_id) REFERENCES users (id),
                FOREIGN KEY (basket_id) REFERENCES baskets (id)
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE services (
                id serial PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                price INTEGER NOT NULL DEFAULT 0
            );
            """
        )

        cur.execute(
            """
            INSERT INTO services (name, price) VALUES ('Аренда ангара', 1000);
            """
        )

        cur.execute(
            """
            CREATE TABLE baskets_services (
                id serial PRIMARY KEY,
                basket_id INTEGER,
                service_id INTEGER,
                FOREIGN KEY (basket_id) REFERENCES baskets (id),
                FOREIGN KEY (service_id) REFERENCES services (id)
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE orders (
                id serial PRIMARY KEY,
                about VARCHAR (500),
                price INTEGER NOT NULL DEFAULT 0,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """
        )

        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def one(text=None):
        conn, cur = DatabaseManager.connect()
        result = None
        cur.execute(text)
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return result

    @staticmethod
    def all(text=None):
        conn, cur = DatabaseManager.connect()
        result = None
        cur.execute(text)
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return result

    @staticmethod
    def execute(text=None):
        conn, cur = DatabaseManager.connect()
        cur.execute(text)
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def tablenames():
        conn, cur = DatabaseManager.connect()
        result = None
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return result
    
    @staticmethod
    def desc(tablename=None):
        conn, cur = DatabaseManager.connect()
        cur.execute(f"SELECT * FROM {tablename} LIMIT 0;")
        result = [desc[0] for desc in cur.description]
        conn.commit()
        cur.close()
        conn.close()
        return result


if __name__ == '__main__':
    DatabaseManager.create_tables_and_admin()
