# ⚡ Quick Reference - Registro de Eventos

## TL;DR - Em 10 segundos

```
João pode registrar em:
✅ Praia
✅ Boliche
✅ Festa
❌ Praia novamente (erro 409)
```

---

## 🎯 Regra Simples

| Ação               | Permitido | Motivo           |
| ------------------ | --------- | ---------------- |
| João em Praia      | ✅        | Evento diferente |
| João em Boliche    | ✅        | Evento diferente |
| João em Praia (2x) | ❌        | Mesmo evento     |

---

## 🔗 SQL Constraint

```sql
UNIQUE (id_event, participant_name)
```

**Tradução:** `(qual evento, qual pessoa)` deve ser único

---

## 💻 API Endpoints

### Registrar

```
POST /eventos/{event_id}/participants
```

→ **409** se pessoa já está registrada naquele evento

### Listar

```
GET /eventos/{event_id}/participants
```

→ Mostra quem está naquele evento

### Remover

```
DELETE /eventos/participants/{registration_id}
```

→ Remove apenas daquele evento

---

## 📊 Banco de Dados

```
events (1) ──┬── event_participants (N)
             │
             └─ (id_event, participant_name) UNIQUE
```

---

## ✨ Características

- ✅ Uma pessoa em múltiplos eventos
- ❌ Uma pessoa 2+ vezes no mesmo evento
- ✅ Diferentes pessoas no mesmo evento
- ✅ Remover e registrar novamente

---

## 🚀 Uso Rápido

```python
# Registrar João em Praia
POST /eventos/1/participants
→ ✅ id_registration = 1

# Registrar João em Boliche
POST /eventos/2/participants
→ ✅ id_registration = 2

# Tentar registrar João em Praia novamente
POST /eventos/1/participants
→ ❌ 409 Conflict

# Remover João de Praia
DELETE /eventos/participants/1
→ ✅ OK

# Registrar João em Praia novamente
POST /eventos/1/participants
→ ✅ id_registration = 3
```

---

## ✅ Status

- **Implementado?** ✅ Sim
- **Funcionando?** ✅ Sim
- **Testado?** ✅ Sim
- **Documentado?** ✅ Sim
