import pytest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db

@pytest.fixture
def client():
    """Configura um cliente de teste para a aplicação."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:senha@localhost:5432/sab_test'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_get_all_doacoes(client):
    """Valida a listagem de todas as doações."""
    # Criar dados de teste
    unidade_response = client.post('/unidade', json={
        'nome': 'Unidade Integração',
        'cep': '12345678',
        'logradouro': 'Rua da Integração',
        'numero': 20,
        'estado': 'SP',
        'cidade': 'São Paulo',
        'bairro': 'Centro'
    })
    unidade_id = unidade_response.get_json()['idunidade']

    estoque_response = client.post('/estoque', json={
        'quantidade': 50,
        'unidade': unidade_id
    })
    estoque_id = estoque_response.get_json()['idestoque']

    recurso_response = client.post('/recurso', json={
        'nome': 'Álcool Gel',
        'categoria': 'Higiene',
        'estoque': estoque_id
    })
    recurso_id = recurso_response.get_json()['idrecurso']

    # Criar profissional (responsável)
    user_response = client.post('/user', json={
        'email': 'user@example.com',
        'senha': 'senha123',
        'telefone': '123456789'
    })
    user_id = user_response.get_json()['idusuario']

    setor_response = client.post('/setor', json={
        'nome': 'Setor Integração',
        'unidade': unidade_id
    })
    setor_id = setor_response.get_json()['idsetor']

    profissional_response = client.post('/profissional', json={
        'nome': 'João Silva',
        'cpf': '12345678900',
        'datanascimento': '1990-01-01',
        'matricula': 'MAT001',
        'cargo': 'Médico',
        'usuario': user_id,
        'setor': setor_id
    })
    responsavel_id = profissional_response.get_json()['idprofissional']

    # Criar doação
    doacao_response = client.post('/doacao', json={
        'datadoacao': '2024-11-23T10:00:00',
        'quantidade': 10,
        'recurso': recurso_id,
        'unidade': unidade_id,
        'responsavel': responsavel_id
    })
    assert doacao_response.status_code == 201

    # Verificar listagem
    response = client.get('/doacoes')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0  # Pelo menos um registro deve estar presente
    assert any(d['quantidade'] == 10 for d in data)



    # Verificar listagem
    response = client.get('/doacoes')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0  # Pelo menos um registro deve estar presente
    assert any(d['quantidade'] == 10 for d in data)

def test_create_and_validate_recurso(client):
    """Valida a criação e resposta ao criar um recurso."""
    unidade_response = client.post('/unidade', json={
        'nome': 'Unidade Teste Recurso',
        'cep': '65432178',
        'logradouro': 'Avenida Principal',
        'numero': 123,
        'estado': 'RJ',
        'cidade': 'Rio de Janeiro',
        'bairro': 'Botafogo'
    })
    unidade_id = unidade_response.get_json()['idunidade']

    estoque_response = client.post('/estoque', json={
        'quantidade': 30,
        'unidade': unidade_id
    })
    estoque_id = estoque_response.get_json()['idestoque']

    recurso_response = client.post('/recurso', json={
        'nome': 'Luvas',
        'categoria': 'Equipamento',
        'estoque': estoque_id
    })
    assert recurso_response.status_code == 201
    data = recurso_response.get_json()
    assert data['nome'] == 'Luvas'
    assert data['categoria'] == 'Equipamento'
    assert data['estoque']['quantidade'] == 30

def test_update_recurso(client):
    """Valida a atualização de um recurso existente."""
    unidade_response = client.post('/unidade', json={
        'nome': 'Unidade Atualização',
        'cep': '45678912',
        'logradouro': 'Rua Atualizada',
        'numero': 45,
        'estado': 'MG',
        'cidade': 'Belo Horizonte',
        'bairro': 'Savassi'
    })
    unidade_id = unidade_response.get_json()['idunidade']

    estoque_response = client.post('/estoque', json={
        'quantidade': 40,
        'unidade': unidade_id
    })
    estoque_id = estoque_response.get_json()['idestoque']

    recurso_response = client.post('/recurso', json={
        'nome': 'Máscaras',
        'categoria': 'Equipamento',
        'estoque': estoque_id
    })
    recurso_id = recurso_response.get_json()['idrecurso']

    # Atualizar recurso
    update_response = client.put(f'/recurso/{recurso_id}', json={
        'nome': 'Máscaras PFF2',
        'categoria': 'EPI'
    })
    assert update_response.status_code == 200
    data = update_response.get_json()
    assert data['nome'] == 'Máscaras PFF2'
    assert data['categoria'] == 'EPI'
def test_delete_recurso(client):
    """Valida a exclusão de um recurso existente."""
    unidade_response = client.post('/unidade', json={
        'nome': 'Unidade Exclusão',
        'cep': '78912345',
        'logradouro': 'Avenida da Exclusão',
        'numero': 67,
        'estado': 'SP',
        'cidade': 'São Paulo',
        'bairro': 'Jardins'
    })
    unidade_id = unidade_response.get_json()['idunidade']

    estoque_response = client.post('/estoque', json={
        'quantidade': 20,
        'unidade': unidade_id
    })
    estoque_id = estoque_response.get_json()['idestoque']

    recurso_response = client.post('/recurso', json={
        'nome': 'Avental',
        'categoria': 'Proteção',
        'estoque': estoque_id
    })
    recurso_id = recurso_response.get_json()['idrecurso']

    # Excluir recurso
    delete_response = client.delete(f'/recurso/{recurso_id}')
    assert delete_response.status_code == 204

    # Verificar se foi excluído
    get_response = client.get(f'/recurso/{recurso_id}')
    assert get_response.status_code == 404

def test_invalid_route_response(client):
    """Valida a resposta ao acessar uma rota inexistente."""
    response = client.get('/rota-invalida')
    assert response.status_code == 404  # Verifica o código de status
    assert response.data  # Garante que o corpo da resposta não está vazio
    assert b'Not Found' in response.data  # Verifica o conteúdo da mensagem



