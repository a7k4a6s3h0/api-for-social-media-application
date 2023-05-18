from rest_framework import serializers
#from django.contrib.auth.models import User
from .models import *
import random
import string, os, re

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_photo', 'mobile_no')


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'mobile_no', 'profile_photo', 'registered_userid','gender')
        extra_kwargs = {'password': {'write_only': True}}
    
 
    def generate_random_string(self):
        # define the character set
        length=8
        letters = string.ascii_letters
        numbers = string.digits
        symbols = string.punctuation
        
        # combine the character set into one string
        characters = letters + numbers + symbols
        
        # generate a random string of the given length
        random_string = ''.join(random.choices(characters, k=length))
    
        return random_string

    def validate_email(self, value):
        """
        Ensure that the email is in a valid format
        """
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', value):
            raise serializers.ValidationError("Email address is not valid")
        return value

    def validate_password(self, value):
        """
        Ensure that the password meets minimum requirements
        """
        if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', value):
            raise serializers.ValidationError("Password must contain at least 8 characters, including both letters and digits")
        return value


    def validate_mobile_no(self, value):
        """
        Ensure that the mobile number is in a valid format
        """
        value = str(value)
        if not re.match(r'^\+?[0-9]{9,15}$', value):
            raise serializers.ValidationError("Mobile number is not valid")
        return int(value)


    def validate(self, data):
        """
        Ensure that the email and password are in a valid format
        """
        if 'email' in data:
            data['email'] = self.validate_email(data['email'])
        if 'password' in data:
            data['password'] = self.validate_password(data['password'])
        if 'mobile_no' in data:
            data['mobile_no'] = self.validate_mobile_no(data['mobile_no'])   
        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            instance.registered_userid = self.generate_random_string()
        instance.save()
        return instance        

class loginserilizer(serializers.Serializer):

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    Registerd_id = serializers.CharField(required=True)

    def validate_email(self, value):
        """
        Ensure that the email is in a valid format
        """
        
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', value):
            raise serializers.ValidationError("Email address is not valid")
        
        return value
        
    def validate_password(self, value):
        """
        Ensure that the password meets minimum requirements
        """
        if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', value):
            raise serializers.ValidationError("Password must contain at least 8 characters, including both letters and digits")
        return value

    def validate(self, data):
        """
        Ensure that the email and password are in a valid format
        """
        if 'email' in data:
            data['email'] = self.validate_email(data['email'])
        if 'password' in data:
           data['password'] = self.validate_password(data['password'])  
        return data


class OTPCHECKINGSerilizer(serializers.Serializer):
    user_entered_otp = serializers.IntegerField(required=True)
    Registerd_id = serializers.CharField(required = True)


class Forgottpasswordserilizer(serializers.Serializer):

    email = serializers.CharField(required=True)

    def validate_email(self, value):
        """
        Ensure that the email is in a valid format
        """
        
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', value):
            raise serializers.ValidationError("Email address is not valid")
        
        return value


    def validate(self, data):
        """
        Ensure that the email is in a valid format
        """
        if 'email' in data:
            data['email'] = self.validate_email(data['email'])
        
        return data

class ResetPasswordSerilizer(serializers.Serializer):

    password = serializers.CharField(required=True)

    def validate_password(self, value):
        """
        Ensure that the password meets minimum requirements
        """
        if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', value):
            raise serializers.ValidationError("Password must contain at least 8 characters, including both letters and digits")
        return value

    def validate(self, data):
        """
        Ensure that the password is in a valid format
        """
        
        if 'password' in data:
           data['password'] = self.validate_password(data['password'])  
        return data    

class ChangePasswordSerializer(serializers.Serializer):

    """
    Serializer for password change endpoint.
    """
    password = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)      
    Registerd_id = serializers.CharField(required=True)  

    def validate_password(self, value):
        """
        Ensure that the password meets minimum requirements
        """
        if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', value):
            raise serializers.ValidationError("Password must contain at least 8 characters, including both letters and digits")
        return value


    def validate(self, data):
        """
        Ensure that the password is in a valid format
        """
        
        if 'password1' in data:
           data['password1'] = self.validate_password(data['password1'])  
        if 'password2' in data:
           data['password2'] = self.validate_password(data['password2'])   
        return data 

