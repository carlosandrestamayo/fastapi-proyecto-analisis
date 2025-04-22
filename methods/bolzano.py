from sympy import symbols, lambdify, sympify # type: ignore
from schemas.bolzano import BolzanoRequest, BolzanoResponse, BolzanoData, BolzanoSteps

def teorema_bolzano(request: BolzanoRequest):
    x = symbols('x')
    try:

        xi = request.xi
        xs = request.xs

        if xi >= xs:
            raise ValueError("Xi debe ser menor que Xs")

        fx = sympify(request.function)
        f = lambdify(x, fx, modules=["math"])
    
        fxi = round(f(request.xi), request.decimals)
        fxs = round(f(request.xs), request.decimals)
        product = round(fxi * fxs, request.decimals)
    
        theorem_satisfied = product < 0

        if theorem_satisfied:
            result_msg = f"Hay al menos una raíz en el intervalo [{request.xi}, {request.xs}]"
        else:
            result_msg = f"La existencia de una raíz en el intervalo [{request.xi}, {request.xs}] no está garantizada."

        
        steps = BolzanoSteps(
            step1="f(Xi) =" + request.function.replace('x',f"({request.xi})") + " = " + str(fxi),
            step2="f(Xs) =" + request.function.replace('x',f"({request.xs})") + " = " + str(fxs),
            step3=f"Calcular el producto  f(Xi) * f(Xs) = {fxi} * {fxs} = {product}.",
            step4=f"Como el producto es menor que cero, hay al menos una raíz en el intervalo [{xi}, {xs}]" if theorem_satisfied
                else f"Como el producto no es menor que cero, no se garantiza la existencia de una raíz en el intervalo [{xi}, {xs}]",
            
        )

        return BolzanoResponse(
            success=True,
            message="Verification completed",
            data=BolzanoData(
                result=result_msg,
                fxi=fxi,
                fxs=fxs,
                product=product,
                theorem_satisfied=theorem_satisfied,
                steps=steps
            )
        )

        
    except Exception as e:
        return BolzanoResponse(
           success=False,
           message=str(e),
           data= None
        )
    
