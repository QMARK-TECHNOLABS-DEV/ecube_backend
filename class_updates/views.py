from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import class_updates_link
from .serializers import class_updates_link_serializer, class_updates_link_get_serializer
from register_student.models import Student
from client_auth.utils import TokenUtil
from client_auth.models import Token
from datetime import datetime, timedelta
from django.utils import timezone
class Class_Updates_Admin(APIView):
    def post(self, request):
        data=request.data
        data['class_name'] = data['class_name'].upper()
        data['batch_year'] = data['batch_year'].upper()
        data['division'] = data['division'].upper()
        data['subject'] = data['subject'].upper()
        data['topic'] = data['topic'].upper()
        
        serializer = class_updates_link_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request):
        class_name = request.query_params.get('class_name')
        batch_year = request.query_params.get('batch_year')
        division = request.query_params.get('division')
        
        if class_name == None or batch_year == None or division == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            class_name = class_name.upper()
            batch_year = batch_year.upper()
            division = division.upper()
            
            queryset = class_updates_link.objects.filter(class_name=class_name, batch_year=batch_year, division=division).order_by('-upload_time')
            serializer = class_updates_link_serializer(queryset, many=True)
            
            if serializer.data == []:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"class_links":serializer.data}, status=status.HTTP_200_OK)
        
        
    def put(self, request):
        link_id = request.query_params.get('link_id')
        
        if link_id == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                queryset = class_updates_link.objects.get(id=link_id)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            data=request.data
            data['class_name'] = data['class_name'].upper()
            data['batch_year'] = data['batch_year'].upper()
            data['division'] = data['division'].upper()
            data['subject'] = data['subject'].upper()
            data['topic'] = data['topic'].upper()
            
            serializer = class_updates_link_serializer(queryset, data=data)
            
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def delete(self, request):
        link_id = request.query_params.get('link_id')
        
        if link_id == None:
            return Response({"message": "Bad Request"},status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                queryset = class_updates_link.objects.get(id=link_id)
            except:
                return Response({"message": "Bad Request"},status=status.HTTP_400_BAD_REQUEST)
            
            queryset.delete()
            return Response({"message": "Class Update Link deleted successfully"},status=status.HTTP_200_OK)
        
        
        
class Class_Update_Client_Side(APIView):
    def get(self, request):
        
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)

        _, token = authorization_header.split()

        token_key = Token.objects.filter(access_token=token).first()

        if not token_key:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

        payload = TokenUtil.decode_token(token_key.access_token)

        # Optionally, you can extract user information or other claims from the payload
        if not payload:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = payload.get('id')

        if not user_id:
            return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate a new access token
        user = Student.objects.get(id=user_id)
        
        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division
        
        if class_name == None or batch_year == None or division == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            class_name = class_name.upper()
            batch_year = batch_year.upper()
            division = division.upper()
            
            queryset = class_updates_link.objects.filter(class_name=class_name, batch_year=batch_year, division=division).order_by('-upload_time')
            
            current_time = timezone.now()
            
            cutoff_time = current_time - timedelta(minutes=1)
            if queryset == []:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                
                for record in queryset:
                    if record.upload_time < cutoff_time:
                        record.delete()
                        
                queryset = class_updates_link.objects.filter(class_name=class_name, batch_year=batch_year, division=division).order_by('-upload_time')
                   
                serializer = class_updates_link_get_serializer(queryset, many=True)
            
            if serializer.data == []:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"class_links":serializer.data}, status=status.HTTP_200_OK)