from sympy import sympify, symbols, lambdify, diff, latex
from sympy.core.sympify import SympifyError
from schemas.bisection import BisectionResponse
from typing import List
import re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from sympy import sympify, symbols, exp, log, sin, cos, tan, sqrt

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
    

def convert_to_sympy_expr(expr_str, variables=None):
    """
    Convierte expresiones matemáticas escritas en notación común a expresiones válidas de sympy.

    Soporta:
    - e^x → exp(x)
    - ln(x) → log(x)
    - sin, cos, tan
    - √x o √(x) → sqrt(x)
    - Multiplicación implícita: 2x → 2*x, 3(x+1) → 3*(x+1), (x+1)(x-1) → (x+1)*(x-1)

    Parámetros:
    - expr_str: str, expresión matemática en notación de usuario
    - variables: lista de variables usadas en la expresión (ej. ["x", "y"])

    Retorna:
    - expresión sympy
    """

    # Paso 1: normalizar potencias
    expr_str = expr_str.replace('^', '**')

    # Paso 2: reemplazos de funciones
    expr_str = re.sub(r'e\^\((.*?)\)', r'exp(\1)', expr_str)
    expr_str = re.sub(r'\be\^(\w+)', r'exp(\1)', expr_str)
    expr_str = re.sub(r'\bln\((.*?)\)', r'log(\1)', expr_str)
    expr_str = re.sub(r'\bsin\((.*?)\)', r'sin(\1)', expr_str)
    expr_str = re.sub(r'\bcos\((.*?)\)', r'cos(\1)', expr_str)
    expr_str = re.sub(r'\btan\((.*?)\)', r'tan(\1)', expr_str)
    expr_str = re.sub(r'√\((.*?)\)', r'sqrt(\1)', expr_str)
    expr_str = re.sub(r'√(\w+)', r'sqrt(\1)', expr_str)

    # Paso 3: multiplicación implícita
    # a) Número seguido de variable o paréntesis: 2x → 2*x, 3(x+1) → 3*(x+1)
    expr_str = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr_str)

    # b) Variable o paréntesis seguida de paréntesis: x(x+1) o )(
    expr_str = re.sub(r'([a-zA-Z0-9)])\s*\(', r'\1*(', expr_str)

    # c) Paréntesis seguida de variable: )(x) → )*x
    expr_str = re.sub(r'\)([a-zA-Z])', r')*\1', expr_str)

    # Paso 4: definir variables simbólicas
    if variables is None:
        variables = ['x']
    sympy_vars = symbols(variables)

    # Paso 5: convertir a sympy
    return sympify(expr_str, locals={str(var): var for var in sympy_vars})


def convert_expresion_latex(expr):
    transformations = standard_transformations + (implicit_multiplication_application,)
    expr = parse_expr(expr.expression, transformations=transformations, evaluate=False)
    #f = sympify(f_str)
        # Resultado numérico
        #resultado = expr.evalf()

        # Expresión simbólica en LaTeX
    expr_latex = latex(sympify(expr))
    print(expr_latex)

    return expr_latex

    # return {
    #     #"latex": f"${expr_latex}$"
    #     "latex": expr_latex
    # }