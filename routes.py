# Rotas do site
from flask import render_template, url_for, redirect
from FakePinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from FakePinterest.models import Usuario, Foto
from FakePinterest.forms import FormLogin, FormCriarConta, FormFoto, FormEditarPerfil
import os
from werkzeug.utils import secure_filename
from flask import render_template, url_for, redirect, request

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

            caminho = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                app.config["UPLOAD_FOLDER"],
                nome_seguro
            )

            arquivo.save(caminho)

            foto = Foto(imagem=nome_seguro, id_usuario=current_user.id)
            database.session.add(foto)
            database.session.commit()

            return redirect(url_for("perfil", id_usuario=current_user.id))

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

@app.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data

        if form.foto_perfil.data:
            arquivo = form.foto_perfil.data
            nome_seguro = secure_filename(arquivo.filename)

            caminho = os.path.join(
            app.root_path,
            'static/fotos_perfil',
            nome_seguro
            )

            arquivo.save(caminho)
            current_user.foto_perfil = nome_seguro

        database.session.commit()

        return redirect(url_for('perfil', id_usuario=current_user.id))

    elif request.method == 'GET':
            form.username.data = current_user.username
            form.bio.data = current_user.bio

    return render_template('editar_perfil.html', form=form)

@app.route("/excluir-foto/<int:id_foto>", methods=["POST"])
@login_required
def excluir_foto(id_foto):
    foto = Foto.query.get_or_404(id_foto)

    if foto.id_usuario != current_user.id:
        return redirect(url_for("perfil", id_usuario=current_user.id))

    caminho_foto = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        app.config["UPLOAD_FOLDER"],
        foto.imagem
    )

    if os.path.exists(caminho_foto):
        os.remove(caminho_foto)

    database.session.delete(foto)
    database.session.commit()

    return redirect(url_for("perfil", id_usuario=current_user.id))