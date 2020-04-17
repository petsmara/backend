from django.views           import View
from django.http            import JsonResponse, HttpResponse

class HealthCheckView(View):
    def get(self, request):
        return HttpResponse(status=200)
        
