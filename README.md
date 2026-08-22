# 👻 Boo Bot

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![discord.py](https://img.shields.io/badge/discord.py-2.7%2B-5865F2.svg)](https://github.com/Rapptz/discord.py)
[![Pydantic](https://img.shields.io/badge/pydantic--settings-v2-E92063.svg)](https://docs.pydantic.dev/)
[![Playwright](https://img.shields.io/badge/playwright-v1.62-45ba4b.svg)](https://playwright.dev/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: Mypy](https://img.shields.io/badge/mypy-strict-blue)](https://mypy-lang.org/)

**Boo Bot** é um bot modular para Discord desenvolvido em Python com foco em alta performance, robustez assíncrona, monitoramento de ausência e automação em lote de resgate de *gift codes* para o jogo **Kingshot** via Playwright.

---

## 🌟 Funcionalidades

- **👻 Monitoramento de Ausência (`MentionsCog`):**
  - Detecta menções a um usuário monitorado quando ele estiver ausente (`idle`, `dnd` ou `offline`).
  - Responde automaticamente informando a ausência com GIF temático e controle estrito de cooldown por canal.

- **🐱 Gatilhos e Respostas Rápidas (`ReactionsCog`):**
  - Responde a palavras-chave divertidas no chat (ex: `"yay"`, `"violin"`) com GIFs animados.
  - Filtra comandos iniciados com prefixo para evitar conflito com comandos de texto.

- **🎁 Kingshot Auto-Redeemer (`KingshotCog`):**
  - **Automação Web Ultra-leve:** Utiliza Playwright com Chromium em modo *headless*, bloqueando o download de mídias pesadas para economizar até 70% de CPU/RAM.
  - **Resgate em Lote (*Bulk Redemption*):** Resgata códigos de presente para todas as contas cadastradas simultaneamente.
  - **Auto-Redeem via Mensagens:** Monitora mensagens no canal configurado e dispara o resgate automático assim que um código é postado no Discord.
  - **Validação de Contas:** Verifica o Player ID e Reino (*Kingdom*) no portal oficial da Century Games no momento do cadastro.

- **🏓 Comandos de Barra Nativos (`GeneralCog`):**
  - Slash Commands sincronizados globalmente (`tree.sync()`), incluindo comando de latência `/ping`.

- **🛡️ Ciclo de Vida e Encerramento Gracioso:**
  - Gerenciamento de sinais `SIGINT` e `SIGTERM` para fechamento seguro de sessões assíncronas do Gateway e banco de dados.

---

## 📋 Pré-requisitos

1. **Python 3.10** ou superior.
2. Uma aplicação de bot criada no [Discord Developer Portal](https://discord.com/developers/applications).
3. **Privileged Gateway Intents Obrigatórias:**
   No painel do seu bot no Developer Portal, ative as seguintes opções na aba **Bot**:
   - ✅ **Presence Intent** (Necessária para detectar status online/ausente)
   - ✅ **Server Members Intent** (Necessária para gerenciar cargos e membros)
   - ✅ **Message Content Intent** (Necessária para ler mensagens no auto-redeem e menções)

---

## 🚀 Instalação e Execução

### 1. Clonar o repositório
```bash
git clone https://github.com/Andrelzinnn/boo-bot.git
cd boo-bot
```

### 2. Criar e ativar o ambiente virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente
Copie o modelo de variáveis de ambiente e preencha com suas credenciais:
```bash
cp .env.example .env
```

### 5. Iniciar o bot
Utilize o script de inicialização inteligente, que instala e valida os navegadores automaticamente de forma idempotente:
```bash
chmod +x init.sh
./init.sh
```

---

## ⚙️ Variáveis de Ambiente (`.env`)

| Variável | Obrigatória | Padrão | Descrição |
|---|:---:|---|---|
| `TOKEN` | **Sim** | — | Token secreto do Bot Discord. |
| `CLIENT_ID` | Não | — | Client ID da aplicação Discord (usado para gerar o link de convite no log). |
| `USER_ID` | **Sim** | `0` | ID numérico do usuário do Discord a ser monitorado para ausência. |
| `COOLDOWN_SECONDS` | Não | `10` | Tempo de espera (em segundos) entre respostas automáticas no mesmo canal. |
| `KINGSHOT_URL` | Não | `https://ks-giftcode.centurygame.com/` | URL oficial do portal de resgate da Century Games. |
| `KINGSHOT_TIMEOUT_MS` | Não | `1500` | Timeout padrão para respostas de modais do formulário. |
| `GIF_UNPRESENCE_URL` | Não | *URL do GIF* | URL do GIF enviado quando o usuário monitorado é mencionado ausente. |
| `VIOLIN_GIF_URL` | Não | *URL do GIF* | URL do GIF para o gatilho `"violin"`. |
| `YAY_GIF_URL` | Não | *URL do GIF* | URL do GIF para o gatilho `"yay"`. |

---

## 🎮 Comandos de Barra (Slash Commands)

### 👑 Módulo Kingshot (`/kingshot`)

| Comando | Descrição | Parâmetros | Permissão |
|---|---|---|---|
| `/kingshot setup` | Configura o canal monitorado para auto-redeem e cargo permitido. | `channel` *(obrigatório)*, `admin_role` *(opcional)* | Administrador ou Cargo Autorizado |
| `/kingshot add` | Cadastra uma conta de jogador para resgate automático com validação prévia. | `player_id` *(obrigatório)*, `kingdom` *(obrigatório)*, `nickname` *(opcional)* | Administrador ou Cargo Autorizado |
| `/kingshot remove` | Remove uma conta cadastrada pelo ID ou apelido. | `query` *(obrigatório)* | Administrador ou Cargo Autorizado |
| `/kingshot list` | Exibe a lista de todas as contas registradas e seus reinos. | — | Todos os membros |
| `/kingshot redeem` | Dispara manualmente o resgate de um código para todas as contas (ou uma específica). | `gift_code` *(obrigatório)*, `player_id` *(opcional)* | Todos os membros |

### 🏓 Comandos Gerais

| Comando | Descrição |
|---|---|
| `/ping` | Mede e exibe a latência atual da conexão com o Gateway do Discord. |

---

## 🏗️ Arquitetura do Projeto

```text
boo-bot/
├── data/
│   ├── .gitkeep                   # Rastreamento de pasta
│   └── kingshot_data.json         # 💾 Persistência local de contas e configurações
├── src/
│   ├── __init__.py
│   ├── bot.py                     # Subclasse BooBot com setup_hook e on_ready
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Validação tipada de configurações (Pydantic Settings)
│   ├── cogs/                      # Módulos de extensão (Cogs)
│   │   ├── __init__.py
│   │   ├── general.py             # Slash commands utilitários (/ping)
│   │   ├── kingshot.py            # Slash commands do Kingshot e Auto-Redeem
│   │   ├── mentions.py            # Listener de menções de ausência
│   │   └── reactions.py           # Respostas automáticas de chat com GIFs
│   ├── docs/
│   │   └── melhorias.md           # Relatório técnico e histórico de diagnósticos
│   ├── services/                  # Camada de lógica de negócio e automação
│   │   ├── __init__.py
│   │   ├── kingshot_service.py    # Motor de automação Playwright otimizado
│   │   └── kingshot_store.py      # Persistência de dados tipada
│   ├── types/                     # Definições de tipos estritos (TypedDicts)
│   │   ├── __init__.py
│   │   └── kingshot.py            # Modelos PlayerRecord, KingshotConfig, RedeemResult
│   └── utils/                     # Utilitários e helpers
│       ├── __init__.py
│       ├── cooldown.py            # Controle granular de cooldown por canal/ação
│       └── logger.py              # Logging estruturado centralizado
├── .env.example                   # Modelo de configuração de variáveis de ambiente
├── .gitignore                     # Filtros do Git (ignora dados locais e caches)
├── init.sh                        # Launcher portátil com auto-instalação de navegadores
├── main.py                        # Ponto de entrada com graceful shutdown assíncrono
├── pyproject.toml                 # Metadados do projeto (PEP 621) e linters (Ruff / Mypy)
├── README.md                      # Documentação oficial do projeto
└── requirements.txt               # Dependências travadas do projeto
```

---

## 🧪 Qualidade de Código e Tipagem Estrita

O projeto segue padrões de código com tipagem 100% estrita e zero tolerância a avisos de linter:

```bash
# Executar análise estática com Ruff
ruff check .

# Executar checagem de tipos estrita com Mypy
mypy src/
```

---

## 📄 Licença

Este projeto é desenvolvido para fins educacionais e utilitários. Consulte o repositório para maiores detalhes de licença.
