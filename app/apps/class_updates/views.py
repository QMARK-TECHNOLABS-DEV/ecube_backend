from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import class_updates_link, announcements, recordings
from .serializers import recordings_get_serializer,class_updates_link_serializer, class_updates_link_get_serializer, announcement_serializer, recording_serializer
from ..register_student.models import Student , class_details
from ..client_auth.utils import TokenUtil
import datetime, requests, json
from django.utils import timezone
from ecube_backend.pagination import CustomPageNumberPagination

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

def send_notification_main(registration,message_title, message_desc, message_type):
    # registration = ['dREWgJKnS5yw3KJ_0w0OaS:APA91bGFBliKfQI4itzjmdhDRCqkBDywYeSQjJvIB1f3bHYEF9QLuD70lHyi3AI9QXDofqxzbjaXXEKdeolg8bGboQQPQXeJuLluw0K3Y-h_GEhHg47Ln_OiioGMiWKpqYX-xnXSUk7b']
    result = send_notification(registration, message_title, message_desc, message_type)
    print(result)
    
class Class_Updates_Admin(APIView, CustomPageNumberPagination):
    def post(self, request):
        data=request.data
        data['class_name'] = data['class_name'].upper()
        data['batch_year'] = data['batch_year'].upper()
        data['division'] = data['division'].upper()
        data['topic'] = data['topic'].upper()
        data['subject'] = data['subject'].upper()
        
        print(data)
        class_group = class_details.objects.filter(class_name=data['class_name'], batch_year=data['batch_year'], division=data['division']).first()
        
        if class_group == None:
            return Response({"message": "Class not found"},status=status.HTTP_400_BAD_REQUEST)
        

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
            class_update_instance = class_updates_link.objects.order_by('-upload_time').first()
            
            if not class_update_instance:
                return Response({'message': 'No class links provided for any class group'}, status=status.HTTP_400_BAD_REQUEST)
            class_name = class_update_instance.class_name
            batch_year = class_update_instance.batch_year
            division = class_update_instance.division
            
        else:
            class_name = class_name.upper()
            batch_year = batch_year.upper()
            division = division.upper()
            
        queryset = class_updates_link.objects.filter(class_name=class_name, batch_year=batch_year, division=division).order_by('-upload_time')
        
        # queryset = class_updates_link.objects.all().order_by('-upload_time')
        
        print(queryset)
        queryset = self.paginate_queryset(queryset, request)
        
        serializer = class_updates_link_serializer(queryset, many=True)
        
        response = {
            "class_name":class_name,
            "batch_year":batch_year,
            "division":division,
            "class_links":serializer.data,
            "total_pages": self.page.paginator.num_pages,
            "has_next": self.page.has_next(),
            "has_previous": self.page.has_previous(),
            "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
            "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,         
        }


        return Response(response, status=status.HTTP_200_OK)
        
        
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
            data['topic'] = data['topic'].upper()
            
            # Update upload_time
            data['upload_time'] = timezone.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            serializer = class_updates_link_serializer(queryset, data=data)
            
            if serializer.is_valid():
                serializer.save()
                
                # students_instance = Student.objects.filter(class_name=data['class_name'], batch_year=data['batch_year'], division=data['division']).values('device_id')
                
                # if students_instance:
                #     device_ids = [student['device_id'] for student in students_instance]

                #     print(device_ids)
                    
                #     if data['subject'] == 'PHYSICS':
                #         message_title = "Physics Class Update"
                #         subject_name = "Physics"
                #     elif data['subject'] == 'CHEMISTRY':
                #         message_title = "Chemistry Class Update"
                #         subject_name = "Chemistry"
                #     elif data['subject'] == 'MATHS':
                #         message_title = "Maths Class Update"
                #         subject_name = "Maths"
                
                #     message_desc = "New live class link added for " + subject_name + " class"
                #     message_type = "liveclass"
                #     send_notification_main(device_ids,message_title, message_desc, message_type)
                    
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

        payload = TokenUtil.decode_token(token)

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
        subjects = []
        if user.subjects:
            subjects = [item.strip().upper() for item in user.subjects.split(",") if item.strip()]
        
        print(class_name, batch_year, division)
        if class_name == None or batch_year == None or division == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            class_name = class_name.upper()
            batch_year = batch_year.upper()
            division = division.upper()

            date = datetime.date.today()
            
            filters = {
                "class_name": class_name,
                "batch_year": batch_year,
                "division": division
            }

            if subjects:
                filters["subject__in"] = subjects
            else:
                filters["subject__isnull"] = True

            queryset = class_updates_link.objects.filter(**filters).order_by('-upload_time')
            
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
                
                    
            if serializer.data == []:
                return Response({"announcement": announcement,"class_links":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({"announcement": announcement,"class_links":serializer.data}, status=status.HTTP_200_OK)

class GetRecordingDates(APIView):
    def get(self, request):
        try:
                    
            authorization_header = request.META.get("HTTP_AUTHORIZATION")

            if not authorization_header:
                return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)

            _, token = authorization_header.split()

            payload = TokenUtil.decode_token(token)

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
            
            dates_instance = recordings.objects.filter(batch_year=batch_year,class_name=class_name,division=division).values('date').distinct().order_by('-date')
  
            unique_dates = [date['date'] for date in dates_instance]

            return Response({"dates": unique_dates})
        except Exception as e:
            print(e)
            return Response({"message": str(e)})  
         
class recording_client_side(APIView, CustomPageNumberPagination):
    def get(self, request):
        try:
            authorization_header = request.META.get("HTTP_AUTHORIZATION")

            if not authorization_header:
                return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)

            _, token = authorization_header.split()

            payload = TokenUtil.decode_token(token)

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
            
            date = request.data['date'] if request.data.get('date') else None
            subject = request.data['subject'] if request.data.get('subject') else None
            
            subject = subject.upper() if subject else None
            userSubjects = user.subjects
            
            userSubjects = userSubjects.split(",")
            userSubjects = [subject.strip().upper() for subject in userSubjects]
            print(userSubjects)

            if subject:
                if subject not in userSubjects:
                    return Response({"message": "You are not allowed to access this subject"}, status=status.HTTP_404_NOT_FOUND)
                
                if subject not in ['PHYSICS', 'CHEMISTRY', 'MATHS']:
                    return Response({"message": "Invalid subject"}, status=status.HTTP_400_BAD_REQUEST)
                
                if class_name == None or batch_year == None or division == None:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                else:
                    class_name = class_name.upper()
                    batch_year = batch_year.upper()
                    division = division.upper()
                    
                    print(subject, class_name, batch_year, division, "subject")
                    recordings_instance = recordings.objects.filter(class_name=class_name, batch_year=batch_year, division=division,subject=subject).order_by('-upload_time')
                
                    recordings_instance = self.paginate_queryset(recordings_instance, request)
                    
                    recording_serializer = recordings_get_serializer(recordings_instance,many=True)

                    return Response({
                        "recorded_classes": recording_serializer.data,
                        "total_pages": self.page.paginator.num_pages,
                        "has_next": self.page.has_next(),
                        "has_previous": self.page.has_previous(),
                        "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
                        "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,  
                        }, status=status.HTTP_200_OK)
                
            elif date:
                if class_name == None or batch_year == None or division == None:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                else:
                    class_name = class_name.upper()
                    batch_year = batch_year.upper()
                    division = division.upper()
                    
                    print(date, class_name, batch_year, division, "date")
                    recordings_instance = recordings.objects.filter(class_name=class_name, batch_year=batch_year, division=division,date=date, subject__in=userSubjects).order_by('-upload_time')
                
                    recording_serializer = recordings_get_serializer(recordings_instance,many=True)

                    return Response({"recorded_classes": recording_serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"message": "Bad Request"},status=status.HTTP_400_BAD_REQUEST) 
        
