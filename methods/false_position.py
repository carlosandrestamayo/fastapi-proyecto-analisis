# def calculate_xr_regla_falsa(fn, a, b, decimales):
    
#     fa = util.evaluate_function(fn, a, decimales)
#     fb = util.evaluate_function(fn, b, decimales)
    
#     xr = ((a * fb - b * fa) / (fb - fa))
    
#     return round(xr, decimales)

#from fastapi import APIRouter, HTTPException, Response  # type: ignore
from sympy import symbols, lambdify
from methods.util import teorema_bolzano, convert_to_decimal, tolerancia, error_relativo, evaluate_function
from schemas.bisection import BisectionRequest, BisectionRow, BisectionResponse, BisectionData, BisectionStep
from typing import List
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, convert_xor

MAX_ITER = 30  # Límite de iteraciones para evitar bucles infinitos

# Calcula el punto medio del intervalo [a, b]
def calculate_xr_false_position(fn, a, b, decimales):
    
    fa = util.evaluate_function(fn, a, decimales)
    fb = util.evaluate_function(fn, b, decimales)
    xr = ((a * fb - b * fa) / (fb - fa))
    return round(xr, decimales)

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
            xr = calculate_xr_false_position(xi, xs, decimals)

            # Evaluar función en xi, xs, xr
            fxi = evaluate_function(fn, xi, decimals)
            fxs = evaluate_function(fn, xs, decimals)
            fxr = evaluate_function(fn, xr, decimals)
           
            # Crear paso a paso para esta iteración
            step = BisectionStep(
                step1=str(iteration),
                step2=f"xi = {xi}, xs = {xs}",
                step3="f(xi) =" + raw_fn.replace('x', f"({xi})") + " = " + str(fxi),
                step4="f(xs) =" + raw_fn.replace('x', f"({xs})") + " = " + str(fxs),
                step5= "xr = (xs * f(xi) - xi * f(xs)) / (f(xi) - f(xs)) = ({xs} * {fxi} - {xi} * {fxs}) / ({fxi} - {fxs}) = {xr}"
                step6="f(Xs) =" + raw_fn.replace('x', f"({xs})") + " = " + str(fxs),
                step7="f(Xr) =" + raw_fn.replace('x', f"({xr})") + " = " + str(fxr),
                step8="",
                step9="",
                step10="",
                step11="se tiene en cuenta el criterio de detenimiento después de la iteración 1"
            )


            step1=str(iteration),
                step2=f"xi = {xi}, xs = {xs}, xr = {xr}",
                step3=f"xr = cambiar",
                step4=f"Intervalos de [{xi}, {xr}] y [{xr}, {xs}]",
                step5="f(Xi) =" + raw_fn.replace('x', f"({xi})") + " = " + str(fxi),
                step6="f(Xs) =" + raw_fn.replace('x', f"({xs})") + " = " + str(fxs),
                step7="f(Xr) =" + raw_fn.replace('x', f"({xr})") + " = " + str(fxr),
                step8="",
                step9="",
                step10="",
                step11="se tiene en cuenta el criterio de detenimiento después de la iteración 1"

            # Validar si fxr es raíz exacta
            if fxr == 0:
                return BisectionResponse(
                    success=True,
                    message="Method Completed",
                    data={
                        "root": xr,
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
                        finished = True

            x = convert_to_decimal(fxi, decimals)
            # Agregar fila a la tabla
            rows.append(BisectionRow(
                iteration=iteration,
                xi=float(xi),
                xs=float(xs),
                xr=xr,
                fxi=convert_to_decimal(fxi, decimals),
                fxs=convert_to_decimal(fxs, decimals),
                fxr=convert_to_decimal(fxr, decimals),
                error= "--" if iteration == 1 else error
            ))

            # rows.append(BisectionRow(
            #     iteration=iteration,
            #     xi=float(xi),
            #     xs=float(xs),
            #     xr=xr,
            #     fxi=fxi,
            #     fxs=fxs,
            #     fxr=fxr,
            #     error= "--" if iteration == 1 else error
            # ))

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
                        "root": xr,
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

{
  "success": true,
  "message": "Method completed",
  "data": {
    "root": -0.5781,
    "message_detention": "El método se ejecutó en 6 iteraciones con un error relativo de 0.0272",
    "headers": [
      "iteration",
      "xi",
      "xs",
      "xr",
      "fxi",
      "fxs",
      "fxr",
      "Er"
    ],
    "rows": [
      {
        "iteration": 1,
        "xi": -1,
        "xs": -0.5,
        "xr": -0.5,
        "fxi": -0.4736,
        "fxs": 1,
        "fxr": 0.1271,
        "error": "--"
      },
      {
        "iteration": 2,
        "xi": -0.75,
        "xs": -0.5,
        "xr": -0.75,
        "fxi": -0.4736,
        "fxs": 0.1271,
        "fxr": -0.2093,
        "error": 0.3333
      },
      {
        "iteration": 3,
        "xi": -0.625,
        "xs": -0.5,
        "xr": -0.625,
        "fxi": -0.2093,
        "fxs": 0.1271,
        "fxr": -0.0498,
        "error": 0.2
      },
      {
        "iteration": 4,
        "xi": -0.625,
        "xs": -0.5625,
        "xr": -0.5625,
        "fxi": -0.0498,
        "fxs": 0.1271,
        "fxr": 0.0365,
        "error": 0.1111
      },
      {
        "iteration": 5,
        "xi": -0.5938,
        "xs": -0.5625,
        "xr": -0.5938,
        "fxi": -0.0498,
        "fxs": 0.0365,
        "fxr": -0.0073,
        "error": 0.0527
      },
      {
        "iteration": 6,
        "xi": -0.5938,
        "xs": -0.5781,
        "xr": -0.5781,
        "fxi": -0.0073,
        "fxs": 0.0365,
        "fxr": 0.0145,
        "error": 0.0272
      }
    ],
    "steps": [
      {
        "step1": "1",
        "step2": "xi = -1.0, xs = 0.0, xr = -0.5",
        "step3": "xr = (-1.0 + 0.0) / 2 = -0.5",
        "step4": "Intervalos de [-1.0, -0.5] y [-0.5, 0.0]",
        "step5": "f(Xi) =sin((-1.0)) + e(-1.0)p((-1.0)) = -0.4736",
        "step6": "f(Xs) =sin((0.0)) + e(0.0)p((0.0)) = 1.0",
        "step7": "f(Xr) =sin((-0.5)) + e(-0.5)p((-0.5)) = 0.1271",
        "step8": "La raíz se encuentra en el intervalo [-1.0, -0.5] porque f(xi)*f(xr) < 0",
        "step9": "Hacemos xs = -0.5",
        "step10": "",
        "step11": "se tiene en cuenta el criterio de detenimiento después de la iteración 1"
      },
      {
        "step1": "2",
        "step2": "xi = -1.0, xs = -0.5, xr = -0.75",
        "step3": "xr = (-1.0 + -0.5) / 2 = -0.75",
        "step4": "Intervalos de [-1.0, -0.75] y [-0.75, -0.5]",
        "step5": "f(Xi) =sin((-1.0)) + e(-1.0)p((-1.0)) = -0.4736",
        "step6": "f(Xs) =sin((-0.5)) + e(-0.5)p((-0.5)) = 0.1271",
        "step7": "f(Xr) =sin((-0.75)) + e(-0.75)p((-0.75)) = -0.2093",
        "step8": "La raíz se encuentra en el intervalo [-0.75, -0.5] porque f(xi)*f(xr) no es < 0",
        "step9": "Hacemos xi = -0.75",
        "step10": "error relativo = |(-0.75 - -0.5) / -0.75| = 0.3333",
        "step11": "0.3333 es mayor que 0.05 continuamos en la siguiente iteración"
      },
      {
        "step1": "3",
        "step2": "xi = -0.75, xs = -0.5, xr = -0.625",
        "step3": "xr = (-0.75 + -0.5) / 2 = -0.625",
        "step4": "Intervalos de [-0.75, -0.625] y [-0.625, -0.5]",
        "step5": "f(Xi) =sin((-0.75)) + e(-0.75)p((-0.75)) = -0.2093",
        "step6": "f(Xs) =sin((-0.5)) + e(-0.5)p((-0.5)) = 0.1271",
        "step7": "f(Xr) =sin((-0.625)) + e(-0.625)p((-0.625)) = -0.0498",
        "step8": "La raíz se encuentra en el intervalo [-0.625, -0.5] porque f(xi)*f(xr) no es < 0",
        "step9": "Hacemos xi = -0.625",
        "step10": "error relativo = |(-0.625 - -0.75) / -0.625| = 0.2",
        "step11": "0.2 es mayor que 0.05 continuamos en la siguiente iteración"
      },
      {
        "step1": "4",
        "step2": "xi = -0.625, xs = -0.5, xr = -0.5625",
        "step3": "xr = (-0.625 + -0.5) / 2 = -0.5625",
        "step4": "Intervalos de [-0.625, -0.5625] y [-0.5625, -0.5]",
        "step5": "f(Xi) =sin((-0.625)) + e(-0.625)p((-0.625)) = -0.0498",
        "step6": "f(Xs) =sin((-0.5)) + e(-0.5)p((-0.5)) = 0.1271",
        "step7": "f(Xr) =sin((-0.5625)) + e(-0.5625)p((-0.5625)) = 0.0365",
        "step8": "La raíz se encuentra en el intervalo [-0.625, -0.5625] porque f(xi)*f(xr) < 0",
        "step9": "Hacemos xs = -0.5625",
        "step10": "error relativo = |(-0.5625 - -0.625) / -0.5625| = 0.1111",
        "step11": "0.1111 es mayor que 0.05 continuamos en la siguiente iteración"
      },
      {
        "step1": "5",
        "step2": "xi = -0.625, xs = -0.5625, xr = -0.5938",
        "step3": "xr = (-0.625 + -0.5625) / 2 = -0.5938",
        "step4": "Intervalos de [-0.625, -0.5938] y [-0.5938, -0.5625]",
        "step5": "f(Xi) =sin((-0.625)) + e(-0.625)p((-0.625)) = -0.0498",
        "step6": "f(Xs) =sin((-0.5625)) + e(-0.5625)p((-0.5625)) = 0.0365",
        "step7": "f(Xr) =sin((-0.5938)) + e(-0.5938)p((-0.5938)) = -0.0073",
        "step8": "La raíz se encuentra en el intervalo [-0.5938, -0.5625] porque f(xi)*f(xr) no es < 0",
        "step9": "Hacemos xi = -0.5938",
        "step10": "error relativo = |(-0.5938 - -0.5625) / -0.5938| = 0.0527",
        "step11": "0.0527 es mayor que 0.05 continuamos en la siguiente iteración"
      },
      {
        "step1": "6",
        "step2": "xi = -0.5938, xs = -0.5625, xr = -0.5781",
        "step3": "xr = (-0.5938 + -0.5625) / 2 = -0.5781",
        "step4": "Intervalos de [-0.5938, -0.5781] y [-0.5781, -0.5625]",
        "step5": "f(Xi) =sin((-0.5938)) + e(-0.5938)p((-0.5938)) = -0.0073",
        "step6": "f(Xs) =sin((-0.5625)) + e(-0.5625)p((-0.5625)) = 0.0365",
        "step7": "f(Xr) =sin((-0.5781)) + e(-0.5781)p((-0.5781)) = 0.0145",
        "step8": "La raíz se encuentra en el intervalo [-0.5938, -0.5781] porque f(xi)*f(xr) < 0",
        "step9": "Hacemos xs = -0.5781",
        "step10": "error relativo = |(-0.5781 - -0.5938) / -0.5781| = 0.0272",
        "step11": "0.0272 menor o igual que 0.05 se detienen las iteraciones"
      }
    ]
  }
}