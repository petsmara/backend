import boto3

from django.views import View
from django.http  import JsonResponse, HttpResponse

from my_settings  import AWS_SECRET_KEY, AWS_ACCESS_SECRET_KEY
from aws_settings import S3_URL, S3_BUCKET_NAME

class ImageView(View):
    s3_client = boto3.client(
        's3',
        aws_access_key_id = AWS_SECRET_KEY,
        aws_secret_access_key = AWS_ACCESS_SECRET_KEY
    )
    S3_URL = S3_URL

    def post(self, request):
        file = request.FILES['filename']
        
        self.s3_client.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            file.name,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
        img_url = self.S3_URL + str(file)

        return JsonResponse({'image':img_url}, status = 200)
