from pydantic import BaseModel, Field
from typing import Optional

class BolzanoRequest(BaseModel):
    function: str = Field(..., description="Mathematical expression, e.g., 'x**2 - 2'")
    xi: float = Field(..., description="Lower bound of the interval")
    xs: float = Field(..., description="Upper bound of the interval")
    decimals: int = Field(..., gt=0, lt=10, description="Number of decimal places (must be > 0 and < 10)")


class BolzanoSteps(BaseModel):
    step1: str
    step2: str
    step3: str
    step4: str


class BolzanoData(BaseModel):
    result: str                          # Explicación del resultado
    fxi: float                           # Valor de f(xi)
    fxs: float                           # Valor de f(xs)
    product: float                       # f(xi) * f(xs)
    theorem_satisfied: bool             # Si se cumple el teorema de Bolzano
    steps: BolzanoSteps                 # Explicación paso a paso


class BolzanoResponse(BaseModel):
    success: bool                        # Si la operación fue exitosa
    message: str                         # Mensaje general (ej. "Verificación completada")
    data: Optional[BolzanoData]         # Datos detallados del resultado (puede ser None en errores)
