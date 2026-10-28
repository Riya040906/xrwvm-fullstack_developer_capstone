import json
import logging

from django.http import JsonResponse
from django.contrib.auth.models import User
from .restapis import get_request, analyze_review_sentiments, post_review
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate

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

def get_cars(request):
    if not CarMake.objects.exists():
        initiate()

    car_models = CarModel.objects.select_related("car_make")
    cars = [
        {
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name,
        }
        for car_model in car_models
    ]
    return JsonResponse({"CarModels": cars})

def get_dealerships(request, state="All"):
    endpoint = (
        "/fetchDealers"
        if state == "All"
        else f"/fetchDealers/{state}"
    )
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id):
    dealership = get_request(f"/fetchDealer/{dealer_id}")
    return JsonResponse({"status": 200, "dealer": dealership})


def get_dealer_reviews(request, dealer_id):
    reviews = get_request(f"/fetchReviews/dealer/{dealer_id}")

    if reviews is None:
        return JsonResponse(
            {"status": 502, "message": "Could not retrieve reviews"},
            status=502,
        )

    for review in reviews:
        result = analyze_review_sentiments(review["review"])
        review["sentiment"] = (
            result.get("sentiment", "neutral") if result else "neutral"
        )

    return JsonResponse({"status": 200, "reviews": reviews})


@csrf_exempt
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": 403, "message": "Unauthorized"},
            status=403,
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse(
            {"status": 400, "message": "Invalid review data"},
            status=400,
        )

    result = post_review(data)
    if result is None:
        return JsonResponse(
            {"status": 502, "message": "Error posting review"},
            status=502,
        )

    return JsonResponse({"status": 200, "review": result})