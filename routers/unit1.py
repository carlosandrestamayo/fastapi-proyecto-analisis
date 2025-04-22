from fastapi import APIRouter # type: ignore
from schemas.bisection import BisectionRequest, BisectionResponse
from methods.bisection import bisection_method
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
