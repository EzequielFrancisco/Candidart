import sqlite3
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Conexão PostgreSQL
def get_pg_connection():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor
    )

# Conexão SQLite
def get_sqlite_connection():
    return sqlite3.connect('candidart.db')

def migrate_users():
    sqlite_conn = get_sqlite_connection()
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT * FROM users")
    users = sqlite_cursor.fetchall()

    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()

    for u in users:
        pg_cursor.execute("""
            INSERT INTO users (id, user_name, senha, company)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (u['id'], u['user_name'], u['senha'], u['company']))

    pg_conn.commit()
    pg_conn.close()
    sqlite_conn.close()
    print("Dados de users migrados!")

def migrate_candidacy():
    sqlite_conn = get_sqlite_connection()
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT * FROM candidacy")
    candidacies = sqlite_cursor.fetchall()

    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()

    for c in candidacies:
        pg_cursor.execute("""
            INSERT INTO candidacy (id, cv, company_name, resumo)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (c['id'], c['cv'], c['company_name'], c['resumo']))

    pg_conn.commit()
    pg_conn.close()
    sqlite_conn.close()
    print("Dados de candidacy migrados!")

def migrate_vacancies():
    sqlite_conn = get_sqlite_connection()
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT * FROM vacancies")
    vacancies = sqlite_cursor.fetchall()

    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()

    for v in vacancies:
        pg_cursor.execute("""
            INSERT INTO vacancies 
            (id, logo, company_name, job_title, job_description, location, job_type, salary_min, salary_max, currency, contact_email)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            v['id'], v['logo'], v['company_name'], v['job_title'], v['job_description'],
            v['location'], v['job_type'], v['salary_min'], v['salary_max'], v['currency'], v['contact_email']
        ))

    pg_conn.commit()
    pg_conn.close()
    sqlite_conn.close()
    print("Dados de vacancies migrados!")

if __name__ == "__main__":
    migrate_users()
    migrate_candidacy()
    migrate_vacancies()
