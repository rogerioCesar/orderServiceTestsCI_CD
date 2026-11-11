# Tutorial detalhado — migrar para Ollama com self-hosted runner

## 0. Premissas

- Linux com Git, Python 3 e `venv` (usuário do laboratório já utilizou Linux no VS Code).
- Conta GitHub, repositório **privado**, PR em branch própria.
- A máquina permanece ligada durante o job.
- `runs-on: [self-hosted, linux, devops-genai-ollama]`: label obrigatória do runner.
- Não utilizar chaves da OpenAI; `GITHUB_TOKEN` é criado pelo Actions.

## 1. Instale e teste o Ollama

Consulte https://docs.ollama.com/linux. Para Linux com systemd, siga a instalação oficial:

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl status ollama
```

Se o serviço não estiver disponível (por exemplo, WSL sem systemd), em outro terminal rode `ollama serve` e deixe-o aberto.

```bash
curl http://127.0.0.1:11434/api/tags
ollama pull qwen2.5-coder:3b-instruct
ollama list
ollama run qwen2.5-coder:3b-instruct
```

Digite `Explique TypeError de Python ao somar float e str` e encerre o chat com `/bye`.

Não configure `OLLAMA_HOST=0.0.0.0`: localhost basta e não deve ser exposto.

## 2. Registre um self-hosted runner

Acesse seu repositório no GitHub > **Settings > Actions > Runners > New self-hosted runner**. Selecione **Linux** e a arquitetura correta (`uname -m`). **Copie os comandos de download e configuração EXATAMENTE da tela**, pois a versão e o token de registro são específicos e podem expirar. Não compartilhe o token.

- Crie a pasta `~/actions-runner-ollama`, fora da pasta do projeto.
- Execute os comandos de download e extração do GitHub nessa pasta.
- Execute o `./config.sh` mostrado no GitHub (ou responda às perguntas interativas).
- Nome sugerido: `runner-ollama-local`.
- Em **additional labels**, informe `devops-genai-ollama`.
- Diretório de trabalho: `_work`.
- Inicie com `./run.sh` e deixe o terminal aberto.
- Confira em GitHub **Settings > Actions > Runners** o status `Idle`/`Online`.

Caso já tenha executado a configuração SEM a label, adicione-a na página de gerenciamento do runner no GitHub antes de disparar o workflow. Ela deve corresponder exatamente à label no YAML.

**Opcional (Linux com systemd):** depois de configurar e testar com `./run.sh`, pare o runner (Ctrl+C) e execute na pasta do runner:

```bash
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

Não execute o runner como root. Se estiver em WSL, confira suporte a `systemd` antes de escolher modo serviço. Documentação: https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners e https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application.

## 3. Migre somente três arquivos no projeto atual

Na sua pasta local `~/Downloads/devops-genai-github` já versionada, substitua a partir deste pacote:

- `genai_analyst.py`
- `.github/workflows/devops-genai.yml`
- `requirements.txt`

**Não copie `app.py` se o TypeError estiver presente no Pull Request** — precisamos preservar a falha para disparar a IA. O YAML novo usa `self-hosted` e não pede `OPENAI_API_KEY`. Você pode remover o secret antigo se não for mais necessário.

Ao migrar, não deixe a versão antiga do workflow em outro arquivo `.yml` na pasta `.github/workflows`, ou haverá dois workflows.

## 4. Teste a inferência local antes do GitHub

