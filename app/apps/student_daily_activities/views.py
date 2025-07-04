from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from ..register_student.models import Student, class_details
from ..client_auth.utils import TokenUtil

from ecube_backend.pagination import CustomPageNumberPagination
import pandas as pd
import requests, json
from datetime import datetime
from django.utils import timezone
from ecube_backend.utils import role_checker


def send_notification(registration_ids, message_title, message_desc, message_type):
    fcm_api = "AAAAqbxPQ_Q:APA91bGWil8YXU8Zr1CLa-tqObZ-DVJUqq0CrN0O76bltTApN51we3kOqrA4rRFZUXauBDtkcR3nWCQ60UPWuroRZpJxuCBhgD6CdHAnjqh8V2zPIzLvuvERmbipMHIoJJxuBegJW3a3"
    url = "https://fcm.googleapis.com/fcm/send"

    headers = {"Content-Type": "application/json", "Authorization": "key=" + fcm_api}

    payload = {
        "registration_ids": registration_ids,
        "priority": "high",
        "notification": {
            "body": message_desc,
            "title": message_title,
        },
        "data": {
            "type": message_type,
        },
    }

    result = requests.post(url, data=json.dumps(payload), headers=headers)
    print(result.json())


def send_notification_main(registration, message_title, message_desc, message_type):
    # registration = ['dREWgJKnS5yw3KJ_0w0OaS:APA91bGFBliKfQI4itzjmdhDRCqkBDywYeSQjJvIB1f3bHYEF9QLuD70lHyi3AI9QXDofqxzbjaXXEKdeolg8bGboQQPQXeJuLluw0K3Y-h_GEhHg47Ln_OiioGMiWKpqYX-xnXSUk7b']
    result = send_notification(registration, message_title, message_desc, message_type)
    print(result)


def split_date(date_str):
    # Split the date string into parts
    if ":" in date_str:
        parts = date_str.split(":")[1].split("/")
    elif "-" in date_str:
        parts = date_str.split("-")[1].split("/")
    # Ensure the year, month, and day are in the desired format
    if len(parts[2]) == 2:
        year = f"20{parts[2]:02}"
    elif len(parts[2]) == 4:
        year = parts[2]

    month = parts[1].zfill(2)
    day = parts[0].zfill(2)

    # return {
    #     "year": year,
    #     "month": month,
    #     "day": day
    # }
    return f"{day}/{month}/{year}"


