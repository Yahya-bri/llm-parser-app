# Deploying the Full Stack Application with Docker Compose

Your project is already well-structured for Docker Compose deployment with all the necessary configuration files in place. Here's how to deploy the entire solution:

## Deployment Steps

1. **Build and start all services**:

   ```bash
   docker-compose up --build -d
   ```

   This command:

   - Builds all the service images (frontend, backend, database)
   - Starts the containers in detached mode

2. **Create a Django superuser** (for admin access):

   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

3. **Access your application**:
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8000/api/
   - API Documentation: http://localhost:8000/api/schema/swagger-ui/
   - Django Admin: http://localhost:8000/admin/

## Application Features

### Document Parser

The application includes a document parsing feature that allows you to:

1. Upload PDF and image documents
2. Preview documents page by page
3. Parse documents using AI vision models
4. Extract structured data according to predefined schemas

Available document schemas:

- Resume parsing
- Invoice parsing
- Receipt parsing
- ID Card parsing

This feature uses the vision-parser package with Google's Gemini vision model.

## Environment Variables

### Required API Keys

The document parsing feature requires a Google API key for the Gemini Vision API:

1. **Get a Google API Key**:

   - Go to the [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key or use an existing one
   - The key should have access to the Gemini Vision models
   - Alternatively, create an API key in the [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
     - First enable the Generative Language API in your Google Cloud project
     - Then create an API key with access to this API

2. **Set the API Key**:

   - For local development, add it to the backend/.env file:
     ```
     GOOGLE_API_KEY=your-actual-api-key-here
     ```
   - For Docker deployment, set it as an environment variable before starting the containers:
     ```bash
     export GOOGLE_API_KEY=your-actual-api-key-here
     docker-compose up -d
     ```

3. **Verify API Key Setup**:
   - To verify your API key is working correctly, try parsing a document
   - If you see an error about an invalid API key, check the following:
     - Make sure you've exported the key properly (for Docker) or added it to .env (for local dev)
     - Verify the API key is active in the Google Cloud Console
     - Ensure the API key has access to the Generative Language API

## Additional Docker Compose Commands

- **View running containers**:

  ```bash
  docker-compose ps
  ```

- **View container logs**:
  ```bash
  docker-compose logs -f
  ```
- **View logs for a specific service**:

  ```bash
  docker-compose logs -f backend
  ```

- **Stop all containers**:

  ```bash
  docker-compose down
  ```

- **Stop and remove volumes** (will delete database data):
  ```bash
  docker-compose down -v
  ```

## Production Considerations

For production deployment, consider these adjustments:

1. **Update environment variables** in docker-compose.yml:

   - Change `SECRET_KEY` to a secure value
   - Keep `DEBUG=False`
   - Update `ALLOWED_HOSTS` to include your domain
   - Add your `GOOGLE_API_KEY` for the vision parser functionality

2. **Enable HTTPS**:

   - Add a reverse proxy like Nginx or Traefik
   - Configure SSL certificates

3. **Data persistence**:

   - The PostgreSQL data is already persisted in a volume (`postgres_data`)
   - Consider regular database backups
   - Media files (uploaded documents) are stored in a volume (`media_files`)

4. **Automatic restarts**:

   - Add `restart: always` to each service in docker-compose.yml for automatic recovery after server reboots

5. **Scale services** if needed:
   ```bash
   docker-compose up -d --scale backend=3
   ```
   (Note: This would require additional load balancing configuration)

## Troubleshooting

### Database Migration Issues

If you encounter errors about missing tables (e.g., "relation 'auth_user' does not exist"), you need to run Django migrations in the correct order:

1. **Run auth migrations first**:

   ```bash
   docker-compose exec backend python manage.py migrate auth
   ```

2. **Then run all other migrations**:

   ```bash
   docker-compose exec backend python manage.py migrate
   ```

3. **If needed, make and apply new migrations**:

   ```bash
   docker-compose exec backend python manage.py makemigrations
   docker-compose exec backend python manage.py migrate
   ```

4. **Restart the services**:
   ```bash
   docker-compose restart
   ```

If problems persist, you can try rebuilding the containers:

```bash
docker-compose down
docker-compose up --build -d
```

Your Docker configuration is already well-structured for a development environment and provides a solid foundation for production deployment.
