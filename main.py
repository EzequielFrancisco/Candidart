from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from supabase import create_client

app = Flask(__name__)
app.secret_key = "hddvdblu-raylesardisc"

# --- CONFIGURAÇÃO SUPABASE ---
SUPABASE_URL = "https://jpcbillqgopqcidgnrws.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpwY2JpbGxxZ29wcWNpZGducndzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzM4OTg4NSwiZXhwIjoyMDc4OTY1ODg1fQ.55Th3O3Ns52p2VaQYgmeLD-KmZfi8CY1f9P-qteM0tU"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- HOME ---
@app.route("/")
def home():
    try:
        users_resp = supabase.table("users").select("id, user_name, company").execute()
        users = users_resp.data
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
            resp = supabase.table("users").select("*").eq("user_name", username).eq("senha", password).execute()
            user = resp.data[0] if resp.data else None
            if user:
                session['username'] = user['user_name']
                session['company'] = user['company']
                flash(f"Bem-vindo, {username}!", "success")
                return redirect(url_for('home'))
            flash("Usuário ou senha incorretos!", "error")
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
            supabase.table("users").insert({
                "user_name": user_name,
                "senha": senha,
                "company": company
            }).execute()
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
    cv_path = f"static/cv/{cv.filename}"
    cv.save(cv_path)

    company_name = request.form['empresa']
    post = request.form['post']
    resumo = request.form['resumo']

    try:
        supabase.table("candidacy").insert({
            "cv": cv.filename,
            "company_name": company_name,
            "resumo": resumo
        }).execute()
        flash("Candidatura enviada com sucesso!", "success")
        return redirect(url_for("home"))
    except Exception as e:
        return f"Erro no banco de dados: {e}"

# --- VACANCIES ---
@app.route("/vacancies")
def vacancies():
    try:
        resp = supabase.table("vacancies").select("*").execute()
        vagas = resp.data
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
        resp = supabase.table("candidacy").select("*").eq("company_name", company_name).execute()
        dates = resp.data
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
            supabase.table("vacancies").insert({
                "logo": logo_name,
                "company_name": company_name,
                "job_title": job_title,
                "job_description": job_description,
                "location": location,
                "job_type": job_type,
                "salary_min": float(salary_min),
                "salary_max": float(salary_max),
                "currency": currency,
                "contact_email": contact_email
            }).execute()
            flash("Vaga criada com sucesso!", "success")
            return redirect(url_for("home"))
        except Exception as e:
            return f"Erro no banco de dados: {e}"
    return render_template("create.html")

# --- ABOUT ---
@app.route("/about")
def about():
    return render_template("about.html")

# --- ERROR 404 ---
@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
