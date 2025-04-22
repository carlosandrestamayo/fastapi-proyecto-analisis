
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field

# ===============================
# 📥 Entrada del usuario
# ===============================

class BisectionRequest(BaseModel):
    function: str = Field(
        ..., 
        description="Expresión matemática como string. Ej: 'x**3 - x - 2'"
    )
    xi: float = Field(
        ..., 
        description="Límite inferior del intervalo"
    )
    xs: float = Field(
        ..., 
        description="Límite superior del intervalo"
    )
    decimals: int = Field(
        ..., 
        gt=0, 
        lt=10, 
        description="Número de decimales (entre 1 y 9)"
    )
    criterion: Literal["error_relativo", "tolerancia"] = Field(
        ..., 
        description="Criterio de parada del método"
    )
    criterion_value: float = Field(
        ..., 
        gt=0,
        description="Valor asociado al criterio de parada. Debe ser mayor que 0"
    )

# ===============================
# 📊 Resultado por iteración
# ===============================

class BisectionRow(BaseModel):
    iteration: int                                  # Número de iteración
    xi: float                                       # Valor actual de xi
    xs: float                                       # Valor actual de xs
    xr: float                                       # Punto medio actual
    fxi: float                                      # Evaluación f(xi)
    fxs: float                                      # Evaluación f(xs)
    fxr: float                                      # Evaluación f(xr)
    error: Optional[Union[float, str]] = None       # Puede ser número (float) o texto (str), útil para mostrar "---" en la primera fila
    isRoot: bool

# ===============================
# 🧾 Detalle paso a paso
# ===============================

class BisectionStep(BaseModel):
    step1: str
    step2: str
    step3: str
    step4: str
    step5: str
    step6: str
    step7: str
    step8: str
    step9: str
    step10: str
    step11: str

# ===============================
# 📦 Contenido completo de la respuesta en éxito
# ===============================

class BisectionData(BaseModel):
    rootValue: float                  # Raíz aproximada encontrada
    rootFunctionValue: float          # Evaluación de la Raíz aproximada encontrada en la función
    message_detention: str            # Mensaje que explica por qué se detuvo
    headers: List[str]                # Encabezados para la tabla de iteraciones
    rows: List[BisectionRow]          # Lista de iteraciones con resultados
    steps: List[BisectionStep]        # Lista de pasos explicativos

# ===============================
# 📤 Respuesta final del endpoint
# ===============================

class BisectionResponse(BaseModel):
    success: bool                     # True si el método se ejecutó correctamente
    message: str                      # Mensaje general: éxito o error
    data: Optional[BisectionData]     # Resultado detallado (None en caso de error)
