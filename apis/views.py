from asyncio.log import logger
import imp
from sre_constants import SUCCESS
from urllib import response
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view,schema, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import *


from rest_framework.status import (
    HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_200_OK,
    )
from .serializers import UserSerializer, UserSigninSerializer
from .authentication import token_expire_handler, expires_in
import applogger
import datetime as dt
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import json    
import re
from django.conf import settings


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
            now = dt.datetime.now()
            time_change = expires_in(token)
            new_time = now + time_change
            expire_time = new_time.strftime("%y-%m-%d %H:%M:%S")
            logger.info("Logged In Successfully")
            return Response({
                'message': 'Logged In Successfully',
                # 'user': user_serialized.data, 
                'expires_in': expire_time,
                'token': token.key
            }, status=HTTP_200_OK)
    except:
        logger.exception("Login Failed")
        response = Response({'status':'Fail','message':'Login Failed'},status = HTTP_400_BAD_REQUEST)
        return response

@api_view(['POST'])
@schema(None)
@permission_classes((AllowAny,))  
def fileExtract(request):
    try:
        file = request.FILES['file']
        if file == '':
            return Response({'status': 'fail','message': 'No file selected'},status = HTTP_400_BAD_REQUEST)
        file_name = file.name
        if file_name.endswith('.pdf') or file_name.endswith('.PDF'):
            FileDetails.objects.create(
                file_name = file_name,
                file_field = file
            )
            lastFileInfo = FileDetails.objects.order_by('-file_id')[0]
            path = 'media/'+str(lastFileInfo.file_field)
            print(path)
            pages = convert_from_path(f'{path}', 500, poppler_path=settings.POPPLER_PATH)
            image_counter = 1

            for page in pages:
                filename = "media/store/page_"+str(image_counter)+".jpg"
                page.save(filename, 'JPEG')
                image_counter = image_counter + 1

            filelimit = image_counter-1
            outfile = "media/store/out_text.txt"
            f = open(outfile, "a")
            for i in range(1, filelimit + 1):
                filename = "media/store/page_"+str(i)+".jpg"
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
                text = str(((pytesseract.image_to_string(Image.open(filename)))))
                text = text.replace('-\n', '')	
                f.write(text)
            f.close()

            _dict = {}
            f = open('media/store/out_text.txt', 'r')
            page_content_list = []
            for line in f:
                page_content_list.append(line)
            for index,line in enumerate(page_content_list):
                if 'Order No' in line:
                    result = re.search('Order No: (.*) Item', line)
                    _dict['Job Number'] = int(result.group(1))
                    
                if 'Item' in line:
                    result = re.search('Item:(.*)', line)
                    item = result.group(1)
                    item = item.replace(" ", "")
                    _dict['Task Item Number'] = item
                
                if 'Qty Ordered:' in line:
                    _dict['Task Quantity'] = int(page_content_list[index+1].strip('\n'))
            extractedItem = ExtractionItems(job_number=_dict['Job Number'],task_item_number=_dict['Task Item Number'],task_quantity=_dict['Task Quantity'])
            extractedItem.save()
            logger.info("File extracted")
            return Response(_dict)
        
        else:
            return Response ({'status': 'Fail','message': 'Allowed file types are -> pdf, PDF'},status = HTTP_400_BAD_REQUEST)
    except:
        logger.exception("File Extraction failed")
        return Response({'status':'Fail','message':'File Extraction Failed'},status = HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@schema(None)
@permission_classes((AllowAny,))  
def getAllExtraction(self):
    try:
        extractionInfo = ExtractionItems.objects.all()
        extractionDict = {}
        extractionList = []
        for each_extraction in extractionInfo:
            extractionDict['Job Number'] = each_extraction.job_number
            extractionDict['Task Item Number'] = each_extraction.task_item_number
            extractionDict['Task Quantity'] = each_extraction.task_quantity
            extractionList.append(extractionDict.copy())
        logger.info("Extraction Information Fetched Successfully")
        return Response(extractionList)
    except:
        logger.exception("Extraction Information Could Not be Fetched")
        return Response({"status":"Fail","message":"Extraction Information Could not be Fetched"})


@api_view(['GET'])
@schema(None)
@permission_classes((AllowAny,))  
def getSingleExtraction(self,id):
    try:
        extractionInfo = ExtractionItems.objects.get(extracted_id=id)
        print(extractionInfo)
        extractionDict = {}
        extractionDict['Job Number'] = extractionInfo.job_number
        extractionDict['Task Item Number'] = extractionInfo.task_item_number
        extractionDict['Task Quantity'] = extractionInfo.task_quantity
        logger.info("Extraction Information Fetched Successfully")
        return Response(extractionDict)
    except:
        logger.exception("Extraction Information Could Not be Fetched")
        return Response({"status":"Fail","message":"Extraction Information Could not be Fetched"})

@api_view(['PUT'])
@schema(None)
@permission_classes((AllowAny,))  
def updateExtraction(request,id):
    try:
        extractionInfo = ExtractionItems.objects.get(extracted_id=id)
        extractionInfo.job_number = request.data.get("job_number")
        extractionInfo.task_item_number = request.data.get("task_item_number")
        extractionInfo.task_quantity = request.data.get("task_quantity")
        extractionInfo.save()
        logger.info("Extraction Information Updated Successfully")
        return Response({"status":"Success","message":"Extraction Information Updated Successfully"})
    except:
        logger.exception("Extraction Information Could Not be Update")
        return Response({"status":"Fail","message":"Extraction Information Could not be Updated"})
