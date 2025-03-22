from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Student, create_tables, class_details
from .serializers import ClassDetailsSerializer, StudentSerializer, ExamStudentDisplaySerializer, StudentDisplaySerializer
import pandas as pd
from django.db import connection, DatabaseError
from ..client_auth.utils import TokenUtil
import re
from ..class_updates.models import class_updates_link, recordings
from django.db.models.functions import Cast
from django.db.models import Max, IntegerField
from ecube_backend.pagination import CustomPageNumberPagination
class StudentSoftDelete(APIView):
    def post(self, request):
        try:
            student_id = request.data.get('user_id')
            restricted_status = request.data.get('restricted_status')
            
            student_instance = Student.objects.filter(id=student_id).first()
            if student_instance:
                student_instance.restricted = restricted_status
                student_instance.save()
                
                        
                return Response({'message': 'Student record restricted successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Student record does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Internal failure', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class NextAdmNumber(APIView):
    def get(self, request):
        try:
            highest_adm_no = Student.objects.annotate(admission_no_int=Cast('admission_no', IntegerField())).aggregate(max_admission_no=Max('admission_no_int'))['max_admission_no']

            
            print(highest_adm_no)
            
            if highest_adm_no:
                return Response({'next_adm_no': highest_adm_no + 1}, status=status.HTTP_200_OK)
            
            return Response({'next_adm_no': 1}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': 'Internal failure', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class AddStudentDataBackup(APIView):
#     def post(self, request):
#         try:
            
         
#             data = [
#                 ("ANANDU", "1111", "9747981367", "10TH CBSE", "A", "physics,chemistry,maths", "BB", "2024", "", "146", "ezv4VhXPRqeh7Es0FfaZhb:APA91bFlhxYJykyOTWKoKg9KQrropt2RNEzeEq4Yzu9Dnko7djDQPNcXzUCf_c55JW3HGWOANzVwLXsmtACQL5L3KMOhyJ5yaCawQOUCiym-yyV_MHZUxlN6oLWruccivdAqmReeMyiA", False),
#                 ("MUHD ISHAN P A", "1", "7012764915", "10TH CBSE", "A", "physics,chemistry,maths", "ILAHIA", "2024", "", "146", "dataSfewQ4eWSn0tM6WyQR:APA91bHxZJN2INhBky4qMHq1N7EdwLez44WHB1AWP7CDoNWjpNly7PSXpU3YKa65rM1kDPKf3lEauOiljWqcdR_lp3nd5UPyYg_EvMkExaarFtpgjhvBUlP4ZmsMMfJBQFnZK--KDw8n", False),
#                 ("ZAMEEN P S", "2", "8137976949", "10TH CBSE", "A", "physics,chemistry,maths", "ILAHIA PUBLIC SCHOOL MUVATTUPUZHA", "2024", "", "146", "f_531vTuRJmtO81nP52jXm:APA91bGoDTKGAUPUtMjFKm6ANnuCbau1ClUkF1iE-wzFlyxWA4zwN9G-ov2RZeX-tTuZB-vp9Mywmj_11vcIQiVOt-3edjHlOiFGUg_9Moy9H6kNvrsKZWHMt3ygAK1gCuxqoLlrz_Vb", False),
#                 ("FATHIMATHU NISSAR", "3", "9605588729", "10TH CBSE", "A", "physics,chemistry,maths", "MALIK DEENAR PUBLIC SCHOOL ADIVAD", "2024", "", "146", "du1Pa2VLQdiP47eqzfoGee:APA91bH-NHtZFl1yUKJ8k2oNdHcCdvSOj6xM5-bwIStglZmRu-_fZBmE8vYo2uXpJzVkUgksDbvUWe_gBq7joSDt-eVoBEa3HbaoF0V0zDgx-48dBupczbY6Xjj2DTj8-Ah4spjh8gHp", False),
#                 ("MUHAMMED THANZEEL C A", "5", "9656583670", "10TH CBSE", "A", "physics,chemistry,maths", "ILAHIA PUBLIC SCHOOL MUVATTUPUZHA", "2024", "", "146", "cM6hKCIlQOSJdW00mlU0sP:APA91bHZuU8X5pXpGu73FIvl5Z31auo8qwhcFICOBIirokwUnHsd1MafgnidYKhkhg33tUFAhdqzOXk239yN_w2qD4v4Fv5IWBnZeuPV5DXGVibvq65a7F2G-jAPCHghSRDQ8dHFiy2d", False),
#                 ("Hasna Ansar", "4", "8606166184", "10TH CBSE", "A", "physics,chemistry,maths", "ILAHIA PUBLIC SCHOOL MUVATTUPUZHA", "2024", "", "146", "dDDlljbnTZSqPfF3z6K1_O:APA91bFi5RFMy9UE5FwfB2dMyyLF3ajJmtGfwigq_JvrwqNLULRERBtcxfOBorAIKn88z_zCKwBFBthCMdDbAiQtZbt97t8ibeVTpvseHVYyhQbp1XLBdxa4KZHspUGl4K42V0QK1yN2", False),
#                 ("Diya fathima", "6", "7012419985", "10TH CBSE", "A", "physics,chemistry,maths", "ILAHIA PUBLIC SCHOOL MUVATTUPUZHA", "2024", "", "146", "", False),
#                 ("NABHAN YASSAR", "7", "7560996153", "10TH CBSE", "A", "physics,chemistry,maths", "ILAHIA PUBLIC SCHOOL MUVATTUPUZHA", "2024", "", "146", "cIrSbBDTRBayl8B87PAaql:APA91bHEvrwfmkAVWlJOepZ0VueQ_GEMGTBc9VCCe8lxomeqM_85rhjNS4CI0gK7HRw69ICdurOmbg62se8xQabBqB6xpcFqj0vvahwOTh-pOQYhXh99JdF7qWwJ8cDup1m2IQw0DBuO", False),
#                 ("IHSAN HUSSAIN", "8", "9744623759", "10TH CBSE", "A", "physics,chemistry,maths", "ILAHIA PUBLIC SCHOOL MUVATTUPUZHA", "2024", "", "146", "dQF7c1wdSRSh3RQRAroLR1:APA91bGxxqsDms-TZ1QmnsDS7jBBgV6aytk4tcPZcKvmgl4TMikWE7A_7Wvk3eCAftQ8PYjlLwLEjAFuufkfxhfZCG9j01NixGqhQp4ICylYOPAwelNwHZhopPTiBOCeRaDuNJ1F82YQ", False),
#                 ("ISHA RAJESH", "9", "7306128427", "10TH CBSE", "A", "physics,maths,chemistry", "NIRMALA PUBLIC SCHOOL MUVATTUPUZHA", "2024", "", "146", "fOib1qcNSnCCShvZrTAFMO:APA91bHS_cDMHXGxyv3Y87zajmXn56dp_sijnGJ_q_6u49UFk7B9MCGOGCUagF1A4R2qo1V-WXU4sXb7k1bT3bP3xmEr810pdZozyYHKCaTCIEkHIwJSaZ2zGB6EHDgezvY1nMdd3UFW", False),
#                 ("Test User", "10", "7356924029", "TEST BATCH", "A", "physics,maths,chemistry", "Testing School", "2024", "", "160", "", False),
#                 ("Faid mohammed", "11", "7356219994", "10TH CBSE", "A", "physics,chemistry,maths", "ILAHIA PUBLIC SCHOOL MUVATTUPUZHA", "2024", "", "146", "cKg88ZLPQfG2vcbmqAxZDE:APA91bEnSb0rFLDMg_V_D92E-OMQGO5C0c-jBodxbUgugo6KhSdKdGrrka-i20s6lwkXsts0Xt40unsNVZfeq05t4haAywFfU--N-P-Qy-MiXc11U38I3eYQy5wTuAYIUne_mzXvWXfk", False),
#                 ("Shahma Fathima KV", "12", "50604054", "10TH CBSE", "A", "physics,chemistry,maths", "MES", "2024", "", "146", "", False),
#                 ("Vyshnavi Sreekumar", "13", "8837095316", "10TH CBSE", "A", "physics,chemistry,maths", "VIMALA PUBLIC SCHOOL", "2024", "", "146", "f8ml9GsoTgquxAYYO0vKPu:APA91bHfrshY2wFAAIJUG49tl572-aci-188aAZqiD33wcyLL0tI7Ka8k-l7jhlbysxlD1BbcNdtOsyJ50g90iAkeYNltVPzE1CO29VNNAWV3R9kssdQyPbeZLyzKP5YIakwiNbJxQSh", False),
#                 ("Afra Fathima M J", "16", "8921353952", "10TH CBSE", "A", "physics,chemistry,maths", "Sree Narayana Vidyapeetam Public school Tripunithura", "2024", "", "146", "dtTJgk08Qw2T_TtaslBhMO:APA91bFEXuwN9EPNByUmA6im5TFtjdkyOGUqIUouESSzRjH5YrCwF0aR36-clXNTvaWv4wRm8HLvQJ6NsgWp2aAws0Mtle7kwS5XaMKbHlGlvIgOkgUTvC2USKqStMqET1oCBEO0SC9A", False),
#                 ("Lakshmi Priya Sagar", "201", "8078509127", "12TH CBSE", "A", "maths", "Vidyadhiraja vidyabhavan senior secondary school mekkad", "2024", "", "162", "", False),
#                 ("Aisleen Aleya Ajay", "14", "9496079824", "12TH CBSE", "A", "chemistry", "St. Peters snior secondary school, kadayirupp", "2024", "", "162", "cGjgueSRSQOsHhRYBTLKOZ:APA91bHrG8GGmWjR68QhIN6yVwOxWxlvlAL-7uYb40iBNuAthSI3B2Yw_xhNaNL0y0XU4fotjpfS_12Whc8nd580E1ub4y3JbbdzFqFrFuyUizqKwTmxDGLVFnoGviB-j92LYifuq6Ok", False),
#                 ("Krishna Pratheesh", "17", "7051625745", "12TH CBSE", "A", "physics,chemistry,maths","Kendriya Vidyalaya, Jalipa Cantt Barmer Rajasthan", "2024", "", "162","fJMoJm_0RxaRCiMQFXjUC_:APA91bHbxtnVo6h7dZ4x5JLGxzbwScRPu4zTY7N6TKQgcZmarAnJ8luCbRgmrTHoYWLBLN4sZVoZQR9ioXsVqNxpigUxdcni-S1-enASO_QzXDV2GCzMsa4GT7OydSa68uHU4HuqhBoz",False)
#             ]
            
#             for item in data:
#                 student = Student.objects.create(
#                     name=item[0],
#                     admission_no=item[1],
#                     phone_no=item[2],
#                     class_name=item[3],
#                     division=item[4],
#                     subjects=item[5],
#                     school_name=item[6],
#                     batch_year=item[7],
#                     class_group=item[9],
#                     device_id=item[10],
#                     restricted=item[11]
#                 )
                
#             return Response({'message': 'Data added successfully'}, status=status.HTTP_200_OK)
#         except Exception as e:
#             print(e)
#             return Response({'message': 'Internal failure'}, status=status.HTTP_400_BAD_REQUEST)    
class StudentMethods(APIView):
    def post(self, request):
        
        batch_year = request.query_params.get('batch_year')
        class_name = request.query_params.get('class_name')
        division = request.query_params.get('division')
        subjects = request.query_params.get('subjects')
        
        class_instance = class_details.objects.filter(batch_year=batch_year,class_name=class_name,division=division)
        
        print(class_instance)
        
        if not class_instance:
            return Response({'message': 'No such class group'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        
        data['batch_year'] = batch_year
        data['class_name'] = class_name
        data['division'] = division
        data['subjects'] = subjects
        data['class_group'] = class_instance[0].id
        
        
        serializer = StudentSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        students = Student.objects.filter(id=request.query_params.get('id'))
        serializer = StudentSerializer(students, many=True)
        
        if serializer.data == []:
            return Response({'Message': 'The record or student does not exist'} ,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data[0], status=status.HTTP_200_OK)
    
    def delete(self, request):
        student = Student.objects.filter(id=request.query_params.get('id'))
        
        if student.exists():
            student.delete()
            return Response({'Message': 'Record successfully deleted'} ,status=status.HTTP_200_OK)
        
        return Response({'Message': 'Record does not  exist'},status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        
        user_id = request.query_params.get('id')
        
        data = {}
        
        students = Student.objects.filter(id=user_id).first()
        
        print(students)
        old_batch_year = request.data['old_batch_year']
        old_class_name = request.data['old_class_name']
        old_division = request.data['old_division']
        
        new_batch_year = request.data['new_batch_year']
        new_class_name = request.data['new_class_name']
        new_division = request.data['new_division']
        
        data['name'] = request.data['name']
        data['admission_no'] = request.data['admission_no']
        data['phone_no'] = request.data['phone_no']
        data['school_name'] = request.data['school_name']
        data['subjects'] = request.data['subjects']
        data['email_id'] = request.data['email_id']  
        
        class_instance = class_details.objects.filter(batch_year=new_batch_year,class_name=new_class_name,division=new_division)

        if not class_instance:
            return Response({'message': 'No such class group'}, status=status.HTTP_400_BAD_REQUEST)
        

        data['batch_year'] = new_batch_year
        data['class_name'] = new_class_name
        data['division'] = new_division
        data['class_group'] = class_instance[0].id
        
        print(old_batch_year, old_class_name, old_division)
        if students is not None:
            if old_batch_year != new_batch_year or old_class_name != new_class_name or old_division != new_division:
                
                new_table_name = f"{new_batch_year}_{new_class_name}_{new_division}".replace(" ","").lower()
                
                old_table_name = f"{old_batch_year}_{old_class_name}_{old_division}".replace(" ","").lower()
                
                app_name = 'register_student_'
                
                feature_group_id = ['_examresults', '_leaderboard', '_attendance', '_dailyupdates']
                

                final_new_table_name = f"{app_name}{app_name}{new_table_name}{feature_group_id[0]}"
                final_old_table_name = f"{app_name}{app_name}{old_table_name}{feature_group_id[0]}"
                
                with connection.cursor() as cur:
                
                    try:                       
                        cur.execute(f"INSERT INTO public.{final_new_table_name} (admission_no, exam_name, physics, chemistry, maths) SELECT admission_no, exam_name, physics, chemistry, maths FROM public.{final_old_table_name} WHERE admission_no = %s", [students.admission_no])
                        cur.execute(f"DELETE FROM public.{final_old_table_name} WHERE admission_no = %s", [students.admission_no])

                    except Exception as e:
                        print(e)
                        
                final_new_table_name = f"{app_name}{app_name}{new_table_name}{feature_group_id[1]}"
                final_old_table_name = f"{app_name}{app_name}{old_table_name}{feature_group_id[1]}"
                
                with connection.cursor() as cur:
                
                    try:                       
                        cur.execute(f"INSERT INTO public.{final_new_table_name} (admission_no, physics, chemistry, maths) SELECT admission_no, physics, chemistry, maths FROM public.{final_old_table_name} WHERE admission_no = %s", [students.admission_no])
                        cur.execute(f"DELETE FROM public.{final_old_table_name} WHERE admission_no = %s", [students.admission_no])

                    except Exception as e:
                        print(e)
                        
                final_new_table_name = f"{app_name}{app_name}{new_table_name}{feature_group_id[2]}"
                final_old_table_name = f"{app_name}{app_name}{old_table_name}{feature_group_id[2]}"
                
                with connection.cursor() as cur:
                
                    try:                       
                        cur.execute(f"INSERT INTO public.{final_new_table_name} (admission_no, month_year_number, date, status) SELECT admission_no, month_year_number, date, status FROM public.{final_old_table_name} WHERE admission_no = %s", [students.admission_no])
                        cur.execute(f"DELETE FROM public.{final_old_table_name} WHERE admission_no = %s", [students.admission_no])


                    except Exception as e:
                        print(e)
                        
                final_new_table_name = f"{app_name}{app_name}{new_table_name}{feature_group_id[3]}"
                final_old_table_name = f"{app_name}{app_name}{old_table_name}{feature_group_id[3]}"
                
                with connection.cursor() as cur:
                
                    try:                       
                        cur.execute(f"INSERT INTO public.{final_new_table_name} (admission_no, date, on_time, voice, nb_sub, mob_net, camera, full_class, activities, engagement, overall_performance_percentage, overall_performance, remarks) SELECT admission_no, date, on_time, voice, nb_sub, mob_net, camera, full_class, activities, engagement, overall_performance_percentage, overall_performance, remarks FROM public.{final_old_table_name} WHERE admission_no = %s", [students.admission_no])
                        cur.execute(f"DELETE FROM public.{final_old_table_name} WHERE admission_no = %s", [students.admission_no])


                    except Exception as e:
                        print(e)
                    
               
                                        

            serializer = StudentSerializer(students, data=data)
            
            if serializer.is_valid():
                serializer.save()
          
            return Response({'Message': 'Record successfully updated'} ,status=status.HTTP_200_OK)        

      
        return Response({'Message': 'Record does not exist'},status=status.HTTP_400_BAD_REQUEST)
    
class ClassCreatTables(APIView):
    def post(self, request):
        try:
            data = request.data
            
            # Convert data values to uppercase
            for key in data:
                if isinstance(data[key], str):
                    data[key] = data[key].upper()
            
            
                    
            table_name = f"{data['batch_year']}_{data['class_name']}_{data['division']}".replace(" ","").lower()
             
            app_name = 'register_student_'
            
            print(table_name)
            create_tables(app_name,table_name)
            
            return Response({'message': 'Table created successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': 'Internal failure'}, status=status.HTTP_400_BAD_REQUEST)
        
def regexFilter(query):
    query = re.sub(r'[^A-Za-z0-9-]', '', query)
    query = query.replace('-', ' ')
    return query

class ClassMethods(APIView):
    def post(self, request):
        try:
            data = request.data
            
            batch_year = regexFilter(data['batch_year'])
            class_name = regexFilter(data['class_name'])
            division = regexFilter(data['division'])
            
            data['batch_year'] = batch_year
            data['class_name'] = class_name
            data['division'] = division
            # Convert data values to uppercase
            for key in data:
                if isinstance(data[key], str):
                    data[key] = data[key].upper()
            
            serializer = ClassDetailsSerializer(data=data)
            
            if serializer.is_valid():
                if class_details.objects.filter(class_name=data['class_name'], division=data['division'], batch_year=data['batch_year']).exists():
                    return Response({'Message': 'Class already exists'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                     
                    table_name = f"{batch_year}_{class_name}_{division}".replace(" ","").lower()
             
                    if table_name:
                        
                        app_name = 'register_student_'
                        create_tables(app_name,table_name)
                        
                        serializer.save()
                        
                        return Response({"message": "Successfully created class group and associated feature group"}, status=status.HTTP_201_CREATED)
            
                 
                    return Response({"message": "Table names not valid"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Serializer not valid"},status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "Internal failure"},status=status.HTTP_400_BAD_REQUEST)
        
    
        
        
    def put(self, request):
        try:
            class_id = request.data.get('id')  # Use request.data instead of request.POST
            
            class_instance = class_details.objects.filter(id=class_id).first()
            
            if class_instance:
                
                app_name = 'register_student_'
                    
                table_name = f"{app_name}{app_name}{class_instance.batch_year}_{class_instance.class_name}_{class_instance.division}".replace(" ","").lower()
                    
                feature_group_id = ['_examresults', '_leaderboard', '_attendance', '_dailyupdates']
                
                data = request.data
                
                new_batch_year = regexFilter(data['batch_year'])
                new_class_name = regexFilter(data['class_name'])
                new_division = regexFilter(data['division'])
                
                new_table_name = f"{app_name}{app_name}{new_batch_year}_{new_class_name}_{new_division}".replace(" ","").lower()
            # Convert data values to uppercase
                for key in data:
                    if isinstance(data[key], str):
                        data[key] = data[key].upper()
                        
                if class_details.objects.filter(class_name=new_class_name, division=new_division, batch_year=new_batch_year).exists():
                    return Response({'Message': 'Class already exists'}, status=status.HTTP_400_BAD_REQUEST)
                
                all_class_updates = class_updates_link.objects.filter(class_name=class_instance.class_name, batch_year=class_instance.batch_year, division=class_instance.division)
                
                for class_updates in all_class_updates:
                    class_updates.class_name = new_class_name
                    class_updates.batch_year = new_batch_year
                    class_updates.division = new_division
                    
                    class_updates.save()
                    
                all_recordings = recordings.objects.filter(class_name=class_instance.class_name, batch_year=class_instance.batch_year, division=class_instance.division)
                
                for recording in all_recordings:
                    recording.class_name = new_class_name
                    recording.batch_year = new_batch_year
                    recording.division = new_division
                    
                    recording.save()
                    
                
                serializer = ClassDetailsSerializer(class_instance, data={
                    'batch_year': new_batch_year,
                    'class_name': new_class_name,
                    'division': new_division
                })
                
                if serializer.is_valid():
           
                    serializer.save()
                    
                    cursor = connection.cursor()
                    
                    for row in feature_group_id:
                        try:
                            cursor = connection.cursor()
                            cursor.execute(f"ALTER TABLE {table_name+row} RENAME TO {new_table_name+row}")
                            print(f'Table {table_name+row} deleted')
                            
                            students_instance = Student.objects.filter(class_group=class_instance.id)
                            
                            for student in students_instance:
                                student.class_name = new_class_name
                                student.division = new_division
                                student.batch_year = new_batch_year
                                student.save()
                                
                        except DatabaseError as e:
                            print(f'Error deleting table {table_name+row}: {str(e)}')        
                    
                    return Response({"message": "Class updated successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Class does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:  # Catch specific exceptions for debugging
            return Response({"message": "Internal failure", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
            
    def get(self, request):
            try: 
                class_id = request.query_params.get('id')
                    
                if class_id:
                    class_instance = class_details.objects.filter(id=class_id).first()
                    
                    if class_instance:
                        serializer = ClassDetailsSerializer(class_instance)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response({"message": "Class does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    classes = class_details.objects.all()
                    serialized_data = []
                    
                    for class_instance in classes:
                        students = Student.objects.filter(class_group=class_instance.id)
                        
                        class_serializer = ClassDetailsSerializer(class_instance)
                        class_data = class_serializer.data
                   
                   
                        class_data['total_students'] = students.count()
                        
                        serialized_data.append(class_data)
                    
                    return Response({"class_details": serialized_data}, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)  
                return Response({"message": "Internal failure"}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
            class_id = request.query_params.get('id')
            if not class_id:
                return Response({"message": "Class ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

            class_instance = class_details.objects.filter(id=class_id).first()
            if not class_instance:
                return Response({"message": "Class group does not exist"}, status=status.HTTP_400_BAD_REQUEST)

            app_name = 'register_student_'
            table_name = f"{class_instance.batch_year}_{class_instance.class_name}_{class_instance.division}".replace(" ", "").lower()
            feature_group_id = ['_examresults', '_leaderboard', '_attendance', '_dailyupdates']

            try:
                with connection.cursor() as cursor:
                    for row in feature_group_id:
                        table_name_to_check = f"{app_name}{app_name}{table_name}{row}"

                        cursor.execute(f"DROP TABLE public.{table_name_to_check}")
                        print(f'Table {table_name_to_check} deleted')


                class_instance.delete()
                print(f'Class group {class_instance} deleted')

                return Response({"message": "Class group deleted successfully"}, status=status.HTTP_200_OK)

            except DatabaseError as e:
                return Response({"message": f"Error deleting tables: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DeviceIdMethods(APIView):
    def put(self, request):
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
            
            device_id = request.data['device_id']
                
            student_instance = Student.objects.filter(id=user_id).first()
                
            if student_instance:
                
                student_instance.device_id = device_id
                student_instance.save()
                    
                return Response({"message": "Device ID updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Student does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:  # Catch specific exceptions for debugging
            return Response({"message": "Internal failure", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class GetClassDetailsDashboard(APIView):
    def get(self, request):
        try:
            year = request.query_params.get('year')
            
            if not year:
                # latest year
                year = class_details.objects.latest('batch_year').batch_year
            
            classInstance = class_details.objects.filter(batch_year=year)
            
            serialized_data = []
            
            for class_instance in classInstance:
                students = Student.objects.filter(class_group=class_instance.id)
                
                class_serializer = ClassDetailsSerializer(class_instance)
                class_data = class_serializer.data
            
            
                class_data['total_students'] = students.count()
                
                serialized_data.append(class_data)
            
            return Response({"class_details": serialized_data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)  
            return Response({"message": "Internal failure"}, status=status.HTTP_400_BAD_REQUEST)
            
            
class StudentBulkMethods(APIView, CustomPageNumberPagination):
    
    def post(self, request, format=None):
        
        try:
            file_obj = request.FILES['doc_file']

            if file_obj:
                # Process the uploaded file (CSV or XLSX)
                if file_obj.name.endswith('.csv'):
                    # Process CSV file
                    data = pd.read_csv(file_obj)
                elif file_obj.name.endswith('.xlsx'):
                    # Process XLSX file
                    data = pd.read_excel(file_obj)
                else:
                    return Response({'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
                
                batch_year = request.POST.get('batch_year')
                class_name = request.POST.get('class_name')
                division = request.POST.get('division')
                subjects = request.POST.get('subjects')
                
                class_instance = class_details.objects.filter(batch_year=batch_year,class_name=class_name,division=division)
                
                if not class_instance:
                    return Response({'message': 'No such class group'}, status=status.HTTP_400_BAD_REQUEST)
                
                data['batch_year'] = batch_year
                data['class_name'] = class_name
                data['division'] = division
                data['subjects'] = subjects
                data['class_group'] = class_instance[0].id

                serializer = StudentSerializer(data=data.to_dict(orient='records'), many=True)

                if serializer.is_valid():
                    # Save the data to the database
                    serializer.save()

                    file_obj.close()  
                
                    return Response({"message": "Successfully added users to class group"}, status=status.HTTP_201_CREATED)
                    
            return Response({'message': 'Invalid file format or data'}, status=status.HTTP_400_BAD_REQUEST)
        
        except:
            return Response({'message': 'Internal failure'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            batch_year = request.query_params.get('batch_year')
            class_name = request.query_params.get('class_name')
            division = request.query_params.get('division')
  
            students = Student.objects.filter(batch_year=batch_year,class_name=class_name,division=division).order_by('name')
            
            try:
                students_result = self.paginate_queryset(students, request)
            except Exception as e:
                return Response({'status': 'failure', 'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            serializer = StudentDisplaySerializer(students_result, many=True)

            if serializer.data == []:
                return Response({'Message': 'No records found'} ,status=status.HTTP_400_BAD_REQUEST)
            
            response = {
                "all_users":serializer.data,
                "total_pages": self.page.paginator.num_pages,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
                "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,
            }
            
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Message': 'Internal failure', 'error': str(e)} ,status=status.HTTP_400_BAD_REQUEST)
 
class GetAllStudents(APIView):
     def get(self, request):
        try:
            students = Student.objects.all()
            serializer = StudentSerializer(students, many=True)
            
            if serializer.data == []:
                return Response({'Message': 'No records found'} ,status=status.HTTP_400_BAD_REQUEST)
            
            
            return Response({'all_users':serializer.data}, status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({'Message': 'Internal failure', 'error': str(e)} ,status=status.HTTP_400_BAD_REQUEST) 
    
class ExamStudentDisplay(APIView):
    def get(self, request):
        try:
            batch_year = request.query_params.get('batch_year')
            class_name = request.query_params.get('class_name')
            division = request.query_params.get('division')
            
            students = Student.objects.filter(batch_year=batch_year,class_name=class_name,division=division)
            serializer = ExamStudentDisplaySerializer(students, many=True)
            
            if serializer.data == []:
                return Response({'Message': 'No records found'} ,status=status.HTTP_400_BAD_REQUEST)
            
            
            return Response({'all_users':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Message': 'Internal failure', 'error': str(e)} ,status=status.HTTP_400_BAD_REQUEST)