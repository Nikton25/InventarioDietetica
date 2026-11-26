# Sistema de Gestión de Inventario para Dietética

Aplicación web desarrollada en **Flask** con arquitectura **App Factory + Blueprints**, persistencia en **SQLAlchemy** (SQLite en desarrollo local y PostgreSQL en producción) e integración de un modelo de **Regresión Logística (`scikit-learn`)** para predecir en tiempo real la necesidad de reposición de stock.

## Características Principales

- **Autenticación segura:** Inicio y cierre de sesión para usuario administrador mediante `Flask-Login` y hashes `Flask-Bcrypt`.
- **CRUD de Productos:** Listado, alta, edición y eliminación de productos con validación del lado del servidor.
- **Predicción de Reposición (IA):** Clasificador binario con `scikit-learn` y `joblib` que evalúa `stock_actual`, `ventas_diarias` y `dias_entrega` para emitir un veredicto y porcentaje de probabilidad.
- **Inicialización automática:** Creación automática de tablas y del usuario administrador inicial a partir de variables de entorno al iniciar la aplicación.


## Requisitos e Instalación Local

1. Crear y activar un entorno virtual:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux/macOS:
   source .venv/bin/activate
   ```

2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno copiando `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

4. (Opcional) Reentrenar el modelo de Machine Learning:
   ```bash
   python ml/train_model.py
   ```

5. Ejecutar la aplicación:
   ```bash
   python run.py
   ```

