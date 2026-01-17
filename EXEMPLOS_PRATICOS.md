# 🧪 Exemplos Práticos - Sistema de Eventos

## Cenário Real

Você quer registrar participantes em múltiplos eventos. Cada pessoa pode participar de quantos eventos quiser, mas apenas UMA VEZ em cada evento.

### Exemplo:

- João pode estar em "Praia", "Boliche" e "Festa"
- Mas João não pode estar 2 vezes em "Praia"

---

## 📌 Passo 1: Criar Eventos

### Evento 1: "Praia"

```bash
curl -X POST "http://localhost:8000/eventos/" \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "Praia",
    "event_description": "Passeio divertido na praia"
  }'
```

**Resposta:** `id_event = 1`

### Evento 2: "Boliche"

```bash
curl -X POST "http://localhost:8000/eventos/" \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "Boliche",
    "event_description": "Noite de boliche"
  }'
```

**Resposta:** `id_event = 2`

### Evento 3: "Festa Juvenil"

```bash
curl -X POST "http://localhost:8000/eventos/" \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "Festa Juvenil",
    "event_description": "Confraternização"
  }'
```

**Resposta:** `id_event = 3`

---

## 📌 Passo 2: Registrar João em Múltiplos Eventos ✅

### João se registra em "Praia" (Event ID 1)

```bash
curl -X POST "http://localhost:8000/eventos/1/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "João Silva",
    "participant_email": "joao@example.com",
    "participant_phone": "11987654321"
  }'
```

**Resposta:** `id_registration = 1` ✅

### João se registra em "Boliche" (Event ID 2)

```bash
curl -X POST "http://localhost:8000/eventos/2/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "João Silva",
    "participant_email": "joao@example.com",
    "participant_phone": "11987654321"
  }'
```

**Resposta:** `id_registration = 2` ✅ (ID diferente, evento diferente)

### João se registra em "Festa Juvenil" (Event ID 3)

```bash
curl -X POST "http://localhost:8000/eventos/3/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "João Silva",
    "participant_email": "joao@example.com",
    "participant_phone": "11987654321"
  }'
```

**Resposta:** `id_registration = 3` ✅ (ID diferente, evento diferente)

---

## 📌 Passo 3: Tentar Registrar João Novamente em "Praia" ❌

```bash
curl -X POST "http://localhost:8000/eventos/1/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "João Silva",
    "participant_email": "joao.novo@example.com"
  }'
```

**Resposta (Erro 409 - Conflito):**

```json
{
  "detail": "Participante 'João Silva' já está registrado neste evento!"
}
```

---

## 📌 Passo 4: Listar Participantes de Cada Evento

### Listar participantes da "Praia" (Event ID 1)

```bash
curl "http://localhost:8000/eventos/1/participants"
```

**Resposta:** João está aqui ✅

### Listar participantes do "Boliche" (Event ID 2)

```bash
curl "http://localhost:8000/eventos/2/participants"
```

**Resposta:** João está aqui também ✅

### Listar participantes da "Festa Juvenil" (Event ID 3)

```bash
curl "http://localhost:8000/eventos/3/participants"
```

**Resposta:** João está aqui também ✅

---

## 📌 Passo 5: Registrar Maria em Alguns Eventos

### Maria se registra em "Praia" (Event ID 1)

```bash
curl -X POST "http://localhost:8000/eventos/1/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "Maria Santos",
    "participant_email": "maria@example.com",
    "participant_phone": "11912345678"
  }'
```

**Resposta:** `id_registration = 4` ✅

### Maria se registra em "Boliche" (Event ID 2)

```bash
curl -X POST "http://localhost:8000/eventos/2/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "Maria Santos",
    "participant_email": "maria@example.com",
    "participant_phone": "11912345678"
  }'
```

**Resposta:** `id_registration = 5` ✅

### Maria tenta se registrar em "Praia" novamente ❌

