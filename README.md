# DevOps + GenAI com GitHub Actions

Laboratório didático inspirado na Unidade V — Projeto Integrador (UFG). Substitui GitLab CI/CD por GitHub Actions e usa Python, pytest, uma API Flask e a OpenAI API.

## Objetivo

1. Subir uma versão correta para `main`.
2. Abrir Pull Request com falha intencional na função de frete.
3. Observar testes falharem; o agente GenAI analisa logs, diff, fonte e testes e publica um comentário no PR.
4. Reverter a falha; observar os testes aprovarem.

## Estrutura

- `app.py`: API Flask com função `calculate_shipping`.
- `test_app.py`: 3 testes (`pytest`).
- `genai_analyst.py`: agente de IA que publica comentários no PR.
- `.github/workflows/devops-genai.yml`: pipeline.
- `requirements.txt`: dependências.
- `.gitignore`: arquivos não versionados.

## Execução local

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -v
```

Os três testes devem passar inicialmente.

## Criar repositório privado no GitHub

Crie um repositório **privado** chamado `devops-genai-lab`. Envie os arquivos usando Git, sem copiar `.venv`, `.env` ou chaves.

```sh
git init
git branch -M main
git add .
git commit -m "Versão inicial com testes passando"
git remote add origin https://github.com/SEU_USUARIO/devops-genai-lab.git
git push -u origin main
```

## Chave da OpenAI

GitHub: `Settings > Secrets and variables > Actions > New repository secret`.

- Nome: `OPENAI_API_KEY`
- Valor: chave criada na plataforma OpenAI (não a publique).

O `GITHUB_TOKEN` é fornecido automaticamente pelo GitHub Actions; o workflow solicita `issues: write` para comentar em Pull Requests via endpoint de comentários de issues.

O modelo configurado no workflow é `gpt-6-luna`. Ajuste `OPENAI_MODEL` se necessário, conforme disponibilidade e custo na sua conta.

## Inserir a falha em uma branch

```sh
git switch -c feature/erro-frete
```

No arquivo `app.py`, substitua a linha:

```python
return base_price + float(tax_rate)
```

por:

```python
return base_price + tax_rate
```

A chamada `calculate_shipping(100.0, "5.50")` passa a levantar `TypeError`.

```sh
python -m pytest -v

git add app.py
git commit -m "Simular erro de tipo no frete"
git push -u origin feature/erro-frete
```

No GitHub, abra um Pull Request `feature/erro-frete -> main`.

Na aba **Actions** ou em **Checks** do PR, veja o workflow. A etapa de testes falhará, o agente tentará comentar no PR, e o workflow terminará com estado de falha (como deve ser quando há testes quebrados).

## Corrigir

Na mesma branch, restaure:

```python
return base_price + float(tax_rate)
```

Execute os testes localmente; confirme que passam. Depois:

```sh
git add app.py
git commit -m "Corrigir conversão de tipo no frete"
git push
```

O PR será atualizado e o workflow deve passar. Só então faça merge, se desejar.

## Cautelas importantes

- Use este laboratório com branches do próprio repositório, sob seu controle. Não habilite acesso a secrets para códigos vindos de forks desconhecidos.
- Não insira chaves, dados pessoais ou logs sensíveis no código, no PR ou nos prompts enviados ao modelo. A sanitização no exemplo é somente demonstrativa.
- A IA diagnostica e comenta, mas **não altera código automaticamente**.
- `continue-on-error: true` na etapa de testes permite executar o agente; a etapa final devolve a falha ao job, preservando a qualidade do pipeline.
- Se `OPENAI_API_KEY` não estiver configurada, o agente falhará ao tentar analisar os testes.
- A ferramenta OpenAI API pode cobrar pelo consumo de tokens, independentemente do plano ChatGPT.
- Projetos de produção precisam de validações adicionais de entrada, testes, segurança e segregação dos privilégios do agente.
