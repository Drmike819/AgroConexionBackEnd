# AgroConexion - BackEnd (Django) 🚜

Este es el backend para la aplicación **AgroConexion**, desarrollado completamente en **Python** utilizando el framework **Django** y **Django REST Framework** para construir una API RESTful robusta y segura.

---

## ✨ Características Principales

* **API RESTful**: Construida siguiendo las mejores prácticas con Django REST Framework (DRF).
* **Autenticación por Tokens**: Sistema de autenticación seguro basado en JSON Web Tokens (JWT) gracias a `djangorestframework-simplejwt`.
* **Gestión de Usuarios**: Endpoints para el registro y la administración de perfiles de usuario.
* **CRUD de Publicaciones**: Funcionalidades completas para Crear, Leer, Actualizar y Eliminar publicaciones, incluyendo manejo de imágenes.
* **Base de Datos Relacional**: Configurado por defecto para usar **SQLite**, fácilmente adaptable a otros motores como PostgreSQL o MySQL.

---

## 🛠️ Tecnologías Utilizadas

* **Python**: Lenguaje principal de desarrollo.
* **Django**: Framework web de alto nivel para un desarrollo rápido y limpio.
* **Django REST Framework (DRF)**: Potente toolkit para la creación de APIs web.
* **DRF Simple JWT**: Para la implementación de la autenticación con JSON Web Tokens.
* **Pillow**: Para el procesamiento y manejo de subida de imágenes.
* **SQLite**: Motor de base de datos por defecto para el desarrollo.

---

## 📋 Prerrequisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

* [Python 3.8](https://www.python.org/) o superior.
* `pip` (el gestor de paquetes de Python).

---

## 🚀 Instalación y Configuración

Sigue estos pasos para configurar el proyecto en tu entorno local.

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/Drmike819/AgroConexionBackEnd.git](https://github.com/Drmike819/AgroConexionBackEnd.git)
    ```

2.  **Navega al directorio del proyecto:**
    ```bash
    cd AgroConexionBackEnd
    ```

3.  **Crea y activa un entorno virtual (Recomendado):**
    Un entorno virtual aísla las dependencias de tu proyecto.
    ```bash
    # Crear el entorno
    python -m venv venv

    # Activarlo en Windows
    .\venv\Scripts\activate

    # Activarlo en macOS/Linux
    source venv/bin/activate
    ```

4.  **Instala las dependencias:**
    El archivo `requirements.txt` contiene todas las librerías necesarias.
    ```bash
    pip install -r requirements.txt
    ```

5.  **Aplica las migraciones de la base de datos:**
    Este comando creará el archivo de base de datos (`db.sqlite3`) y las tablas necesarias.
    ```bash
    python manage.py migrate
    ```

---

## ⚡ Ejecución de la Aplicación

Una vez configurado, puedes iniciar el servidor de desarrollo de Django.

* **Inicia el servidor:**
    ```bash
    python manage.py runserver
    ```
* **Accede a la API:**
    El servidor estará disponible en `http://127.0.0.1:8000/`.

---

## 🤖 Endpoints Principales de la API

La API expone las siguientes rutas para interactuar con los recursos.

### Autenticación (JWT)

* `POST /api/token/`
    **Descripción**: Envía `username` y `password` para obtener los tokens de acceso (`access`) y de refresco (`refresh`).

* `POST /api/token/refresh/`
    **Descripción**: Envía el token de `refresh` para obtener un nuevo token de `access`.

### Usuarios

* `POST /api/users/`
    **Descripción**: Crea un nuevo usuario. No requiere autenticación.

### Publicaciones (Posts)

* `GET /api/posts/`
    **Descripción**: Obtiene una lista de todas las publicaciones. Requiere autenticación.

* `POST /api/posts/`
    **Descripción**: Crea una nueva publicación. Los datos se envían como `multipart/form-data` si incluyen una imagen. Requiere autenticación.

* `GET /api/posts/<id>/`
    **Descripción**: Obtiene los detalles de una publicación específica. Requiere autenticación.

* `PUT /api/posts/<id>/`
    **Descripción**: Actualiza una publicación existente. Requiere autenticación.

* `DELETE /api/posts/<id>/`
    **Descripción**: Elimina una publicación. Requiere autenticación.

**Nota**: Para acceder a los endpoints protegidos, debes incluir el token de acceso en la cabecera de la petición de la siguiente manera:
`Authorization: Bearer <tu_access_token>`
