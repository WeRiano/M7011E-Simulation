from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from simulation.manager import Manager


@api_view(['GET'])
def get_conditions(request, conditions):
    if "Authorization" not in request.headers.keys():
        response = {
            "error": "Please provide an auth token (Token <auth_token>)."
        }
        return Response(data=response, status=status.HTTP_403_FORBIDDEN)
    conditions = Manager.get_conditions(conditions, request.headers['Authorization'])
    return Response(data=conditions, status=status.HTTP_200_OK)


@api_view(['POST'])
def set_delta(request, delta):
    if delta > 3600 or delta < 5:
        response = {
            "error": "simulation update frequency must be on the interval [5, 3600] seconds"
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    Manager.set_delta(request.headers['Authorization'], delta)
    return Response(data={}, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def set_ratios(request, storing, using):
    if (storing < 0.0 or storing > 1.0) or (using < 0.0 or using > 1.0):
        response = {
            "error": "Ratios must be on the interval [0.0, 1.0] (0% to 100%)"
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    Manager.set_ratios(storing, using, request.headers["Authorization"])
    return Response(data={}, status=status.HTTP_202_ACCEPTED)
