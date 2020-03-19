import boto3
import datetime

from django.views import View
from django.http  import JsonResponse, HttpResponse

from my_settings  import AWS_SECRET_KEY, AWS_ACCESS_SECRET_KEY
from aws_settings import S3_URL, S3_BUCKET_NAME
from user.utils   import login_decorator

class ImageView(View):
    s3_client = boto3.client(
        's3',
        aws_access_key_id = AWS_SECRET_KEY,
        aws_secret_access_key = AWS_ACCESS_SECRET_KEY
    )
    S3_URL = S3_URL

    def _new_filename(self, user_id, index, file):
        infos = [
            user_id, 
            datetime.datetime.today().date(), 
            index,
            file.name
        ]
        new_filename = '-'.join(list(map(lambda info:str(info), infos)))
        return new_filename

    @login_decorator
    def post(self, request):
        img_urls = []
        limit = 5

        try:
            files = request.FILES.getlist('filename')

            img_index = 1
            for file in files:
                if img_index > limit:
                    break
                new_filename = self._new_filename(request.user.id, img_index, file)
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

