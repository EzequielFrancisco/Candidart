from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "hddvdblu-raylesardisc"

@app.route("/")
def home():
    try:
        conn = sqlite3.connect('candidart.db')
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users')
        users = cursor.fetchall()

        return render_template("index.html", session=session, users=users)
     
    except Exception as e:
        return f"Erro algures no banco de dados {e}"
    

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = sqlite3.connect('candidart.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_name = ? AND senha = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            # Aqui poderias validar o username/password com o DB
            if user:
                session['username'] = user[1]
                session['company'] = user[3]
                flash(f"Bem-vindo, {username}!", "success")
                return redirect(url_for('home'))
            else:
                flash("Preencha todos os campos com os dados correctos!", "error")
                return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash("Ocorreu um erro na base de dados: {e}")
            return render_template('login.html')

    # GET request: renderiza formulário HTML simples
    return render_template('login.html')

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['username']
        senha = request.form['password']
        company = request.form['company']
        try:
            conn = sqlite3.connect('candidart.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_name, senha, company)
                VALUES (?, ?, ?)
            """, (user_name, senha, company))

            conn.commit()
            flash("Registo enviada com sucesso!", "success")
            return redirect(url_for("login"))
            
        except Exception as e:
            return f"Erro no banco de dados: {e}"

        finally:
            conn.close()
        
    return render_template('register.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash("Sessão terminada!", "info")
    return redirect(url_for('home'))


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

        if not cv:
            flash("O currículo é obrigatório.", "error")
            return redirect(url_for("home"))

        os.makedirs("static/cv", exist_ok=True)
        cv.save(f"static/cv/{cv.filename}")

        company_name = request.form['empresa']
        post = request.form['post']
        resumo = request.form['resumo']

        try:
            conn = sqlite3.connect('candidart.db')
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidacy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cv TEXT,
                company_name TEXT,
                resumo TEXT
            )
            """)

            cursor.execute("""
                INSERT INTO candidacy (cv, company_name, resumo)
                VALUES (?, ?, ?)
            """, (cv.filename, company_name, resumo))

            conn.commit()
            flash("Candidatura enviada com sucesso!", "success")
            return redirect(url_for("home"))
            
        except Exception as e:
            return f"Erro no banco de dados: {e}"

        finally:
            conn.close()

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
    
@app.route("/date")
def date():
    if 'company' in session:
        company_name = session['company']

        try:
            conn = sqlite3.connect('candidart.db')
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM candidacy WHERE company_name = ?', (company_name,))
            dates = cursor.fetchall()
            
            return render_template("date.html", dates=dates)
        
        except Exception as e:
            return f"Erro no banco de dados: {e}"

    else:
        flash("Método não permitido", "error")
        return redirect(url_for('home'))


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
    app.run(debug=True, use_reloader=True)
