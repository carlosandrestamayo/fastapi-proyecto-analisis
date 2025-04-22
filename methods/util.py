from sympy import sympify, symbols, lambdify, diff
from sympy.core.sympify import SympifyError
from schemas.bisection import BisectionResponse
from typing import List

def convert_to_decimal(n, decimales):
    formato = f"{{:.{decimales}f}}"
    return formato.format(n)
    
def evaluate_function(fn, a, decimales=4):
    x = symbols('x')
    f = lambdify(x, fn)
    return round(f(a), decimales)
    
    
def teorema_bolzano(fn, a, b, decimales):
    fa = evaluate_function(fn, a, decimales)
    fb = evaluate_function(fn, b, decimales)
    
    if fa * fb < 0:
        return True, "Existen Raices en el intervalo"
    else:
        return False, "No existe raices en este intervalo"

def error_absoluto(xr_anterior, xr):
  return abs((xr - xr_anterior) / xr)

def tolerancia(xr_last, xr, decimals):
    return round(abs(xr- xr_last), decimals)

def error_relativo(xr_anterior, xr, decimals):
  return round(abs((xr - xr_anterior) / xr), decimals)




def validar_funcion_sympy(expr_str: str, variables_permitidas: List[str] = ["x"]) -> BisectionResponse:
    #except SympifyError as e:

    # try:
    #     expr = sympify(expr_str)
    #     return BisectionResponse(success=True, message="Función válida.", data=None)
    # except SympifyError as e:
    #     return BisectionResponse(success=False, message=f"Error de parsing: {e}", data=None)
    # except Exception as e:
    #     return BisectionResponse(success=False, message=f"Error inesperado: {e}", data=None)
    try:
        expr = sympify(expr_str)
        # Verificar que no haya variables inesperadas
        variables_usadas = [str(s) for s in expr.free_symbols]
        for v in variables_usadas:
            if v not in variables_permitidas:
                return BisectionResponse(
                    success=False,
                    message=f"La expresión usa variables no permitidas: {v}",
                    data=None
                )
        return BisectionResponse(
            success=True,
            message="La función es válida.",
            data=None
        )
    except Exception as e:
        return BisectionResponse(
            success=False,
            message=f"La función es inválida: {str(e)}",
            data=None
        )
