from rest_framework import status
from rest_framework.response import Response

def BAD_REQUEST_RESPONSE(message):

    return Response({
        "status": status.HTTP_400_BAD_REQUEST,
        "message": message
    })


def NOT_FOUND_RESPONSE(message):

    return Response({
        "status": status.HTTP_404_NOT_FOUND,
        "message": message
    })


def FREE_TRAIL_EXPIRED_RESPONSE(is_paid , message):
    
    return Response({
        "status": status.HTTP_403_FORBIDDEN,
        "trial": is_paid,
        "message":message
        })



def TRAIL_PENDING(is_paid , message):
    
    return Response({
        "status": status.HTTP_403_FORBIDDEN,
        "trial": is_paid,
        "message":message
        })


def InternalServer_Response(message):

    return Response({
        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "message": message
    })
