import os
import pytesseract
import re
import json
import docx2txt
import pandas
import uuid
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from api.models import File
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from pdf2image import convert_from_bytes
from PIL import Image
from spire.doc.common import *
from spire.doc import *
from django.conf import settings


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_id="Upload CV",
        operation_description="Upload a batch of CVs and extract the useful information from them to a excel sheet",
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="Document to be uploaded",
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")
        emails = []
        phone_numbers = []
        for file in files:
            File.objects.create(file=file)
            if file.name.endswith(".pdf"):
                media_dir = settings.MEDIA_ROOT
                file_path = os.path.join(media_dir, file.name)
                uploaded_file = open(file_path, "rb")
                pdf_images = convert_from_bytes(uploaded_file.read())
                extracted_text = ""
                for page in pdf_images:
                    extracted_text += pytesseract.image_to_string(page)
                phone_number = re.findall(
                    r"\b(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
                    extracted_text,
                )
                email = re.findall(r"[\w\.-]+@[\w\.-]+", extracted_text)
                emails.append(email[0])
                phone_numbers.append(phone_number[0])
            elif file.name.endswith((".docx")):
                extracted_text = docx2txt.process(file)
                phone_number = re.findall(
                    r"\b(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
                    extracted_text,
                )
                email = re.findall(r"[\w\.-]+@[\w\.-]+", extracted_text)
                emails.append(email[0])
                phone_numbers.append(phone_number[0])
            elif file.name.endswith(".doc"):
                media_dir = settings.MEDIA_ROOT
                file_path = os.path.join(media_dir, file.name)
                docx_filename = os.path.splitext(file.name)[0] + ".docx"
                docx_path = os.path.join(media_dir, docx_filename)
                document = Document()
                document.LoadFromFile(file_path)
                document.SaveToFile(docx_path, FileFormat.Docx)
                document.Close()
                extracted_text = docx2txt.process(docx_path)
                phone_number = re.findall(
                    r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s-]?\d{3,5}[\s-]?\d{4}\b",
                    extracted_text,
                )
                email = re.findall(r"[\w\.-]+@[\w\.-]+", extracted_text)
                emails.append(email[0])
                phone_numbers.append(phone_number[0])
            elif file.name.endswith((".png", ".jpg", ".jpeg")):
                image_text = pytesseract.image_to_string(Image.open(file))
                phone_number = re.findall(
                    r"\b(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
                    image_text,
                )
                email = re.findall(r"[\w\.-]+@[\w\.-]+", image_text)
                emails.append(email[0])
                phone_numbers.append(phone_number[0])
            else:
                return Response(
                    {"error": "Unsupported file format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        data = {
            "Phone": phone_numbers,
            "Email": emails,
        }
        records_folder = os.path.join(settings.MEDIA_ROOT, "records")
        if not os.path.exists(records_folder):
            os.makedirs(records_folder)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output_{timestamp}_{uuid.uuid4().hex}.xlsx"
        file_path = os.path.join(records_folder, filename)
        df = pandas.DataFrame(data)
        df.to_excel(file_path, index=False)
        download_url = os.path.join(settings.MEDIA_URL, "records", filename)
        return Response({"download_url": download_url}, status=status.HTTP_201_CREATED)
