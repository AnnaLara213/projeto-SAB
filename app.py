from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
import os
from flask import Flask, send_from_directory

# Criar a aplicação Flask
app = Flask(__name__)

# Habilitar CORS (se necessário)
CORS(app)

# Configuração do SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if os.getenv('FLASK_ENV') == 'testing':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Happyland1990@localhost:5432/sab_test'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Happyland1990@localhost:5432/postgres'

# Instanciar o banco de dados
app.config['SECRET_KEY'] = 'sua_chave_secreta'
db = SQLAlchemy(app)

# Caminho absoluto para a pasta onde os arquivos de front-end estão localizados
FRONTEND_DIR = r"C:\Users\annal\OneDrive\Documentos\projeto-SAB\SAB_front-end\IHC_(corrigido)\IHC\IHC\IHC"

# Modelo User
class User(db.Model):
    __tablename__ = 'users'
    idusuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(14), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        return {
            "idusuario": self.idusuario,
            "email": self.email,
            "senha": self.senha,
            "telefone": self.telefone
        }
class Unidade(db.Model):
    __tablename__ = 'unidade'

    idunidade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    logradouro = db.Column(db.String(70), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    complemento = db.Column(db.String(70))
    estado = db.Column(db.String(2), nullable=False)
    cidade = db.Column(db.String(70), nullable=False)
    bairro = db.Column(db.String(70), nullable=False)

    def __repr__(self):
        return f"<Unidade {self.nome}>"

    def to_dict(self):
        return {
            'idunidade': self.idunidade,
            'nome': self.nome,
            'cep': self.cep,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'complemento': self.complemento,
            'estado': self.estado,
            'cidade': self.cidade,
            'bairro': self.bairro
        }

class Setor(db.Model):
    __tablename__ = 'setor'

    idsetor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    unidade = db.Column(db.Integer, db.ForeignKey('unidade.idunidade'), nullable=False)

    unidade_rel = db.relationship('Unidade', backref=db.backref('setores', lazy=True))

    def __repr__(self):
        return f"<Setor {self.nome}>"

    def to_dict(self):
        return {
            'idsetor': self.idsetor,
            'nome': self.nome,
            'unidade': self.unidade_rel.to_dict() if self.unidade_rel else None
        }

class Profissional(db.Model):
    __tablename__ = 'profissional'

    idprofissional = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    datanascimento = db.Column('datanascimento', db.Date, nullable=False) 
    matricula = db.Column(db.String(20), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    usuario = db.Column(db.Integer, db.ForeignKey('users.idusuario'), nullable=False)
    setor = db.Column(db.Integer, db.ForeignKey('setor.idsetor'), nullable=False)

    usuario_rel = db.relationship('User', backref=db.backref('profissionais', lazy=True))
    setor_rel = db.relationship('Setor', backref=db.backref('profissionais', lazy=True))

    def __repr__(self):
        return f"<Profissional {self.nome}>"

    def to_dict(self):
        return {
            'idprofissional': self.idprofissional,
            'nome': self.nome,
            'cpf': self.cpf,
            'datanascimento': self.datanascimento,
            'matricula': self.matricula,
            'cargo': self.cargo,
            'usuario': self.usuario_rel.to_dict() if self.usuario_rel else None,
            'setor': self.setor_rel.to_dict() if self.setor_rel else None
        }

class Estoque(db.Model):
    __tablename__ = 'estoque'

    idestoque = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantidade = db.Column(db.Integer, nullable=False)
    unidade = db.Column(db.Integer, db.ForeignKey('unidade.idunidade'), nullable=False)

    unidade_rel = db.relationship('Unidade', backref=db.backref('estoques', lazy=True))

    def __repr__(self):
        return f"<Estoque {self.idestoque}>"

    def to_dict(self):
        return {
            'idestoque': self.idestoque,
            'quantidade': self.quantidade,
            'unidade': self.unidade_rel.to_dict() if self.unidade_rel else None
        }


class Recurso(db.Model):
    __tablename__ = 'recurso'

    idrecurso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(45))
    tamanho = db.Column(db.String(255))
    descricao = db.Column(db.String(1000))
    estoque = db.Column(db.Integer, db.ForeignKey('estoque.idestoque'), nullable=False)

    estoque_rel = db.relationship('Estoque', backref=db.backref('recursos', lazy=True))

    def __repr__(self):
        return f"<Recurso {self.idrecurso}>"

    def to_dict(self):
        return {
            'idrecurso': self.idrecurso,
            'nome': self.nome,
            'categoria': self.categoria,
            'marca': self.marca,
            'tamanho': self.tamanho,
            'descricao': self.descricao,
            'estoque': self.estoque_rel.to_dict() if self.estoque_rel else None
        }



class Doacao(db.Model):
    __tablename__ = 'doacao'

    iddoacao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datadoacao = db.Column('datadoacao', db.DateTime, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    recurso = db.Column(db.Integer, db.ForeignKey('recurso.idrecurso'), nullable=False)
    unidade = db.Column(db.Integer, db.ForeignKey('unidade.idunidade'), nullable=False)
    responsavel = db.Column(db.Integer, db.ForeignKey('profissional.idprofissional'), nullable=False)

    # Relacionamentos
    recurso_rel = db.relationship('Recurso', backref=db.backref('doacoes', lazy=True))
    unidade_rel = db.relationship('Unidade', backref=db.backref('doacoes', lazy=True))
    responsavel_rel = db.relationship('Profissional', backref=db.backref('doacoes', lazy=True))

    def to_dict(self):
        return {
            'iddoacao': self.iddoacao,
            'datadoacao': self.datadoacao,
            'quantidade': self.quantidade,
            'recurso': self.recurso_rel.to_dict() if self.recurso_rel else None,
            'unidade': self.unidade_rel.to_dict() if self.unidade_rel else None,
            'responsavel': self.responsavel_rel.to_dict() if self.responsavel_rel else None
        }


class Emprestimo(db.Model):
    __tablename__ = 'emprestimo'

    idemprestimo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dataemprestimo = db.Column(db.DateTime, nullable=False)
    responsavel = db.Column(db.Integer, db.ForeignKey('profissional.idprofissional'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    recurso = db.Column(db.Integer, db.ForeignKey('recurso.idrecurso'), nullable=False)
    unidade = db.Column(db.Integer, db.ForeignKey('unidade.idunidade'), nullable=False)

    # Relacionamentos
    recurso_rel = db.relationship('Recurso', backref=db.backref('emprestimos', lazy=True))
    unidade_rel = db.relationship('Unidade', backref=db.backref('emprestimos', lazy=True))
    responsavel_rel = db.relationship('Profissional', backref=db.backref('emprestimos', lazy=True))

    def __repr__(self):
        return f"<Emprestimo {self.idemprestimo}>"

    def to_dict(self):
        return {
            'idemprestimo': self.idemprestimo,
            'dataemprestimo': self.dataemprestimo,
            'responsavel': self.responsavel_rel.to_dict() if self.responsavel_rel else None,
            'quantidade': self.quantidade,
            'recurso': self.recurso_rel.to_dict() if self.recurso_rel else None,
            'unidade': self.unidade_rel.to_dict() if self.unidade_rel else None,
        }


class Devolucao(db.Model):
    __tablename__ = 'devolucao'

    iddevolucao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datadevolucao = db.Column('datadevolucao', db.DateTime, nullable=False)  # TIMESTAMP no banco
    recurso = db.Column(db.Integer, db.ForeignKey('recurso.idrecurso'), nullable=False)
    unidade = db.Column(db.Integer, db.ForeignKey('unidade.idunidade'), nullable=False)
    responsaveldevolucao = db.Column(db.Integer, db.ForeignKey('profissional.idprofissional'), nullable=False)

    # Relacionamentos
    recurso_rel = db.relationship('Recurso', backref=db.backref('devolucoes', lazy=True))
    unidade_rel = db.relationship('Unidade', backref=db.backref('devolucoes', lazy=True))
    responsavel_rel = db.relationship('Profissional', backref=db.backref('devolucoes', lazy=True))

    def __repr__(self):
        return f"<Devolucao {self.iddevolucao}>"

    def to_dict(self):
        return {
            'iddevolucao': self.iddevolucao,
            'datadevolucao': self.datadevolucao.isoformat() if self.datadevolucao else None,
            'recurso': self.recurso_rel.to_dict() if self.recurso_rel else None,
            'unidade': self.unidade_rel.to_dict() if self.unidade_rel else None,
            'responsaveldevolucao': self.responsavel_rel.to_dict() if self.responsavel_rel else None
        }




# Testar a conexão com o banco de dados
@app.route('/test_connection')
def test_connection():
    try:
        # Verifica se o banco de dados está funcionando e se há dados
        user = User.query.first()  # Verificando o primeiro usuário
        if user:
            return jsonify(message=f"Conexão bem-sucedida! Primeiro usuário encontrado: {user.email}")
        else:
            return jsonify(message="Conexão bem-sucedida, mas nenhum usuário encontrado.")
    except Exception as e:
        return jsonify(message=f"Erro ao acessar o banco de dados: {str(e)}")

# Rota para listar todos os usuários
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# Rota para listar um único usuário pelo ID
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({'message': 'User not found'}), 404

# Rota para adicionar um novo usuário
@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400
    
    new_user = User(
        email=data['email'],
        senha=generate_password_hash(data['senha']),
        telefone=data['telefone']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

# Rota para atualizar um usuário existente
@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if user:
        user.email = data.get('email', user.email)
        user.senha = data.get('senha', user.senha)
        user.telefone = data.get('telefone', user.telefone)
        db.session.commit()
        return jsonify(user.to_dict())
    return jsonify({'message': 'User not found'}), 404

# Rota para deletar um usuário
@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'}), 204
    return jsonify({'message': 'User not found'}), 404

# Rota para listar todas as unidades
@app.route('/unidades', methods=['GET'])
def get_unidades():
    unidades = Unidade.query.all()
    return jsonify([unidade.to_dict() for unidade in unidades])

# Rota para listar uma unidade específica
@app.route('/unidade/<int:id>', methods=['GET'])
def get_unidade(id):
    unidade = Unidade.query.get(id)
    if unidade:
        return jsonify(unidade.to_dict())
    return jsonify({'message': 'Unidade not found'}), 404

# Rota para adicionar uma nova unidade
@app.route('/unidade', methods=['POST'])
def add_unidade():
    data = request.get_json()
    new_unidade = Unidade(
        nome=data['nome'],
        cep=data['cep'],
        logradouro=data['logradouro'],
        numero=data['numero'],
        complemento=data.get('complemento'),
        estado=data['estado'],
        cidade=data['cidade'],
        bairro=data['bairro']
    )
    db.session.add(new_unidade)
    db.session.commit()
    return jsonify(new_unidade.to_dict()), 201

# Rota para atualizar uma unidade existente
@app.route('/unidade/<int:id>', methods=['PUT'])
def update_unidade(id):
    data = request.get_json()
    unidade = Unidade.query.get(id)
    if unidade:
        unidade.nome = data.get('nome', unidade.nome)
        unidade.cep = data.get('cep', unidade.cep)
        unidade.logradouro = data.get('logradouro', unidade.logradouro)
        unidade.numero = data.get('numero', unidade.numero)
        unidade.complemento = data.get('complemento', unidade.complemento)
        unidade.estado = data.get('estado', unidade.estado)
        unidade.cidade = data.get('cidade', unidade.cidade)
        unidade.bairro = data.get('bairro', unidade.bairro)
        db.session.commit()
        return jsonify(unidade.to_dict())
    return jsonify({'message': 'Unidade not found'}), 404

# Rota para deletar uma unidade
@app.route('/unidade/<int:id>', methods=['DELETE'])
def delete_unidade(id):
    unidade = Unidade.query.get(id)
    if unidade:
        db.session.delete(unidade)
        db.session.commit()
        return jsonify({'message': 'Unidade deleted'}), 204
    return jsonify({'message': 'Unidade not found'}), 404

# Rota para listar todos os profissionais
@app.route('/profissionais', methods=['GET'])
def get_profissionais():
    profissionais = Profissional.query.all()
    return jsonify([profissional.to_dict() for profissional in profissionais])

# Rota para listar um profissional específico
@app.route('/profissional/<int:id>', methods=['GET'])
def get_profissional(id):
    profissional = Profissional.query.get(id)
    if profissional:
        return jsonify(profissional.to_dict())
    return jsonify({'message': 'Profissional not found'}), 404

# Rota para adicionar um novo profissional
@app.route('/profissional', methods=['POST'])
def add_profissional():
    data = request.get_json()
    new_profissional = Profissional(
        nome=data['nome'],
        cpf=data['cpf'],
        datanascimento=data['datanascimento'],
        matricula=data['matricula'],
        cargo=data['cargo'],
        usuario=data['usuario'],
        setor=data['setor']
    )
    db.session.add(new_profissional)
    db.session.commit()
    return jsonify(new_profissional.to_dict()), 201

# Rota para atualizar um profissional existente
@app.route('/profissional/<int:id>', methods=['PUT'])
def update_profissional(id):
    data = request.get_json()
    profissional = Profissional.query.get(id)
    if profissional:
        profissional.nome = data.get('nome', profissional.nome)
        profissional.cpf = data.get('cpf', profissional.cpf)
        profissional.datanascimento = data.get('datanascimento', profissional.datanascimento)
        profissional.matricula = data.get('matricula', profissional.matricula)
        profissional.cargo = data.get('cargo', profissional.cargo)
        profissional.usuario = data.get('usuario', profissional.usuario)
        profissional.setor = data.get('setor', profissional.setor)
        db.session.commit()
        return jsonify(profissional.to_dict())
    return jsonify({'message': 'Profissional not found'}), 404

# Rota para deletar um profissional
@app.route('/profissional/<int:id>', methods=['DELETE'])
def delete_profissional(id):
    profissional = Profissional.query.get(id)
    if profissional:
        db.session.delete(profissional)
        db.session.commit()
        return jsonify({'message': 'Profissional deleted'}), 204
    return jsonify({'message': 'Profissional not found'}), 404

# Rota para listar todos os setores
@app.route('/setores', methods=['GET'])
def get_setores():
    setores = Setor.query.all()
    return jsonify([setor.to_dict() for setor in setores])

# Rota para listar um setor específico
@app.route('/setor/<int:id>', methods=['GET'])
def get_setor(id):
    setor = Setor.query.get(id)
    if setor:
        return jsonify(setor.to_dict())
    return jsonify({'message': 'Setor not found'}), 404

# Rota para adicionar um novo setor
@app.route('/setor', methods=['POST'])
def add_setor():
    data = request.get_json()
    new_setor = Setor(
        nome=data['nome'],
        unidade=data['unidade']
    )
    db.session.add(new_setor)
    db.session.commit()
    return jsonify(new_setor.to_dict()), 201

# Rota para atualizar um setor existente
@app.route('/setor/<int:id>', methods=['PUT'])
def update_setor(id):
    data = request.get_json()
    setor = Setor.query.get(id)
    if setor:
        setor.nome = data.get('nome', setor.nome)
        setor.unidade = data.get('unidade', setor.unidade)
        db.session.commit()
        return jsonify(setor.to_dict())
    return jsonify({'message': 'Setor not found'}), 404

# Rota para deletar um setor
@app.route('/setor/<int:id>', methods=['DELETE'])
def delete_setor(id):
    setor = Setor.query.get(id)
    if setor:
        db.session.delete(setor)
        db.session.commit()
        return jsonify({'message': 'Setor deleted'}), 204
    return jsonify({'message': 'Setor not found'}), 404

# Rota para listar todos os estoques
@app.route('/estoques', methods=['GET'])
def get_estoques():
    estoques = Estoque.query.all()
    return jsonify([estoque.to_dict() for estoque in estoques])

# Rota para listar um estoque específico
@app.route('/estoque/<int:id>', methods=['GET'])
def get_estoque(id):
    estoque = Estoque.query.get(id)
    if estoque:
        return jsonify(estoque.to_dict())
    return jsonify({'message': 'Estoque not found'}), 404

# Rota para adicionar um novo estoque
@app.route('/estoque', methods=['POST'])
def add_estoque():
    data = request.get_json()
    new_estoque = Estoque(
        quantidade=data['quantidade'],
        unidade=data['unidade']
    )
    db.session.add(new_estoque)
    db.session.commit()
    return jsonify(new_estoque.to_dict()), 201

# Rota para atualizar um estoque existente
@app.route('/estoque/<int:id>', methods=['PUT'])
def update_estoque(id):
    data = request.get_json()
    estoque = Estoque.query.get(id)
    if estoque:
        estoque.quantidade = data.get('quantidade', estoque.quantidade)
        estoque.unidade = data.get('unidade', estoque.unidade)
        db.session.commit()
        return jsonify(estoque.to_dict())
    return jsonify({'message': 'Estoque not found'}), 404

# Rota para deletar um estoque
@app.route('/estoque/<int:id>', methods=['DELETE'])
def delete_estoque(id):
    estoque = Estoque.query.get(id)
    if estoque:
        db.session.delete(estoque)
        db.session.commit()
        return jsonify({'message': 'Estoque deleted'}), 204
    return jsonify({'message': 'Estoque not found'}), 404

# Rota para listar todos os recursos
@app.route('/recursos', methods=['GET'])
def get_recursos():
    recursos = Recurso.query.all()
    return jsonify([recurso.to_dict() for recurso in recursos])

# Rota para listar um recurso específico
@app.route('/recurso/<int:id>', methods=['GET'])
def get_recurso(id):
    recurso = Recurso.query.get(id)
    if recurso:
        return jsonify(recurso.to_dict())
    return jsonify({'message': 'Recurso not found'}), 404

# Rota para adicionar um novo recurso
@app.route('/recurso', methods=['POST'])
def add_recurso():
    data = request.get_json()

    try:
        # Agora, você usará 'estoque_id' para referenciar a chave estrangeira
        new_recurso = Recurso(
            nome=data['nome'],
            categoria=data['categoria'],
            descricao=data.get('descricao'),  # Campo opcional
            marca=data.get('marca'),          # Campo opcional
            tamanho=data.get('tamanho'),      # Campo opcional
            estoque=data['estoque']        # Note que agora usamos 'estoque_id'
        )
        
        db.session.add(new_recurso)
        db.session.commit()
        
        return jsonify(new_recurso.to_dict()), 201
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400


# Rota para atualizar um recurso existente
@app.route('/recurso/<int:id>', methods=['PUT'])
def update_recurso(id):
    data = request.get_json()
    recurso = Recurso.query.get(id)
    if recurso:
        recurso.nome = data.get('nome', recurso.nome)
        recurso.categoria = data.get('categoria', recurso.categoria)
        recurso.marca = data.get('marca', recurso.marca)
        recurso.tamanho = data.get('tamanho', recurso.tamanho)
        recurso.descricao = data.get('descricao', recurso.descricao)
        recurso.estoque = data.get('estoque', recurso.estoque)
        db.session.commit()
        return jsonify(recurso.to_dict())
    return jsonify({'message': 'Recurso not found'}), 404

# Rota para deletar um recurso
@app.route('/recurso/<int:id>', methods=['DELETE'])
def delete_recurso(id):
    recurso = Recurso.query.get(id)
    if recurso:
        db.session.delete(recurso)
        db.session.commit()
        return jsonify({'message': 'Recurso deleted'}), 204
    return jsonify({'message': 'Recurso not found'}), 404

# Rota para listar todas as doações
@app.route('/doacoes', methods=['GET'])
def get_doacoes():
    doacoes = Doacao.query.all()
    return jsonify([doacao.to_dict() for doacao in doacoes])

# Rota para listar uma doação específica
@app.route('/doacao/<int:id>', methods=['GET'])
def get_doacao(id):
    doacao = Doacao.query.get(id)
    if doacao:
        return jsonify(doacao.to_dict())
    return jsonify({'message': 'Doação not found'}), 404

# Rota para adicionar uma nova doação
@app.route('/doacao', methods=['POST'])
def add_doacao():
    data = request.get_json()

    try:
        new_doacao = Doacao(
            datadoacao=datetime.strptime(data['datadoacao'], '%Y-%m-%dT%H:%M:%S'),
            quantidade=data['quantidade'],
            recurso=data['recurso'],
            unidade=data['unidade'],
            responsavel=data['responsavel']
        )

        db.session.add(new_doacao)
        db.session.commit()

        return jsonify(new_doacao.to_dict()), 201
    except KeyError as e:
        return jsonify({"error": f"Missing key in request: {e.args[0]}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Rota para atualizar uma doação existente
@app.route('/doacao/<int:id>', methods=['PUT'])
def update_doacao(id):
    data = request.get_json()
    doacao = Doacao.query.get(id)
    if doacao:
        doacao.dataDoacao = data.get('dataDoacao', doacao.dataDoacao)
        doacao.responsavel = data.get('responsavel', doacao.responsavel)
        doacao.quantidade = data.get('quantidade', doacao.quantidade)
        doacao.recurso = data.get('recurso', doacao.recurso)
        doacao.unidade = data.get('unidade', doacao.unidade)
        db.session.commit()
        return jsonify(doacao.to_dict())
    return jsonify({'message': 'Doação not found'}), 404

# Rota para deletar uma doação
@app.route('/doacao/<int:id>', methods=['DELETE'])
def delete_doacao(id):
    doacao = Doacao.query.get(id)
    if doacao:
        db.session.delete(doacao)
        db.session.commit()
        return jsonify({'message': 'Doação deleted'}), 204
    return jsonify({'message': 'Doação not found'}), 404


# Rota para listar todos os empréstimos
@app.route('/emprestimos', methods=['GET'])
def get_emprestimos():
    emprestimos = Emprestimo.query.all()
    return jsonify([emprestimo.to_dict() for emprestimo in emprestimos])

# Rota para listar um empréstimo específico
@app.route('/emprestimo/<int:id>', methods=['GET'])
def get_emprestimo(id):
    emprestimo = Emprestimo.query.get(id)
    if emprestimo:
        return jsonify(emprestimo.to_dict())
    return jsonify({'message': 'Empréstimo not found'}), 404

# Rota para adicionar um novo empréstimo
@app.route('/emprestimo', methods=['POST'])
def add_emprestimo():
    try:
        data = request.get_json()
        new_emprestimo = Emprestimo(
            dataemprestimo=data['dataemprestimo'],
            responsavel=data['responsavel'],
            quantidade=data['quantidade'],
            recurso=data['recurso'],
            unidade=data['unidade']
        )
        db.session.add(new_emprestimo)
        db.session.commit()
        return jsonify(new_emprestimo.to_dict()), 201
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Rota para atualizar um empréstimo existente
@app.route('/emprestimo/<int:id>', methods=['PUT'])
def update_emprestimo(id):
    data = request.get_json()
    emprestimo = Emprestimo.query.get(id)
    if emprestimo:
        emprestimo.dataEmprestimo = data.get('dataEmprestimo', emprestimo.dataEmprestimo)
        emprestimo.responsavel = data.get('responsavel', emprestimo.responsavel)
        emprestimo.quantidade = data.get('quantidade', emprestimo.quantidade)
        emprestimo.recurso = data.get('recurso', emprestimo.recurso)
        emprestimo.unidadeOrigem = data.get('unidadeOrigem', emprestimo.unidadeOrigem)
        emprestimo.unidadeDestino = data.get('unidadeDestino', emprestimo.unidadeDestino)
        db.session.commit()
        return jsonify(emprestimo.to_dict())
    return jsonify({'message': 'Empréstimo not found'}), 404

# Rota para deletar um empréstimo
@app.route('/emprestimo/<int:id>', methods=['DELETE'])
def delete_emprestimo(id):
    emprestimo = Emprestimo.query.get(id)
    if emprestimo:
        db.session.delete(emprestimo)
        db.session.commit()
        return jsonify({'message': 'Empréstimo deleted'}), 204
    return jsonify({'message': 'Empréstimo not found'}), 404

# Rota para listar todas as devoluções
@app.route('/devolucoes', methods=['GET'])
def get_devolucoes():
    devolucoes = Devolucao.query.all()
    return jsonify([devolucao.to_dict() for devolucao in devolucoes])

# Rota para listar uma devolução específica
@app.route('/devolucao/<int:id>', methods=['GET'])
def get_devolucao(id):
    devolucao = Devolucao.query.get(id)
    if devolucao:
        return jsonify(devolucao.to_dict())
    return jsonify({'message': 'Devolução not found'}), 404

# Rota para adicionar uma nova devolução
@app.route('/devolucao', methods=['POST'])
def add_devolucao():
    data = request.get_json()

    try:
        # Criar uma nova devolução
        new_devolucao = Devolucao(
            datadevolucao=data['datadevolucao'],  # Exemplo: "2024-11-22T14:00:00"
            recurso=data['recurso'],  # ID do recurso
            unidade=data['unidade'],  # ID da unidade
            responsaveldevolucao=data['responsaveldevolucao']  # ID do profissional
        )

        # Adicionar ao banco de dados
        db.session.add(new_devolucao)
        db.session.commit()

        return jsonify(new_devolucao.to_dict()), 201
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Rota para atualizar uma devolução existente
@app.route('/devolucao/<int:id>', methods=['PUT'])
def update_devolucao(id):
    data = request.get_json()
    devolucao = Devolucao.query.get(id)
    if devolucao:
        devolucao.dataDevolucao = data.get('dataDevolucao', devolucao.dataDevolucao)
        devolucao.responsavel = data.get('responsavel', devolucao.responsavel)
        devolucao.quantidade = data.get('quantidade', devolucao.quantidade)
        devolucao.recurso = data.get('recurso', devolucao.recurso)
        devolucao.unidadeOrigem = data.get('unidadeOrigem', devolucao.unidadeOrigem)
        devolucao.unidadeDestino = data.get('unidadeDestino', devolucao.unidadeDestino)
        db.session.commit()
        return jsonify(devolucao.to_dict())
    return jsonify({'message': 'Devolução not found'}), 404

# Rota para deletar uma devolução
@app.route('/devolucao/<int:id>', methods=['DELETE'])
def delete_devolucao(id):
    devolucao = Devolucao.query.get(id)
    if devolucao:
        db.session.delete(devolucao)
        db.session.commit()
        return jsonify({'message': 'Devolução deleted'}), 204
    return jsonify({'message': 'Devolução not found'}), 404



# Função de verificação do token JWT
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated_function

# Rota de login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.senha, data['senha']):
        # Gera o token JWT
        token = jwt.encode({
            'user_id': user.idusuario,
            'exp': datetime.utcnow() + timedelta(hours=1)  # O token expira em 1 hora
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401


# Rota protegida com token
@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({'message': f'Hello {current_user.email}'}), 200



# Configurar rota principal para servir o arquivo HTML principal
@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Rota para páginas sem precisar do .html
@app.route('/<page>')
def serve_page_without_html(page):
    return send_from_directory(FRONTEND_DIR, f'{page}.html')


# Rota para servir arquivos estáticos como CSS, JS e imagens
@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# Rota de teste
@app.route('/')
def home():
    return jsonify(message="SAB API funcionando!")

if __name__ == '__main__':
    app.run(debug=True)