# Rotas do site
from flask import render_template, url_for, redirect
from FakePinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from FakePinterest.models import Usuario, Foto
from FakePinterest.forms import FormLogin, FormCriarConta

@app.route("/", methods=["GET", "POST"])
def homepage():
    form_Login = FormLogin()
    if form_Login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_Login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_Login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", usuario=usuario.username))
    return render_template("home.html", form=form_Login)


@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    formcriarconta = FormCriarConta()
    if formcriarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(formcriarconta.senha.data)
        usuario = Usuario(username=formcriarconta.username.data,
                          senha=senha, 
                          email=formcriarconta.email.data )
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", usuario=usuario.username))
    return render_template("criarconta.html", form=formcriarconta)

@app.route("/perfil/<usuario>")
@login_required
def perfil(usuario):
    return render_template("perfil.html", usuario=usuario)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))
