# Importación de componentes principales de FastAPI
from fastapi import FastAPI, Request  # type: ignore # Gestión de solicitudes y creación de la app
from fastapi.middleware.cors import CORSMiddleware  # type: ignore # Middleware para habilitar CORS
from fastapi.responses import JSONResponse  # type: ignore # Personalización de respuestas JSON
from fastapi.exceptions import RequestValidationError  # type: ignore # Manejo de errores de validación

# Importación del esquema de respuesta estándar para errores
from schemas.error import ErrorResponse

# Importación del router correspondiente al módulo de la Unidad 1
from routers import unit1

# Instanciación de la aplicación principal con título descriptivo
app = FastAPI(title="Numerik Lab API")

# Declaración de los orígenes permitidos para el frontend (por ejemplo, Vite o React en localhost)
origins = ["http://localhost:5173"]

# Configuración del middleware CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"]   # Permite todos los encabezados
)

# Manejador global para errores de validación generados por Pydantic
@app.exception_handler(RequestValidationError)
async def custom_validation_handler(request: Request, exc: RequestValidationError):
    """
    Captura errores de validación en el body de las solicitudes.
    Retorna una respuesta estandarizada en formato ErrorResponse.
    """
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            success=False,
            message="Error de validación en los datos enviados: " + str(exc.errors()[0]["msg"]),
            data=None
        ).dict()
    )

# Inclusión del router de la unidad 1 (por ejemplo, métodos como bisección)
app.include_router(unit1.router)

# Ruta raíz de prueba (puede usarse para verificar si el servidor está en línea)
@app.get("/")
def read_root():
    return {"FASTAPI Numerik Lab"}