```bash
curl -X POST "http://localhost:8000/eventos/1/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "Maria Santos"
  }'
```

**Resposta (Erro 409):**

```json
{
  "detail": "Participante 'Maria Santos' já está registrado neste evento!"
}
```

---

## 📌 Passo 6: Estado Final dos Eventos

### Praia (Event ID 1)

```bash
curl "http://localhost:8000/eventos/1/participants"
```

**Resposta:**

```json
[
  {
    "id_registration": 1,
    "id_event": 1,
    "participant_name": "João Silva",
    "registration_date": "2026-01-17T10:15:00+00:00"
  },
  {
    "id_registration": 4,
    "id_event": 1,
    "participant_name": "Maria Santos",
    "registration_date": "2026-01-17T10:20:00+00:00"
  }
]
```

### Boliche (Event ID 2)

```bash
curl "http://localhost:8000/eventos/2/participants"
```

**Resposta:**

```json
[
  {
    "id_registration": 2,
    "id_event": 2,
    "participant_name": "João Silva",
    "registration_date": "2026-01-17T10:16:00+00:00"
  },
  {
    "id_registration": 5,
    "id_event": 2,
    "participant_name": "Maria Santos",
    "registration_date": "2026-01-17T10:21:00+00:00"
  }
]
```

### Festa Juvenil (Event ID 3)

```bash
curl "http://localhost:8000/eventos/3/participants"
```

**Resposta:**

````json
[
  {
    "id_registration": 3,
    "id_event": 3,
    "participant_name": "João Silva",
    "registration_date": "2026-01-17T10:17:00+00:00"
  }
]
---

## 📌 Passo 7: Remover João da "Praia" (Mas ele continua nos outros)

```bash
curl -X DELETE "http://localhost:8000/eventos/participants/1"
````

**Resposta:**

```json
{
  "detail": "Participante 1 removido do evento com sucesso"
}
```

**Resultado:** João foi removido da "Praia", mas continua registrado em "Boliche" e "Festa Juvenil" ✅

---

## 📌 Passo 8: Agora João Pode se Registrar Novamente em "Praia" ✅

```bash
curl -X POST "http://localhost:8000/eventos/1/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "João Silva",
    "participant_email": "joao@example.com",
    "participant_phone": "11987654321"
  }'
```

**Resposta:**

```json
{
  "id_registration": 6,
  "id_event": 1,
  "participant_name": "João Silva",
  "participant_email": "joao@example.com",
  "participant_phone": "11987654321",
  "registration_date": "2026-01-17T10:30:00+00:00"
}
```

**Nota:** ID de registro = 6 (novo), não 1 como antes ✅

---

## 🐍 Exemplo em Python - Múltiplos Eventos

```python
import requests
from typing import List, Dict

