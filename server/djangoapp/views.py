import json
import logging
# from datetime import datetime

# from django.contrib import messages
from django.contrib.auth import login, logout as django_logout, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse   # HttpResponse, HttpResponseRedirect
# from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review
from .restapis import get_request, analyze_review_sentiments, post_review, searchcars_request

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Code for the view
def get_inventory(request, dealer_id):
    data = request.GET
    if (dealer_id):
        if 'year' in data:
            endpoint = "/carsbyyear/"+str(dealer_id)+"/"+data['year']
        elif 'make' in data:
            endpoint = "/carsbymake/"+str(dealer_id)+"/"+data['make']
        elif 'model' in data:
            endpoint = "/carsbymodel/"+str(dealer_id)+"/"+data['model']
        elif 'mileage' in data:
            endpoint = "/carsbymaxmileage/"+str(dealer_id)+"/"+data['mileage']
        elif 'price' in data:
            endpoint = "/carsbyprice/"+str(dealer_id)+"/"+data['price']
        else:
            endpoint = "/cars/"+str(dealer_id)
 
        cars = searchcars_request(endpoint)
        return JsonResponse({"status": 200, "cars": cars})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})
    return JsonResponse({"status": 400, "message": "Bad Request"})


def get_cars(request):
    """
    Initialize data if needed and return all car models with their makes.
    """
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = [
        {"CarModel": model.name, "CarMake": model.car_make.name}
        for model in car_models
    ]

    return JsonResponse({"CarModels": cars})


@csrf_exempt
def login_user(request):
    """
    Handle user login using JSON payload.
    """
    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"userName": username,
                                 "status": "Authenticated"})

        return JsonResponse({"userName": username,
                             "status": "Unauthorized"}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def logout(request):
    """
    Handle user logout and return empty username.
    """
    django_logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
def registration(request):
    """
    Register a new user with JSON payload.
    """
    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")
        first_name = data.get("firstName")
        last_name = data.get("lastName")
        email = data.get("email")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"userName": username,
                                 "error": "Already Registered"})

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)
        return JsonResponse({"userName": username,
                             "status": "Authenticated"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def get_dealerships(request, state="All"):
    """
    Get a list of dealerships, optionally filtered by state.
    """
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id):
    """
    Get details of a single dealer by ID.
    """
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    endpoint = f"/fetchDealer/{dealer_id}"
    dealership = get_request(endpoint)
    return JsonResponse({"status": 200, "dealer": dealership})


def get_dealer_reviews(request, dealer_id):
    """
    Get all reviews for a given dealer, with sentiment analysis.
    """
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Bad Request"})

    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)

    for review in reviews:
        text = review.get('review', '')
        response = analyze_review_sentiments(text)
        if (response):
            review['sentiment'] = response.get('sentiment', 'unknown')
        else:
            review['sentiment'] = 'unknown'

    return JsonResponse({
            "status": 200,
            "reviews": reviews
         })


@csrf_exempt
def add_review(request):
    """
    Post a new review to the backend service.
    """
    try:
        data = json.loads(request.body)
        post_review(data)
        return JsonResponse({"status": 200})
    except Exception as e:
        logger.error(f"Review post failed: {e}")
        return JsonResponse({"status": 401,
                             "message": "Error in posting review"})
