import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
from admin_auth.models import Admin
from register_student.models import Student
from asgiref.sync import sync_to_async

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

            user = await sync_to_async(Student.objects.get)(admission_no=self.admission_no)

            if user is None:
                raise ValueError(f"User with admission_no {self.admission_no} not found.")

            chat_room, created = await self.get_or_create_chat_room(self.admission_no, user)

            self.room_group_name = f"group_chat_{self.admission_no}"

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
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