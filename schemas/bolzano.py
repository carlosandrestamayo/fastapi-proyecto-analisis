from pydantic import BaseModel, Field
from typing import Optional

class BolzanoRequest(BaseModel):
    """
    Modelo de entrada para solicitar la evaluación del Teorema de Bolzano.
    """
    function: str = Field(..., description="Expresión matemática en texto, e.g., 'x**2 - 2'.")
    xi: float = Field(..., description="Extremo inferior del intervalo de evaluación.")
    xs: float = Field(..., description="Extremo superior del intervalo de evaluación.")
    decimals: int = Field(
        ..., gt=0, lt=10,
        description="Número de decimales para redondeo (mayor que 0 y menor que 10)."
    )

class BolzanoSteps(BaseModel):
    """
    Modelo opcional para describir el paso a paso del análisis de Bolzano.
    (Actualmente no usado en la respuesta principal pero puede usarse para detalle extendido).
    """
    step1: str
    step2: str
    step3: str
    step4: str

class BolzanoData(BaseModel):
    """
    Modelo que representa los datos matemáticos del resultado de Bolzano.
    """
    xi: float = Field(..., description="Extremo inferior del intervalo evaluado.")
    xs: float = Field(..., description="Extremo superior del intervalo evaluado.")
    fxi: float = Field(..., description="Valor de la función evaluada en xi.")
    fxs: float = Field(..., description="Valor de la función evaluada en xs.")
    product: float = Field(..., description="Producto de f(xi) * f(xs), redondeado.")
    theoremSatisfied: bool = Field(..., description="Indicador de si se cumple el Teorema de Bolzano.")

class BolzanoResponse(BaseModel):
    """
    Modelo de salida que representa la respuesta final del análisis de Bolzano.
    """
    success: bool = Field(..., description="Indica si la operación fue exitosa.")
    message: str = Field(..., description="Mensaje explicativo general del resultado.")
    data: Optional[BolzanoData] = Field(
        None, 
        description="Datos detallados del resultado si la operación fue exitosa, None en caso de error."
    )
