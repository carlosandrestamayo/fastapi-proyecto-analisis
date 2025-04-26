from sympy import sympify, symbols, lambdify, diff
from sympy.core.sympify import SympifyError
from schemas.bisection import BisectionResponse
from typing import List
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, convert_xor
import re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, convert_xor

x = symbols('x')  # Declaramos la variable x globalmente


def convert_to_decimal(n, decimales):
    formato = f"{{:.{decimales}f}}"
    return formato.format(n)
    
def evaluate_function(fn, a, decimales=4):
    #x = symbols('x')
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


def parse_user_function(raw_fn: str):
    """
    Preprocesa y parsea una función escrita por el usuario para que sea compatible con SymPy.
    Corrige notaciones comunes como 'e(x)', 'sen', 'ln', 'tg', y convierte '^' a '**'.

    Parámetros:
        raw_fn (str): Función original escrita por el usuario.

    Retorna:
        sympy.Expr: Expresión simbólica lista para usar en SymPy.
    """

    # 🔥 Paso 1: Reemplazos de palabras comunes
    raw_fn = raw_fn.replace('e(', 'exp(')
    raw_fn = re.sub(r'\bsen\(', 'sin(', raw_fn)
    raw_fn = re.sub(r'\bln\(', 'log(', raw_fn)
    raw_fn = re.sub(r'\btg\(', 'tan(', raw_fn)

    # 🔥 Paso 2: Configurar transformaciones para que ^ funcione como **
    transformations = standard_transformations + (convert_xor,)

    # 🔥 Paso 3: Parsear la función
    fn = parse_expr(raw_fn, transformations=transformations)

    return fn

def validar_funcion_sympy(expr_str: str, variables_permitidas: List[str] = ["x"]) -> BisectionResponse:
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
