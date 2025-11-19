
# AR Construction API (Django + DRF)

A ready-to-run Django REST Framework backend for **AR Construction**: Services, Gallery, Blog, Site Info, and Contact Messages, with OpenAPI docs and a Postman collection.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scriptsctivate
pip install -r requirements.txt

# Create local .env if you want to override defaults
cp .env.example .env  # optional

python manage.py migrate
python manage.py createsuperuser

# Load sample data (services, blog, site info, gallery)
python manage.py loaddata fixtures/initial_site.json fixtures/sample_services.json fixtures/sample_blog.json fixtures/sample_gallery.json

python manage.py runserver
```

Open **http://localhost:8000/api/docs/** for Swagger UI.

## Endpoints
- `GET /api/site/` – Site info (address, phones, email, opening hours)
- `GET /api/pages/{slug}/` – Static pages (e.g., `about`, `privacy`) – optional
- `GET /api/services/` – List services
- `GET /api/services/{slug}/` – Service detail (+ FAQs)
- `GET /api/gallery/` – Paginated gallery list
- `GET /api/blog/` – Blog list
- `GET /api/blog/{slug}/` – Blog detail
- `POST /api/contact-messages/` – Submit contact message
- `GET /api/schema/` – OpenAPI schema (JSON)
- `GET /api/docs/` – Swagger UI

## Editing content (for your client)
- **Blogs**: Use Django Admin → Blog → Posts. Body accepts Markdown or HTML (choose one convention). Upload a cover image. Publish by setting a publish date and enabling *is_published*.
- **Services / Gallery**: Also editable in Admin (even if your frontend stores some items statically, the API is available for future use).
- **Images**: Uploaded images are served from `/media/` in development.

## Configuration
Environment variables (via `.env` or OS env):

```
DJANGO_DEBUG=true
DJANGO_SECRET_KEY=change-me
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://www.arconstruction.ie
CONTACT_NOTIFY_EMAIL=info@arconstruction.ie
DEFAULT_FROM_EMAIL=web@arconstruction.ie
TIME_ZONE=Europe/Dublin
```

## Notes
- Default DB is SQLite. For Postgres, set `DATABASE_URL` and add `psycopg2-binary` in requirements.
- OpenAPI docs provided by **drf-spectacular**.
- Basic CORS is enabled (configure as needed).

## License
MIT
