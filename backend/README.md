# Django REST Framework Backend

A simple Django REST Framework backend template.

## Setup Instructions

1. Create a virtual environment:

   ```
   python -m venv venv
   ```

2. Activate the virtual environment:

   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL:

   - Install PostgreSQL if you haven't already
   - Create a new database:
     ```
     createdb django_db
     ```
   - Or from PostgreSQL shell:
     ```
     CREATE DATABASE django_db;
     ```

5. Configure environment variables:

   - Copy the .env.example file to .env (if provided) or create a new .env file with:

     ```
     SECRET_KEY=your-secure-secret-key
     DEBUG=True
     ALLOWED_HOSTS=localhost,127.0.0.1

     # Database settings
     DB_NAME=django_db
     DB_USER=postgres
     DB_PASSWORD=your_db_password
     DB_HOST=localhost
     DB_PORT=5432
     ```

6. Run migrations:

   ```
   python manage.py migrate
   ```

7. Create a superuser:

   ```
   python manage.py createsuperuser
   ```

8. Run the development server:

   ```
   python manage.py runserver
   ```

9. Access the API at http://localhost:8000/api/
   - Admin interface: http://localhost:8000/admin/

## API Documentation

The API documentation is automatically generated using drf-spectacular. You can access it at:

- **Swagger UI**: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **ReDoc**: [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)
- **Download OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

The documentation is interactive and allows you to:

- Browse all available endpoints
- Read endpoint descriptions and parameters
- Test API calls directly from the browser
- See response formats and status codes
