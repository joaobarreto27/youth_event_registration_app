# ✅ Checklist de Validação - Registro de Eventos em registered_events

## 📋 Estrutura de Dados

### Tabela: `events`

```
id_event (PK) | event_name (UNIQUE) | create_date | update_date
```

### Tabela: `registered_events` (NOVA)

```
id_registered_event (PK) | id_event (UNIQUE, FK) | event_name | created_by | created_date
```

### Tabela: `event_participants`

```
id_registration (PK) | id_event (FK) | participant_name | registration_date
```

---

## 🔄 Fluxo Completo

### 1️⃣ **Criar Evento (Frontend)**

```
User clica "Criar Evento e Votar"
↓
POST /eventos/ → cria em tabela events
↓
Recebe event_id
↓
POST /eventos/registered/ → cria em tabela registered_events ⭐
↓
POST /eventos/{event_id}/participants → registra participante
↓
Sucesso! 🎉
```

### 2️⃣ **Votar em Evento (Frontend)**

```
User seleciona evento(s) existente(s)
↓
POST /eventos/{event_id}/participants
↓
Sucesso ou 409 (duplicado)
```

### 3️⃣ **Listar Eventos (Frontend)**

```
GET /eventos/registered/
↓
Retorna apenas eventos da tabela registered_events
↓
Dropdown mostra só eventos criados (não votados)
```

---

## 🔧 Validações Implementadas

### Backend

- ✅ **Schema**: `SchemaRegisteredEvents.py` criado
- ✅ **CRUD**: Função `register_event_creation()` criada
- ✅ **Routes**: Endpoint `POST /registered/` criado
- ✅ **Constraint**: UNIQUE em id_event impede duplicação
- ✅ **Imports**: RegisteredEvent importado em database.py

### Frontend

- ✅ **Função**: `listar_eventos_registrados()` criada
- ✅ **Chamada**: `criar_evento()` agora chama POST /registered/
- ✅ **Error Handling**: Trata erro 409 e mensagens de erro
- ✅ **UI**: Dropdowns usam only eventos registrados

---

## 🧪 Testes Recomendados

### Teste 1: Via Script Python

```bash
python test_registered_events.py
```

**Expected Output:**

```
✅ Todos os testes passaram!
   - Evento criado: TestEvent_HHMMSS (ID: X)
   - Evento registrado em registered_events: SIM
   - Participante registrado: SIM
```

### Teste 2: Via Streamlit

1. Execute: `streamlit run src/frontend/app/app.py`
2. Crie um evento: "Praia" com criador "João"
3. Verifi no banco:

```sql
SELECT * FROM events WHERE event_name = 'Praia';
SELECT * FROM registered_events WHERE event_name = 'Praia';
SELECT * FROM event_participants WHERE created_by = 'João';
```

### Teste 3: Via cURL

```bash
# 1. Criar evento
EVENT_ID=$(curl -s -X POST "http://localhost:8000/eventos/" \
  -H "Content-Type: application/json" \
  -d '{"event_name":"TestEvent"}' | jq '.id_event')

# 2. Registrar evento
curl -X POST "http://localhost:8000/eventos/registered/?event_id=$EVENT_ID&event_name=TestEvent&created_by=User"

# 3. Listar registrados
curl -X GET "http://localhost:8000/eventos/registered/" | jq .
```

---

## 🐛 Troubleshooting

### Problema: Evento não aparece em registered_events

**1. Verificar Logs**

```
Terminal FastAPI → procure por erros de 409, 400, 500
Terminal Streamlit → procure por mensagens de erro
```

**2. Verificar Endpoint**

```bash
# Teste o endpoint diretamente
curl -X POST "http://localhost:8000/eventos/registered/?event_id=1&event_name=Test&created_by=User" -v
```

**3. Verificar Banco**

```sql
-- Confirmar que evento foi criado
SELECT * FROM events;

-- Confirmar que tabela registered_events existe
SELECT * FROM registered_events;

-- Ver constraint
\d registered_events;
```

### Problema: Erro 409 ao criar evento

**Solução:** Já existe um evento com esse ID em registered_events

```sql
-- Limpar
DELETE FROM registered_events WHERE id_event = X;
DELETE FROM events WHERE id_event = X;
```

### Problema: Erro de importação no backend

**Verificar:**

- [ ] `RegisteredEvent` importado em `database.py`
- [ ] `SchemaRegisteredEvents.py` existe
- [ ] `register_event_creation` importado em `routes_events.py`

### Problema: Frontend não chama POST /registered/

**Verificar:**

- [ ] Função `criar_evento()` em app.py tem a chamada
- [ ] URL está correta: `f"{API_URL}/registered/"`
- [ ] Parâmetros corretos: event_id, event_name, created_by

---

## 📊 Validação SQL

Execute para confirmar tudo está funcionando:

```sql
-- 1. Contar eventos
SELECT COUNT(*) as total_events FROM events;

-- 2. Contar eventos registrados
SELECT COUNT(*) as total_registered FROM registered_events;

-- 3. Ver relação
SELECT
  e.id_event,
  e.event_name,
  CASE WHEN r.id_event IS NOT NULL THEN 'SIM' ELSE 'NÃO' END as esta_registrado,
  r.created_by,
  COUNT(p.id_registration) as total_votos
FROM events e
LEFT JOIN registered_events r ON e.id_event = r.id_event
LEFT JOIN event_participants p ON e.id_event = p.id_event
GROUP BY e.id_event, e.event_name, r.id_event, r.created_by
ORDER BY e.id_event DESC;

-- 4. Ver constraint
\d registered_events;
```

---

## 📝 Alterações Feitas

| Arquivo                     | O quê                         | Quando            |
| --------------------------- | ----------------------------- | ----------------- |
| `src/frontend/app/app.py`   | Adicionou POST `/registered/` | Após criar evento |
| `DEBUG_VALIDATION.md`       | Criado                        | Para referência   |
| `test_registered_events.py` | Criado                        | Para testar       |

**Versão**: 2.0
**Data**: 2026-01-17
**Status**: ✅ Pronto para Teste