class UserProfileAdd(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ( 'about', 'profile_photo')

    def update(self, instance, validated_data):
        instance.about = validated_data.get('about', instance.about)
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
        instance.save()
        return instance


class UserProfileEditClass(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username','about','profile_photo')

    def update(self, instance, validated_data):
       instance.username = validated_data.get('username', instance.username)
       instance.about = validated_data.get('about', instance.about)
       instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
       instance.save()
       return instance    

class MobileNumberUpdate(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('mobile_no',)

    def update(self, instance, validated_data):
        instance.mobile_no = validated_data.get('mobile_no', instance.mobile_no)
        instance.save()
        return instance          

class EmailUpdate(serializers.ModelSerializer):
    Registerd_id = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ('email','Registerd_id')

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance     

class EmailRecoverySerailizer(serializers.Serializer):
    Registerd_id = serializers.CharField(required=False)
    mobile_Number = serializers.IntegerField(required=False)   


class generateRegisterid(serializers.Serializer):
    email = serializers.CharField(required=True)


class MessageSaverSerializer(serializers.ModelSerializer):
    attachment = serializers.FileField(required=False)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'attachment', 'text', 'conversation_id']

    def create(self, validated_data):
        files_data = validated_data.pop('attachment', None)
        message = Message.objects.create(**validated_data)

        if files_data:
            message.attachment.save(files_data.name, files_data)
            message.save()

        return message


class user_listSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = ['room_type', 'room_name', 'start_time']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.room_type != 'Group' and instance.room_type != 'brodcast':
        
            if instance.initiator == self.context['request'].user:
                current_reciever = instance.receiver
            else:
                current_reciever = instance.initiator

            representation['users'] = UserSerializer(current_reciever).data
            representation['satus_add'] = show_userStatus(current_reciever).data
        else:
         
            counter =  1
            for id in  instance.group_members:
                if id != self.context['request'].user.id:
                    user = User.objects.get(id=id)
                    representation[f'group_member{counter}'] = UserSerializer(user).data
                    counter += 1
        return representation


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        exclude = ('conversation_id',)


class ConversationListSerializer(serializers.ModelSerializer):
    initiator = UserSerializer()
    receiver = UserSerializer()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['initiator', 'receiver', 'last_message']

    def get_last_message(self, instance):
        message = instance.message_set.first()
        return MessageSerializer(instance=message)


class ConversationSerializer(serializers.ModelSerializer):
    initiator = UserSerializer()
    receiver = UserSerializer()
    message_set = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ['initiator', 'receiver', 'room_type', 'room_name', 'start_time', 'message_set']


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['receiver'] is None:
            group_members = instance.group_members
            counter = 1
            for users in group_members:
                each_user = User.objects.filter(id = users)
                representation[f'group_member{counter}'] = UserSerializer(each_user, many=True).data
                counter += 1
            representation.pop('receiver')    
        return representation


class ShowUserParticipantGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = ['room_type', 'room_name', 'start_time']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        group_members = instance.group_members
        if instance.room_type != 'brodcast':
            counter = 1
            representation[f'group_member{counter}'] = UserSerializer(instance.initiator).data
            for users in group_members:
                if users != self.context['request'].user.id:
                    each_user = User.objects.filter(id = users)
                    counter += 1
                    representation[f'group_member{counter}'] = UserSerializer(each_user, many=True).data
                        
            return representation




class CallHistorySerializer(serializers.ModelSerializer):
    caller_name = serializers.StringRelatedField(read_only=True)
    reciever_name = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CallHistory
        fields = ('id', 'caller_name', 'reciever_name', 'started_time', 'ended_time','is_accept') 



class NotificationsSerializer(serializers.ModelSerializer):
    
    caller_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='conversation_id.receiver.username', read_only=True)
    conversation_id = serializers.IntegerField(source='conversation_id.id', read_only=True)
    is_calling = serializers.SerializerMethodField()

    class Meta:
        model = Notifications
        fields = ['id', 'caller_name', 'receiver_name', 'conversation_id', 'message', 'is_read', 'timestamp', 'is_calling']


    def to_representation(self, instance):
        if instance.is_calling:
            if instance.calling_details.caller_name != self.context['request'].user:
                # Get the latest call notification with is_calling=True
                latest_call_notification = Notifications.objects.filter(is_calling=True).latest('timestamp')
                # Use the calling_details of the latest call notification
                return {"calling_details": CallHistorySerializer(latest_call_notification.calling_details).data, "is_calling": True} 
            else:
                return None       
        else:
            return super(NotificationsSerializer, self).to_representation(instance)


class show_userStatus(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = user_status
        fields = ('id', 'user_id','created_time', 'videos', 'pictures', 'text')




