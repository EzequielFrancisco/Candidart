import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Função de conexão
def get_connection():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor
    )

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_name TEXT,
        senha TEXT,
        company TEXT
    );
    """)

    # Tabela candidacy
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidacy (
        id SERIAL PRIMARY KEY,
        cv TEXT,
        company_name TEXT,
        resumo TEXT
    );
    """)

    # Tabela vacancies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vacancies (
        id SERIAL PRIMARY KEY,
        logo TEXT,
        company_name TEXT,
        job_title TEXT,
        job_description TEXT,
        location TEXT,
        job_type TEXT,
        salary_min REAL,
        salary_max REAL,
        currency TEXT,
        contact_email TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    create_tables()
