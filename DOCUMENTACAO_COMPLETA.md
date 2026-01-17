# 📋 Sistema de Registro de Eventos e Participantes

## 🎯 Visão Geral

Sistema web para **cadastro de eventos e registro de participantes**.

### Conceito Principal

- **Criar eventos**: Nome e descrição do evento (ex: "Praia", "Festa Juvenil")
- **Registrar participantes**: Cada pessoa pode se registrar **uma única vez EM CADA evento**
- **Múltiplos eventos**: Uma pessoa pode registrar em **quantos eventos ela quiser**
- **Gerenciar registros**: Atualizar ou remover registros de participantes

### Exemplo

```
João pode se registrar em múltiplos eventos:
├── Evento: "Praia"       → João registrado ✅
├── Evento: "Boliche"     → João registrado ✅
├── Evento: "Festa"       → João registrado ✅
└── Evento: "Praia" (novo) → João não pode ❌ (já está registrado)

Maria:
├── Evento: "Praia"       → Maria registrada ✅
├── Evento: "Boliche"     → Maria pode registrar ✅
└── Evento: "Festa"       → Maria pode registrar ✅

Fluxo:
1. João se registra em "Praia" → ✅ OK
2. João se registra em "Boliche" → ✅ OK
3. João tenta se registrar em "Praia" novamente → ❌ Erro 409
4. João se registra em "Festa" → ✅ OK
```

---

## 📊 Estrutura do Banco de Dados

### Tabela: `events`

```sql
id_event          (INT, PRIMARY KEY)
event_name        (VARCHAR 255, UNIQUE)
event_description (TEXT, NULL)
create_date       (TIMESTAMP, auto)
update_date       (TIMESTAMP, auto)
```

### Tabela: `event_participants`

```sql
id_registration   (INT, PRIMARY KEY)
id_event          (INT, FOREIGN KEY → events)
participant_name  (VARCHAR 255)
participant_email (VARCHAR 255, NULL)
participant_phone (VARCHAR 20, NULL)
registration_date (TIMESTAMP, auto)

UNIQUE CONSTRAINT: (id_event, participant_name)
↑ Garante: Uma pessoa por evento (não por sistema)
```

---

## 🔌 API Endpoints

### EVENTOS

#### 1️⃣ Listar todos os eventos

```
GET /eventos/
```

**Response:**

```json
[
  {
    "id_event": 1,
    "event_name": "Praia",
    "event_description": "Passeio na praia",
    "create_date": "2026-01-17T10:00:00+00:00",
    "update_date": "2026-01-17T10:00:00+00:00"
  },
  {
    "id_event": 2,
    "event_name": "Festa Juvenil",
    "event_description": "Confraternização",
    "create_date": "2026-01-17T10:30:00+00:00",
    "update_date": "2026-01-17T10:30:00+00:00"
  }
]
```

#### 2️⃣ Criar novo evento

```
POST /eventos/
```

**Request:**

```json
{
  "event_name": "Praia",
  "event_description": "Passeio na praia"
}
```

**Response:**

```json
{
  "id_event": 1,
  "event_name": "Praia",
  "event_description": "Passeio na praia",
  "create_date": "2026-01-17T10:00:00+00:00",
  "update_date": "2026-01-17T10:00:00+00:00"
}
```

#### 3️⃣ Obter evento específico

```
GET /eventos/{event_id}
```

#### 4️⃣ Atualizar evento

```
PUT /eventos/{event_id}
```

**Request:**

```json
{
  "event_name": "Praia - Atualizado",
  "event_description": "Nova descrição"
}
```

#### 5️⃣ Deletar evento

```
DELETE /eventos/{event_id}
```

**Response:**

```json
{
  "detail": "Evento 1 deletado com sucesso"
}
```

---

### PARTICIPANTES

#### 1️⃣ Registrar participante em evento

```
POST /eventos/{event_id}/participants
```

**Request:**

```json
{
  "participant_name": "João Silva",
  "participant_email": "joao@example.com",
  "participant_phone": "11987654321"
}
```

**Response:**

```json
{
  "id_registration": 1,
  "id_event": 1,
  "participant_name": "João Silva",
  "participant_email": "joao@example.com",
  "participant_phone": "11987654321",
  "registration_date": "2026-01-17T10:15:00+00:00"
}
```

**❌ Erro se tentar registrar novamente:**

```json
{
  "detail": "Participante 'João Silva' já está registrado neste evento!"
}
```

#### 2️⃣ Listar participantes de um evento

```
GET /eventos/{event_id}/participants
```

**Response:**

```json
[
  {
    "id_registration": 1,
    "id_event": 1,
    "participant_name": "João Silva",
    "participant_email": "joao@example.com",
    "participant_phone": "11987654321",
    "registration_date": "2026-01-17T10:15:00+00:00"
  },
  {
    "id_registration": 2,
    "id_event": 1,
    "participant_name": "Maria Santos",
    "participant_email": "maria@example.com",
    "participant_phone": "11912345678",
    "registration_date": "2026-01-17T10:20:00+00:00"
  }
]
```

