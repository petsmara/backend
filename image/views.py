import json
import uuid
import boto3
import time

from django.views import View
from django.http  import JsonResponse, HttpResponse

from user.utils   import login_decorator
from aws_settings import S3_URL, S3_BUCKET_NAME
from my_settings  import AWS_SECRET_KEY, AWS_ACCESS_SECRET_KEY

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
                self.s3_client.upload_fileobj(
                    file,
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

