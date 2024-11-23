import pytest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, User, Unidade, Setor, Profissional, Estoque, Recurso, Doacao, Emprestimo  # Certifique-se de que os imports estejam corretos

@pytest.fixture
def client():
    """Fixture para configurar o cliente de teste."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Happyland1990@localhost:5432/sab_test'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Cria tabelas no banco de testes
        yield client  # Retorna o cliente de teste
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Remove tudo após o teste

def test_add_user(client):
    """Testa a criação de um novo usuário."""
    response = client.post('/user', json={
        'email': 'testuser@example.com',
        'senha': 'senha123',
        'telefone': '123456789'
    })
    assert response.status_code == 201  # Verifica se o usuário foi criado
    data = response.get_json()
    assert data['email'] == 'testuser@example.com'

def test_get_user(client):
    """Testa a busca de um usuário existente."""
    # Primeiro, cria um usuário
    user = User(email='novousuario@exemplo.com', senha='senha123', telefone='98765432100')
    with app.app_context():
        db.session.add(user)
        db.session.commit()

        # Recupere o usuário novamente após o commit para garantir que ele tenha um ID
        user = User.query.get(user.idusuario)

    # Busca o usuário pelo ID
    response = client.get(f'/user/{user.idusuario}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == 'novousuario@exemplo.com'

# Testes de Unidade
def test_add_unidade(client):
    """Teste para criação de unidade."""
    response = client.post('/unidade', json={
        'nome': 'Unidade 1',
        'cep': '12345678',
        'logradouro': 'Rua Exemplo',
        'numero': 100,
        'complemento': 'Sala 1',
        'estado': 'SP',
        'cidade': 'São Paulo',
        'bairro': 'Centro'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['nome'] == 'Unidade 1'

# Testes de Estoque
def test_add_estoque(client):
    """Teste para criação de estoque."""
    with app.app_context():
        unidade = Unidade(nome='Unidade 1', cep='12345678', logradouro='Rua Exemplo', numero=100, estado='SP', cidade='São Paulo', bairro='Centro')
        db.session.add(unidade)
        db.session.commit()
        db.session.refresh(unidade)  # Garante que unidade está na sessão ativa

    response = client.post('/estoque', json={
        'quantidade': 50,
        'unidade': unidade.idunidade
    })
    assert response.status_code == 201


# Testes de Recurso
def test_add_recurso(client):
    """Teste para criação de recurso."""
    with app.app_context():
        unidade = Unidade(nome='Unidade 1', cep='12345678', logradouro='Rua Exemplo', numero=100, estado='SP', cidade='São Paulo', bairro='Centro')
        db.session.add(unidade)
        db.session.commit()
        db.session.refresh(unidade)  # Atualizar unidade

        estoque = Estoque(quantidade=100, unidade=unidade.idunidade)
        db.session.add(estoque)
        db.session.commit()
        db.session.refresh(estoque)  # Atualizar estoque

    response = client.post('/recurso', json={
        'nome': 'Álcool Gel',
        'categoria': 'Higiene',
        'marca': 'Marca X',
        'tamanho': '500ml',
        'descricao': 'Antisséptico',
        'estoque': estoque.idestoque
    })
    assert response.status_code == 201


def test_add_doacao(client):
    """Teste para criação de doação utilizando a API."""
    # Criar unidade
    unidade_response = client.post('/unidade', json={
        'nome': 'Unidade Teste',
        'cep': '12345678',
        'logradouro': 'Rua A',
        'numero': 100,
        'estado': 'SP',
        'cidade': 'São Paulo',
        'bairro': 'Centro'
    })
    unidade_id = unidade_response.get_json()['idunidade']

    # Criar recurso
    estoque_response = client.post('/estoque', json={
        'quantidade': 100,
        'unidade': unidade_id
    })
    estoque_id = estoque_response.get_json()['idestoque']

    recurso_response = client.post('/recurso', json={
        'nome': 'Recurso Teste',
        'categoria': 'Categoria A',
        'estoque': estoque_id
    })
    recurso_id = recurso_response.get_json()['idrecurso']

    # Criar usuário
    user_response = client.post('/user', json={
        'email': 'user1@example.com',
        'senha': 'senha123',
        'telefone': '123456789'
    })
    user_id = user_response.get_json()['idusuario']

    # Criar setor
    setor_response = client.post('/setor', json={
        'nome': 'Setor 1',
        'unidade': unidade_id
    })
    setor_id = setor_response.get_json()['idsetor']

    # Criar profissional
    profissional_response = client.post('/profissional', json={
        'nome': 'João Silva',
        'cpf': '12345678900',
        'datanascimento': '1980-01-01',
        'matricula': 'MAT001',
        'cargo': 'Médico',
        'usuario': user_id,
        'setor': setor_id
    })
    profissional_id = profissional_response.get_json()['idprofissional']

    # Criar doação
    response = client.post('/doacao', json={
        'datadoacao': '2024-11-23T10:00:00',
        'quantidade': 5,
        'recurso': recurso_id,
        'unidade': unidade_id,
        'responsavel': profissional_id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['quantidade'] == 5
    assert data['recurso']['idrecurso'] == recurso_id  # Extrai o id do recurso retornado




def test_add_profissional(client):
    """Teste para criação de profissional utilizando a API."""
    # Criar unidade
    unidade_response = client.post('/unidade', json={
        'nome': 'Unidade B',
        'cep': '98765432',
        'logradouro': 'Rua B',
        'numero': 200,
        'estado': 'RJ',
        'cidade': 'Rio de Janeiro',
        'bairro': 'Botafogo'
    })
    unidade_id = unidade_response.get_json()['idunidade']

    # Criar setor
    setor_response = client.post('/setor', json={
        'nome': 'Setor Clínico',
        'unidade': unidade_id
    })
    setor_id = setor_response.get_json()['idsetor']

    # Criar usuário
    user_response = client.post('/user', json={
        'email': 'user2@example.com',
        'senha': 'senha123',
        'telefone': '987654321'
    })
    user_id = user_response.get_json()['idusuario']

    # Criar profissional
    response = client.post('/profissional', json={
        'nome': 'Maria Oliveira',
        'cpf': '98765432100',
        'datanascimento': '1990-05-15',
        'matricula': 'MAT002',
        'cargo': 'Enfermeira',
        'usuario': user_id,
        'setor': setor_id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['nome'] == 'Maria Oliveira'
    assert data['cpf'] == '98765432100'



def test_add_emprestimo(client):
    """Teste para criação de empréstimo utilizando a API."""
    # Criar unidade
    unidade_response = client.post('/unidade', json={
        'nome': 'Unidade C',
        'cep': '65432178',
        'logradouro': 'Rua C',
        'numero': 300,
        'estado': 'MG',
        'cidade': 'Belo Horizonte',
        'bairro': 'Savassi'
    })
    unidade_id = unidade_response.get_json()['idunidade']

    # Criar recurso
    estoque_response = client.post('/estoque', json={
        'quantidade': 50,
        'unidade': unidade_id
    })
    estoque_id = estoque_response.get_json()['idestoque']

    recurso_response = client.post('/recurso', json={
        'nome': 'Recurso Emprestado',
        'categoria': 'Equipamentos',
        'estoque': estoque_id
    })
    recurso_id = recurso_response.get_json()['idrecurso']

    # Criar usuário
    user_response = client.post('/user', json={
        'email': 'user3@example.com',
        'senha': 'senha123',
        'telefone': '456789123'
    })
    user_id = user_response.get_json()['idusuario']

    # Criar setor
    setor_response = client.post('/setor', json={
        'nome': 'Setor Técnico',
        'unidade': unidade_id
    })
    setor_id = setor_response.get_json()['idsetor']

    # Criar profissional
    profissional_response = client.post('/profissional', json={
        'nome': 'Carlos Almeida',
        'cpf': '45678912300',
        'datanascimento': '1985-08-10',
        'matricula': 'MAT003',
        'cargo': 'Técnico',
        'usuario': user_id,
        'setor': setor_id
    })
    profissional_id = profissional_response.get_json()['idprofissional']

    # Criar empréstimo
    response = client.post('/emprestimo', json={
        'dataemprestimo': '2024-11-23T12:00:00',
        'quantidade': 10,
        'recurso': recurso_id,
        'unidade': unidade_id,
        'responsavel': profissional_id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['quantidade'] == 10
    assert data['recurso']['idrecurso'] == recurso_id  # Extrai o id do recurso retornado





# Teste de validação de rotas
def test_invalid_route(client):
    """Teste para validar rota inexistente."""
    response = client.get('/invalid-route')
    assert response.status_code == 404

