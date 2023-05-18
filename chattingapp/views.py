import random, string, datetime, time, json, base64, imghdr
from .models import User,OTP_Checking
from PIL import Image
from io import BytesIO
from django.db.models import Q
from django.core.files.uploadedfile import InMemoryUploadedFile
from .find_files_extensions import get_file_type
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from agora_token_builder import RtcTokenBuilder
from rest_framework.exceptions import APIException, AuthenticationFailed, ValidationError
from rest_framework.authentication import get_authorization_header, SessionAuthentication
from .serializers import *
from .otp_generator import send_otp, send_message
from .token_authentication import access_token, refresh_token, decode_access_token, decode_refresh_token
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated, AllowAny
from . custom_permissions import IsRegisteredUser, isLoginedUser, IsCurrentUser



# Create your views here.

def register(request):
    return render(request, 'user_register.html')

def user_login(request):
    return render(request, 'user_login.html')    


def otp(request):
    return render(request, 'otp.html')  


def user_home(request):
    return render(request, 'home.html')

def chat_room(request):
    return render(request, "chat_room.html")

def room(request, room_name):
    return render(request, 'room.html',{"room_name": room_name})


def video_call(request):
    return render(request, 'video_call.html')

def user_calling(request):
    return render(request, "calling.html")

def user_accept(request):
    return render(request, "call_coming.html")    

def notification_testing(request):
    return render(request, "notification.html")

# Generate Random Channel Name 

def generate_random_channel_name():
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(8))


class RegisterAPI(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            user = serializer.data
            response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'successfully Registerd',
                    'Your_Register_id':' Please copy the ID and save it for future reference, as it may be required for accessing or using certain features --->'+ ' ' + user['registered_userid']
                }
            return Response(response)
        else:
            
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)   


class User_LoginAPI(generics.GenericAPIView):
    permission_classes = [IsRegisteredUser]
    serializer_class = loginserilizer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            flag = True
            user = User.objects.filter(email = serializer.data.get("email")).first()
            if not user:
                flag = False
                raise APIException("invalid credentails..!")
            if not user.check_password(serializer.data.get("password")):
                    flag = False
                    raise APIException("invalid credentails..!")
            if flag is True:
                
                if not OTP_Checking.objects.filter(user_id = user.id).exists():
                    send_otp(serializer.data.get("email"))
                    response = {
                        'message':'OTP is sent to Your mail Please Check it and please not this your have check otp in 3 times',
                        'status':status.HTTP_200_OK
                    }
                    return Response(response)
                else:
                    otp_count = OTP_Checking.objects.get(user_id = user.id)
                    if otp_count.otp_generating_count != 0:
                        otp_count.otp_generating_count -= 1
                        otp_count.save()
                        send_otp(serializer.data.get("email"))
                        response = {
                            'message':f'OTP is sent to Your mail Please Check it and please not this your have check otp in {otp_count.otp_generating_count} times',
                            'status':status.HTTP_200_OK
                        }
                        return Response(response)
                    else:
                        current_time = timezone.now()
                        # Calculate the time difference between the OTP generation time and the current time
                        time_diff = current_time - otp_count.created_time
                        # Check if the time difference is greater than 1 hour
                        if time_diff.total_seconds() > 3600:

                            otp_count.otp_generating_count = 3
                            otp_count.save()
                            send_otp(serializer.data.get("email"))
                            response = {
                                'message':f'OTP is sent to Your mail Please Check it and please not this your have check otp in {otp_count.otp_generating_count} times',
                                'status':status.HTTP_200_OK
                            }
                            return Response(response)
                        else:
                
                            response = {
                                'message':'Your otp generating Limit Exceeued you can try it after 1 hour',
                                'status':status.HTTP_400_BAD_REQUEST
                            }
                            return Response(response) 
        else:        
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   


