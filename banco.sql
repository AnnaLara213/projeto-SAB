CREATE TABLE users (
    idUsuario SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(14) NOT NULL
);

CREATE TABLE unidade (
    idUnidade SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cep VARCHAR(9) NOT NULL,
    logradouro VARCHAR(70) NOT NULL,
    numero INTEGER NOT NULL,
    complemento VARCHAR(70),
    estado VARCHAR(2) NOT NULL,
    cidade VARCHAR(70) NOT NULL,
    bairro VARCHAR(70) NOT NULL
);

CREATE TABLE setor (
    idSetor SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    unidade INTEGER NOT NULL,
    CONSTRAINT fk_unidadeSetor FOREIGN KEY (unidade) REFERENCES unidade(idUnidade)
);

CREATE TABLE profissional (
    idProfissional SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    dataNascimento DATE,
    matricula VARCHAR(20) NOT NULL,
    cargo VARCHAR(50) NOT NULL,
    usuario INTEGER NOT NULL,
    setor INTEGER NOT NULL,
    CONSTRAINT fk_usuarioProfissional FOREIGN KEY (usuario) REFERENCES users(idUsuario),
    CONSTRAINT fk_setorProfissional FOREIGN KEY (setor) REFERENCES setor(idSetor)
);

CREATE TABLE estoque (
    idEstoque SERIAL PRIMARY KEY,
    quantidade INTEGER NOT NULL,
    unidade INTEGER NOT NULL,
    CONSTRAINT fk_estoqueUnidade FOREIGN KEY (unidade) REFERENCES unidade(idUnidade)
);

CREATE TABLE recurso (
    idRecurso SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    marca VARCHAR(45),
    tamanho VARCHAR(255),
    descricao VARCHAR(1000),
    estoque INTEGER NOT NULL,
    CONSTRAINT fk_estoqueRecurso FOREIGN KEY (estoque) REFERENCES estoque(idEstoque)
);

CREATE TABLE doacao (
    idDoacao SERIAL PRIMARY KEY,
    dataDoacao TIMESTAMP NOT NULL,
    responsavel INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    recurso INTEGER NOT NULL,
    unidade INTEGER NOT NULL,
    CONSTRAINT fk_doacaoUnidade FOREIGN KEY (unidade) REFERENCES unidade(idUnidade),
    CONSTRAINT fk_doacaoRecurso FOREIGN KEY (recurso) REFERENCES recurso(idRecurso),
    CONSTRAINT fk_responsavelDoacao FOREIGN KEY (responsavel) REFERENCES profissional(idProfissional)
);

CREATE TABLE emprestimo (
    idEmprestimo SERIAL PRIMARY KEY,
    dataEmprestimo TIMESTAMP NOT NULL,
    responsavel INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    recurso INTEGER NOT NULL,
    unidade INTEGER NOT NULL,
    CONSTRAINT fk_emprestimoUnidade FOREIGN KEY (unidade) REFERENCES unidade(idUnidade),
    CONSTRAINT fk_emprestimoRecurso FOREIGN KEY (recurso) REFERENCES recurso(idRecurso),
    CONSTRAINT fk_responsavelEmprestimo FOREIGN KEY (responsavel) REFERENCES profissional(idProfissional)
);

CREATE TABLE devolucao (
    idDevolucao SERIAL PRIMARY KEY,
    dataDevolucao TIMESTAMP NOT NULL,
    recurso INTEGER NOT NULL,
    unidade INTEGER NOT NULL,
    responsavelDevolucao INTEGER NOT NULL,
    CONSTRAINT fk_devolucaoUnidade FOREIGN KEY (unidade) REFERENCES unidade(idUnidade),
    CONSTRAINT fk_devolucaoRecurso FOREIGN KEY (recurso) REFERENCES recurso(idRecurso),
    CONSTRAINT fk_devolucaoResponsavel FOREIGN KEY (responsavelDevolucao) REFERENCES profissional(idProfissional)
);

-- Inserir dados
INSERT INTO users (email, senha, telefone) 
VALUES 
    ('usuario@gmail.com', 'Desi1973', '(84) 7142-4926'),
    ('adm@gmail.com', 'Fachur', '(49) 6602-8505'),
    ('enfermeiro@outlook.com', 'eex6Quia', '(71) 5343-3474'),
    ('medico@yahoo.com', 'Bei5Ieseixa', '(11) 3323-9914'),
    ('doutor@exemplo.com', 'eleenu0Qua9', '(61) 2310-9212');

