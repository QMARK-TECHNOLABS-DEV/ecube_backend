import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
from admin_auth.models import Admin
from register_student.models import Student
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
class ChatListConsumer(AsyncWebsocketConsumer):
    
    @sync_to_async
    def create_chat_room(self, admission_no, superuser):
        chatroom, created = ChatRoom.objects.get_or_create(admission_no=admission_no, superuser=superuser)
        return chatroom, created

    async def broadcast_new_room(self, admission_no, superuser):
        # Create or retrieve the chat room
        chat_room, created = await self.create_chat_room(admission_no, superuser)
        
        self.channel_layer = get_channel_layer()
        
        if created:
            # This is a new chat room, send a message to group_chat_list
            student_instance = await sync_to_async(Student.objects.get)(admission_no=admission_no)


            
            channel_data = json.dumps({
                "admission_no": chat_room.admission_no,
                "name": student_instance.name,
                "batch_year": student_instance.batch_year,
                "class_name": student_instance.class_name,
                "division": student_instance.division,
                "superuser": chat_room.superuser.id,
            })
            
            await self.send(text_data=channel_data)
            
        return chat_room, created


    @sync_to_async
    def get_chat_rooms(self):
        chat_rooms = ChatRoom.objects.all()
        return list(chat_rooms.values('admission_no', 'superuser'))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        
    async def connect(self):
        try:
            self.room_group_name = "group_chat_list"

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            
            chat_rooms = await self.get_chat_rooms()
            for chat_room in chat_rooms:
                
                student_instance = await sync_to_async(Student.objects.get)(admission_no=chat_room['admission_no'])
                await self.send(text_data=json.dumps({
                    "admission_no": chat_room['admission_no'],
                    "name": student_instance.name,
                    "batch_year": student_instance.batch_year,
                    "class_name": student_instance.class_name,
                    "division": student_instance.division,
                    "superuser": chat_room['superuser'],
                }))
            
        except Exception as e:
            print(f"Error in connect: {e}")
            
    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
    async def receive(self, text_data):
        
        channel_data = json.loads(text_data)
        admission_no = channel_data["admission_no"]
        superuser = channel_data["superuser"]
        name = channel_data["name"]
        batch_year = channel_data["batch_year"]
        class_name = channel_data["class_name"]
        division = channel_data["division"]
        
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "broadcastMessage",
                "admission_no": admission_no,
                "superuser": superuser,
                "name": name,
                "batch_year": batch_year,
                "class_name": class_name,
                "division": division,
            })    

        
class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None  # Define room_group_name at the class level
        self.admission_no = None
        self.sender = None
        self.messages = []

    @sync_to_async
    def get_or_create_chat_room(self, admission_no, user):
        chatroom, created = ChatRoom.objects.get_or_create(admission_no=admission_no, superuser=user)
        

        return chatroom, created

    @sync_to_async
    def create_chat_message(self, chat_room, messages):
        for message in messages:
            superadmin = False
            
            if message['username'] == 'Management':
                superadmin = True
                
                
            ChatMessage.objects.create(chat_room=chat_room, message=message['message'], sender_id=message['username'], superadmin=superadmin)
        
    @sync_to_async
    def get_previous_messages(self, chat_room):
        # Retrieve previous messages from the database
        previous_messages = ChatMessage.objects.filter(chat_room=chat_room).order_by('timestamp')
        return list(previous_messages.values('message', 'sender_id'))
    
    async def connect(self):
        try:
            query_string = self.scope.get("query_string", b"").decode("utf-8")
            query_params = query_string.split("&")

            for param in query_params:
                key, value = param.split("=")
                if key == "admission_no":
                    self.admission_no = value
                elif key == "sender":
                    self.sender = value

            if self.admission_no is not None and self.sender is not None:
                print(f"admission_no: {self.admission_no}, sender: {self.sender}")
            else:
                print("admission_no or sender is missing in the WebSocket URL")

            student_instance = await sync_to_async(Student.objects.get)(admission_no=self.admission_no)

            if student_instance is None:
                raise ValueError(f"User with admission_no {self.admission_no} not found.")

            chat_list_consumer = ChatListConsumer()  # Create an instance of ChatListConsumer
            chat_room, created = await chat_list_consumer.broadcast_new_room(self.admission_no, student_instance)
            
            
            self.room_group_name = f"group_chat_{self.admission_no}"

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Retrieve previous messages from the database and send them to the user
            previous_messages = await self.get_previous_messages(chat_room)
            for message in previous_messages:
                await self.send(text_data=json.dumps({
                    "message": message['message'],
                    "username": message['sender_id'],
                }))
            
            # # Send the channel data after the connection is accepted
            

        except Exception as e:
            print(f"Error in connect: {e}")

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            messages = getattr(self, 'messages', [])
            if messages:
                chat_room = await sync_to_async(ChatRoom.objects.get)(admission_no=self.admission_no)
                await self.create_chat_message(chat_room, messages)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        
        
        self.messages.append({
            "message": message,
            "username": username,
        })

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "sendMessage",
                "message": message,
                "username": username,
            })

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]

        text_data = json.dumps({"message": message, "username": username})

        await self.send(text_data=text_data)