Entre no diretório do projeto e gere um log:

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -v --tb=short > pytest.log 2>&1
python3 genai_analyst.py --local
```

Os testes devem falhar enquanto `app.py` contiver a soma incompatível. O script imprime um diagnóstico real, fornecido pelo modelo local. Se o comando `pytest` retornar exit code 1, isso é **esperado** nesta etapa.

Se o sistema impedir pip fora de `venv`, ative a `.venv` já existente ou crie uma (`python3 -m venv .venv && source .venv/bin/activate`).

## 5. Atualize o Pull Request

```bash
git status
git branch --show-current
git add genai_analyst.py .github/workflows/devops-genai.yml requirements.txt
git commit -m "Migrar diagnostico GenAI para Ollama local"
git push
```

A branch deve ser sua `feature/erro-frete` (ou a branch utilizada no PR), apontando para `main`.

O runner deve estar `Online`, o Ollama deve responder em `127.0.0.1:11434`, o modelo deve estar instalado e a internet deve estar ativa.

Ao fazer `git push` na branch do PR, o GitHub Actions dispara o workflow. Ele irá:

1. baixar o código do PR no runner local;
2. instalar dependências em `.venv-ci`;
3. verificar o serviço Ollama e a disponibilidade do modelo;
4. executar `pytest` e salvar `pytest.log`;
5. se falhou, consultar o Qwen2.5-Coder via API local;
6. publicar a resposta no PR com `GITHUB_TOKEN` e a permissão `issues: write`;
7. manter o job vermelho até os testes ficarem verdes.

## 6. Corrija e valide

No `app.py`, restaure:

```python
return base_price + float(tax_rate)
```

Execute `python3 -m pytest -v`. Faça `git add app.py && git commit -m 'Corrigir erro de tipo no frete' && git push`. O mesmo PR dispara outra execução que deve terminar verde.

## 7. Evidências para o fórum

Registre: PR criado, logs com TypeError, job Ollama finalizado, comentário do bot no PR, e segunda execução com testes passando. Discuta limitações: velocidade dependente do hardware, proteção contra prompt injection, risco de acesso ao runner local, revisão humana antes de aplicar a sugestão.

## 8. Diagnóstico de problemas

- **Job em Queued**: runner Offline, label `devops-genai-ollama` ausente ou não corresponde, PC desligado.
- **`curl: Could not connect to server`**: Ollama não iniciou (`systemctl`/`ollama serve`).
- **`ollama show` falhou**: execute `ollama pull qwen2.5-coder:3b-instruct` no serviço correto.
- **`python3 -m venv` falhou**: instalar `python3-venv` via gerenciador da distribuição.
- **Modelo demora ou sai por memória**: feche aplicações, reduza tamanho do modelo; para trocar utilize `ollama pull qwen2.5-coder:1.5b`, e altere `OLLAMA_MODEL` no YAML e no teste local.
- **`GitHub recusou o comentário: HTTP 403`**: verifique `issues: write`, políticas do repositório e Workflow permissions em Settings > Actions > General.
- **Agente não rodou**: confirmação de que `steps.testes.outcome == failure` e o guard do owner permitiu o PR.
- **GitHub Action em vermelho após a resposta**: esperado enquanto o defeito intencional continuar presente.
- **Comando `ollama` não encontrado no runner**: seu serviço pode estar instalado em um PATH diferente do usuário que executa o runner; teste a partir da conta do runner.

## 9. Segurança (indispensável)

- Repositório privado; **não aceite contribuições desconhecidas**. Self-hosted não isola código de PR automaticamente.
- Não rode o runner com `sudo`/root e não use a máquina do trabalho ou com segredos de produção.
- Não exponha `11434` à internet; preferir bind em 127.0.0.1.
- O workflow limita execução a PRs internos cujo ator é o proprietário; isso **não substitui** uma política de confiança.
- Não envie logs confidenciais para o agente. Mesmo com inferência local, o comentário vai ao GitHub.
- Mantenha Ollama, Linux, GitHub runner e actions atualizados.
- A IA **não** altera código; apenas produz um comentário técnico de apoio.

## Referências oficiais

- GitHub runners: https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners
- GitHub segurança: https://docs.github.com/en/actions/reference/security/secure-use
- Ollama Linux: https://docs.ollama.com/linux
- Ollama API: https://docs.ollama.com/api/chat
- Modelo: https://ollama.com/library/qwen2.5-coder:3b-instruct
