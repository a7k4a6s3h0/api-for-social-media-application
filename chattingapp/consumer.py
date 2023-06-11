import json, jwt, base64, re, imghdr, redis
from django.db.models import Q
from .models import *
from PIL import Image
from io import BytesIO
from .serializers import *
from .find_files_extensions import get_file_type
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.files.storage import FileSystemStorage
from channels.generic.websocket import WebsocketConsumer
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

class ChatConsumer(WebsocketConsumer):
    

    def connect(self):
        print(self.scope["url_route"])
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        try:
            token_key = self.scope['query_string'].decode().split('=')

            # Check if the token is a refresh token, in which case authentication is not needed
            decoded_token = jwt.decode(token_key[1], 'SECRET_KEY', algorithms=['HS256'])
            if decoded_token.get('token_type') == 'access_token':
                
                # Check if the token is a valid access token
                user = User.objects.get(id=decoded_token['id'])
                self.scope['user'] = user

        except (jwt.exceptions.DecodeError, User.DoesNotExist, IndexError):
            raise AuthenticationFailed('Invalid token')
        
        '''This if condition check the coming user is a member of that chat room'''

        conversation = Conversation.objects.get(room_name = self.room_name)
        if conversation.room_type != 'Group':
        
            if self.scope['user'].username not in [conversation.initiator.username, conversation.receiver.username]:        
                message = {
                    'type':'warning',
                    'text': 'You are trying to connect to the wrong chat room.'
                }
                
                async_to_sync(self.channel_layer.send)(self.channel_name, message)
                # Disconnect the user
               
        else:
            members_id = conversation.group_members
            if self.scope['user'].id not in members_id:
                message = {
                    'type':'warning',
                    'text': 'You are trying to connect to the wrong chat room.'
                }
                
                async_to_sync(self.channel_layer.send)(self.channel_name, message)
                
        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()
        self.users_online_or_offline("connect")    

    # Send warning_message to WebSocket
    def warning(self, text):
        warning_Message = text['text']
        self.send(text_data=json.dumps({"Warning_Message": warning_Message}))    
        # Disconnect the user
        self.close()

    def disconnect(self, close_code):
        # Leave room group
        self.users_online_or_offline("disconnect")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )    

    count = 1
    users_list = {}
    # Receive message from WebSocket
    def receive(self, text_data):


        if bool(self.users_list):
            self.users_list.clear()

        self.Update_is_read_status(self.scope['user'].id)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        files_data = text_data_json.get('attachment', None)

        if files_data:
            file_url = self.store_files_into_system(files_data)
        else:
            file_url = None  

        conv_details = Conversation.objects.get(room_name = self.room_name)
        current_receiver = conv_details.receiver if conv_details.initiator.id == self.scope['user'].id else conv_details.initiator
        if current_receiver.is_online is False:
            add_notification = Notifications.objects.create(
                                sender = self.scope['user'],
                                conversation_id = conv_details,
                                message = message
                            )

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message, "attachment":file_url}
        )

    # Receive message from room group
    def chat_message(self, event):
        
        message = event["message"]
        
        files_url = event.get("attachment", None)
        sender = self.scope['user']
        
        # check if the has any conversion between other user
 
        if Conversation.objects.filter(room_name = self.room_name).exists():

            conversation = Conversation.objects.get(room_name = self.room_name)

            # storing conversetions ...!
            if files_url:
                
                _message = Message.objects.create(
                    sender=sender,
                    attachment=files_url,
                    text=message,
                    conversation_id=conversation,
                )
               
            else:    
                _message = Message.objects.create(
                        sender=sender,
                        text=message,
                        conversation_id=conversation,
                    )     
            
            self.Update_is_read_status(self.scope['user'].id)
            
            serializer = MessageSerializer(instance=_message)    
            # Send message to WebSocket
            self.send(text_data=json.dumps({"message": serializer.data}))    

        else:
            raise AuthenticationFailed("invalid credentials...!")

    '''This store_files_into_system() store the user sended files in system memory (media folder)'''

    def store_files_into_system(self, files_data):
        b64_regex = re.compile(r'^[A-Za-z0-9+/]*[A-Za-z0-9+/][A-Za-z0-9+/=]{0,2}$')
        if not b64_regex.match(files_data):
            raise ValueError("Invalid base64-encoded data")
        decoded_data = base64.b64decode(files_data)
        # it will recieve the file type
        file_type = get_file_type(decoded_data)  
        extension = file_type.split('/')
        # Save the image file to media folder in the filesystem
        fs = FileSystemStorage() 
        if extension[0] == 'image':
            # verify that the data can be decoded into an image    
            try:
                img = Image.open(BytesIO(decoded_data))
                img.verify()
            except Exception as e:
                raise ValueError("Invalid base64-encoded image data") from e    
            # find the extension of the given image file 
            image_type = imghdr.what(None, decoded_data)
            # Genrete a random number to store image name as unique in database
            number = str(random.randint(10, 99))
            filename = 'image'+number+'.' + image_type
            # # convert the image_file into InMemoryUploadedFile
            image_file = InMemoryUploadedFile(
                file=BytesIO(decoded_data),
                field_name='attachment',
                name=filename,
                content_type=extension,
                size=len(decoded_data),
                charset=None
            )
            saved_file_name = fs.save(os.path.join('images', filename), image_file)

            # Return the URL of the saved image file
            return fs.url(saved_file_name)

        elif extension[0] == 'video':
            video_extension = extension[1]
            # Genrete a random number to store image name as unique in database
            number = str(random.randint(10, 99))
            filename = 'video'+number+'.' + video_extension
            image_file = InMemoryUploadedFile(
                    file=BytesIO(decoded_data),
                    field_name='attachment',
                    name=filename,
                    content_type=extension,
                    size=len(decoded_data),
                    charset=None
                )
            saved_file_name = fs.save(os.path.join('videos', filename), image_file)

            # Return the URL of the saved image file
            return fs.url(saved_file_name)    
        else:
             raise ValidationError('Unsupported file type!.')

    '''This Update_is_read_status() find who is the current sender and reciever and update the field (is_read) in  reciever column set as True '''

    def Update_is_read_status(self, receiver):
        if 'sender' not in self.users_list:
            self.users_list['sender'] = receiver
        else: 
            if self.users_list['sender'] != receiver:
                self.users_list[f'receiver{self.count}'] = receiver 
                self.count += 1

                for key, reciver_user in self.users_list.items():
                    if key != 'sender':
                        mark_as_read = Message.objects.filter(sender=reciver_user)
                        for i in mark_as_read:
                            i.is_read = True
                            i.save()


    
    '''This users_online_or_offline() find the user is connect to webscoket or not if the user is connect then it will update of the current user is_online field as True . 
        and if the user is discconect  the time this function will tigger . This function will work according to number of authorized users in a chat room '''

    def users_online_or_offline(self, connect_or_not):
        details = Conversation.objects.get(room_name = self.room_name)
        if details.room_type != 'Group':
            if connect_or_not != "disconnect":
                update_status = self.scope['user']
                update_status.is_online = True
                update_status.save()

                if details.initiator.id == self.scope['user'].id:
                    current_reciever = details.receiver   
                else:
                    current_reciever = details.initiator

                current_status = User.objects.get(username=current_reciever)
                if current_status.is_online == True:
                    status = "ONLINE"
                else:
                    status = "OFFLINE"
                    if Notifications.objects.exists():  
                        last_message = Message.objects.all().order_by('-timestamp').first()
                
                        notification_data = Notifications.objects.filter(sender = self.scope['user'].id)
                        
                        for data in notification_data:
                            if data.is_read == True:

                                create_message = Message.objects.create(
                                    
                                    sender=current_status,
                                    attachment=last_message.attachment,
                                    text=last_message.text,
                                    conversation_id=details,
                                    is_read = True
                                
                                )

            else:
                update_status = self.scope['user']
                update_status.is_online = False
                update_status.save()
                status = "OFFLINE"

        else:
            if connect_or_not != "disconnect":
                group_members_status = User.objects.get(id= self.scope['user'].id)
                group_members_status.is_online = True
                group_members_status.save()
            else:
                group_members_status = User.objects.get(id= self.scope['user'].id)
                group_members_status.is_online = False
                group_members_status.save()   

        async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type":"send_updated_status", "message": status}
            )

    '''This send_updated_status() help to send current status like (is_online or is_offline) of a user '''

    def send_updated_status(self, event):
        message = event["message"]
        self.send(text_data=json.dumps({"status": message}))




