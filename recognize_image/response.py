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


def FREE_TRAIL_EXPIRED_RESPONSE(Trail_Status , message):
    
    return Response({
        "status": status.HTTP_403_FORBIDDEN,
        "trial": Trail_Status,
        "message":message
        })



def TRAIL_PENDING(Trail_Status , message):
    
    return Response({
        "status": status.HTTP_200_OK,
        "trial": Trail_Status,
        "message":message
        })


def InternalServer_Response(message):

    return Response({
        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "message": message
    })
