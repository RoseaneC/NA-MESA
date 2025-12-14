# VEXIA – NA MESA

Demo simples em FastAPI + SQLite que simula uma conversa estilo WhatsApp com a VEXIA para fluxos de doação, ONG, pedido de comida e voluntariado. Não requer chaves externas.

## Requisitos

- Python 3.11+
- pip

## Instalação e execução (PowerShell)

Na pasta do projeto e já dentro do PowerShell:

```powershell
.\scripts\windows_fix.ps1
```

Acesse:
- Chat: http://127.0.0.1:8010/
- Admin: http://127.0.0.1:8010/admin

## Estrutura

```
na-mesa-vexia/
  app/
    main.py
    db.py
    models.py
    schemas.py
    services/state_machine.py
    routes/
      chat.py
      pages.py
    templates/
      index.html
      admin.html
    static/
      styles.css
      app.js
  requirements.txt
  README.md
```

## Notas

- Tabelas são criadas automaticamente ao subir (create_all).
- A API expõe `/health`, `/api/chat`, `/api/reset`, `/api/session/{id}`, `/admin`.
- Logs no console mostram `session_id`, estado anterior e novo a cada mensagem.