class AddDailyUpdatesBulk(APIView):
    def post(self, request):

        batch_year = request.GET.get("batch_year")
        class_name = request.GET.get("class_name")
        division = request.GET.get("division")
        date_variable = request.GET.get("date")

        batch_year_notif = batch_year
        class_name_notif = class_name
        division_notif = division

        if batch_year is None or class_name is None or division is None:
            return Response(
                {
                    "status": "failure",
                    "message": "batch_year, class_name, and division are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "")
        class_name = str(class_name).lower()
        division = str(division).replace(" ", "")
        division = str(division).lower()

        file_obj = request.FILES["media_file"]

        if file_obj:
            # Process the uploaded file (CSV or XLSX)
            if file_obj.name.endswith(".csv"):
                # Process CSV file
                df = pd.read_csv(file_obj)
            elif file_obj.name.endswith(".xlsx"):
                # Process XLSX file
                df = pd.read_excel(file_obj)
            else:
                return Response(
                    {"message": "Unsupported file format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        data_dict = {"students": []}

        activity_code = {
            "O": "Contact Institution",
            "N": "Student have not answered in the QnA session",
        }
        # Extract the date from the first cell in the Excel sheet
        # raw_date = df.columns[0]
        # date_variable = split_date(raw_date)
        admission_nos = []

        max_count_of_y = -1
        # Iterate through rows (excluding the header) and count "Y" values
        for index, row in df.iterrows():
            adm_no = row[0]  # Assuming the first column contains student names
            if pd.notna(adm_no) and adm_no != "AD NO":
                print(batch_year_notif, class_name_notif, division_notif)

                student_instance = None

                try:

                    student_instance = Student.objects.get(
                        batch_year=batch_year_notif,
                        class_name=class_name_notif,
                        division=division_notif,
                        admission_no=adm_no,
                    )

                except Exception as e:
                    print(e)
                    pass  # student_instance = Student.objects.get(admission_no=adm_no)

                if student_instance:
                    print("admission no ")

                    admission_nos.append(str(adm_no))

                    student_data = {
                        "admission_no": adm_no,
                        "date": date_variable,
                        "on_time": True,
                        "voice": (
                            False if str(row.iloc[2]).upper().strip() == "M" else True
                        ),
                        "nb_sub": (
                            False if str(row.iloc[2]).upper().strip() == "B" else True
                        ),
                        "mob_net": (
                            False if str(row.iloc[2]).upper().strip() == "R" else True
                        ),
                        "camera": (
                            False if str(row.iloc[2]).upper().strip() == "V" else True
                        ),
                        "full_class": True,
                        "activities": sum(1 for val in row[3:] if val == "Y"),
                        "engagement": (
                            False if str(row.iloc[2]).upper().strip() == "L" else True
                        ),
                        "remarks": (
                            activity_code[str(row.iloc[2]).upper().strip()]
                            if str(row.iloc[2]).upper().strip() in ["O", "N"]
                            else ""
                        ),
                    }

                    count_of_y = student_data["activities"]

                    if count_of_y > max_count_of_y:
                        max_count_of_y = count_of_y

                    data_dict["students"].append(student_data)

        app_name = "register_student"

        table_name = (
            app_name
            + "_"
            + app_name
            + "_"
            + batch_year
            + "_"
            + class_name
            + "_"
            + division
            + "_dailyupdates"
        )

        cursor = connection.cursor()

        try:

            for student in data_dict["students"]:

                if max_count_of_y > 0:
                    student["overall_performance_percentage"] = (
                        int((int(student["activities"]) / int(max_count_of_y)) * 50)
                        + 25
                        if student["nb_sub"]
                        else 0 + 25 if student["engagement"] else 0
                    )
                    print(max_count_of_y)
                    student["activities"] = f"{student['activities']}/{max_count_of_y}"
                elif max_count_of_y == 0:
                    student["overall_performance_percentage"] = (
                        25
                        if student["nb_sub"]
                        else 0 + 25 if student["engagement"] else 0
                    )
                    print(max_count_of_y)
                    student["activities"] = "0"
                student["overall_performance"] = (
                    "EXCELLENT"
                    if student["overall_performance_percentage"] >= 85
                    else (
                        "GOOD"
                        if student["overall_performance_percentage"] >= 50
                        else (
                            "AVERAGE"
                            if student["overall_performance_percentage"] > 25
                            else "POOR"
                        )
                    )
                )

                print("Before insert")
                sql_query = f"""
                    INSERT INTO public.{table_name} (admission_no, date, on_time, voice, nb_sub, mob_net, camera, full_class, activities, engagement, overall_performance_percentage, overall_performance, remarks) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (admission_no, date) DO UPDATE
                    SET 
                        on_time = EXCLUDED.on_time,
                        voice = EXCLUDED.voice,
                        nb_sub = EXCLUDED.nb_sub,
                        mob_net = EXCLUDED.mob_net,
                        camera = EXCLUDED.camera,
                        full_class = EXCLUDED.full_class,
                        activities = EXCLUDED.activities,
                        engagement = EXCLUDED.engagement,
                        overall_performance_percentage = EXCLUDED.overall_performance_percentage,
                        overall_performance = EXCLUDED.overall_performance,
                        remarks = EXCLUDED.remarks
                """

                cursor.execute(
                    sql_query,
                    (
                        str(student["admission_no"]),
                        student["date"],
                        student["on_time"],
                        student["voice"],
                        student["nb_sub"],
                        student["mob_net"],
                        student["camera"],
                        student["full_class"],
                        student["activities"],
                        student["engagement"],
                        student["overall_performance_percentage"],
                        student["overall_performance"],
                        student["remarks"],
                    ),
                )

            cursor.close()
            student_list = Student.objects.filter(
                batch_year=batch_year_notif,
                class_name=class_name_notif,
                division=division_notif,
            ).values("device_id", "admission_no")

            if student_list:
                device_ids = [
                    student["device_id"]
                    for student in student_list
                    if student["admission_no"] in admission_nos
                ]

                print(device_ids)

                if device_ids:
                    message_title = "Daily Class Updates"
                    message_desc = f"Check your daily class update on {date_variable}."
                    message_type = "dailyClass"

                    send_notification_main(
                        device_ids, message_title, message_desc, message_type
                    )

            class_group_instance = class_details.objects.get(
                batch_year=batch_year_notif,
                class_name=class_name_notif,
                division=division_notif,
            )

            class_group_instance.daily_class = timezone.now()

            class_group_instance.daily_class_date = date_variable

            class_group_instance.save()

            return Response(
                {"message": "Data saved successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            # Handle exceptions here
            print(f"Error: {str(e)}")
            return Response(
                {"message": "Failed to save data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetDates(APIView):
    def get(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response(
                {"error": "Access token is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        _, token = authorization_header.split()

        payload = TokenUtil.decode_token(token)

        # Optionally, you can extract user information or other claims from the payload
        if not payload:
            return Response(
                {"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = payload.get("id")

        if not user_id:
            return Response(
                {"error": "The refresh token is not associated with a user."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Generate a new access token
        user = Student.objects.get(id=user_id)

        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "").lower()
        division = str(division).replace(" ", "").lower()

        app_name = "register_student"

        table_name = (
            app_name
            + "_"
            + app_name
            + "_"
            + batch_year
            + "_"
            + class_name
            + "_"
            + division
            + "_dailyupdates"
        )

        try:
            cursor = connection.cursor()

            cursor.execute(
                f"SELECT DISTINCT date, TO_DATE(date, 'DD/MM/YYYY') AS parsed_date FROM public.{table_name} ORDER BY parsed_date DESC"
            )

            dates = cursor.fetchall()

        except Exception as e:
            # Handle exceptions here
            print(f"Error: {str(e)}")
            return Response(
                {"message": "Failed to save data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        dates_list = []

        for date in dates:
            dates_list.append(date[0])

        return Response({"dates": dates_list}, status=status.HTTP_200_OK)


class GetDailyUpdate(APIView):
    def get(self, request):
        date = request.GET.get("date")

        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response(
                {"error": "Access token is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        _, token = authorization_header.split()

        payload = TokenUtil.decode_token(token)

        # Optionally, you can extract user information or other claims from the payload
        if not payload:
            return Response(
                {"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = payload.get("id")

        if not user_id:
            return Response(
                {"error": "The refresh token is not associated with a user."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Generate a new access token
        user = Student.objects.get(id=user_id)

        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "").lower()
        division = str(division).replace(" ", "").lower()

        app_name = "register_student"

        table_name = (
            app_name
            + "_"
            + app_name
            + "_"
            + batch_year
            + "_"
            + class_name
            + "_"
            + division
            + "_dailyupdates"
        )

        cursor = connection.cursor()

        cursor.execute(
            f"SELECT * FROM public.{table_name} WHERE date = %s AND admission_no = %s ORDER BY id",
            [date, user.admission_no],
        )

        query_result = cursor.fetchall()

        cursor.close()

        daily_updates = []

        if query_result:
            for row in query_result:
                daily_update = {
                    "admission_no": row[1],
                    "date": row[2],
                    "on_time": row[3],
                    "voice": row[4],
                    "nb_sub": row[5],
                    "mob_net": row[6],
                    "camera": row[7],
                    "full_class": row[8],
                    "activities": row[9],
                    "engagement": row[10],
                    "overall_performance_percentage": row[11],
                    "overall_performance": row[12],
                    "remarks": row[13],
                }

                daily_updates.append(daily_update)

        else:
            daily_update = {
                "admission_no": user.admission_no,
                "date": date,
                "on_time": False,
                "voice": False,
                "nb_sub": False,
                "mob_net": False,
                "camera": False,
                "full_class": False,
                "activities": 0,
                "engagement": False,
                "overall_performance_percentage": 0,
                "overall_performance": "POOR",
                "remarks": "",
            }

            daily_updates.append(daily_update)

        return Response({"daily_updates": daily_updates}, status=status.HTTP_200_OK)


class AdminGetDates(APIView):
    @role_checker(allowed_roles=["admin"])
    def get(self, request):
        user_id = request.GET.get("user_id")

        if not user_id:
            return Response(
                {"error": "The refresh token is not associated with a user."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Generate a new access token
        user = Student.objects.get(id=user_id)

        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division

        if batch_year is None or class_name is None or division is None:
            return Response(
                {
                    "status": "failure",
                    "message": "batch_year, class_name, and division are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        class_details_instance = class_details.objects.filter(
            batch_year=batch_year, class_name=class_name, division=division
        ).first()

        if not class_details_instance:
            return Response(
                {"status": "failure", "message": "Invalid class details"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "").lower()
        division = str(division).replace(" ", "").lower()

        app_name = "register_student"

        table_name = (
            app_name
            + "_"
            + app_name
            + "_"
            + batch_year
            + "_"
            + class_name
            + "_"
            + division
            + "_dailyupdates"
        )

        try:
            cursor = connection.cursor()

            cursor.execute(
                f"SELECT DISTINCT TO_CHAR(TO_DATE(date, 'DD/MM/YYYY'), 'MM/YYYY') AS month_year FROM public.{table_name}"
            )
            month_years = cursor.fetchall()

        except Exception as e:
            # Handle exceptions here
            print(f"Error: {str(e)}")
            return Response(
                {"message": "Failed to save data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        dates_list = []

        for date in month_years:
            dates_list.append(date[0])

        return Response({"dates": dates_list}, status=status.HTTP_200_OK)


class AdminDailyUpdateViewHome(APIView, CustomPageNumberPagination):
    @role_checker(allowed_roles=["admin"])
    def get(self, request):
        try:
            batch_year_cap = request.query_params.get("batch_year")
            class_name_cap = request.query_params.get("class_name")
            division_cap = request.query_params.get("division")
            date = request.query_params.get("date")

            if batch_year_cap is None or class_name_cap is None or division_cap is None:
                class_group_instance = (
                    class_details.objects.filter(
                        daily_class__isnull=False, daily_class_date__isnull=False
                    )
                    .order_by("-daily_class")
                    .first()
                )

                if class_group_instance is None:
                    return Response(
                        {"message": "Nothing to show here"}, status=status.HTTP_200_OK
                    )
                else:
                    batch_year_cap = class_group_instance.batch_year
                    class_name_cap = class_group_instance.class_name
                    division_cap = class_group_instance.division
                    date_cap = class_group_instance.daily_class_date

            batch_year = str(batch_year_cap)
            class_name = str(class_name_cap).replace(" ", "")
            class_name = str(class_name).lower()
            division = str(division_cap).replace(" ", "")
            division = str(division).lower()

            app_name = "register_student_"

            table_name_examresults = (
                app_name
                + app_name
                + batch_year
                + "_"
                + class_name
                + "_"
                + division
                + "_dailyupdates"
            )

            if not date:
                date = date_cap

            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM public.{table_name_examresults} WHERE date = %s", [date]
            )
            query_results = cursor.fetchall()

            cursor.close()

            daily_class_results = []
            if query_results:
                for result in query_results:

                    try:
                        student_instance = Student.objects.get(admission_no=result[1])
                        print("inside the loop")
                        daily_class_results.append(
                            {
                                "admission_no": result[1],
                                "name": student_instance.name,
                                "date": result[2],
                                "on_time": result[3],
                                "voice": result[4],
                                "nb_sub": result[5],
                                "mob_net": result[6],
                                "camera": result[7],
                                "full_class": result[8],
                                "activities": result[9],
                                "engagement": result[10],
                                "overall_performance_percentage": result[11],
                                "overall_performance": result[12],
                                "remarks": result[13],
                            }
                        )
                    except Exception as e:
                        print(e)
                        pass

            try:
                daily_class_results = self.paginate_queryset(
                    daily_class_results, request
                )
            except Exception as e:
                return Response(
                    {"status": "failure", "msg": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            response = {
                "class_name": class_name_cap,
                "batch_year": batch_year_cap,
                "division": division_cap,
                "result_data": daily_class_results,
                "total_pages": self.page.paginator.num_pages,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next_page_number": (
                    self.page.next_page_number() if self.page.has_next() else None
                ),
                "previous_page_number": (
                    self.page.previous_page_number()
                    if self.page.has_previous()
                    else None
                ),
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": "failure", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminGetDailyUpdate(APIView):
    @role_checker(allowed_roles=["admin"])
    def get(self, request):
        user_id = request.query_params.get("user_id")
        month_year = request.query_params.get("date")

        if not user_id:
            return Response(
                {"error": "The refresh token is not associated with a user."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = Student.objects.get(id=user_id)

        batch_year = user.batch_year
        class_name = user.class_name
        division = user.division

        if batch_year is None or class_name is None or division is None:
            return Response(
                {
                    "status": "failure",
                    "message": "batch_year, class_name, and division are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        class_details_instance = class_details.objects.filter(
            batch_year=batch_year, class_name=class_name, division=division
        ).first()

        if not class_details_instance:
            return Response(
                {"status": "failure", "message": "Invalid class details"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        batch_year = str(batch_year)
        class_name = str(class_name).replace(" ", "").lower()
        division = str(division).replace(" ", "").lower()

        app_name = "register_student"

        table_name = (
            app_name
            + "_"
            + app_name
            + "_"
            + batch_year
            + "_"
            + class_name
            + "_"
            + division
            + "_dailyupdates"
        )

        print(table_name)
        cursor = connection.cursor()

        if month_year:
            cursor.execute(
                f"SELECT * FROM public.{table_name} WHERE date LIKE %s AND admission_no = %s",
                [f"%{month_year}", user.admission_no],
            )
            query_result = cursor.fetchall()
        else:
            cursor.execute(
                f"SELECT * FROM public.{table_name} WHERE admission_no = %s",
                [user.admission_no],
            )

            print("query result obtained")

            query_result = cursor.fetchall()

            print(query_result)
        cursor.close()

        daily_updates = []

        if query_result:
            for row in query_result:
                daily_update = {
                    "admission_no": row[1],
                    "date": row[2],
                    "on_time": row[3],
                    "voice": row[4],
                    "nb_sub": row[5],
                    "mob_net": row[6],
                    "camera": row[7],
                    "full_class": row[8],
                    "activities": row[9],
                    "engagement": row[10],
                    "overall_performance_percentage": row[11],
                    "overall_performance": row[12],
                    "remarks": row[13],
                }

                daily_updates.append(daily_update)

            message = "Daily updates fetched successfully"

        else:

            message = "No daily updates found"

        return Response(
            {"daily_updates": daily_updates, "message": message},
            status=status.HTTP_200_OK,
        )
