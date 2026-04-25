# Quickstart: Swagger Security Testing Guide (EDI-29)

**Feature**: 004-swagger-security-testing  
**Branch**: `004-create-feature-branch`

## Pre-requisitos

- Python 3.11+.
- Repositorio em `c:\projects\interasisai-engine`.
- Ambiente virtual ativo.
- Variavel de ambiente de seguranca configurada (`X_INTERNAL_SECRET`).
- URL da API disponivel localmente ou em ambiente de homologacao.

## 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 2. Subir a API

```bash
uvicorn presentation.main:app --reload --port 8000
```

## 3. Abrir Swagger

- Acesse `http://localhost:8000/docs`.
- Confirme metadados da API (nome, descricao e versao).
- Confirme se os endpoints estao agrupados por tags funcionais.

## 4. Executar teste sem chave (deve bloquear)

1. Escolha um endpoint protegido.
2. Execute sem clicar em Authorize.
3. Valide retorno de bloqueio de acesso.

## 5. Executar teste com chave invalida (deve bloquear)

1. Clique em Authorize.
2. Informe um valor invalido para `X-Internal-Secret`.
3. Execute o mesmo endpoint protegido.
4. Valide novo bloqueio de acesso.

## 6. Executar teste com chave valida (deve autorizar)

1. Atualize o valor no Authorize com segredo valido do ambiente.
2. Execute novamente o endpoint protegido.
3. Valide retorno de sucesso funcional.

## 7. Registrar evidencias

- Status code dos tres cenarios (sem chave, chave invalida, chave valida).
- Corpo de resposta resumido.
- Data/hora do teste e ambiente utilizado.

## 8. Rodar testes automatizados de suporte

```bash
pytest --cov=. --cov-report=term-missing
```

Esperado:
- Suites de seguranca/documentacao sem regressao.
- Cobertura global minima de 80%.