class recording_client_side_web(APIView):
    def get(self, request):
        try:
            authorization_header = request.META.get("HTTP_AUTHORIZATION")

            if not authorization_header:
                return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)

            _, token = authorization_header.split()

            payload = TokenUtil.decode_token(token)

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
            userSubjects = [s.strip().upper() for s in (user.subjects or "").split(",") if s.strip()]
            
            date = request.query_params.get('date')
            
            if not date:
                return Response({"message": "Date not found"},status=status.HTTP_400_BAD_REQUEST)
            
            if class_name == None or batch_year == None or division == None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                class_name = class_name.upper()
                batch_year = batch_year.upper()
                division = division.upper()
                
                print(date, class_name, batch_year, division)
                recordings_instance = recordings.objects.filter(class_name=class_name, batch_year=batch_year, division=division,date=date, subject__in=userSubjects).order_by('-upload_time')
            
                recording_serializer = recordings_get_serializer(recordings_instance,many=True)

                return Response({"recorded_classes": recording_serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"message": "Bad Request"},status=status.HTTP_400_BAD_REQUEST) 
              
class Announcements(APIView, CustomPageNumberPagination):
    def post(self, request):
        data=request.data

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
        
        if not announcement:
            return Response({'message': 'No announcements found...'},status=status.HTTP_400_BAD_REQUEST)
        
        announcement = self.paginate_queryset(announcement,request)
        
        serializer = announcement_serializer(announcement, many=True)
        
        response={
            "announcements": serializer.data,
            "total_pages": self.page.paginator.num_pages,
            "has_next": self.page.has_next(),
            "has_previous": self.page.has_previous(),
            "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
            "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,         
        }
        
        return Response(response, status=status.HTTP_200_OK)
        
    def put(self, request):
        data=request.data
        data['upload_date'] = data['upload_date'].upper()
        
        announcement_instance = announcements.objects.filter(upload_date=data['upload_date']).first()
        
        if announcement_instance != None:
            announcement_instance.announcement = data['announcement']
            announcement_instance.save()
            
            return Response({"message": "announcements updated successfully"},status=status.HTTP_200_OK)
        
    def delete(self, request):
        upload_date=request.query_params.get('upload_date')
        upload_date = upload_date.upper()
        
        announcement_instance = announcements.objects.filter(upload_date=upload_date).first()
        
        if announcement_instance != None:
            announcement_instance.delete()
            
            return Response({"message": "announcements deleted successfully"},status=status.HTTP_200_OK)
        else:
            return Response({"message": "announcements not found"},status=status.HTTP_400_BAD_REQUEST)
        
