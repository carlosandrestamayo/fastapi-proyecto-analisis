from typing import List
from sympy import symbols
from methods.util import (
    teorema_bolzano,
    convert_to_decimal,
    tolerancia,
    error_relativo,
    evaluate_function,
    parse_user_function
)
from schemas.bisection import (
    BisectionRequest,
    BisectionRow,
    BisectionResponse,
    BisectionData,
    BisectionStep
)

MAX_ITER = 30  # Límite de iteraciones para evitar bucles infinitos

# Calcula el punto medio del intervalo [a, b], redondeado a un número de decimales
def calculate_xr_biseccion(a: float, b: float, decimals: int) -> float:
    return round((a + b) / 2, decimals)

# Método principal para ejecutar el método de la bisección
async def bisection_method(data: BisectionRequest) -> BisectionResponse:
    try:
        # Extracción de parámetros del request
        raw_fn = data.function
        xi = data.xi
        xs = data.xs
        decimals = data.decimals
        criterion = data.criterion
        criterion_value = data.criterion_value

        # Validar que xi < xs
        if xi >= xs:
            return BisectionResponse(success=False, message="Xi debe ser menor que Xs.", data=None)

        # Parsear y preparar la función del usuario
        fn = parse_user_function(raw_fn)

        # Inicializar variables de control
        iteration = 1
        xr_last = None
        xr = None
        headers: List[str] = ["iteration", "xi", "xs", "xr", "fxi", "fxs", "fxr", "error"]
        rows: List[BisectionRow] = []
        steps: List[BisectionStep] = []
        error = ""

        # Verificar si se cumple el teorema de Bolzano en [xi, xs]
        value_bolzano, msg_bolzano = teorema_bolzano(fn, xi, xs, decimals)
        if not value_bolzano:
            return BisectionResponse(success=False, message=msg_bolzano, data=None)

        # Ciclo principal de iteraciones
        while True:
            # Calcular xr (punto medio)
            xr = calculate_xr_biseccion(xi, xs, decimals)

            # Evaluar función en xi, xs, xr
            fxi = evaluate_function(fn, xi, decimals)
            fxs = evaluate_function(fn, xs, decimals)
            fxr = evaluate_function(fn, xr, decimals)

            # Crear fila de resultados para la tabla
            row = BisectionRow(
                iteration=iteration,
                xi=xi,
                xs=xs,
                xr=xr,
                fxi=convert_to_decimal(fxi, decimals),
                fxs=convert_to_decimal(fxs, decimals),
                fxr=convert_to_decimal(fxr, decimals),
                error="--" if iteration == 1 else error,
                isRoot=False
            )

            # Crear el paso a paso de esta iteración
            step = BisectionStep(
                step1=str(iteration),
                step2=f"xi = {xi}, xs = {xs}, xr = {xr}",
                step3=f"xr = ({xi} + {xs}) / 2 = {xr}",
                step4=f"Intervalos de [{xi}, {xr}] y [{xr}, {xs}]",
                step5=f"f(Xi) = {raw_fn.replace('x', f'({xi})')} = {fxi}",
                step6=f"f(Xs) = {raw_fn.replace('x', f'({xs})')} = {fxs}",
                step7=f"f(Xr) = {raw_fn.replace('x', f'({xr})')} = {fxr}",
                step8="",
                step9="",
                step10="",
                step11="Se tiene en cuenta el criterio de detenimiento después de la iteración 1."
            )

            # Validar si fxr es una raíz exacta
            if fxr == 0:
                return BisectionResponse(
                    success=True,
                    message="Método completado: raíz exacta encontrada.",
                    data=BisectionData(
                        rootValue=xr,
                        rootFunctionValue=evaluate_function(fn, xr, decimals),
                        headers=headers,
                        rows=rows,
                        steps=steps,
                        message_detention=f"Raíz exacta encontrada: f({xr}) = 0 en la iteración {iteration}."
                    )
                )

            # Actualizar intervalo según el signo de f(xr)
            if fxi * fxr < 0:
                xs = xr
                step.step8 = f"La raíz está en [{xi}, {xs}] porque f(xi)*f(xr) < 0."
                step.step9 = f"Actualizamos xs = {xr}."
            else:
                xi = xr
                step.step8 = f"La raíz está en [{xi}, {xs}] porque f(xi)*f(xr) no es < 0."
                step.step9 = f"Actualizamos xi = {xr}."

            # Evaluar criterios de parada
            finished = False
            message_detention = ""
            isRoot = False
            criterio_headers = {
                "error_relativo": "Er",
                "tolerancia": "Tolerancia"
            }

            if iteration > 1:
                if criterion == "tolerancia":
                    headers[-1] = criterio_headers[criterion]
                    error = tolerancia(xr_last, xr, decimals)
                    step.step10 = f"Tolerancia = |{xr} - {xr_last}| = {error}"
                    if error <= criterion_value:
                        step.step11 = f"Tolerancia {error} <= {criterion_value}, se detienen las iteraciones."
                        message_detention = f"Proceso terminado en {iteration} iteraciones con tolerancia de {error}."
                        isRoot = True
                        finished = True
                    else:
                        step.step11 = f"Tolerancia {error} > {criterion_value}, continuamos iterando."
                else:
                    headers[-1] = criterio_headers[criterion]
                    error = error_relativo(xr_last, xr, decimals)
                    step.step10 = f"Error relativo = |({xr} - {xr_last}) / {xr}| = {error}"
                    if error <= criterion_value:
                        step.step11 = f"Error relativo {error} <= {criterion_value}, se detienen las iteraciones."
                        message_detention = f"Proceso terminado en {iteration} iteraciones con error relativo de {error}."
                        isRoot = True
                        finished = True
                    else:
                        step.step11 = f"Error relativo {error} > {criterion_value}, continuamos iterando."

            # Actualizar fila actual
            row.isRoot = isRoot
            row.error = "--" if iteration == 1 else error

            # Agregar fila y paso a las listas
            rows.append(row)
            steps.append(step)

            # Validar si alcanzó máximo de iteraciones
            if iteration == MAX_ITER:
                message_detention = f"Se alcanzó el máximo de iteraciones permitido: {MAX_ITER}."
                finished = True

            # Si terminó el proceso, retornar resultados
            if finished:
                return BisectionResponse(
                    success=True,
                    message="Método completado.",
                    data=BisectionData(
                        rootValue=xr,
                        rootFunctionValue=evaluate_function(fn, xr, decimals),
                        headers=headers,
                        rows=rows,
                        steps=steps,
                        message_detention=message_detention
                    )
                )

            # Preparar siguiente iteración
            iteration += 1
            xr_last = round(xr, decimals)

    except Exception as e:
        # Captura de errores inesperados
        return BisectionResponse(
            success=False,
            message=f"Excepción en bisección: {str(e)}",
            data=None
        )
