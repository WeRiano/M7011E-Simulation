from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from simulation.manager import Manager
from api.backend import request_get_user_info, request_get_all_users


@api_view(['POST'])
def admin_reset_sim(request, user_id):
    error, response = __check_auth_header(request)
    if error:
        return response

    token_header = request.headers['Authorization']
    error, response = __admin_endpoint_validations(user_id, token_header)
    if error:
        return response

    Manager.restart_instance(user_id)
    response = {
        "success": "The simulation belonging to user with id {0} what successfully reset".format(user_id)
    }
    return Response(data=response, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_conditions(request, conditions):
    error, response = __check_auth_header(request)
    if error:
        return response

    token_header = request.headers['Authorization']
    request_get_user_info(token_header)
    user_id = request_get_user_info(token_header)["id"]     # Get "my" id

    conditions = Manager.get_conditions(conditions, user_id)
    return Response(data=conditions, status=status.HTTP_200_OK)


@api_view(['GET'])
def admin_get_conditions(request, conditions, user_id):
    error, response = __check_auth_header(request)
    if error:
        return response

    token_header = request.headers['Authorization']
    error, response = __admin_endpoint_validations(user_id, token_header)
    if error:
        return response

    conditions = Manager.get_conditions(conditions, user_id)

    return Response(data=conditions, status=status.HTTP_200_OK)


@api_view(['POST'])
def set_delta(request, delta):
    error, response = __check_auth_header(request)
    if error:
        return response

    error, response = __validate_delta(delta)
    if error:
        return response

    token_header = request.headers['Authorization']
    user_id = request_get_user_info(token_header)["id"]  # Get "my" id

    Manager.set_delta(delta, user_id)
    return Response(data={"success": "User simulation update frequency (delta) updated"
                                     "successfully to {0}.".format(delta)}, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def admin_set_delta(request, delta, user_id):
    error, response = __check_auth_header(request)
    if error:
        return response

    error, response = __validate_delta(delta)
    if error:
        return response

    token_header = request.headers['Authorization']
    error, response = __admin_endpoint_validations(user_id, token_header)
    if error:
        return response

    Manager.set_delta(delta, user_id)
    return Response(data={"success": "User simulation update frequency (delta) updated"
                                     "successfully to {0}.".format(delta)}, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def set_ratios(request, storing, using):
    error, response = __check_auth_header(request)
    if error:
        return response

    error, response = __validate_ratios(storing, using)
    if error:
        return response

    token_header = request.headers['Authorization']
    user_id = request_get_user_info(token_header)["id"]  # Get "my" id

    Manager.set_ratios(storing, using, user_id)
    return Response(data={"success": "User ratios updated successfully to storing: {0}"
                                     "and using using: {1}.".format(storing, using)},
                    status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def admin_set_ratios(request, storing, using, user_id):
    error, response = __check_auth_header(request)
    if error:
        return response

    error, response = __validate_ratios(storing, using)
    if error:
        return response

    token_header = request.headers['Authorization']
    error, response = __admin_endpoint_validations(user_id, token_header)
    if error:
        return response

    Manager.set_ratios(storing, using,  user_id)
    return Response(data={"success": "User ratios updated successfully to storing: {0}"
                                     "and using using: {1}.".format(storing, using)},
                    status=status.HTTP_202_ACCEPTED)


# Just a couple of validations that are consistent for all admin endpoints
def __admin_endpoint_validations(user_id, admin_token_header):
    error, response = __validate_admin(admin_token_header)
    if error:
        return response

    error, response = __validate_user_id(user_id)
    if error:
        return response

    error, response = __validate_simulation(user_id, admin_token_header)
    if error:
        return error, response

    return False, None


# Makes sure that the given user_id is not 'made up' and actually matches a user in the backend service
# (This is only a problem when an admin manually provides a user_id for any of the admin endpoints.
#  In a 'regular' endpoint, the user_id is fetched from the backend service itself with auth token,
#  so no error can occur unless internal in django)
def __validate_simulation(user_id, admin_token_header):
    all_users = request_get_all_users(admin_token_header)["users"]
    for user in all_users:
        if user["id"] == user_id:
            return False, None
    response = {
        "error": "The given user id does not match any user in the backend service."
    }
    return True, response


def __validate_delta(delta):
    if delta > 3600 or delta < 5:
        response = {
            "error": "simulation update frequency must be on the interval [5, 3600] seconds"
        }
        return True, Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    return False, None


def __validate_user_id(user_id):
    if user_id <= 0:
        response = {
            "error": "The user id must be a positive integer."
        }
        return True, Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    return False, None


def __validate_admin(admin_token_header):
    is_admin = request_get_user_info(admin_token_header)["admin"]
    if not is_admin:
        response = {
            "error": "This endpoint requires admin status if a user id is provided."
        }
        return True, Response(data=response, status=status.HTTP_403_FORBIDDEN)
    return False, None


# Checks if the two ratios storing and using are valid decimals. If either isn't, an error is returned
def __validate_ratios(storing, using):
    if (storing < 0.0 or storing > 1.0) or (using < 0.0 or using > 1.0):
        response = {
            "error": "Ratios must be on the interval [0.0, 1.0] (0% to 100%)"
        }
        return True, Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    return False, None


# Checks if an auth token is present in http header and returns an error if it was not provided
def __check_auth_header(request):
    if "Authorization" not in request.headers.keys():
        response = {
            "error": "Please provide an auth token (Token <auth_token>)."
        }
        return True, Response(data=response, status=status.HTTP_403_FORBIDDEN)
    return False, None
