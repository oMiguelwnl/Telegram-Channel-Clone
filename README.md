# 🤖 Telegram Channel & Group Cloner

Um script avançado em **Python** para **clonar canais e grupos do Telegram**, com suporte a **salvamento de progresso**, **continuação automática** e **gerenciamento de múltiplas clonagens**.  
Baseado na biblioteca **Pyrogram**, o script permite copiar mensagens entre canais, grupos ou supergrupos de forma automatizada — **inclusive de grupos com envio bloqueado**.

---

## ⚙️ Funcionalidades

- 🧠 Clonagem completa de canais e grupos (mensagens, mídias e arquivos)  
- 💾 Salvamento automático de progresso em arquivos `.json`  
- 🔄 Continuação de clonagens interrompidas  
- 🧱 Pode clonar **grupos onde o envio de mensagens está bloqueado** (apenas leitura)  
- 🚀 Suporte a diferentes modos:
  - **Encaminhar** (mantém autoria original)
  - **Copiar** (envia como você)
- ⏳ Detecção automática de `FloodWait` e pausa inteligente  
- 🧩 Interface interativa no terminal

---

## 📁 Estrutura do Projeto

```

├── clone.py           # Script principal de clonagem
├── config.ini         # Arquivo de configuração com API ID e API Hash
├── user.session       # Sessão do Pyrogram (gerada automaticamente)
├── *.json             # Arquivos de progresso salvos (um por clonagem)

````

---

## 🧰 Requisitos

- Python 3.8+
- Conta Telegram com **API ID** e **API Hash**  
  (obtenha em [https://my.telegram.org/apps](https://my.telegram.org/apps))
- Biblioteca **Pyrogram**

---

## 📦 Instalação

```bash
pip install pyrogram tgcrypto
````

---

## 🚀 Uso

Execute o script no terminal:

```bash
python clone.py
```

Se for a primeira execução, será solicitado o **API ID** e **API Hash**, que serão salvos em `config.ini`.

---

## 🧭 Menu principal

Após a conexão, o programa mostrará um menu interativo:

```
1. 🆕 Nova Clonagem
2. 🔄 Continuar Clonagem
3. 📊 Ver Clonagens Salvas
4. 🔍 Verificar Chats
5. ❌ Sair
```

### 🆕 Nova Clonagem

Permite configurar uma nova clonagem informando:

* Nome da clonagem
* Canal ou grupo de origem (ID ou @username)
* Canal ou grupo de destino (ID ou @username)
* Tipo (Encaminhar ou Copiar)

O progresso é salvo automaticamente a cada 10 mensagens.

> 💡 Mesmo que o grupo de origem tenha o **envio bloqueado**, o script ainda consegue **ler e clonar todas as mensagens**.

---

### 🔄 Continuar Clonagem

Retoma automaticamente a clonagem a partir do ponto onde parou, usando o arquivo `.json` salvo anteriormente.

---

### 📊 Ver Clonagens Salvas

Exibe todas as clonagens já criadas, com status, quantidade de mensagens e data da última atualização.

---

### 🔍 Verificar Chats

Lista todos os grupos e canais que o usuário pode acessar, mostrando seus IDs e nomes.

---

## 💾 Sistema de salvamento

Cada clonagem é salva em um arquivo JSON com o seguinte formato:

```json
{
  "clone_name": "canal_teste",
  "source_channel": "-1001234567890",
  "destination_channel": "-1009876543210",
  "last_message_id": 42,
  "total_messages": 500,
  "processed_messages": 120,
  "last_update": "2025-11-08T10:00:00",
  "status": "in_progress"
}
```

Esses arquivos permitem continuar uma clonagem a qualquer momento.

---

## 🧠 Exemplos de uso

### Clonar grupo A → grupo B (mesmo com envio bloqueado)

1. Execute `python clone.py`
2. Escolha `1. Nova Clonagem`
3. Insira:

   * Nome: `clone_grupo`
   * Origem: `@grupoA` (mesmo se for somente leitura)
   * Destino: `@grupoB`
   * Tipo: `2 (Copiar)`
4. Aguarde o processo. O script mostrará o progresso e salvará automaticamente.

---

## ⚠️ Cuidados

* Use apenas em canais ou grupos **onde você tem permissão para ler mensagens**.
* Grupos com envio bloqueado podem ser clonados normalmente, **desde que as mensagens sejam públicas ou visíveis**.
* Mensagens de tipo não suportado (ex: enquetes, jogos, etc.) são ignoradas automaticamente.

---

## 🧾 Licença

Este projeto é de uso **pessoal e educacional**.
Você pode modificar e adaptar conforme suas necessidades.

---

## ✨ Autor

Desenvolvido por **Miguel Rafael**
[github.com/oMiguelwnl](https://github.com/oMiguelwnl)

```
