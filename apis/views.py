from asyncio.log import logger
import imp
from urllib import response
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view,schema, permission_classes
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import *


from rest_framework.status import (
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_200_OK,
    )
from .serializers import UserSerializer, UserSigninSerializer
from .authentication import token_expire_handler, expires_in
import applogger
# from datetime import datetime, timezone, timedelta


@api_view(['GET'])
@permission_classes((AllowAny,))  
def home(self):
    return Response({"status":"Success","message":"Home Page of Thbred Project"},status=HTTP_200_OK)

@api_view(['POST'])
@schema(None)
@permission_classes((AllowAny,))  
def userRegistration(request):
    try:
        username = request.data.get("username")
        password = request.data.get("password")
        if (username is None and password is None):
            return Response({"status":"Fail","message":"error in payload"},status = HTTP_400_BAD_REQUEST)
        user = User(
            username = username
        )
        user.set_password(password)
        user.is_active = True
        user.save()
        logger.info("User Registered successfully!")
        return Response({"status":"Success","message":"User Registered Successfully!"},status = HTTP_200_OK)
    except:
        logger.exception("User Registered Failed!")
        return Response({"status":"Fail","message":"User Registered Failed"},status = HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@schema(None)
@permission_classes((AllowAny,))  
def userAuthentication(request):
    try:
        username = request.data.get("username")
        password = request.data.get("password")
        logger.info(f"username : {username}")
        logger.info(f"password : {password}")
        
        if (username is None and password is None):
            return Response({'status':'Fail','message':'error in payload'},status = HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if not user:
            logger.info("Invalid Credentials ")
            return Response({'status':'Fail','message': 'Invalid Credentials'},status=HTTP_401_UNAUTHORIZED)
        else:
            token, _ = Token.objects.get_or_create(user = user)
            is_expired, token = token_expire_handler(token)
            # user_serialized = UserSerializer(user)
            logger.info("Logged In Successfully")
            return Response({
                'message': 'Logged In Successfully',
                # 'user': user_serialized.data, 
                'expires_in': expires_in(token),
                'token': token.key
            }, status=HTTP_200_OK)
    except:
        logger.exception("Login Failed")
        response = Response({'status':'Fail','message':'Login Failed'},status = HTTP_400_BAD_REQUEST)
        return response

@api_view(['GET'])
def getUserInfo(self):
    try:
        print("coming here")
        userInfo = User.objects.all()
        print(userInfo)
        return Response({"status":"Success","message":"User Information Fetched Successfully"})
    except:
        logger.exception("User Info Could Not be Fetched")
        return Response({"status":"Fail","message":"User Information Could not be Fetched"})


@api_view(['POST'])
@schema(None)
@permission_classes((AllowAny,))  
def fileUpload(request):
    file = request.FILES['file']

    # if (file is None ):
    #     return Response({"status":"0","message":"upload a file"})

    # if file is not None:
    #     return Response({"status":"1","message":"succesfully uploaded"})
    # else:
    #     return Response({"status":"0","message":"error in upload"})

    try:
        FileSave.objects.create(
        file_field = file
        )
        return Response({"status":1 ,"message":"succesfully uploaded"})
    except :
        print("hi")
        # pass
        # return Response({"status":"0","message":"upload a file"})
    
	
	    

