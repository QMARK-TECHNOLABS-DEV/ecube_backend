from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import class_updates_link, announcements, recordings
from .serializers import recordings_get_serializer,class_updates_link_serializer, class_updates_link_get_serializer, announcement_serializer, recording_serializer
from register_student.models import Student
from client_auth.utils import TokenUtil
from client_auth.models import Token
import datetime
from django.utils import timezone
from django.db.models import ExpressionWrapper, F, TimeField
from django.db.models.functions import Cast
import requests
import json
import pytz

def send_notification(registration_ids, message_title, message_desc, message_type):
    fcm_api = "AAAAqbxPQ_Q:APA91bGWil8YXU8Zr1CLa-tqObZ-DVJUqq0CrN0O76bltTApN51we3kOqrA4rRFZUXauBDtkcR3nWCQ60UPWuroRZpJxuCBhgD6CdHAnjqh8V2zPIzLvuvERmbipMHIoJJxuBegJW3a3"
    url = "https://fcm.googleapis.com/fcm/send"

    headers = {
        "Content-Type": "application/json",
        "Authorization": 'key=' + fcm_api
    }

    payload = {
        "registration_ids": registration_ids,
        "priority": "high",
        "notification": {
            "body": message_desc,
            "title": message_title,
        },
        "data": {
            "type": message_type,
        }
    }

    result = requests.post(url, data=json.dumps(payload), headers=headers)
    print(result.json())

def send(registration,message_title, message_desc, message_type):
    # registration = ['dREWgJKnS5yw3KJ_0w0OaS:APA91bGFBliKfQI4itzjmdhDRCqkBDywYeSQjJvIB1f3bHYEF9QLuD70lHyi3AI9QXDofqxzbjaXXEKdeolg8bGboQQPQXeJuLluw0K3Y-h_GEhHg47Ln_OiioGMiWKpqYX-xnXSUk7b']
    result = send_notification(registration, message_title, message_desc, message_type)
    print(result)
class Class_Updates_Admin(APIView):
    def post(self, request):
        data=request.data
        data['class_name'] = data['class_name'].upper()
        data['batch_year'] = data['batch_year'].upper()
        data['division'] = data['division'].upper()
        data['subject'] = data['subject'].upper()
        data['topic'] = data['topic'].upper()
        data['date'] = data['date'].upper()
        data['class_time'] = data['class_time'].upper()
        
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
        
        if link_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                queryset = class_updates_link.objects.get(id=link_id)
            except class_updates_link.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            data = request.data
            data['class_name'] = data['class_name'].upper()
            data['batch_year'] = data['batch_year'].upper()
            data['division'] = data['division'].upper()
            data['subject'] = data['subject'].upper()
            data['topic'] = data['topic'].upper()
            
            # Update upload_time
            data['upload_time'] = timezone.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            
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
            date = datetime.date.today()
            
            print(date)
            
            
            
            print(date)
            
            queryset = class_updates_link.objects.filter(
                class_name=class_name,
                batch_year=batch_year,
                division=division,
                date=date
            ).annotate(
                class_time_as_time=ExpressionWrapper(
                    Cast(F('class_time'), output_field=TimeField()),
                    output_field=TimeField()
                )
            ).order_by('class_time_as_time')
            
            announcement = announcements.objects.filter(upload_date=str(date)).first()
            
            if announcement == None:
                announcement = ""
            else:
                announcement = announcement.announcement
            
            print(date)
            if queryset == []:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:                  
                serializer = class_updates_link_get_serializer(queryset, many=True)
                
            recordings_instance = recordings.objects.filter(class_name=class_name, batch_year=batch_year, division=division, date=date).order_by('-upload_time')
            
            recording_serializer = recordings_get_serializer(recordings_instance,many=True)
            
            
                    
            if serializer.data == []:
                return Response({"class_name": class_name,"batch_year":batch_year,"division":division,"announcement": announcement,"date": date,"class_links":serializer.data,"recorded_classes": recording_serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({"class_name": class_name,"batch_year":batch_year,"division":division,"announcement": announcement,"date": date,"class_links":serializer.data,"recorded_classes": recording_serializer.data}, status=status.HTTP_200_OK)
            
            
class Announcements(APIView):
    def post(self, request):
        data=request.data
        data['upload_date'] = data['upload_date'].upper()
        
        announcement_instance = announcements.objects.filter(upload_date=data['upload_date']).first()
        
        if announcement_instance != None:
            announcement_instance.announcement = data['announcement']
            announcement_instance.save()
            
            return Response({"message": "announcements updated succefully"},status=status.HTTP_200_OK)
        else:
        
            announcements.objects.create(announcement=data['announcement'], upload_date=data['upload_date'])
            
            return Response({"message": "announcements added succefully"},status=status.HTTP_201_CREATED)
    
    def get(self, request):
        announcement = announcements.objects.all()
        
        serializer = announcement_serializer(announcement, many=True)
        
        if announcement == None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"announcements": serializer.data}, status=status.HTTP_200_OK)
        
    def put(self, request):
        data=request.data
        data['upload_date'] = data['upload_date'].upper()
        
        announcement_instance = announcements.objects.filter(upload_date=data['upload_date']).first()
        
        if announcement_instance != None:
            announcement_instance.announcement = data['announcement']
            announcement_instance.save()
            
            return Response({"message": "announcements updated successfully"},status=status.HTTP_200_OK)
        
    def delete(self, request):
        data=request.data
        data['upload_date'] = data['upload_date'].upper()
        
        announcement_instance = announcements.objects.filter(upload_date=data['upload_date']).first()
        
        if announcement_instance != None:
            announcement_instance.delete()
            
            return Response({"message": "announcements deleted successfully"},status=status.HTTP_200_OK)
        else:
            return Response({"message": "announcements not found"},status=status.HTTP_400_BAD_REQUEST)
        
        
