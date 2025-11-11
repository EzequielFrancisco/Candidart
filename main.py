from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "hddvdblu-raylesardisc"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return"login"

@app.route("/candidacy")
def candidacy():
    return render_template("candidacy.html")

@app.route("/apply/<empresa>/<post>")
def apply(empresa, post):
    return render_template("apply.html",empresa=empresa,post=post)

@app.route("/insert", methods=['POST'])
def insert():

    if request.method == 'POST':
        cv = request.files.get('curriculo')

        if cv:
            # Garante que a pasta 'img' existe
            os.makedirs("static/cv", exist_ok=True)
            cv.save(f"static/cv/{cv.filename}")
            logo_name = cv.filename
        else:
            flash("O Curriculo e Obrigatorio")
            return render_template('home.html')
        
        company_name = request.form['empresa']
        post = request.form['post']
        resumo = request.form['resumo']

        try:
            conn = sqlite3.connect('candidart.db')
            cursor = conn.cursor()

            # Cria a tabela se não existir
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidacy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cv TEXT,
                company_name TEXT,
                resumo TEXT,
            )
            """)

            # Inserir dados de forma segura
            cursor.execute("""
                INSERT INTO vacancies 
                (cv, company_name, resumo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cv, company_name, resumo))

            conn.commit()

            flash("Vaga criada com sucesso!", "success")  # tipo: success, error, warning, info
            return redirect(url_for("home"))
            

        except Exception as e:
                return f"Erro no banco de dados: {e}"

        finally:
                conn.close()

    return render_template("home.html")
        

@app.route("/vacancies")
def vacancies():
    try:
        conn = sqlite3.connect('candidart.db')
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vacancies')
        vagas = cursor.fetchall()
        return render_template("vacancies.html",vagas=vagas)
     
    except Exception as e:
        return "Erro algures no banco de dados"
    
@app.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        logo = request.files.get('logo')

        if logo:
            # Garante que a pasta 'img' existe
            os.makedirs("static/img", exist_ok=True)
            logo.save(f"static/img/{logo.filename}")
            logo_name = logo.filename
        else:
            logo_name = "padrao.png"

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
            conn = sqlite3.connect('candidart.db')
            cursor = conn.cursor()

            # Cria a tabela se não existir
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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

            # Inserir dados de forma segura
            cursor.execute("""
                INSERT INTO vacancies 
                (logo, company_name, job_title, job_description, location, job_type, salary_min, salary_max, currency, contact_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (logo_name, company_name, job_title, job_description, location, job_type, salary_min, salary_max, currency, contact_email))

            conn.commit()

            flash("Vaga criada com sucesso!", "success")  # tipo: success, error, warning, info
            return redirect(url_for("home"))
            

        except Exception as e:
            return f"Erro no banco de dados: {e}"

        finally:
            conn.close()

    return render_template("create.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
