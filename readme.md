# In development
In development the docker-compose file to use is "docker-compose.dev.yml"

# Start the Django server
cd /path/to/your/django/project
docker-compose -f docker-compose.local.yml build
docker-compose -f docker-compose.local.yml up

# Create superuser
docker-compose -f docker-compose.local.yml run app sh -c "python manage.py createsuperuser"


---

# Arquitectura

Este proyecto implementa una aplicación web de Preguntas y Respuestas utilizando Django como framework principal, Docker para la contenerización y Celery (y Redis) para la gestión de tareas asíncronas. A continuación los roles:

1.  Django (webapp):
    - Maneja las peticiones HTTP del cliente, el browser.
    - Interactúa con modelos por ORM.
    - Renderizar las templates.

2.  PostgreSQL (DB):
    - Almacena toda la información persistente del sistema (Usuarios, Preguntas, Respuestas, Votos, Notificaciones, configuración de Retrievers).

3.  Redis (Broker):
    - Actúa como intermediario de alto rendimiento para la comunicación entre la aplicación Django y los Celery Workers.
    - Almacena la cola de tareas pendientes.

4.  Celery (tareas):
    - Procesa tareas de fondo de forma asíncrona.
    - Escucha a lo que le pasa Redis.
    - Principalmente usado para enviar contenido a analizar a la API externa y ahorrarle al usuario tiempos de espera.

5.  Analyzer (API):
    - Un servicio independiente que valida si el texto de una Pregunta o Respuesta es apropiado.
    - Consultada únicamente por los Celery Workers.

6.  Docker:
    - Empaqueta cada servicio en contenedores aislados.
    - Usa compose para desplegar la aplicación de manera conveniente.

Flujo Clave (Análisis Asíncrono de Contenido):

Al crear una Pregunta o Respuesta, la Aplicación Django la guarda inicialmente en la Base de Datos con apto=unknown. Inmediatamente enacola una tarea en Celery (a través de Redis) para analizar este contenido. Un Celery Worker recoge la tarea, consulta la API Externa, recibe el resultado del análisis y actualiza el campo apto en el modelo. Las Views de Django solo muestran el contenido donde apto es True.
