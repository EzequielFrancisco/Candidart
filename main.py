from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = "hddvdblu-raylesardisc"

# URL da base de dados PostgreSQL do Render (fallback)
DEFAULT_DB_URL = "postgresql://candidart_user:iamRDIGYHltN7Eoft4QNu6p56YY2Qhbn@dpg-d4cmoaidbo4c73dbs1f0-a.oregon-postgres.render.com/candidart"

def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL") or DEFAULT_DB_URL
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# --- TESTE DE BASE DE DADOS ---
@app.route("/test_db/<senha_secreta>")
def test_db(senha_secreta):
    if senha_secreta != "3z3qui3lfr4ncisc0":
        return "Senha incorreta!", 403
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        return f"Conexão com PostgreSQL OK! Resultado: {result}"
    except Exception as e:
        return f"Erro ao ligar à base de dados: {e}"

# --- HOME ---
@app.route("/")
def home():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_name TEXT,
                senha TEXT,
                company TEXT
            )
        """)
        cursor.execute("SELECT id, user_name, company FROM users")
        users = cursor.fetchall()
        conn.close()
        return render_template("index.html", session=session, users=users)
    except Exception as e:
        return f"Erro na base de dados: {e}"

# --- LOGIN ---
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_name=%s AND senha=%s", (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['username'] = user['user_name']
                session['company'] = user['company']
                flash(f"Bem-vindo, {username}!", "success")
                return redirect(url_for('home'))
            flash("Preencha todos os campos com os dados corretos!", "error")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Ocorreu um erro na base de dados: {e}", "error")
            return render_template("login.html")
    return render_template("login.html")

# --- REGISTER ---
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == "POST":
        user_name = request.form['username']
        senha = request.form['password']
        company = request.form['company']
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (user_name, senha, company) VALUES (%s,%s,%s)", (user_name, senha, company))
            conn.commit()
            conn.close()
            flash("Registo enviado com sucesso!", "success")
            return redirect(url_for("login"))
        except Exception as e:
            return f"Erro no banco de dados: {e}"
    return render_template("register.html")

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Sessão terminada!", "info")
    return redirect(url_for("home"))

# --- CANDIDACY ---
@app.route("/candidacy")
def candidacy():
    return render_template("candidacy.html")

@app.route("/apply/<empresa>/<post>")
def apply(empresa, post):
    return render_template("apply.html", empresa=empresa, post=post)

@app.route("/insert", methods=["POST"])
def insert():
    cv = request.files.get("curriculo")
    if not cv:
        flash("O currículo é obrigatório.", "error")
        return redirect(url_for("home"))
    os.makedirs("static/cv", exist_ok=True)
    cv.save(f"static/cv/{cv.filename}")

    company_name = request.form['empresa']
    post = request.form['post']
    resumo = request.form['resumo']

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidacy (
                id SERIAL PRIMARY KEY,
                cv TEXT,
                company_name TEXT,
                resumo TEXT
            )
        """)
        cursor.execute("INSERT INTO candidacy (cv, company_name, resumo) VALUES (%s,%s,%s)", (cv.filename, company_name, resumo))
        conn.commit()
        conn.close()
        flash("Candidatura enviada com sucesso!", "success")
        return redirect(url_for("home"))
    except Exception as e:
        return f"Erro no banco de dados: {e}"

# --- VACANCIES ---
@app.route("/vacancies")
def vacancies():
    try:
        conn = get_connection()
        cursor = conn.cursor()
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
            )
        """)
        cursor.execute("SELECT * FROM vacancies")
        vagas = cursor.fetchall()
        conn.close()
        return render_template("vacancies.html", vagas=vagas)
    except Exception as e:
        return f"Erro na base de dados: {e}"

# --- DATE ---
@app.route("/date")
def date():
    if "company" not in session:
        flash("Método não permitido", "error")
        return redirect(url_for("home"))
    company_name = session['company']
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidacy WHERE company_name=%s", (company_name,))
        dates = cursor.fetchall()
        conn.close()
        return render_template("date.html", dates=dates)
    except Exception as e:
        return f"Erro no banco de dados: {e}"

# --- CREATE JOB ---
@app.route("/create", methods=["GET","POST"])
def create():
    if request.method == "POST":
        logo = request.files.get("logo")
        logo_name = logo.filename if logo else "padrao.png"
        if logo:
            os.makedirs("static/img", exist_ok=True)
            logo.save(f"static/img/{logo_name}")

        company_name = request.form['company-name']
        job_title = request.form['job-title']
        job_description = request.form['job-description']
        location = request.form['location']
        job_type = request.form['job-type']
        salary_min = request.form['salary-min']
        salary_max = request.form['salary-max']
        currency = request.form['currency']
        contact_email = request.form['contact-email']

        try:
            conn = get_connection()
            cursor = conn.cursor()
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
                )
            """)
            cursor.execute("""
                INSERT INTO vacancies 
                (logo, company_name, job_title, job_description, location, job_type, salary_min, salary_max, currency, contact_email)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (logo_name, company_name, job_title, job_description, location, job_type, salary_min, salary_max, currency, contact_email))
            conn.commit()
            conn.close()
            flash("Vaga criada com sucesso!", "success")
            return redirect(url_for("home"))
        except Exception as e:
            return f"Erro no banco de dados: {e}"
    return render_template("create.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
