from django.http import JsonResponse

def health_check(request):
  return JsonResponse({"status":"Api Is Up!"})
