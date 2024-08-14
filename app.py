from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask import redirect
from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)
import hashlib




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@127.0.0.1:3306/meubanco' #conex'ao com o banco mysql
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://renantavares123:toledo22@renantavares123.mysql.pythonanywhere-services.com/renantavares123$meubanco'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) 

app.secret_key = '12345'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(db.Model):
	id = db.Column('usu_id', db.Integer, primary_key = True)
	nome = db.Column('usu_nome', db.String(256))
	email = db.Column('usu_email', db.String(256))
	senha = db.Column('usu_senha', db.String(256))
	end = db.Column('usu_endereco', db.String(256))

	def __init__(self, nome, email, senha, end):
		self.nome = nome
		self.email = email
		self.senha = senha
		self.end = end

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False
	
	def get_id(self):
		return str(self.id)



class Categoria(db.Model):
    
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))

    def __init__ (self, nome):
        self.nome = nome
	

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anc_id', db.Integer, primary_key=True)
    nome = db.Column('anc_nome', db.String(256))
    desc = db.Column('anc_desc', db.String(256))
    qtd = db.Column('anc_qtd', db.Integer)
    preco = db.Column('anc_preco', db.Float)
    cat_id = db.Column('cat_id',db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id',db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id

#Favoritos
class Favorito(db.Model):
    __tablename__ = "favorito"
    id = db.Column('fav_id', db.Integer, primary_key=True)
    anc_id = db.Column('anc_id',db.Integer, db.ForeignKey("anuncio.anc_id"))
    usu_id = db.Column('usu_id',db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, anc_id, usu_id):
        self.anc_id = anc_id
        self.usu_id = usu_id

#Pergunta
class Pergunta(db.Model):
    __tablename__ = "pergunta"
    id = db.Column('per_id', db.Integer, primary_key=True)
    desc = db.Column('per_desc', db.String(256))
    resp = db.Column('per_resp', db.String(256))
    anc_id = db.Column('anc_id',db.Integer, db.ForeignKey("anuncio.anc_id"))
    usu_id = db.Column('usu_id',db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, desc, resp, anc_id, usu_id):
        self.desc = desc
        self.resp = resp
        self.anc_id = anc_id
        self.usu_id = usu_id

#Compra
class Compra(db.Model):
    __tablename__ = "compra"
    id = db.Column('com_id', db.Integer, primary_key=True)
    
    desc = db.Column('com_desc', db.Float)
    qtd = db.Column('com_qtd', db.Integer)
    total = db.Column('com_total', db.Float)
    anc_id = db.Column('anc_id',db.Integer, db.ForeignKey("anuncio.anc_id"))
    usu_id = db.Column('usu_id',db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, desc, qtd, total, anc_id, usu_id):
        
        self.desc = desc
        self.qtd = qtd
        self.total = total
        self.anc_id = anc_id
        self.usu_id = usu_id


@app.errorhandler(404)
def paginanaoencontrada(error):
	return render_template('paginanaoencontrada.html')

@login_manager.user_loader
def load_user(id):
	return Usuario.query.get(id)

@app.route('/')
@login_required
def index():
	#db.create_all() #Python ANywhere
	return render_template('index.html')

@app.route("/login", methods=['GET','POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')
		passwd = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
		

		user = Usuario.query.filter_by(email=email, senha=passwd).first()

		if user:
			login_user(user)
			return redirect(url_for('index'))
		
		else:
			return redirect(url_for('login'))
	
	return render_template('login.html')

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('index'))
#-------------------------------------------
# -----------------------------------
####Usuário####
@app.route("/cad/usuario")
@login_required
def cadusuario():
	return render_template('usuario.html',usuarios = Usuario.query.all(), titulo="Usuário")

@app.route("/usuario/criar", methods=['POST'] )
@login_required
def criarusuario():
	hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest() #senha/passwd
	usuario = Usuario(request.form.get('user'), request.form.get('email'), hash, request.form.get('end'))
	db.session.add(usuario)
	db.session.commit()
	return redirect(url_for('cadusuario'))

@app.route("/usuario/buscar/<int:id>")
def buscausuario(id):
	usuario = Usuario.query.get(id)
	return usuario.nome

@app.route("/usuario/editar/<int:id>", methods=['GET','POST'])
@login_required
def editarusuario(id):
	usuario = Usuario.query.get(id)
	if request.method == 'POST':
		usuario.nome = request.form.get('user')
		usuario.email = request.form.get('email')
		usuario.senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
		usuario.end = request.form.get('end')
	
		db.session.add(usuario)
		db.session.commit()
		return redirect(url_for('cadusuario'))
	
	return render_template('ausuario.html', usuario = usuario, titulo="Usuário")

@app.route("/usuario/deletar/<int:id>")
@login_required
def deletarusuario(id):
	usuario = Usuario.query.get(id)
	db.session.delete(usuario)
	db.session.commit()
	return redirect(url_for('cadusuario'))


#------------------------------------------------------------------------------
####Anúncios####
@app.route("/cad/anuncio")
@login_required
def anuncio():
	return render_template('anuncio.html', anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), usuarios = Usuario.query.all(), titulo="Anuncio")