INSERT INTO unidade (nome, cep, logradouro, numero, complemento, estado, cidade, bairro)
VALUES 
    ('Hospital Municipal de Salvador', '41301-110', 'R. Ver. Zezéu Ribeiro', 0, '', 'BA', 'Salvador', 'Cajazeiras'),
    ('Hospital Regional do Oeste', '89812-505', 'R. Florianópolis', 1448, 'E', 'SC', 'Chapecó', 'Santa Maria'),
    ('Hospital Municipal de Natal', '59012-330', 'Rua Coronel Joaquim Manoel', 654, '', 'RN', 'Natal', 'Petrópolis'),
    ('Hospital do Servidor Público Municipal', '01532-000', 'R. Castro Alves', 60, '', 'SP', 'São Paulo', 'Aclimação'),
    ('Hospital de Base do Distrito Federal', '70330-150', 'SMHS - Área Especial', 101, '', 'DF', 'Brasília', 'Asa Sul'),
    ('Hospital Regional da Asa Norte', '70710-100', 'SMHN', 2, '', 'DF', 'Brasília', 'Asa Norte');

INSERT INTO setor (nome, unidade)
VALUES 
    ('Unidade de Terapia Intensiva', 1),
    ('Administrativo', 2),
    ('Fisioterapia', 3),
    ('Pronto-socorro', 4),
    ('Cardiologia', 5),
    ('Enfermaria', 6);

INSERT INTO profissional
    (idProfissional, nome, cpf, dataNascimento, matricula, cargo, usuario, setor)
VALUES
    (1, 'Joao Martins Araujo', '926.124.289-84', '1970-11-16', 'E000001', 'Enfermeiro', 1, 1),
    (2, 'Vitória Correia Souza', '545.685.758-85', '1962-07-15', 'A000001', 'Administrador', 2, 2),
    (3, 'Júlio Melo Carvalho', '272.495.120-48', '2000-08-25', 'U000001', 'Estagiário', 3, 3),
    (4, 'Tiago Lima Santos', '320.181.046-08', '1985-02-03', 'M000001', 'Médico', 4, 4),
    (5, 'Gabrielly Melo Lima', '495.420.865-39', '1979-04-20', 'D000001', 'Doutor', 5, 5),
    (6, 'Lavinia Cardoso Ribeiro', '254.641.134-95', '2005-12-14', 'U000001', 'Estagiário', 1, 6);

INSERT INTO estoque (quantidade, unidade) 
VALUES 
    (1000, 1), (100, 1), (5, 1),
    (5, 2), (10000, 2), (10000, 3),
    (10000, 3), (100, 3), (100, 4), (100, 4);

INSERT INTO recurso (nome, categoria, marca, tamanho, estoque)
VALUES 
    ('Seringa Descartável 3ml', 'Descartáveis', 'Descarpack', '3ml', 1),
    ('Fita Cirúrgica De Silicone Adesiva 2,5cm x 5 metros', 'Curativo', 'Vital Derme', 'Rolo 2,5cm x 5 metros', 2),
    ('Cânula De Traqueostomia Biesalski Sem Balão Com Válvula de Fonação 8.0mm', 'Cânulas', 'BCI Medical', '8.0mm (Diâmetro Interno) e 9.7mm (Diâmetro Externo)', 3),
    ('Sonda Nasoenteral Dobbhoff 12fr', 'Sonda Alimentação', 'Covidien', '12fr x 109cm', 4),
    ('Fixador para Cânula de Traqueostomia Adulto', 'Cânulas', 'MDL', '', 5),
    ('Máscara Cirúrgica Tripla Branca c/ Elast c/50 Un', 'Máscara', 'Medix', '', 6),
    ('Luva de Látex Com Pó Profissional Tamanho M c/100 Unidades', 'Descartáveis', 'Descarpack', '', 7),
    ('Álcool em Sachê 70% Swab CX C/100 Unidades', 'Consumo', 'Uniqmed', '', 8),
    ('Avental Manga Longa GR20 C/10 Unidades', 'Descartáveis', 'Anadona', 'Manga Longa', 9),
    ('Bota de Unna 7,5cm x 9,14m', 'Curativo', 'Casex', '7,5cm x 9,14m', 10);

INSERT INTO doacao (dataDoacao, responsavel, quantidade, recurso, unidade) 
VALUES 
    ('2020-06-12 23:18:10', 1, 50, 1, 1),
    ('2021-12-03 08:00:55', 2, 100, 2, 3),
    ('2023-05-12 12:45:23', 3, 1000, 4, 5);

ALTER TABLE doacao DROP CONSTRAINT fk_doacaorecurso;
ALTER TABLE doacao ALTER COLUMN recurso TYPE INTEGER USING recurso::INTEGER;
ALTER TABLE doacao
ADD CONSTRAINT fk_doacaorecurso
FOREIGN KEY (recurso) REFERENCES recurso(idrecurso);

SELECT * FROM doacao;