class RecordingsLink(APIView):
    def post(self, request):
        try:
            data=request.data
            data['class_name'] = data['class_name'].upper()
            data['batch_year'] = data['batch_year'].upper()
            data['division'] = data['division'].upper()
            data['subject'] = data['subject'].upper()
            data['date'] = data['date'].upper()
            
            recordings_instance = recordings.objects.filter(
                class_name=data['class_name'],
                batch_year=data['batch_year'],
                division=data['division'],
                subject=data['subject'],
                date=data['date']
            ).first()
            
            if recordings_instance:
                recordings_instance.recording_link = data['recording_link']
                recordings_instance.save()
            else:
                recordings.objects.create(
                    class_name=data['class_name'],
                    batch_year=data['batch_year'],
                    division=data['division'],
                    subject=data['subject'],
                    date=data['date'],
                    recording_link=data['recording_link']
                )
                
            return Response({"message": "Recordings link added successfully"},status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(e)
            return Response({"message": "Bad Request"},status=status.HTTP_400_BAD_REQUEST)
        
    
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

            
            queryset = recordings.objects.filter(
                class_name=class_name,
                batch_year=batch_year,
                division=division,
            ).order_by('-upload_time')
            
            serializer = recording_serializer(queryset, many=True)
            
            if serializer.data == []:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"recordings":serializer.data}, status=status.HTTP_200_OK)
            
    
    def put(self, request):
        data=request.data
        data['class_name'] = data['class_name'].upper()
        data['batch_year'] = data['batch_year'].upper()
        data['division'] = data['division'].upper()
        data['subject'] = data['subject'].upper()
        data['date'] = data['date'].upper()
        
        recordings_instance = recordings.objects.filter(
            class_name=data['class_name'],
            batch_year=data['batch_year'],
            division=data['division'],
            subject=data['subject'],
            date=data['date']
        ).first()
        
        if recordings_instance:
            recordings_instance.recording_link = data['recording_link']
            recordings_instance.save()
            
            return Response({"message": "Recordings link updated successfully"},status=status.HTTP_200_OK)
        else:
            return Response({"message": "Recordings link not found"},status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        recordings_id = request.query_params.get('recordings_id')
        
        if recordings_id == None:
            return Response({"message": "Bad Request"},status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                queryset = recordings.objects.get(id=recordings_id)
            except:
                return Response({"message": "Bad Request"},status=status.HTTP_400_BAD_REQUEST)
            
            queryset.delete()
            return Response({"message": "Recordings link deleted successfully"},status=status.HTTP_200_OK)