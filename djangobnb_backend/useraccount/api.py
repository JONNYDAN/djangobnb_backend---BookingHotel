from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from .models import User
from .serializers import UserDetailSerializer
from property.serializers import ReservationsListSerializer



@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def landlord_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return JsonResponse({'detail': 'Not found.'}, status=404)

    serializer = UserDetailSerializer(user, many=False)
    return JsonResponse(serializer.data, safe=False)



@api_view(['GET'])
def reservations_list(request):
    reservations = request.user.reservations.all()
    
    serializer = ReservationsListSerializer(reservations, many=True)
    return JsonResponse(serializer.data, safe=False)
