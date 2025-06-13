# routes.py

from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
from models import db  # Importa o db do __init__.py
from models.post import Post
from models.user import User
from werkzeug.utils import secure_filename
import json


def register_routes(app):
    # Rota para a Home
    @app.route('/')
    def home():
        # Verifica se o usuário está logado
        user = User.query.get(session.get('user_id'))
        if user:
            posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).limit(5).all()
        else:
            posts = []
        return render_template('home.html', user=user, posts=posts)

    # Rota para o Login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Buscar o usuário no banco de dados pelo username
            user = User.query.filter_by(username=username).first()

            # Verificar se o usuário existe e se a senha corresponde
            if user and user.password == password:  # Comparar senha diretamente (em texto simples)
                session['user_id'] = user.id  # Inicia a sessão com o ID do usuário
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Usuário ou senha inválidos', 'danger')

        return render_template('login.html')

    # Rota para o Cadastro
    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']  # Senha em texto simples
            phone = request.form['phone']

            # Cria o novo usuário sem criptografar a senha
            new_user = User(username=username, email=email, password=password, phone=phone)
            db.session.add(new_user)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Agora faça o login.', 'success')
            return redirect(url_for('login'))

        return render_template('cadastro.html')

    # Rota para Logout
    @app.route('/logout')
    def logout():
        session.pop('user_id', None)  # Remove o ID do usuário da sessão
        return redirect(url_for('home'))

    @app.route('/posts')
    def listar_posts():
        # Lista todos os posts ordenados pela data de criação (do mais recente para o mais antigo)
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template('listar_posts.html', posts=posts)

    @app.route('/post/new', methods=['GET', 'POST'])
    def novo_post():
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']

            # Recuperar o ID do usuário da sessão
            user_id = session.get('user_id')

            if user_id:
                user = User.query.get(user_id)  # Recupera o usuário logado

                new_post = Post(title=title, content=content, user_id=user.id)
                db.session.add(new_post)
                db.session.commit()
                flash('Post criado com sucesso!', 'success')
                return redirect(url_for('listar_posts'))
            else:
                flash('Você precisa estar logado para criar um post', 'danger')
                return redirect(url_for('login'))

        # Passa o usuário logado para o template
        user = User.query.get(session.get('user_id'))  # Se o usuário estiver logado
        return render_template('novo_post.html', user=user)

    @app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
    def editar_post(id):
        post = Post.query.get(id)

        # Salvar a URL anterior na sessão
        if request.method == 'GET':
            session['previous_url'] = request.referrer

        if post is None:
            flash('Post não encontrado!', 'danger')
            return redirect(session.get('previous_url', url_for('home')))  # Redireciona para a URL anterior

        if request.method == 'POST':
            post.title = request.form['title']
            post.content = request.form['content']
            db.session.commit()
            flash('Post atualizado com sucesso!', 'success')
            return redirect(session.get('previous_url', url_for('home')))  # Redireciona para a URL anterior

        return render_template('editar_post.html', post=post)

    @app.route('/post/delete/<int:id>', methods=['POST'])
    def excluir_post(id):
        post = Post.query.get(id)

        # Salvar a URL anterior na sessão
        session['previous_url'] = request.referrer

        if post:
            db.session.delete(post)
            db.session.commit()
            flash('Post excluído com sucesso!', 'success')
        else:
            flash('Post não encontrado!', 'danger')

        return redirect(session.get('previous_url', url_for('home')))  # Redireciona para a URL anterior

    @app.route('/post/<int:id>', methods=['GET'])
    def visualizar_post(id):
        post = Post.query.get(id)  # Busca o post pelo id

        if post is None:
            flash('Post não encontrado!', 'danger')
            return redirect(url_for('home'))  # Redireciona para a home caso não encontre o post

        return render_template('visualizar_post.html', post=post)

    @app.route('/exportar_posts')
    def exportar_posts():
        # Pega todos os posts do banco de dados
        posts = Post.query.all()

        # Lista de posts em formato dicionário
        posts_list = []

        for post in posts:
            posts_list.append({
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'created_at': post.created_at.isoformat(),  # Converte datetime para string
                'user_id': post.user_id
            })

        # Caminho para salvar o arquivo JSON temporariamente
        file_path = 'posts.json'

        # Salva os posts no arquivo JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(posts_list, f, ensure_ascii=False, indent=4)

        # Retorna o arquivo JSON para o download
        return send_file(file_path, as_attachment=True, download_name='posts.json', mimetype='application/json')

    @app.route('/importar_posts', methods=['GET', 'POST'])
    def importar_posts():
        if request.method == 'POST':
            # Verifica se o arquivo foi enviado
            if 'file' not in request.files:
                flash('Nenhum arquivo foi enviado!', 'danger')
                return redirect(url_for('home'))

            file = request.files['file']

            # Verifica se o arquivo tem um nome
            if file.filename == '':
                flash('Nenhum arquivo selecionado!', 'danger')
                return redirect(url_for('home'))

            # Salva o arquivo temporariamente
            if file and file.filename.endswith('.json'):
                filename = secure_filename(file.filename)
                file.save(f'./uploads/{filename}')  # Salva o arquivo em uma pasta 'uploads'

                # Abre o arquivo e lê os dados
                with open(f'./uploads/{filename}', 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Recuperar o ID do usuário da sessão
                    user_id = session.get('user_id')

                    if not user_id:
                        flash('Você precisa estar logado para importar posts!', 'danger')
                        return redirect(url_for('login'))  # Redireciona para a página de login


                    for post_data in data:
                        # Cria um novo post para cada item do arquivo JSON
                        post = Post(
                            title=post_data['title'],
                            content=post_data['content'],
                            user_id=user_id
                        )
                        db.session.add(post)

                    db.session.commit()  # Salva todos os posts no banco

                flash('Posts importados com sucesso!', 'success')
                return redirect(url_for('home'))

            flash('Arquivo inválido! Envie um arquivo JSON.', 'danger')
            return redirect(url_for('home'))

        # Se o método for GET, apenas renderiza o formulário
        return render_template('importar_posts.html')

    @app.route('/sobre')
    def sobre():
        return render_template('sobre.html')


