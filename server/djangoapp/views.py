import json
import logging

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'POST method required'},
            status=405
        )

    try:
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')

        if not username or not password:
            return JsonResponse(
                {'error': 'Username and password are required'},
                status=400
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return JsonResponse({
                'userName': username,
                'status': 'Authenticated'
            })

        return JsonResponse({
            'userName': username,
            'status': 'Authentication Failed'
        }, status=401)

    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
def logout_request(request):
    logout(request)
    return JsonResponse({'status': 'Logged out'})

@csrf_exempt
def registration(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")

        if not username or not password:
            return JsonResponse(
                {"error": "Username and password are required"},
                status=400,
            )

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        User.objects.create_user(
            username=username,
            password=password,
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            email=data.get("email", ""),
        )
        return JsonResponse(
            {"userName": username, "status": "Registered"},
            status=201,
        )
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)