def get_yt_video_id(url):
    from urllib.parse import urlparse, parse_qs

    if url.startswith(('youtu', 'www')):
        url = 'http://' + url
        
    query = urlparse(url)

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        return query.path[1:]
    else:
        return ""
    
class RecordingsLink(APIView, CustomPageNumberPagination):
    def post(self, request):
        try:
            data = request.data
            print("Incoming data:", data)  

            class_name = data.get('class_name', '').strip().upper()
            batch_year = data.get('batch_year', '').strip().upper()
            division = data.get('division', '').strip().upper()
            subject = data.get('subject', '').strip().upper()
            date = data.get('date', '').strip().upper()
            recording_link = data.get('recording_link', '').strip()

            if not all([class_name, batch_year, division, subject]):
                return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                video_id = get_yt_video_id(recording_link)
            except Exception as ve:
                print("Error extracting video ID:", ve)
                return Response({"error": "Invalid YouTube recording link."}, status=status.HTTP_400_BAD_REQUEST)

            recordings.objects.create(
                class_name=class_name,
                batch_year=batch_year,
                division=division,
                subject=subject,
                date=date,
                recording_link=recording_link,
                video_id=video_id
            )

            students_instance = Student.objects.filter(
                class_name=class_name,
                batch_year=batch_year,
                division=division
            ).values('device_id')

            if students_instance:
                device_ids = [student['device_id'] for student in students_instance if student.get('device_id')]

                if device_ids:
                    subject_display = {
                        'PHYSICS': 'Physics',
                        'CHEMISTRY': 'Chemistry',
                        'MATHS': 'Maths',
                    }.get(subject, subject.capitalize())

                    message_title = "Recorded Class Added"
                    message_desc = f"Recorded class for {subject_display} on {date} has been added"
                    message_type = "liveclass"

                    send_notification_main(device_ids, message_title, message_desc, message_type)

            return Response({"message": "Recordings link added successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("exception check", e)
            return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        
    
    def get(self, request):
        class_name = request.query_params.get('class_name')
        batch_year = request.query_params.get('batch_year')
        division = request.query_params.get('division')
        
        if class_name == None or batch_year == None or division == None:
            recordings_instance = recordings.objects.order_by('-upload_time').first()
            
            if not recordings_instance:
                return Response({'message': 'No video links provided for any class group'}, status=status.HTTP_400_BAD_REQUEST)
            class_name = recordings_instance.class_name
            batch_year = recordings_instance.batch_year
            division = recordings_instance.division
            
        else:
            class_name = class_name.upper()
            batch_year = batch_year.upper()
            division = division.upper()

            
        queryset = recordings.objects.filter(
            class_name=class_name,
            batch_year=batch_year,
            division=division,
        ).order_by('-upload_time')
        
        # queryset = self.paginate_queryset(queryset, request)
        
        # serializer = recording_serializer(queryset, many=True)
        
        # response = {
        #     "class_name":class_name,
        #     "batch_year":batch_year,
        #     "division":division,
        #     "recordings":serializer.data,
        #     "total_pages": self.page.paginator.num_pages,
        #     "has_next": self.page.has_next(),
        #     "has_previous": self.page.has_previous(),
        #     "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
        #     "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,         
        # }
        
        serializer = recording_serializer(queryset, many=True)
        
        response = {
            "class_name":class_name,
            "batch_year":batch_year,
            "division":division,
            "recordings":serializer.data,
            "total_pages": 1,
            "has_next": False,
            "has_previous": False,
            "next_page_number": None,
            "previous_page_number": None,
        }
        
        return Response(response, status=status.HTTP_200_OK)


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
            video_id = get_yt_video_id(data['recording_link'])
            recordings_instance.video_id = video_id
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