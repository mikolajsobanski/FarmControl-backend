import datetime
import random
import string
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import status
from django.core.mail import send_mail
from django.db.models import Q

from .authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_refresh_token
from .serializers import FarmerSerializer
from .models import Farmer, FarmerToken, Forgot

class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')
        
        serializer = FarmerSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

class LoginAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        farmer = Farmer.objects.filter(email=email).first()

        if farmer is None:
            raise exceptions.AuthenticationFailed('Invalid credentails')
        
        if not farmer.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid credentails')
        
        access_token = create_access_token(farmer.id)
        refresh_token = create_refresh_token(farmer.id)

        FarmerToken.objects.create(
            user_id = farmer.id,
            token = refresh_token,
            expired_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        )
        
        response = Response()
        
        response.data = {
            'token': access_token,
            'refresh_token' : refresh_token
        }
        return response
    
class FarmerAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response(FarmerSerializer(request.user).data)
    
class FarmerShortDetailsAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        farmer = Farmer.objects.filter(id=pk).first()
        response = Response()
        
        if farmer is not None:
            response.data = {
                'first_name': farmer.first_name,
                'last_name': farmer.last_name 
            }
            return response
        else:
            response.data = {
                'message': 'Farmer not found'
            }
            return response

    

class RefreshAPIView(APIView):
    def post(self, request):
        refresh_token = request.data['refresh_token']
        id = decode_refresh_token(refresh_token)

        if not FarmerToken.objects.filter(
            user_id=id,
            token=refresh_token,
            expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)
        ).exists():
            raise exceptions.AuthenticationFailed('Unauthenticated')

        access_token = create_access_token(id)

        return Response({
            'token': access_token
        })
    

class LogoutAPIView(APIView):
    def post(self, request):
        refresh_token = request.data['refresh_token']
        FarmerToken.objects.filter(token=refresh_token).delete()

        response = Response()

        response.data = {
            'message': 'success'
        }
        return response
    

class ForgotAPIView(APIView):
    def post(self,request):
        email = request.data['email']

        farmer = Farmer.objects.filter(email=email)
        if not farmer:
            raise exceptions.APIException('User not found!')
        
        token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

        Forgot.objects.create(
            email=request.data['email'],
            token=token
        )

        url = 'http://localhost:3000/reset/' + token

        send_mail(
            subject='Reset you password!',
            message='Click <a href="%s">here<a/> to reset your password!' % url,
            from_email='farmcontrol.management@gmail.com',
            recipient_list=[email]
        )


        return Response({
            'message': 'success'
        })
    

class ResetAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')
        
        reset_password = Forgot.objects.filter(token=data['token']).first()

        if not reset_password:
            raise exceptions.APIException('Invalid link!')
        
        farmer = Farmer.objects.filter(email=reset_password.email).first()

        if not farmer:
            raise exceptions.APIException('User not found!')
        
        farmer.set_password(data['password'])
        farmer.save()
        return Response({
            'message': 'success'
        })
    
class UpdateAPIView(APIView):
    def patch(self, request):
        pk = request.data['pk']
        haslo = request.data['haslo']
        
        farmer = Farmer.objects.filter(id=pk).first()

        if not farmer:
            raise exceptions.APIException('User not found!')

        if not farmer.check_password(haslo):
            raise exceptions.AuthenticationFailed('User not found!')

        if 'password' in request.data:
            farmer.set_password(request.data['password'])
            farmer.save()
            return  Response({
                'message': 'success'
        })

        serializer = FarmerSerializer(farmer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'success'
        })

class PhotoAPIView(APIView):
    def post(self, request):
        data = request.data
        farmer_id = data['pk']
        farmer = Farmer.objects.get(id=farmer_id)
        farmer.photo = request.FILES.get('photo')
        farmer.save()
        return Response({
            'message': 'success'
        })



class DeleteAPIView(APIView):
    def delete(self, request):
        pk = request.query_params.get('pk')
        haslo = request.query_params.get('haslo')
        
        farmer = Farmer.objects.filter(id=pk).first()

        if not farmer:
            raise exceptions.APIException('User not found!')
        
        if not farmer.check_password(haslo):
            raise exceptions.AuthenticationFailed('User not found!')
        
        farmer.delete()
        return Response({
            'message': 'success'
        })

class DeleteWorkerAPIView(APIView):
    def delete(self, request):
        pk = request.query_params.get('pk')
        haslo = request.query_params.get('haslo')
        pk_worker = request.query_params.get('pk_worker')
        farmer = Farmer.objects.filter(id=pk, is_owner=True).first()

        if not farmer:
            raise exceptions.APIException('User not found!')
        
        if not farmer.check_password(haslo):
            raise exceptions.AuthenticationFailed('User not found!')
        
        worker = Farmer.objects.filter(id=pk_worker).first()
        
        worker.delete()
        return Response({
            'message': 'success'
        })

class ContactSupportAPIView(APIView):
     def post(self, request):
        email = request.data.get('email')
        content = request.data.get('content')

        farmer = Farmer.objects.filter(email=email)
        if not farmer:
            raise exceptions.APIException('User not found!')

        send_mail(
            subject='Wiadomosc od %s' % email,
            message='"%s"' % content,
            from_email='farmcontrol.management@gmail.com',
            recipient_list=['farmcontrol.help@gmail.com']
        )

        return Response({
            'message': 'success'
        })
     
class EmployeeAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        employees = Farmer.objects.filter(id_owner=pk, id_owner__isnull=False)
        serializer = FarmerSerializer(employees, many=True)
        return Response({'employees': serializer.data})
    
class CoworkersAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        worker = Farmer.objects.get(id=pk)
        owner = worker.id_owner
        workers = Farmer.objects.filter(id_owner = owner)
        coworkers = workers.exclude(id=pk)
        serializer = FarmerSerializer(coworkers, many=True)
        return Response({'coworkers': serializer.data})