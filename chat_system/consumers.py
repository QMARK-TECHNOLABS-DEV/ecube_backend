import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
from admin_auth.models import Admin
from register_student.models import Student
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    room_group_name = None  # Define room_group_name at the class level
    
    @sync_to_async
    def get_or_create_chat_room(self, admission_no, user):
        chatroom, created = ChatRoom.objects.get_or_create(admission_no=admission_no, superuser=user)
        return chatroom, created
    
    @sync_to_async
    def filter_chat_messages(self,chat_room):
        return ChatMessage.objects.filter(chat_room=chat_room)
    
    @database_sync_to_async
    def create_chat_message(self, chat_room, message,sender):
        
        if sender == 'superuser':
            ChatMessage.objects.create(chat_room=chat_room, message=message,sender_id=sender,superadmin=True)
        else:
            ChatMessage.objects.create(chat_room=chat_room, message=message,sender_id=sender)
    
    async def connect(self):
        try:
            query_string = self.scope.get("query_string", b"").decode("utf-8")
            query_params = query_string.split("&")
            admission_no = None
            sender = None

            for param in query_params:
                key, value = param.split("=")
                if key == "admission_no":
                    admission_no = value
                elif key == "sender":
                    sender = value

            if admission_no is not None and sender is not None:
                # Now you have both admission_no and sender
                print(f"admission_no: {admission_no}, sender: {sender}")
            else:
                # Handle the case where one or both parameters are missing
                print("admission_no or sender is missing in the WebSocket URL")
            
        
            #if admission_no != 'superuser':
            user = await sync_to_async(Student.objects.get)(admission_no=admission_no)
            
            if user is None:
                raise ValueError(f"User with admission_no {admission_no} not found.")
            
            print(f"admission_no: {admission_no}")
                # Use sync_to_async to run the synchronous database operation asynchronously
            chat_room, created = await self.get_or_create_chat_room(admission_no, user)
            
            print(f"created: {created}")
            
            # if not created:
            #     previous_messages = await self.filter_chat_messages(chat_room)
                
            #     print(f"previous_messages: {previous_messages}")
            #     if previous_messages is not None:
            #         for message in previous_messages:
            #             await self.send(json.dumps({
            #                 "type": "chat.message",
            #                 "message": message.message,
            #                 "timestamp": message.timestamp.isoformat(),
            #             }))
                        
                
            self.room_group_name = f"group_chat_{admission_no}"
            
            print(f"room_group_name: {self.room_group_name}")
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            print(f"Added {self.channel_name} channel to {self.room_group_name} group.")
            await self.accept()
        except Exception as e:
        
            print(f"Error in connect: {e}")

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        else:
            print("self.room_group_name is None")
            pass


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "sendMessage",
                "message": message,
            })

    async def sendMessage(self, event):
        message = event["message"]
        text_data = json.dumps({"message": message})
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        query_params = query_string.split("&")
        admission_no = None
        sender = None

        for param in query_params:
            key, value = param.split("=")
            if key == "admission_no":
                admission_no = value
            elif key == "sender":
                sender = value

        if admission_no is not None and sender is not None:
            # Now you have both admission_no and sender
            print(f"admission_no: {admission_no}, sender: {sender}")
        else:
            # Handle the case where one or both parameters are missing
            print("admission_no or sender is missing in the WebSocket URL")
        
        
            
        
        chat_room = await sync_to_async(ChatRoom.objects.get)(admission_no=admission_no)
        
        await self.create_chat_message(chat_room, message, sender)
        
        await self.send(text_data=text_data)