@app.route("/anuncio/criar", methods=['POST'] )
@login_required
def criaranuncio():
	anuncio = Anuncio(request.form.get('nome'), request.form.get('desc'),request.form.get('qtd'),request.form.get('preco'),request.form.get('cat'), request.form.get('uso'))
	db.session.add(anuncio)
	db.session.commit()
	return redirect(url_for('anuncio'))

@app.route("/anuncio/buscar/<int:id>")
def buscaanuncio(id):
	anuncio = Anuncio.query.get(id)
	return anuncio.nome

@app.route("/anuncio/deletar/<int:id>")
@login_required
def deletaranuncio(id):
	anuncio = Anuncio.query.get(id)
	db.session.delete(anuncio)
	db.session.commit()
	return redirect(url_for('anuncio'))

@app.route("/anuncio/editar/<int:id>", methods=['GET','POST'])
@login_required
def editaranuncio(id):
	anuncio = Anuncio.query.get(id)
	if request.method == 'POST':
		anuncio.nome = request.form.get('nome')
		anuncio.desc = request.form.get('desc')
		anuncio.qtd = request.form.get('qtd')
		anuncio.preco = request.form.get('preco')
		anuncio.cat_id = request.form.get('cat')
		anuncio.usu_id = request.form.get('uso')
	
		db.session.add(anuncio)
		db.session.commit()
		return redirect(url_for('anuncio'))
	
	return render_template('aanuncio.html', anuncio = anuncio, categorias = Categoria.query.all(), usuarios = Usuario.query.all(), titulo="Anúncio")
#------------------------------------------------------------------------------
####Perguntas####
@app.route("/cad/pergunta")
def pergunta():
	return render_template('pergunta.html',perguntas = Pergunta.query.all(), anuncios = Anuncio.query.all(), usuarios = Usuario.query.all(), titulo="Perguntas")

@app.route("/pergunta/criar", methods=['POST'] )
@login_required
def criarpergunta():
	pergunta = Pergunta(request.form.get('desc'),request.form.get('resp'), request.form.get('anc'), request.form.get('uso'))
	db.session.add(pergunta)
	db.session.commit()
	return redirect(url_for('pergunta'))

@app.route("/pergunta/deletar/<int:id>")
@login_required
def deletarpergunta(id):
	pergunta = Pergunta.query.get(id)
	db.session.delete(pergunta)
	db.session.commit()
	return redirect(url_for('pergunta'))

@app.route("/pergunta/editar/<int:id>", methods=['GET','POST'])
@login_required
def editarpergunta(id):
	pergunta = Pergunta.query.get(id)
	if request.method == 'POST':
		
		pergunta.desc = request.form.get('desc')
		pergunta.resp = request.form.get('resp')
		pergunta.anc_id = request.form.get('anc')
		pergunta.usu_id = request.form.get('uso')
	
		db.session.add(pergunta)
		db.session.commit()
		return redirect(url_for('pergunta'))
	
	return render_template('apergunta.html', pergunta = pergunta, anuncios = Anuncio.query.all(), usuarios = Usuario.query.all(), titulo="Pergunta")
#------------------------------------------------------------------------------
####Compra####
@app.route("/cad/compra")
def compra():
	return render_template('compra.html',compras = Compra.query.all(), anuncios = Anuncio.query.all(), usuarios = Usuario.query.all(), titulo="Compras")

