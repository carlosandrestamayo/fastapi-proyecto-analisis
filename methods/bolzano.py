import math
from methods.util import evaluate_function, parse_user_function
from schemas.bolzano import BolzanoRequest, BolzanoResponse, BolzanoData
from sympy import Interval, symbols
from sympy.calculus.util import continuous_domain

# Definir el símbolo 'x' para evaluación simbólica
x = symbols('x')

async def evaluate_bolzano(data: BolzanoRequest):
    """
    Evalúa si se cumple el Teorema de Bolzano para una función dada en un intervalo [xi, xs].
    Valida continuidad, signos, evaluabilidad de extremos y retorna información detallada.
    """
    try:
        # Extraer datos del request
        raw_fn = data.function
        xi = data.xi
        xs = data.xs
        decimals = data.decimals

        # Validar que xi < xs
        if xi >= xs:
            return BolzanoResponse(
                success=False,
                message="Xi debe ser menor que Xs.",
                data=None
            )

        # Parsear y preparar función del usuario
        fn = parse_user_function(raw_fn)

        # Evaluar función en xi y xs
        fxi = evaluate_function(fn, xi, decimals)
        fxs = evaluate_function(fn, xs, decimals)

        # Validar si fxi o fxs son NaN o Inf
        errors = []
        if math.isnan(fxi) or math.isinf(fxi):
            errors.append(f"en xi = {xi}")
        if math.isnan(fxs) or math.isinf(fxs):
            errors.append(f"en xs = {xs}")

        if errors:
            error_message = "La función no se puede evaluar " + " y ".join(errors) + "."
            return BolzanoResponse(
                success=False,
                message=error_message,
                data=None
            )

        # Verificar continuidad en el intervalo [xi, xs]
        domain = continuous_domain(fn, x, Interval(xi, xs))
        is_continuous = domain.contains(xi) and domain.contains(xs)

        # Calcular y redondear el producto f(xi) * f(xs)
        product = round(fxi * fxs, decimals)  # 👈 Redondeo correcto

        # Evaluar condición de Bolzano
        theorem_satisfied = bool(is_continuous and (product < 0))

        # Preparar datos de respuesta incluyendo el producto
        response_data = BolzanoData(
            xi=xi,
            xs=xs,
            fxi=fxi,
            fxs=fxs,
            product=product,
            theoremSatisfied=theorem_satisfied
        )

        # Construir mensaje de acuerdo al resultado
        if theorem_satisfied:
            message = "La función es continua en el intervalo y hay cambio de signo. Se cumple Bolzano."
        elif is_continuous and not (product < 0):
            message = "La función es continua en el intervalo, pero no hay cambio de signo. No se cumple Bolzano."
        else:
            message = "La función no es continua en el intervalo dado. No se puede aplicar Bolzano."

        # Retornar respuesta exitosa
        return BolzanoResponse(
            success=True,
            message=message,
            data=response_data
        )

    except Exception as e:
        # Captura y responde cualquier otra excepción inesperada
        return BolzanoResponse(
            success=False,
            message=f"Error al evaluar la función exception: {str(e)}",
            data=None
        )
