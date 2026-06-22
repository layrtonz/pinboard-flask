# Rotas do site
from flask import render_template, url_for, redirect
from FakePinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from FakePinterest.models import Usuario, Foto
from FakePinterest.forms import FormLogin, FormCriarConta, FormFoto
import os
from werkzeug.utils import secure_filename

@app.route("/", methods=["GET", "POST"])
def homepage():
    form_Login = FormLogin()
    if form_Login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_Login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_Login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("home.html", form=form_Login)


@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    formcriarconta = FormCriarConta()

    if formcriarconta.validate_on_submit():
        print("FORMULÁRIO VALIDOU")

        senha = bcrypt.generate_password_hash(formcriarconta.senha.data)

        usuario = Usuario(
            username=formcriarconta.username.data,
            senha=senha,
            email=formcriarconta.email.data
        )

        database.session.add(usuario)
        database.session.commit()

        login_user(usuario, remember=True)

        return redirect(url_for("perfil", id_usuario=usuario.id))

    print(formcriarconta.errors)

    return render_template("criarconta.html", form=formcriarconta)

@app.route("/perfil/<id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)
            # salvar o arquivo na pasta foto_posts
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
            app.config["UPLOAD_FOLDER"], nome_seguro)
            arquivo.save(caminho)
            # registrar arquivo no banco de dados
            foto = Foto(imagem=nome_seguro, id_usuario=current_user.id)
            database.session.add(foto)
            database.session.commit()
        return render_template("perfil.html", usuario=current_user, form=form_foto)
    else:
        usuario = Usuario.query.get(int(id_usuario))
    return render_template("perfil.html", usuario=usuario, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao.desc()).all()
    usuarios = Usuario.query.all()
    return render_template("feed.html", fotos=fotos, usuarios=usuarios)