# 🚀 GUIA RÁPIDO DE TESTE

## ⚡ Teste Rápido (2 minutos)

### 1. Abra 3 terminais

**Terminal 1 - API**

```bash
cd c:\projects\youth_event_registration_app
uvicorn src.backend.app.main:app --reload
```

✅ Esperado: `Uvicorn running on http://127.0.0.1:8000`

**Terminal 2 - Frontend**

```bash
cd c:\projects\youth_event_registration_app
streamlit run src/frontend/app/app.py
```

✅ Esperado: `You can now view your Streamlit app in your browser`

**Terminal 3 - Teste**

```bash
cd c:\projects\youth_event_registration_app
python test_registered_events.py
```

✅ Esperado:

```
============================================================
  VALIDAÇÃO DE REGISTRO DE EVENTOS
============================================================

✅ Todos os testes passaram!
   - Evento criado: TestEvent_HHMMSS (ID: X)
   - Evento registrado em registered_events: SIM
   - Participante registrado: SIM
```

---

## 🎯 Teste no Streamlit

1. Abra browser: `http://localhost:8501`
2. Em "Criar Novo Evento":
   - **Nome do Criador**: João
   - **Nome do Evento**: Praia
3. Clique: **Criar Evento e Votar**
4. Resultado esperado:
   ```
   ✅ Evento criado: Praia
   ✅ Voto registrado em: Praia
   ```
5. Em abas: **👥 Participantes por Evento**
   - Deve aparecer aba "🎉 Praia"
   - Deve mostrar: João como participante

---

## 📊 Verificação no Banco (SQL)

```bash
# Conecte ao banco PostgreSQL
psql -U seu_user -d sua_database

# Execute:
SELECT * FROM events WHERE event_name LIKE '%Praia%';
SELECT * FROM registered_events WHERE event_name LIKE '%Praia%';
SELECT * FROM event_participants WHERE participant_name = 'João';
```

Esperado: 3 registros aparecerão (um em cada tabela)

---

## ✅ Sucesso!

Se os 3 testes passaram, significa que:

- ✅ Evento foi criado em `events`
- ✅ Evento foi registrado em `registered_events`
- ✅ Participante foi registrado em `event_participants`
- ✅ Tudo está funcionando! 🎉

---

## ❌ Se Algo Der Errado

### Erro 1: Endpoint não encontrado (404)

```
❌ POST /eventos/registered/ → 404
```

**Solução:**

- Verifique se FastAPI está rodando (Terminal 1)
- Verifique se a porta é 8000
- Tente: `curl http://localhost:8000/eventos/registered/`

### Erro 2: Conexão recusada

```
❌ Connection refused
```

**Solução:**

- Verifique se FastAPI está rodando
- Verifique se a porta 8000 está livre: `netstat -an | findstr 8000`

### Erro 3: Tabela registered_events não existe

```
❌ SQLAlchemy: no such table: registered_events
```

**Solução:**

- Reinicie a API (ela cria automaticamente)
- Ou execute manualmente:
  ```sql
  CREATE TABLE registered_events (
    id_registered_event SERIAL PRIMARY KEY,
    id_event INT UNIQUE NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_event) REFERENCES events(id_event)
  );
  ```

---

## 🔧 Resumo da Correção

| O quê                     | Mudança             | Arquivo            |
| ------------------------- | ------------------- | ------------------ |
| Chamada POST /registered/ | Adicionada          | `app.py` linha ~50 |
| Tratamento de erro 409    | Adicionado          | `app.py` linha ~60 |
| Backend                   | Nada (já estava ok) | N/A                |

**Total de mudanças: 1 arquivo** ✅

---

## 📞 Dúvidas?

Se não funcionar:

1. Verifique os 3 terminais estão rodando
2. Execute: `python test_registered_events.py`
3. Leia `PROBLEMA_E_SOLUCAO.md`
4. Leia `VALIDATION_CHECKLIST.md`
