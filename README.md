# bela_raiz

Bela Raiz is a hybrid platform integrating:
- Salon bookings with deposit via M-Pesa
- Reseller product catalog and sales
- Courier logistics for deliveries

## Tech Stack
- Django 5.x + Django REST Framework
- PostgreSQL + PostGIS (geolocation)
- HTMX + Tailwind (lightweight UI)
- M-Pesa API integration (C2B/B2C)
- MCP (Model Context Protocol) for AI-driven reporting

## Quick Start
```bash
docker-compose up --build

## Authentication API

The backend uses DRF token authentication. Endpoints live under `/api/accounts/`:

- `POST /api/accounts/register/` – fields: `username`, `email`, `password`, `password2`, `first_name`, `last_name`, `phone_number`, `role`.
  - returns a token on success.
- `POST /api/accounts/login/` – provide `username` and `password` to receive a token.
- `GET/PUT /api/accounts/me/` – retrieve or update your authenticated profile (requires `Authorization: Token <key>` header).

Tokens are sent in requests like:

```
Authorization: Token bd305975a31fd0c0b745555dd0b9d9280e12f151
```

User roles (`client`, `salon`, `reseller`, `courier`) are chosen at registration and control access throughout the API.