@app.route("/compra/criar", methods=['POST'] )
@login_required
def criarcompra():
	compra = Compra(request.form.get('desc'), request.form.get('qtd'), request.form.get('total'), request.form.get('anc'), request.form.get('uso'))
	db.session.add(compra)
	db.session.commit()
	return redirect(url_for('compra'))

@app.route("/compra/deletar/<int:id>")
@login_required
def deletarcompra(id):
	compra = Compra.query.get(id)
	db.session.delete(compra)
	db.session.commit()
	return redirect(url_for('compra'))

@app.route("/compra/editar/<int:id>", methods=['GET','POST'])
@login_required
def editarcompra(id):
	compra = Compra.query.get(id)
	if request.method == 'POST':
		
		compra.qtd = request.form.get('qtd')
		compra.desc = request.form.get('desc')
		compra.anc_id = request.form.get('anc')
		compra.usu_id = request.form.get('uso')
	
		db.session.add(compra)
		db.session.commit()
		return redirect(url_for('compra'))
	
	return render_template('acompra.html', compra = compra, anuncios = Anuncio.query.all(), usuarios = Usuario.query.all(), titulo="Compra")
#------------------------------------------------------------------------------
####Anúncios Favoritos####
@app.route("/cad/favorito")
@login_required
def favorito():
	return render_template('favorito.html',favoritos = Favorito.query.all(), anuncios = Anuncio.query.all(), usuarios = Usuario.query.all(), titulo="Favoritos")

@app.route("/favorito/criar", methods=['POST'] )
@login_required
def criarfavorito():
	favorito = Favorito(request.form.get('anc'), request.form.get('uso'))
	db.session.add(favorito)
	db.session.commit()
	return redirect(url_for('favorito'))

@app.route("/favorito/deletar/<int:id>")
@login_required
def deletarfavorito(id):
	favorito = Favorito.query.get(id)
	db.session.delete(favorito)
	db.session.commit()
	return redirect(url_for('favorito'))

@app.route("/favorito/editar/<int:id>", methods=['GET','POST'])
@login_required
def editarfavorito(id):
	favorito = Favorito.query.get(id)
	if request.method == 'POST':
	
		favorito.anc_id = request.form.get('anc')
		favorito.usu_id = request.form.get('uso')
	
		db.session.add(favorito)
		db.session.commit()
		return redirect(url_for('favorito'))
	
	return render_template('afavorito.html', favorito = favorito, anuncios = Anuncio.query.all(), usuarios = Usuario.query.all(), titulo="Favorito")

#------------------------------------------------------------------------------
####Categoria####
@app.route("/config/categoria")
@login_required
def categoria():
	return render_template('categoria.html',categorias = Categoria.query.all(), titulo="Categoria")

@app.route("/categoria/criar", methods=['POST'] )
@login_required
def criarcategoria():
	categoria = Categoria(request.form.get('nome'))
	db.session.add(categoria)
	db.session.commit()
	return redirect(url_for('categoria'))

@app.route("/categoria/buscar/<int:id>")
def buscarcategoria(id):
	categoria = Categoria.query.get(id)
	return categoria.nome

@app.route("/categoria/deletar/<int:id>")
@login_required
def deletarcategoria(id):
	categoria = Categoria.query.get(id)
	db.session.delete(categoria)
	db.session.commit()
	return redirect(url_for('categoria'))

@app.route("/categoria/editar/<int:id>", methods=['GET','POST'])
@login_required
def editarcategoria(id):
	categoria = Categoria.query.get(id)
	#Apesar das configurações estarem certas na acategoria.html (bootstrap funcionando), ao editar a página, o bootstrap não é pego
	if request.method == 'POST':
		categoria.nome = request.form.get('nome')
		db.session.add(categoria)
		db.session.commit()
		return redirect(url_for('categoria'))
	
	return render_template('acategoria.html', categoria = categoria, titulo="Categoria")
#------------------------------------------------------------------------------
####Relatório Vendas####
@app.route("/relatorios/vendas")
def relVendas():
	return render_template('relVendas.html', titulo="Relatório de Vendas")

#------------------------------------------------------------------------------
####Relatório Compras####
@app.route("/relatorios/compras")
def relCompras():
	return render_template('relCompras.html', titulo="Relatório de Compras")


#app.py
if __name__ == 'app': 
	
	db.create_all()
	#app.run() #Python Anywhere