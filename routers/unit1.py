from fastapi import APIRouter # type: ignore
from schemas.bisection import BisectionRequest, BisectionResponse
from schemas.bolzano import BolzanoRequest, BolzanoResponse
from methods.bisection import bisection_method
from methods.bolzano import evaluate_bolzano
from pydantic import ValidationError

router = APIRouter()

@router.post('/biseccion', response_model=BisectionResponse)
async def bisection(request: BisectionRequest):
    """
    Endpoint para ejecutar el método de la bisección.
    Recibe una expresión matemática, intervalo y criterios de parada.
    """
    try:
        # Validación manual de los datos, útil si se extiende con reglas adicionales
        try:
            request_data = BisectionRequest(
                function=request.function,
                xi=request.xi,
                xs=request.xs,
                decimals=request.decimals,
                criterion=request.criterion,
                criterion_value=request.criterion_value
            )
        except ValidationError as e:
            return BisectionResponse(
                success=False,
                message=f"Error de validación: {str(e)}",
                data=None
            )

        # Ejecutar el método de la bisección
        return await bisection_method(request_data)

    except Exception as e:
        # Captura de errores no controlados
        return BisectionResponse(
            success=False,
            message=f"Error inesperado: {str(e)}",
            data=None
        )


@router.post('/bolzano', response_model=BolzanoResponse)
async def bolzano(request: BolzanoRequest):
    try:
        # Validación manual de los datos, útil si se extiende con reglas adicionales
        try:
            request_data = BolzanoRequest(
                function=request.function,
                xi=request.xi,
                xs=request.xs,
                decimals=request.decimals
            )
        except ValidationError as e:
            return BolzanoResponse(
                success=False,
                message=f"Error de validación: {str(e)}",
                #theoremSatisfied=False,
                data=None
            )

        # Ejecutar el método de la bisección
        return await evaluate_bolzano(request_data)

    except Exception as e:
        # Captura de errores no controlados
        return BolzanoResponse(
            success=False,
            message=f"Error inesperado: {str(e)}",
            #theoremSatisfied=False,
            data=None
        )
    
    from fastapi import FastAPI
from pydantic import BaseModel
from sympy import symbols, sin, exp, sympify, latex, E
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

#app = FastAPI()

x = symbols('x')  # Definimos símbolo para expresiones

transformations = standard_transformations + (implicit_multiplication_application,)

class ExpressionInput(BaseModel):
    expression: str  # Por ejemplo: "sin(0) + E**0"

@router.post("/evaluar")
def evaluar_expresion(data: ExpressionInput):
    try:
        # Parseamos expresión como símbolo
        expr = parse_expr(data.expression, transformations=transformations, evaluate=False)

        # Resultado numérico
        #resultado = expr.evalf()

        # Expresión simbólica en LaTeX
        expr_latex = latex(expr)

        return {
            "resultado": float(3),
            #"latex": f"${expr_latex}$"
            "latex": expr_latex
        }

        
    except Exception as e:
        return {"error": str(e)}
