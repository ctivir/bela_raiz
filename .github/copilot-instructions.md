# Copilot Instructions for Bela Raiz

## Architecture Overview
Bela Raiz is a hybrid Django platform integrating salon bookings, reseller product catalogs, and courier logistics. The project uses a multi-app Django structure with role-based user authentication.

**Key Apps:**
- `accounts/`: User management with roles (client, salon, reseller)
- `salon/`: Service offerings and bookings with M-Pesa deposit system
- `reseller/`: Product catalog and sales (models not yet implemented)
- `payments/`: M-Pesa API integration (models not yet implemented)
- `delivery/`: Courier logistics (models not yet implemented)

## Development Setup
```bash
docker-compose up --build  # Production-like environment with PostgreSQL + PostGIS
python manage.py runserver  # Local development with SQLite
```

## Key Patterns & Conventions

### Role-Based User System
Users have roles that determine their capabilities:
- `client`: Can book salon services
- `salon`: Can offer services and manage bookings
- `reseller`: Can manage product catalogs (future)

**Example from `salon/models.py`:**
```python
salon = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    limit_choices_to={'role': 'salon'}  # Role-based filtering
)
```

### Business Rules
Deposit calculation logic in `salon/views.py`:
- 20% deposit required for services > 1000 MT (Mozambican Metical)
- Integrated with M-Pesa payment flow

### API Design
- Django REST Framework for all APIs
- Nested serializers for related data (e.g., `BookingSerializer` includes `SalonServiceSerializer`)
- Status-based booking workflow: pending → deposit_paid → confirmed → completed

### Database
- SQLite for local development
- PostgreSQL + PostGIS for production (geolocation features planned)
- Default Django migrations

### Frontend
- HTMX + Tailwind planned for lightweight, interactive UI
- Currently API-only with no frontend implementation

## Critical Workflows

### Adding New Features
1. Create/update models in appropriate app (e.g., `salon/models.py`)
2. Add business logic in views with proper validation
3. Use DRF serializers for API responses
4. Update URL patterns in `core/urls.py`
5. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Payment Integration
- M-Pesa C2B/B2C flows planned
- Store payment references in model fields (e.g., `mpesa_reference`)
- Update booking status based on payment confirmation

### Testing
- Standard Django TestCase framework
- Test business logic thoroughly (deposit calculations, status transitions)
- API endpoint testing with DRF test clients

## File Structure Reference
- `core/settings.py`: App configuration and database settings
- `salon/models.py`: Current working example of models with role relationships
- `salon/views.py`: Business logic implementation pattern
- `salon/serializer.py`: DRF serialization patterns

## Future Components
- MCP (Model Context Protocol) integration for AI-driven reporting
- HTMX/Tailwind frontend implementation
- Complete reseller, payments, and delivery app models
- Geolocation features using PostGIS