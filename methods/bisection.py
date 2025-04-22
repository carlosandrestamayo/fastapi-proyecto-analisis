#from fastapi import APIRouter, HTTPException, Response  # type: ignore
from sympy import symbols, lambdify
from methods.util import teorema_bolzano, convert_to_decimal, tolerancia, error_relativo, evaluate_function
from schemas.bisection import BisectionRequest, BisectionRow, BisectionResponse, BisectionData, BisectionStep
from typing import List
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, convert_xor

MAX_ITER = 30  # Límite de iteraciones para evitar bucles infinitos

# Calcula el punto medio del intervalo [a, b]
def calculate_xr_biseccion(a, b, decimales):
    return round((a + b) / 2, decimales)

# Método principal de bisección
async def bisection_method(data: BisectionRequest):
    try:
        # Extraer los datos del request
        #fn = data.function
        raw_fn = data.function
        xi = data.xi
        xs = data.xs
        decimals = data.decimals
        criterion = data.criterion
        criterion_value = data.criterion_value

         # Convertir la función con soporte para ^ como potencia
        transformations = standard_transformations + (convert_xor,)
        fn = parse_expr(raw_fn, transformations=transformations)

        # Inicialización de variables
        iteration = 1
        xr_last = None
        xr = None
        headers = ["iteration", "xi", "xs", "xr", "fxi", "fxs", "fxr", "error"]
        rows: List[BisectionRow] = []
        steps: List[BisectionStep] = []
        error = ""

        # Validar que xi < xs
        if xi >= xs:
            return BisectionResponse(success=False, message="Xi debe ser menor que Xs", data=None)

        # Verificar el teorema de Bolzano
        value_bolzano, msg_bolzano = teorema_bolzano(fn, xi, xs, decimals)
        if not value_bolzano:
            return BisectionResponse(success=False, message=msg_bolzano, data=None)

        while True:
            xr = calculate_xr_biseccion(xi, xs, decimals)

            # Evaluar función en xi, xs, xr
            fxi = evaluate_function(fn, xi, decimals)
            fxs = evaluate_function(fn, xs, decimals)
            fxr = evaluate_function(fn, xr, decimals)


            row = BisectionRow(
                iteration=iteration,
                xi=float(xi),
                xs=float(xs),
                xr=xr,
                fxi=convert_to_decimal(fxi, decimals),
                fxs=convert_to_decimal(fxs, decimals),
                fxr=convert_to_decimal(fxr, decimals),
                error= "--" if iteration == 1 else error,
                isRoot= False
            )
           
            # Crear paso a paso para esta iteración
            step = BisectionStep(
                step1=str(iteration),
                step2=f"xi = {xi}, xs = {xs}, xr = {xr}",
                step3=f"xr = ({xi} + {xs}) / 2 = {xr}",
                step4=f"Intervalos de [{xi}, {xr}] y [{xr}, {xs}]",
                step5="f(Xi) =" + raw_fn.replace('x', f"({xi})") + " = " + str(fxi),
                step6="f(Xs) =" + raw_fn.replace('x', f"({xs})") + " = " + str(fxs),
                step7="f(Xr) =" + raw_fn.replace('x', f"({xr})") + " = " + str(fxr),
                step8="",
                step9="",
                step10="",
                step11="se tiene en cuenta el criterio de detenimiento después de la iteración 1"
            )

            # Validar si fxr es raíz exacta
            if fxr == 0:
                return BisectionResponse(
                    success=True,
                    message="Method Completed",
                    data={
                        "rootValue": xr,
                        "rootFunctionValue": evaluate_function(fn, xr, decimals),
                        "headers": headers,
                        "rows": rows,
                        "steps": steps,
                        "message_detention": f"El método encontró la raíz {xr} en {iteration} iteraciones porque f(xr) = 0"
                    }
                )

            # Elegir nuevo intervalo
            if fxi * fxr < 0:
                xs = xr
                step.step8 = f"La raíz se encuentra en el intervalo [{xi}, {xs}] porque f(xi)*f(xr) < 0"
                step.step9 = f"Hacemos xs = {xr}"
            else:
                xi = xr
                step.step8 = f"La raíz se encuentra en el intervalo [{xi}, {xs}] porque f(xi)*f(xr) no es < 0"
                step.step9 = f"Hacemos xi = {xr}"

            # Evaluar criterio de parada
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
                    step.step10 = f"tolerancia = |{xr} - {xr_last}| = {error}"
                    if error > criterion_value:
                        step.step11 = f"{error} es mayor que {criterion_value} continuamos en la siguiente iteración"
                    else:
                        step.step11 = f"{error} menor o igual que {criterion_value} se detienen las iteraciones"
                        message_detention = f"El método se ejecutó en {iteration} iteraciones con una tolerancia de {error}"
                        isRoot = True
                        finished = True
                else:
                    headers[-1] = criterio_headers[criterion]
                    error = error_relativo(xr_last, xr, decimals)
                    step.step10 = f"error relativo = |({xr} - {xr_last}) / {xr}| = {error}"
                    if error > criterion_value:
                        step.step11 = f"{error} es mayor que {criterion_value} continuamos en la siguiente iteración"
                    else:
                        step.step11 = f"{error} menor o igual que {criterion_value} se detienen las iteraciones"
                        message_detention = f"El método se ejecutó en {iteration} iteraciones con un error relativo de {error}"
                        isRoot = True
                        finished = True

            row.isRoot = isRoot
            row.error = "--" if iteration == 1 else error
            
            #Cambio para push
            # Agregar fila a la tabla
            # rows.append(BisectionRow(
            #     iteration=iteration,
            #     xi=float(xi),
            #     xs=float(xs),
            #     xr=xr,
            #     fxi=convert_to_decimal(fxi, decimals),
            #     fxs=convert_to_decimal(fxs, decimals),
            #     fxr=convert_to_decimal(fxr, decimals),
            #     error= "--" if iteration == 1 else error,
            #     isRoot= isRoot
            # ))

            rows.append(row)

            # Agregar paso a la lista
            steps.append(step)

            if iteration == MAX_ITER:
                message_detention = f"Número máximo de iteraciones permitido por la calculadora es {MAX_ITER}"
                finished = True
            
            if finished:
                return BisectionResponse(
                    success=True,
                    message="Method completed",
                    data={
                        "rootValue": xr,
                        "rootFunctionValue": evaluate_function(fn, xr, decimals),
                        "headers": headers,
                        "rows": rows,
                        "steps": steps,
                        "message_detention": message_detention,
                    }
                )

            # Preparar para la siguiente iteración
            iteration += 1
            xr_last = round(xr, decimals)

    except Exception as e:
        # Captura de errores inesperados
        return BisectionResponse(
            success=False,
            message="exception final bisección " + str(e),
            data=None
        )