class OTP_checking(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = OTPCHECKINGSerilizer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            current_user = User.objects.get(registered_userid = serializer.data.get('Registerd_id'))
            user = OTP_Checking.objects.filter(user_id = current_user.id).first()
            current_timestamp = timezone.now()
            verification_timestamp = user.created_time
            verification_window_duration = timezone.timedelta(minutes=5)
            expiration_timestamp = verification_timestamp + verification_window_duration
            # validate user enterd otp
            if user.is_verified is False:
                if user.OTP == int(serializer.data.get('user_entered_otp')) and current_timestamp <= expiration_timestamp:
                    current_user.is_verified = True
                    current_user.save()
                    user.is_verified = True
                    user.save()
                    permission_token = access_token(current_user.id)
                    refresh_tok = refresh_token(current_user.id)
                    success = {
                        'refresh_token':refresh_tok,
                        'asscess_token':permission_token,
                        'status':status.HTTP_200_OK,
                        'message': 'OTP VALIDATED SUCCESSFULLY'
                    }
                    
                    return Response(success)
                else:
                    error = {
                        'message':'INVALID OTP OR OTP TIME OUT',
                        'status':status.HTTP_408_REQUEST_TIMEOUT
                    }
                    return Response(error, status=status.HTTP_408_REQUEST_TIMEOUT)   
            else:
                return Response({
                    'message':'OTP Already Verified',
                    'status':status.HTTP_400_BAD_REQUEST
                })        
        else:
            # Resend OTP 
            user = User.objects.get(registered_userid = request.data['Registerd_id'])
            if user:
                otp_checker = OTP_Checking.objects.get(user_id = user.id)
                if otp_checker.otp_generating_count <= 3:
                    otp_checker.otp_generating_count = 4
                    otp_checker.save()
                
                if otp_checker.otp_generating_count != 0:
                    otp_checker.otp_generating_count -= 1
                    otp_checker.save()
                    send_otp(user.email)
                    response = {
                        'message':f'Resent OTP sented to your mail and please not you have limited 4 times to resend otp ---> {otp_checker.otp_generating_count} ',
                        'status':status.HTTP_201_CREATED
                    }
                    return Response(response)
                else:
                    response = {
                            'message':'Your otp generating Limit Exceeued you need to login again',
                            'status':status.HTTP_400_BAD_REQUEST
                        }
                    return Response(response) 

            return Response({
                'msg':'INVALID REGISTER ID'
            })    


class ForgottPassword(generics.GenericAPIView):
    permission_classes = [IsRegisteredUser]
    serializer_class = Forgottpasswordserilizer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(email = serializer.data.get('email')).first()
        
            if user:
                subject = 'account recovery link'
                message = 'Your password updating link : http://localhost:8000/api/changepassword/. Please use this link to update your password'
                send_message(user.email, subject, message)
                return Response({'msg':f'Link is sended to your {user.email} please check it'})
            else:
                raise APIException("invalid credentails..!")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class ResetPassword(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    serializer_class = ResetPasswordSerilizer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_vaild():
            user = User.objects.filter(id = request.user.id).first()
            if user:
                if user.check_password(serializer.data.get('password')):
                    subject = 'Account Password Reset Link'
                    message = 'Your password updating link : http://localhost:8000/api/changepassword/. Please use this link to update your password'
                    send_message(user.email, subject, message)
                    return Response({'msg':f"Link is sended to your {user.email} please check it"})
                return Response({'msg':'INVALID PASSWORD'})   
            else:
                raise APIException("invalid credentails..!")  

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class ChangePassword(generics.GenericAPIView):
    """
    An endpoint for changing password.
    """
    permission_classes = [IsRegisteredUser]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(registered_userid = serializer.data.get('Registerd_id')).first()
            if user:
                if serializer.data.get("password") == serializer.data.get("password2"):
                    user.set_password(serializer.data.get("password2"))
                    user.save()
                    subject = 'account recovery'
                    message = 'Your account password updated successfully'
                    send_message(user.email, subject, message)
                    
                    response = {
                        'status': 'success',
                        'code': status.HTTP_200_OK,
                        'message': 'Password updated successfully'
                    }

                    return Response(response)
                else:
                    return Response({
                        'msg':'Both Password Doesnt Match',
                        'status':status.HTTP_400_BAD_REQUEST
                    })
            else:
                return Response({
                    'message':'invalid credentails..!',
                    'status':status.HTTP_400_BAD_REQUEST
                })        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
          



class RefreshAPIVIEW(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def get(self, request):
        auth_header = get_authorization_header(request).split()
      
        if auth_header and len(auth_header) == 2:
            token = auth_header[1].decode('utf-8')
            print(token)
            id = decode_refresh_token(token)
            new_access_token = access_token(id)
            return Response({
                'token':new_access_token
            })
        else:
            return Response({
                'msg':'Token not provided',
                'status':status.HTTP_204_NO_CONTENT
            })


class userProfileView(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    serializer_class = [UserSerializer]
    def get(self, request):
        user = User.objects.filter(id = request.user.id).first()
        if user:
            return Response(UserSerializer(user).data)
        else:
            return Response(UserSerializer.errors, status=status.HTTP_401_UNAUTHORIZED)      


class UserProfileadd(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    serializer_class = UserProfileAdd
    def post(self, request):
        serializer = UserProfileAdd(instance=request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'msg':'data added successfully',
                'status':status.HTTP_200_OK
            })
        return Response(
            serializer.errors, status.HTTP_400_BAD_REQUEST
        )    

# S
class userProfileEdit(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    serializer_class = UserProfileEditClass
    def put(self, request):
        serializer = UserProfileEditClass(instance=request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                'msg':'data updated successfully',
                'status':status.HTTP_200_OK
            }
            return Response(response)
        else:
            response = {
                    'msg':serializer.errors,
                    'status':status.HTTP_401_UNAUTHORIZED
                }
            return Response(response)


class UserMobile_Number_Update(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    serializer_class = MobileNumberUpdate
    def put(self, request):
        try:
            user =  User.objects.get(id = request.user.id)
        except:
            raise AuthenticationFailed('invalid credentials...!')     
        serializer = MobileNumberUpdate(instance=user, data=request.data)
        if serializer.is_vaild():
            serializer.save()
            response = {
                'msg':'Your Mobile Number Changed Successfully',
                'staus':status.HTTP_200_OK
            }
            return Response(response)
        else:
            return Response(
                serializer.errors, status.HTTP_400_BAD_REQUEST
            )    


class SendMail_ChangeMail(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    def get(self, request):
        subject = 'Gmail Changing'
        message = 'Your Gmail updating link : http://localhost:8000/api/UserEmailUpdate/. Please use this link to change your Gmail'
        send_message(request.user.email, subject, message)
        return Response({
            'msg':f"Link is sended to your {request.user.email} please check it"
        })


class UserEmailUpdate(generics.GenericAPIView):
    permission_classes = [IsCurrentUser]
    serializer_class = EmailUpdate
    def put(self, request):
        try:
            user =  User.objects.get(registered_userid = request.data['Registerd_id'])
        except:
            raise AuthenticationFailed('invalid credentials...!') 
        serializer = EmailUpdate(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                'msg':'Gmail updated successfully',
                'status':status.HTTP_200_OK
            }
            return Response(response)
        else:
            return Response(
                serializer.errors, status.HTTP_400_BAD_REQUEST
            )  

class ForgotEmail(generics.GenericAPIView):
    permission_classes = [IsRegisteredUser]
    serializer_class = EmailRecoverySerailizer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if serializer.data.get('Registerd_id') is None and serializer.data.get('mobile_Number') is None:
                return Response({
                    'msg':'Fill any one field',
                    'status':status.HTTP_400_BAD_REQUEST
                })
            if serializer.data.get('Registerd_id'):
                try:
                    user = User.objects.get(registered_userid = serializer.data.get('Registerd_id'))
                except:
                    raise AuthenticationFailed('invalid credentials...!')     
                if user:
                    response = {
                        'msg':f'Your Gmail is {user.email}',
                        'status':status.HTTP_200_OK
                    }                
                    return Response(response)
                else:
                    response = {
                        'msg':'invalid credentials...!',
                        'status':status.HTTP_400_BAD_REQUEST
                    }
                    return Response(response)
    
            else:
                try:
                    user = User.objects.get(mobile_no = serializer.data.get('mobile_Number'))    
                except:
                    raise AuthenticationFailed('invalid credentials...!')     
                if user:
                        response = {
                            'msg':f'Your Gmail is {user.email}',
                            'status':status.HTTP_200_OK
                        }      
                        return Response(response)
                else:
                    response = {
                        'msg':'invalid credentials...!',
                        'status':status.HTTP_400_BAD_REQUEST
                    }
                    return Response(response)

        return Response(
                serializer.errors, status.HTTP_400_BAD_REQUEST
            )  

class forgottRegisterid(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = generateRegisterid
    def put(self, request):
        try:
            user = User.objects.get(email = request.data['email'])
        except:
            raise AuthenticationFailed('invalid credentials...!')     
          
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
             
            length=8
            letters = string.ascii_letters
            numbers = string.digits
            symbols = string.punctuation
            
            # combine the character set into one string
            characters = letters + numbers + symbols
            
            # generate a random string of the given length
            random_string = ''.join(random.choices(characters, k=length))
            user.registered_userid = random_string
            user.save()

            subject = 'New Register Id'
            message = f'Your New Register Id ---> {user.registered_userid}'
            send_message(user.email, subject, message)
            responces = {
                'msg':f'Successfully Generated Your new Register Id Please Check Your Mail ',
                'status':status.HTTP_200_OK
            }     
            return Response(responces)             
        return Response(
                serializer.errors, status.HTTP_400_BAD_REQUEST
            )     


class UserSerarch(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    serializer_class = UserSerializer
    def get(self, request):
        queryset = User.objects.all()
        search_param = self.request.query_params.get('q', None)
        if search_param is not None:
            queryset = queryset.filter(
                Q(mobile_no__contains=search_param)
            )
            if queryset.exists():
               username = ""
               mobile_no = ""
               for details in queryset:
                   username = details.username
                   mobile_no = details.mobile_no
               response = {
                   'username': username,
                   'mobile number': mobile_no
               }
               return Response(response)

            return Response({'message': 'No matching user found.'})


class show_users(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    serializer_class = [user_listSerializer]
    def get(self, request):
        user_list = []
        group_serializer = None
        current_user = UserSerializer(request.user).data
        
        user_conversation =  Conversation.objects.filter(Q(initiator=request.user) | Q(receiver=request.user))
        for info in user_conversation:

            if info.room_type == 'Group' or info.room_type == 'brodcast':
                group_serializer = user_listSerializer(instance=info, context={'request': request}).data
            else:
                serializer = user_listSerializer(instance=info,  context={'request': request})
                user_list.append(serializer.data)

        user_groups = Conversation.objects.filter(group_members__contains=[request.user.id])
        participant_groups = ShowUserParticipantGroupSerializer(user_groups, many=True, context={'request': request}).data

        data = {
            'user': current_user,
            'conversation_users': user_list,
            'created_groups': group_serializer ,
            'participant_groups': participant_groups
        }
        return Response(data)               
        
@api_view(['POST'])
@permission_classes([isLoginedUser])
def start_convo(request):
    data = request.data
    username = data.get('username', None)
    room_channelName = data.get('room_channelName', None)
    room_types = data.get('room_type', None)
    members = data.get('members_id', None)

    try:
        if username is None:
            for id in members:
                if not User.objects.filter(id=id):
                    raise AuthenticationFailed("You cannot chat with a non existent user")
                participant = None
                conversation = Conversation.objects.filter(room_name=room_channelName)
        
        else:        
            participant = User.objects.get(username=username)
            conversation = Conversation.objects.filter(Q(initiator=request.user, receiver=participant) |
                                    Q(initiator=participant, receiver=request.user))
       
    except User.DoesNotExist:
        return Response({'message': 'You cannot chat with a non existent user'})
    
    if conversation.exists():
        return redirect(reverse('get_conversation', args=(conversation[0].id,)))
    else:
        conversation = Conversation.objects.create(initiator=request.user, receiver=participant, room_name = generate_random_channel_name(), room_type = room_types, group_members = members)
        return Response(ConversationSerializer(instance=conversation).data)            


@api_view(['GET'])
@permission_classes([isLoginedUser])    
def get_conversation(request, convo_id):
    conversation = Conversation.objects.filter(id=convo_id)
    if not conversation.exists():
        return Response({'message': 'Conversation does not exist'})
    else:
        serializer = ConversationSerializer(instance=conversation[0])
        return Response(serializer.data)

global stop_calling 

Agora_data = []

@api_view(['POST'])
@permission_classes([isLoginedUser])
def Call_Handler(request):
    global stop_calling
    global Agora_data
    command = request.data.get("status", None)

    
    try:
        if command == None:
            details = Conversation.objects.filter(Q(initiator=request.user) | Q(receiver=request.user))
            for users in details:
                current_reciever = users.receiver if users.initiator.id == request.user.id else users.initiator
                break
          
            save_history = CallHistory.objects.create(
                caller_name = request.user,
                reciever_name = current_reciever

            )
            call_history_data = CallHistorySerializer(save_history).data
            reciever_details = UserSerializer(current_reciever).data

            # create call Notificaton
            create_callNotification = Notifications()
            create_callNotification.is_calling = True
            create_callNotification.calling_details = save_history 
            create_callNotification.conversation_id = users 
                       
            create_callNotification.save()

            channelName = generate_random_channel_name()
            appId = '7f7dd169c1904d2bba91d90c5b542a6a'
            appCertificate = 'fa63b0d376e84038978495d5dc1b886c'
            
            uid = random.randint(1, 500)
            expiration_time = 3600 * 24
            current_timestamp = time.time()
            privilegeExpiredTs = current_timestamp + expiration_time
            role = "user-published"
            token = RtcTokenBuilder.buildTokenWithAccount(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
            Agora_data = [channelName, token, uid]

            data = {
                "reciever_details":reciever_details, 
                "calling_details":call_history_data,
                "channel_name":channelName,
                "calling_status":"Calling....",
                'uid':uid,
                'token':token,
                "status":status.HTTP_200_OK
            }
            return Response(data) 

        elif command == "end":
            
            call_history_id = request.data.get("call_id", None)
                
            if call_history_id is not None:
                stop_calling = False
                update_call_history = CallHistory.objects.get(id=call_history_id)
                update_call_history.ended_time = timezone.now()
                update_call_history.save()


                calling_data = CallHistorySerializer(update_call_history).data
            
               
                return Response({"message":"Call_ended", "calling_details":calling_data}, status=status.HTTP_200_OK)
            else:
                raise AuthenticationFailed("INVALID CALL ID")  
        
        elif command == "accept":
            call_end_time = request.data.get("call_end_time", None)
            call_id = request.data.get("call_id", None)
            if call_id:
                call_data = CallHistory.objects.get(id = call_id)
                call_data.is_accept = True
                call_data.ended_time = call_end_time
                call_data.save()

                stop_calling = True

                #delete call notification
                notification_data = Notifications.objects.get(calling_details=call_data)
                notification_data.delete()
            
            else:
                raise AuthenticationFailed("INVALID CALL ID")
            data = {

                'token':Agora_data[1],
                'uid':Agora_data[2],
                'channel_name' : Agora_data[0]
            }

            return Response(data)

    except Conversation.DoesNotExist:
        return Response({"message": "No conversation found."}, status=status.HTTP_404_NOT_FOUND)      


@api_view(['GET'])
@permission_classes([isLoginedUser])
def Show_notification(request):

    notification_data = Notifications.objects.filter(Q(conversation_id__initiator=request.user) | Q(conversation_id__receiver=request.user))
    for update_status in notification_data:
        update_status.is_read = True
        update_status.save()
    serializer = NotificationsSerializer(notification_data, many=True, context={'request':request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([isLoginedUser])
def checker(request):
    global stop_calling
    stop_calling = None
    call_id = request.data.get("call_id", None)
    if call_id is not None:
        call_details = CallHistory.objects.get(id=call_id)
        start_time = time.time()
        while True:

            if stop_calling is False:
                
                #delete call notification
                notification_data = Notifications.objects.get(calling_details=call_details)
                notification_data.delete()

                return Response({"calling_status":"call_ended"})

            if stop_calling is True:

              serializer = CallHistorySerializer(call_details).data
              return Response({"calling_status": True, "call_history": serializer}, status=status.HTTP_200_OK)

            # check if 1 minute has elapsed
            elapsed_time = time.time() - start_time
            if elapsed_time >= 60:
                ended_time = timezone.now()
                call_details.ended_time = ended_time
                call_details.save()

                #delete call notification
                notification_data = Notifications.objects.get(calling_details=call_details)
                notification_data.delete()

                serializer = CallHistorySerializer(call_details).data

                return Response({"calling_status": "call_ended", "call_history": serializer}, status=status.HTTP_200_OK)

             
    else:
        raise AuthenticationFailed("INVALID CALL ID")    


@api_view(['GET'])
@permission_classes([isLoginedUser])
def Show_Call_History(request):
    # Retrieve the current user's call history
    call_history = CallHistory.objects.filter(Q(caller_name=request.user) | Q(reciever_name=request.user))

    # Serialize the call history data
    serializer = CallHistorySerializer(call_history, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)        


class User_Status_update(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    serializer_class  = [show_userStatus]
    def post(self, request):

        files_data = request.data.get('files', None)
        text_message = request.data.get('text_message', None)


        if files_data:    
            b64_regex = re.compile(r'^[A-Za-z0-9+/]*[A-Za-z0-9+/][A-Za-z0-9+/=]{0,2}$')
            if not b64_regex.match(files_data):
                raise ValueError("Invalid base64-encoded data")
            decoded_data = base64.b64decode(files_data)
            # it will recieve the file type
            file_type = get_file_type(decoded_data)  
            print(file_type)

            try:
                
                current_status = user_status.objects.get(user_id=request.user)
                
            except Exception as e:
                # print(e)
                pass


            extension = file_type.split('/')
            # Save the image file to media folder in the filesystem
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
                if current_status is not None:
                    current_status.pictures = image_file
                    current_status.save()
                else:    
                    current_status = user_status.objects.create(
                        user_id=request.user.id,
                        image_file=image_file
                    )
                serializer = show_userStatus(current_status).data
                return Response({
                    'message': 'Successfully saved',
                    'data': serializer,
                    'status':status.HTTP_200_OK
                })  
            elif extension[0] == 'video':
                video_extension = extension[1]
                # Genrete a random number to store image name as unique in database
                number = str(random.randint(10, 99))
                filename = 'video'+number+'.' + video_extension
                video_file = InMemoryUploadedFile(
                        file=BytesIO(decoded_data),
                        field_name='attachment',
                        name=filename,
                        content_type=extension,
                        size=len(decoded_data),
                        charset=None
                    )
                if current_status is not None:
                    current_status.pictures = video_file
                    current_status.save()
                else:    
                    current_status = user_status.objects.create(
                        user_id=request.user.id,
                        image_file=video_file
                    )
                # Return the URL of the saved image file
                serializer = show_userStatus(current_status).data
                return Response({
                    'message': 'Successfully saved',
                    'data': serializer,
                    'status':status.HTTP_200_OK
                })    
            else:
                #raise Exception based on unsupported files type
                 raise ValidationError('Unsupported file type!')    
        else:
            try:
                current_status = user_status.objects.get(user_id=request.user)
            except:
                pass
            if current_status is not None:
                current_status.text = text_message
                current_status.save()
            else:        
                current_status = user_status.objects.create(
                        user_id=request.user.id,
                        text=text_message
                    )

            serializer = show_userStatus(current_status).data
            return Response({
                'message': 'Successfully saved',
                'data': serializer,
                'status':status.HTTP_200_OK
            })  



class delete_status(generics.GenericAPIView):
    permission_classes = [isLoginedUser]
    serializer_class = [show_userStatus]
    def post(self, request):
        
    
        status_id = request.data.get('status_id', None)
        if status_id is not None:
            status = user_status.objects.get(status_id=status_id)
            status.delete()
            serializer = show_userStatus(status).data
        else:
            raise AuthenticationFailed("INVALID STATUS ID")
            
        return Response({"message": "Successfully deleted", "status":status.HTTP_200_OK})