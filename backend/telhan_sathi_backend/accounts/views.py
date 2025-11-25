import random
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Farmer, OTP

@api_view(['POST'])
def generate_otp(request):
    farmer_id = request.data.get('farmer_id')

    try:
        farmer = Farmer.objects.get(farmer_id=farmer_id)
    except Farmer.DoesNotExist:
        return Response({'error': 'Farmer ID not found'}, status=404)

    otp_value = str(random.randint(1000, 9999))

    OTP.objects.create(farmer=farmer, otp=otp_value)

    # For demo only, print instead of SMS API
    print("OTP sent:", otp_value)

    return Response({'message': 'OTP sent to your registered mobile number'})

@api_view(['POST'])
def verify_otp(request):
    farmer_id = request.data.get('farmer_id')
    otp_entered = request.data.get('otp')

    try:
        farmer = Farmer.objects.get(farmer_id=farmer_id)
        otp_obj = OTP.objects.filter(farmer=farmer).last()
    except:
        return Response({'error': 'Invalid farmer or OTP'}, status=400)

    if otp_obj.otp == otp_entered:
        return Response({
            'message': 'Login successful',
            'farmer': {
                'name': farmer.name,
                'district': farmer.district,
                'land_size': farmer.land_size
            }
        })
    else:
        return Response({'error': 'Invalid OTP'}, status=400)