class EventoManager:
    """Gerenciador de eventos e participantes"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def criar_evento(self, nome: str, descricao: str = None) -> Dict:
        """Criar um novo evento"""
        response = requests.post(
            f"{self.base_url}/eventos/",
            json={
                "event_name": nome,
                "event_description": descricao
            }
        )
        return response.json()

    def registrar_participante(
        self,
        event_id: int,
        nome: str,
        email: str = None,
        phone: str = None
    ) -> Dict:
        """Registrar participante em evento (por evento, não globalmente)"""
        try:
            response = requests.post(
                f"{self.base_url}/eventos/{event_id}/participants",
                json={
                    "participant_name": nome,
                    "participant_email": email,
                    "participant_phone": phone
                }
            )
            if response.status_code == 409:
                print(f"❌ {response.json()['detail']}")
                return None
            return response.json()
        except Exception as e:
            print(f"Erro: {e}")
            return None

    def listar_participantes_evento(self, event_id: int) -> List[Dict]:
        """Listar participantes de um evento específico"""
        response = requests.get(f"{self.base_url}/eventos/{event_id}/participants")
        return response.json()

    def remover_participante(self, registration_id: int) -> Dict:
        """Remover um participante (apenas daquele evento)"""
        response = requests.delete(
            f"{self.base_url}/eventos/participants/{registration_id}"
        )
        return response.json()


# Uso Prático: João em múltiplos eventos
if __name__ == "__main__":
    manager = EventoManager()

    print("=" * 70)
    print("EXEMPLO: João e Maria em múltiplos eventos")
    print("=" * 70)

    # 1. Criar 3 eventos
    print("\n📌 Criando eventos...")
    praia = manager.criar_evento("Praia", "Passeio na praia")
    boliche = manager.criar_evento("Boliche", "Noite de boliche")
    festa = manager.criar_evento("Festa Juvenil", "Confraternização")

    praia_id = praia["id_event"]
    boliche_id = boliche["id_event"]
    festa_id = festa["id_event"]

    print(f"✅ Praia (ID: {praia_id})")
    print(f"✅ Boliche (ID: {boliche_id})")
    print(f"✅ Festa (ID: {festa_id})")

    # 2. João se registra em TODOS os 3 eventos
    print("\n📌 João se registra em 3 eventos diferentes...")

    joao_praia = manager.registrar_participante(praia_id, "João Silva", "joao@example.com")
    joao_boliche = manager.registrar_participante(boliche_id, "João Silva", "joao@example.com")
    joao_festa = manager.registrar_participante(festa_id, "João Silva", "joao@example.com")

    if joao_praia:
        print(f"✅ João em 'Praia' (Reg ID: {joao_praia['id_registration']})")
    if joao_boliche:
        print(f"✅ João em 'Boliche' (Reg ID: {joao_boliche['id_registration']})")
    if joao_festa:
        print(f"✅ João em 'Festa' (Reg ID: {joao_festa['id_registration']})")

    # 3. Maria se registra em 2 eventos
    print("\n📌 Maria se registra em 2 eventos...")

    maria_praia = manager.registrar_participante(praia_id, "Maria Santos", "maria@example.com")
    maria_boliche = manager.registrar_participante(boliche_id, "Maria Santos", "maria@example.com")

    if maria_praia:
        print(f"✅ Maria em 'Praia' (Reg ID: {maria_praia['id_registration']})")
    if maria_boliche:
        print(f"✅ Maria em 'Boliche' (Reg ID: {maria_boliche['id_registration']})")

    # 4. Tentar registrar João novamente em Praia (deve falhar)
    print("\n📌 Tentando registrar João novamente em 'Praia'...")
    joao_praia_2 = manager.registrar_participante(praia_id, "João Silva")

    # 5. Listar participantes de cada evento
    print("\n📌 Estado atual de cada evento:")

    print(f"\n  Praia:")
    for p in manager.listar_participantes_evento(praia_id):
        print(f"    - {p['participant_name']}")

    print(f"\n  Boliche:")
    for p in manager.listar_participantes_evento(boliche_id):
        print(f"    - {p['participant_name']}")

    print(f"\n  Festa Juvenil:")
    for p in manager.listar_participantes_evento(festa_id):
        print(f"    - {p['participant_name']}")

    # 6. Remover João da Praia
    print(f"\n📌 Removendo João apenas da 'Praia'...")
    result = manager.remover_participante(joao_praia["id_registration"])
    print(f"✅ {result['detail']}")

    # 7. Verificar que João continua em Boliche e Festa
    print("\n📌 João após ser removido de 'Praia':")

    praia_participants = manager.listar_participantes_evento(praia_id)
    boliche_participants = manager.listar_participantes_evento(boliche_id)
    festa_participants = manager.listar_participantes_evento(festa_id)

    print(f"\n  Praia: {len(praia_participants)} participantes")
    if len(praia_participants) == 0:
        print("    (João foi removido)")

    print(f"\n  Boliche: {len(boliche_participants)} participantes")
    for p in boliche_participants:
        if p['participant_name'] == "João Silva":
            print(f"    - João continua aqui ✅")

    print(f"\n  Festa: {len(festa_participants)} participantes")
    for p in festa_participants:
        if p['participant_name'] == "João Silva":
            print(f"    - João continua aqui ✅")
```

**Output esperado:**

```
======================================================================
EXEMPLO: João e Maria em múltiplos eventos
======================================================================

📌 Criando eventos...
✅ Praia (ID: 1)
✅ Boliche (ID: 2)
✅ Festa (ID: 3)

📌 João se registra em 3 eventos diferentes...
✅ João em 'Praia' (Reg ID: 1)
✅ João em 'Boliche' (Reg ID: 2)
✅ João em 'Festa' (Reg ID: 3)

📌 Maria se registra em 2 eventos...
✅ Maria em 'Praia' (Reg ID: 4)
✅ Maria em 'Boliche' (Reg ID: 5)

📌 Tentando registrar João novamente em 'Praia'...
❌ Participante 'João Silva' já está registrado neste evento!

📌 Estado atual de cada evento:

  Praia:
    - João Silva
    - Maria Santos

  Boliche:
    - João Silva
    - Maria Santos

  Festa Juvenil:
    - João Silva

📌 Removendo João apenas da 'Praia'...
✅ Participante 1 removido do evento com sucesso

📌 João após ser removido de 'Praia':

  Praia: 1 participantes
    (João foi removido)

  Boliche: 2 participantes
    - João continua aqui ✅

  Festa: 1 participantes
    - João continua aqui ✅
```

---

## 🐍 Classe EventoManager Simples (versão anterior)

```python
import requests
from typing import List, Dict

class EventoManager:
    "participant_name": "João Silva",
    "participant_email": "joao@example.com",
    "participant_phone": "11987654321"
  }'
```

**Resposta:**

```json
{
  "id_registration": 3,
  "id_event": 1,
  "participant_name": "João Silva",
  "participant_email": "joao@example.com",
  "participant_phone": "11987654321",
  "registration_date": "2026-01-17T10:30:00+00:00"
}
```

---

## 🐍 Exemplo em Python

```python
import requests
from typing import List, Dict

class EventoManager:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def criar_evento(self, nome: str, descricao: str = None) -> Dict:
        """Criar um novo evento"""
        response = requests.post(
            f"{self.base_url}/eventos/",
            json={
                "event_name": nome,
                "event_description": descricao
            }
        )
        return response.json()

    def registrar_participante(self, event_id: int, nome: str, email: str = None, phone: str = None) -> Dict:
        """Registrar participante em evento"""
        try:
            response = requests.post(
                f"{self.base_url}/eventos/{event_id}/participants",
                json={
                    "participant_name": nome,
                    "participant_email": email,
                    "participant_phone": phone
                }
            )
            if response.status_code == 409:
                print(f"❌ {response.json()['detail']}")
                return None
            return response.json()
        except Exception as e:
            print(f"Erro: {e}")
            return None

    def listar_participantes(self, event_id: int) -> List[Dict]:
        """Listar todos os participantes de um evento"""
        response = requests.get(f"{self.base_url}/eventos/{event_id}/participants")
        return response.json()

    def remover_participante(self, registration_id: int) -> Dict:
        """Remover um participante"""
        response = requests.delete(f"{self.base_url}/eventos/participants/{registration_id}")
        return response.json()


# Uso
if __name__ == "__main__":
    manager = EventoManager()

    # 1. Criar evento
    print("📌 Criando evento 'Praia'...")
    evento = manager.criar_evento("Praia", "Passeio na praia")
    event_id = evento["id_event"]
    print(f"✅ Evento criado: {evento['event_name']} (ID: {event_id})")

    # 2. Registrar participantes
    print("\n📌 Registrando participantes...")
    p1 = manager.registrar_participante(event_id, "João Silva", "joao@example.com")
    if p1:
        print(f"✅ {p1['participant_name']} registrado")

    p2 = manager.registrar_participante(event_id, "Maria Santos", "maria@example.com")
    if p2:
        print(f"✅ {p2['participant_name']} registrado")

    # 3. Tentar registrar novamente
    print("\n📌 Tentando registrar João novamente...")
    p3 = manager.registrar_participante(event_id, "João Silva")

    # 4. Listar participantes
    print(f"\n📌 Participantes do evento '{evento['event_name']}':")
    participantes = manager.listar_participantes(event_id)
    for p in participantes:
        print(f"  - {p['participant_name']} ({p['participant_email']})")

    # 5. Remover participante
    print(f"\n📌 Removendo {p1['participant_name']}...")
    result = manager.remover_participante(p1["id_registration"])
    print(f"✅ {result['detail']}")

    # 6. Registrar novamente
    print("\n📌 Registrando João novamente...")
    p4 = manager.registrar_participante(event_id, "João Silva")
    if p4:
        print(f"✅ {p4['participant_name']} registrado novamente (ID: {p4['id_registration']})")
```

**Output esperado:**

```
📌 Criando evento 'Praia'...
✅ Evento criado: Praia (ID: 1)

📌 Registrando participantes...
✅ João Silva registrado
✅ Maria Santos registrado

📌 Tentando registrar João novamente...
❌ Participante 'João Silva' já está registrado neste evento!

📌 Participantes do evento 'Praia':
  - João Silva (joao@example.com)
  - Maria Santos (maria@example.com)

📌 Removendo João Silva...
✅ Participante 1 removido do evento com sucesso

📌 Registrando João novamente...
✅ João Silva registrado novamente (ID: 3)
```

---

## 📊 Dados no Banco

Após executar o exemplo acima:

### Tabela: `events`

| id_event | event_name | event_description | create_date   | update_date   |
| -------- | ---------- | ----------------- | ------------- | ------------- |
| 1        | Praia      | Passeio na praia  | 2026-01-17... | 2026-01-17... |

### Tabela: `event_participants`

| id_registration | id_event | participant_name | participant_email | registration_date |
| --------------- | -------- | ---------------- | ----------------- | ----------------- |
| 2               | 1        | Maria Santos     | maria@example.com | 2026-01-17...     |
| 3               | 1        | João Silva       | joao@example.com  | 2026-01-17...     |

_(Registros 1 foi removido)_

---

## 🛠️ Testes com Pytest

```python
import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app

client = TestClient(app)

def test_create_event():
    """Testar criação de evento"""
    response = client.post(
        "/eventos/",
        json={
            "event_name": "Test Event",
            "event_description": "Test Description"
        }
    )
    assert response.status_code == 200
    assert response.json()["event_name"] == "Test Event"

def test_register_participant():
    """Testar registro de participante"""
    # Criar evento
    event_resp = client.post(
        "/eventos/",
        json={"event_name": "Test Event"}
    )
    event_id = event_resp.json()["id_event"]

    # Registrar participante
    response = client.post(
        f"/eventos/{event_id}/participants",
        json={"participant_name": "João"}
    )
    assert response.status_code == 200
    assert response.json()["participant_name"] == "João"

def test_duplicate_participant():
    """Testar erro ao registrar participante duplicado"""
    # Criar evento
    event_resp = client.post(
        "/eventos/",
        json={"event_name": "Test Event 2"}
    )
    event_id = event_resp.json()["id_event"]

    # Registrar participante
    client.post(
        f"/eventos/{event_id}/participants",
        json={"participant_name": "João"}
    )

    # Tentar registrar novamente
    response = client.post(
        f"/eventos/{event_id}/participants",
        json={"participant_name": "João"}
    )
    assert response.status_code == 409
    assert "já está registrado" in response.json()["detail"]
```

---

**Pronto para usar! 🚀**
