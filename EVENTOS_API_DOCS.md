# 📋 API de Eventos - Documentação

## Visão Geral

Sistema de cadastro de eventos juvenis com suporte CRUD completo. Cada evento possui:

- **ID**: Identificador único (auto-incrementado)
- **Nome do Evento**: Campo obrigatório e único
- **Descrição**: Campo opcional com detalhes do evento
- **Data de Criação**: Registrada automaticamente ao criar
- **Data de Atualização**: Registrada automaticamente ao atualizar

## Endpoints

### 1. Listar Todos os Eventos

**GET** `/eventos/`

**Response:** Array de eventos

```json
[
  {
    "id_event": 1,
    "event_name": "Festa Juvenil 2026",
    "event_description": "Celebração de confraternização",
    "create_date": "2026-01-17T10:30:00+00:00",
    "update_date": "2026-01-17T10:30:00+00:00"
  }
]
```

### 2. Obter Evento por ID

**GET** `/eventos/{event_id}`

**Path Parameters:**

- `event_id` (int): ID do evento

**Response:** Objeto do evento

```json
{
  "id_event": 1,
  "event_name": "Festa Juvenil 2026",
  "event_description": "Celebração de confraternização",
  "create_date": "2026-01-17T10:30:00+00:00",
  "update_date": "2026-01-17T10:30:00+00:00"
}
```

### 3. Criar Novo Evento

**POST** `/eventos/`

**Request Body:**

```json
{
  "event_name": "Festa Juvenil 2026",
  "event_description": "Celebração de confraternização"
}
```

**Response:** Evento criado com ID e datas

```json
{
  "id_event": 1,
  "event_name": "Festa Juvenil 2026",
  "event_description": "Celebração de confraternização",
  "create_date": "2026-01-17T10:30:00+00:00",
  "update_date": "2026-01-17T10:30:00+00:00"
}
```

### 4. Atualizar Evento

**PUT** `/eventos/{event_id}`

**Path Parameters:**

- `event_id` (int): ID do evento

**Request Body:**

```json
{
  "event_name": "Festa Juvenil 2026 - Atualizado",
  "event_description": "Nova descrição"
}
```

**Response:** Evento atualizado

```json
{
  "id_event": 1,
  "event_name": "Festa Juvenil 2026 - Atualizado",
  "event_description": "Nova descrição",
  "create_date": "2026-01-17T10:30:00+00:00",
  "update_date": "2026-01-17T11:00:00+00:00"
}
```

### 5. Deletar Evento

**DELETE** `/eventos/{event_id}`

**Path Parameters:**

- `event_id` (int): ID do evento

**Response:** Mensagem de sucesso

```json
{
  "detail": "Evento 1 deletado com sucesso"
}
```

## Códigos HTTP

| Código | Significado                              |
| ------ | ---------------------------------------- |
| 200    | OK - Requisição bem-sucedida             |
| 201    | Created - Recurso criado                 |
| 400    | Bad Request - Dados inválidos            |
| 404    | Not Found - Evento não encontrado        |
| 500    | Internal Server Error - Erro do servidor |

## Validações

### Campo: event_name

- ✅ Obrigatório
- ✅ Máximo 255 caracteres
- ✅ Deve ser único na tabela
- ✅ Não pode estar vazio

### Campo: event_description

- ✅ Opcional
- ✅ Máximo 1000 caracteres

## Estrutura do Banco de Dados

```sql
CREATE TABLE events (
    id_event SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL UNIQUE,
    event_description TEXT,
    create_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Exemplos de Uso

### cURL

**Criar evento:**

```bash
curl -X POST "http://localhost:8000/eventos/" \
  -H "Content-Type: application/json" \
  -d '{"event_name":"Festa 2026","event_description":"Descrição"}'
```

**Listar eventos:**

```bash
curl "http://localhost:8000/eventos/"
```

**Obter evento específico:**

```bash
curl "http://localhost:8000/eventos/1"
```

**Atualizar evento:**

```bash
curl -X PUT "http://localhost:8000/eventos/1" \
  -H "Content-Type: application/json" \
  -d '{"event_name":"Novo Nome"}'
```

**Deletar evento:**

```bash
curl -X DELETE "http://localhost:8000/eventos/1"
```

### Python (requests)

```python
import requests

# Criar evento
response = requests.post(
    "http://localhost:8000/eventos/",
    json={
        "event_name": "Festa 2026",
        "event_description": "Descrição do evento"
    }
)
print(response.json())

# Listar eventos
response = requests.get("http://localhost:8000/eventos/")
print(response.json())

# Obter evento específico
response = requests.get("http://localhost:8000/eventos/1")
print(response.json())

# Atualizar evento
response = requests.put(
    "http://localhost:8000/eventos/1",
    json={"event_name": "Novo Nome"}
)
print(response.json())

# Deletar evento
response = requests.delete("http://localhost:8000/eventos/1")
print(response.json())
```

## Arquivos da Aplicação

- `schemas/SchemaEvents.py` - Modelo SQLAlchemy
- `validator/EventValidatorSchema.py` - Validadores Pydantic
- `crud/create_crud.py` - Funções CRUD
- `routes/routes_events.py` - Endpoints da API
- `sql/query/` - Queries SQL reutilizáveis
  - `create_event.sql`
  - `get_all_events.sql`
  - `get_event_by_id.sql`
  - `update_event.sql`
  - `delete_event.sql`
