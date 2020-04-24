import json
import uuid
import boto3
import time

from django.views import View
from django.http  import JsonResponse, HttpResponse
from PIL          import Image, ImageOps, ExifTags
from io           import BytesIO

from user.utils   import login_decorator
from aws_settings import S3_URL, S3_BUCKET_NAME, AWS_SECRET_KEY, AWS_ACCESS_SECRET_KEY

class ImageView(View):
    s3_client = boto3.client(
        's3',
        aws_access_key_id = AWS_SECRET_KEY,
        aws_secret_access_key = AWS_ACCESS_SECRET_KEY
    )
    S3_URL = S3_URL

    def _new_filename(self, user_id, index):
        infos = [
            uuid.uuid3(uuid.NAMESPACE_URL, str(user_id)), 
            time.time(),
            index
        ]
        new_filename = '-'.join(list(map(lambda info:str(info), infos)))
        return new_filename

    def _resize_file(self, file):
        standard_size = (500, 500)
        
        image = Image.open(file)
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            exif = dict(image._getexif().items())
        
            if exif[orientation] == 3:
                image=image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image=image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image=image.rotate(90, expand=True)
        
        except:
            pass

        image = image.resize(standard_size, Image.ANTIALIAS)
        image = image.convert("RGB")
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        return image_file

    @login_decorator
    def post(self, request):
        limit = int(request.POST.get('limit')) if request.POST.get('limit') else 5
        img_urls = []

        try:
            files = request.FILES.getlist('filename')
            if not files:
                return JsonResponse({'message':'EMPTY_FILE'}, status = 204)

            img_index = 1
            for file in files:
                if img_index > limit:
                    break
                new_filename = self._new_filename(request.user.id, img_index)
                resized_image = self._resize_file(file)
                self.s3_client.upload_fileobj(
                    resized_image,
                    S3_BUCKET_NAME,
                    new_filename,
                    ExtraArgs={
                         "ContentType": file.content_type
                    }
                )
                img_urls.append(self.S3_URL + new_filename)
                img_index += 1

            return JsonResponse({'images':img_urls}, status = 200)

        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)

