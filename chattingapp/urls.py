from django.urls import path, re_path
from . import views 
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny


schema_view = get_schema_view(
   openapi.Info(
      title="Api Documentaion for Social Media Application",
      default_version='v1',
      description="no",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[AllowAny],
)


urlpatterns = [
    # api documention url
    
    # re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api_documentation/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api_docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Template rendering Urls

    path('',views.register),
    path('userlogin',views.user_login, name='userlogin'),
    path('otp',views.otp, name='otp'),
    path("home",views.user_home, name="home"),
    path("chat_room",views.chat_room,name="chat_room"),
    path("chat/<str:room_name>/", views.room,name="chat"),
    path("calling",views.user_calling,name="calling"),
    path("accept",views.user_accept,name="accept"),
    path("video_call", views.video_call,name="video_call"),
    path("notificationul", views.notification_testing, name="notificationul"),

    # class based view  functions url

    path('api/register/', views.RegisterAPI.as_view(), name='register'),
    path('api/Userlogin/', views.User_LoginAPI.as_view(), name='Userlogin'),
    path('api/Newtoken/', views.RefreshAPIVIEW.as_view(), name='Newtoken'),
    path('api/otpchecking/', views.OTP_checking.as_view(), name='otpchecking'),
    path('api/forgottpassword/', views.ForgottPassword.as_view(), name='forgottpassword'),
    path('api/changepassword/', views.ChangePassword.as_view(), name='changepassword'),
    path('api/resetpassword/', views.ResetPassword.as_view(), name='resetpassword'),
    path('api/UserProfileView/', views.userProfileView.as_view(), name='UserProfileView'),
    path('api/UserProfileAdd/',views.UserProfileadd.as_view(), name='UserProfileAdd'),
    path('api/UserProfileEdit/',views.userProfileEdit.as_view(), name='UserProfileEdit'),
    path('api/MobileNumberUpdate/',views.UserMobile_Number_Update.as_view(), name='MobileNumberUpdate'),
    path('api/SendMail/',views.SendMail_ChangeMail.as_view(), name='SendMail'),
    path('api/UserEmailUpdate/',views.UserEmailUpdate.as_view(), name='UserEmailUpdate'),
    path('api/MailRecovery/',views.ForgotEmail.as_view(), name='MailRecovery'),
    path('api/newRegisterid/',views.forgottRegisterid.as_view(), name='newRegisterid'),
    path('api/userSearch/',views.UserSerarch.as_view(), name='userSearch'),
    path('api/show_user/',views.show_users.as_view(), name='show_user'),
    path('api/status/',views.User_Status_update.as_view(),name='status'),
    path('api/statusDelete/',views.delete_status.as_view(), name='statusDelete'),
    
    # function based views function url

    path('api/start/', views.start_convo, name='start_convo'),
    path('api/get_conversation/<int:convo_id>', views.get_conversation, name='get_conversation'),
    path('api/call_connecting/', views.Call_Handler, name="call_connecting"),
    path('api/get_notification/', views.Show_notification, name="get_notification"),
    path('api/status_checker/',views.checker, name="status_checker"),
    path('api/call_history/',views.Show_Call_History, name="call_history"),
    
]

