# 🔍 Validação de Registro de Eventos em registered_events

## Checklist de Validação

### 1. **Backend - Função `register_event_creation` em create_crud.py**

- ✅ Função está definida corretamente (linhas 384-432)
- ✅ Valida se evento existe em `events`
- ✅ Valida se evento já foi registrado em `registered_events` (409)
- ✅ Usa `RegisteredEvent` ORM para inserir
- ✅ Faz `db.add()` e `db.commit()`

### 2. **Backend - Endpoint POST /registered/ em routes_events.py**

- ✅ Endpoint está definido (linhas 152-156)
- ✅ Recebe parâmetros: event_id, event_name, created_by
- ✅ Retorna ValidatorRegisteredEventResponse
- ✅ Usa db.Session = Depends(get_db)

### 3. **Frontend - Função `criar_evento()` em app.py**

- ✅ Criado evento primeiro com POST /
- ✅ Obtém event_id da resposta
- ✅ **AGORA CHAMA** POST /registered/ com params
- ✅ Registra criador como participante

### 4. **Database.py - Imports**

- ✅ RegisteredEvent está importado
- ✅ RegisteredEvent está na inicialização

## Como Testar

### Teste 1: Criar evento via API (sem Streamlit)

```bash
# Criar evento
curl -X POST "http://localhost:8000/eventos/" \
  -H "Content-Type: application/json" \
  -d '{"event_name": "Praia Test"}'

# Resposta deve ter id_event, ex: {"id_event": 1, "event_name": "Praia Test", ...}

# Registrar evento com esse ID
curl -X POST "http://localhost:8000/eventos/registered/?event_id=1&event_name=Praia%20Test&created_by=João" \
  -H "Content-Type: application/json"

# Listar eventos registrados
curl -X GET "http://localhost:8000/eventos/registered/"
```

### Teste 2: Criar evento via Frontend

1. Abra o Streamlit: `streamlit run src/frontend/app/app.py`
2. Em "Criar Novo Evento":
   - Nome: "Boliche"
   - Nome do Criador: "Maria"
   - Clique em "Criar Evento e Votar"
3. Verifique no banco de dados:
   ```sql
   SELECT * FROM events WHERE event_name = 'Boliche';
   SELECT * FROM registered_events WHERE event_name = 'Boliche';
   SELECT * FROM event_participants WHERE participant_name = 'Maria';
   ```

### Teste 3: Verificar Logs

Se houver erro, veja:

1. Terminal do FastAPI - procure por erros
2. Terminal do Streamlit - procure por mensagens de erro
3. Response do POST /registered/ - deve estar retornando erro ou sucesso

## Possíveis Problemas

### Problema 1: Endpoint retorna 404

- Verifique se a rota está registrada: `router_events.post("/registered/")`
- Verifique se o prefix está correto em main.py: `prefix="/eventos"`

### Problema 2: Função não é chamada

- Verifique se `register_event_creation` está importada em routes_events.py
- Verifique se está no `from ..crud.create_crud import ...`

### Problema 3: Erro 409 (evento já registrado)

- Significa que registrou uma vez mas tentou registrar novamente
- Limpar e recriar o evento

### Problema 4: Erro de integração entre eventos e registered_events

- Verifique Foreign Key constraint
- Verifique se event_id existe em events antes de inserir em registered_events

## Commands para Limpar Base (se necessário)

```sql
-- Deletar dados de teste
DELETE FROM event_participants WHERE event_id IN (SELECT id_event FROM events WHERE event_name LIKE '%Test%');
DELETE FROM registered_events WHERE event_name LIKE '%Test%';
DELETE FROM events WHERE event_name LIKE '%Test%';

-- Verificar estado
SELECT COUNT(*) as total_events FROM events;
SELECT COUNT(*) as total_registered FROM registered_events;
SELECT COUNT(*) as total_participants FROM event_participants;
```

## Resumo da Correção Feita

### Frontend (app.py)

- Adicionado chamada `requests.post(f"{API_URL}/registered/", params={...})`
- Após criar evento (POST /)
- Com dados: event_id, event_name, created_by
- Trata erro 409 se for chamado duas vezes

### Backend

- Nenhuma mudança necessária ✅
- Já estava implementado corretamente