#### 3️⃣ Obter detalhes de um registro

```
GET /eventos/participants/{registration_id}
```

#### 4️⃣ Atualizar registro de participante

```
PUT /eventos/participants/{registration_id}
```

**Request:**

```json
{
  "participant_email": "novo_email@example.com",
  "participant_phone": "11999999999"
}
```

#### 5️⃣ Remover participante de um evento

```
DELETE /eventos/participants/{registration_id}
```

**Response:**

```json
{
  "detail": "Participante 1 removido do evento com sucesso"
}
```

---

## 🔐 Validações e Regras de Negócio

### Eventos

- ✅ **event_name**: Obrigatório, máximo 255 caracteres, ÚNICO
- ✅ **event_description**: Opcional, máximo 1000 caracteres
- ✅ Data de criação e atualização automáticas

### Participantes

- ✅ **participant_name**: Obrigatório, máximo 255 caracteres
- ✅ **participant_email**: Opcional, máximo 255 caracteres
- ✅ **participant_phone**: Opcional, máximo 20 caracteres
- ✅ **REGRA PRINCIPAL**: Cada pessoa pode se registrar **UMA ÚNICA VEZ** por evento
- ✅ Deletar evento remove todos os participantes (CASCADE)

---

## 📝 Códigos HTTP

| Código | Significado                              |
| ------ | ---------------------------------------- |
| 200    | OK - Requisição bem-sucedida             |
| 400    | Bad Request - Dados inválidos            |
| 404    | Not Found - Recurso não encontrado       |
| 409    | Conflict - Participante já registrado    |
| 500    | Internal Server Error - Erro do servidor |

---

## 💻 Exemplos de Uso

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Criar evento
response = requests.post(
    f"{BASE_URL}/eventos/",
    json={
        "event_name": "Praia",
        "event_description": "Passeio na praia"
    }
)
event_id = response.json()["id_event"]

# 2. Registrar participante
response = requests.post(
    f"{BASE_URL}/eventos/{event_id}/participants",
    json={
        "participant_name": "João Silva",
        "participant_email": "joao@example.com",
        "participant_phone": "11987654321"
    }
)
print(response.json())

# 3. Listar participantes
response = requests.get(f"{BASE_URL}/eventos/{event_id}/participants")
print(response.json())

# 4. Tentar registrar novamente (erro)
response = requests.post(
    f"{BASE_URL}/eventos/{event_id}/participants",
    json={"participant_name": "João Silva"}
)
print(response.status_code)  # 409 Conflict
print(response.json())  # Erro: já registrado
```

### cURL

```bash
# Criar evento
curl -X POST "http://localhost:8000/eventos/" \
  -H "Content-Type: application/json" \
  -d '{"event_name":"Praia","event_description":"Passeio na praia"}'

# Registrar participante (event_id = 1)
curl -X POST "http://localhost:8000/eventos/1/participants" \
  -H "Content-Type: application/json" \
  -d '{"participant_name":"João Silva","participant_email":"joao@example.com"}'

# Listar participantes
curl "http://localhost:8000/eventos/1/participants"

# Remover participante (registration_id = 1)
curl -X DELETE "http://localhost:8000/eventos/participants/1"
```

---

## 📁 Estrutura de Arquivos

```
src/backend/app/
├── schemas/
│   ├── SchemaEvents.py              ← Modelo do evento
│   └── SchemaEventParticipants.py   ← Modelo do participante
├── validator/
│   ├── EventValidatorSchema.py       ← Validadores de evento
│   └── ParticipantValidatorSchema.py ← Validadores de participante
├── crud/
│   └── create_crud.py                ← Lógica CRUD
├── routes/
│   └── routes_events.py              ← Endpoints da API
├── sql/query/
│   ├── create_event.sql
│   ├── get_all_events.sql
│   ├── get_event_by_id.sql
│   ├── update_event.sql
│   ├── delete_event.sql
│   ├── register_participant.sql
│   ├── get_event_participants.sql
│   ├── get_participant_by_id.sql
│   ├── update_participant.sql
│   └── delete_participant.sql
└── main.py                           ← Aplicação principal
```

---

## 🚀 Como Usar

### 1. Setup Inicial

```bash
# Criar tabelas no banco
psql -U user -d database -f src/backend/app/sql/create_tables.sql
```

### 2. Iniciar Servidor

```bash
cd c:\projects\youth_event_registration_app
uvicorn src.backend.app.main:app --reload --port 8000
```

### 3. Acessar API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API: http://localhost:8000/eventos

---

## ✨ Recursos

- ✅ CRUD completo de eventos
- ✅ CRUD completo de participantes
- ✅ Validação de unicidade (uma pessoa por evento)
- ✅ Queries SQL reutilizáveis
- ✅ Tratamento de erros robusto
- ✅ Documentação automática (Swagger)
- ✅ Timestamps automáticos

---

**Versão:** 2.0  
**Data:** 17 de janeiro de 2026  
**Status:** ✅ Pronto para uso
