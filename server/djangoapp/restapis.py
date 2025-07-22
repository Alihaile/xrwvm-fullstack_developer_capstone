import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

backend_url = os.getenv("backend_url", default="http://localhost:3030")
sentiment_analyzer_url = os.getenv("sentiment_analyzer_url",
                                   default="http://localhost:5050/")
searchcars_url = os.getenv(
    'searchcars_url', default="http://localhost:3050/")


def get_request(endpoint, **kwargs):
    """
    Perform a GET request to the backend with optional query parameters.
    """
    request_url = f"{backend_url}{endpoint}"
    if kwargs:
        query_string = urlencode(kwargs)
        request_url = f"{request_url}?{query_string}"

    print(f"GET from {request_url}")
    try:
        response = requests.get(request_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Network exception occurred: {e}")
        return None


def analyze_review_sentiments(text):
    """
    Send a review text to the sentiment
    analysis service and return the result.
    """
    request_url = f"{sentiment_analyzer_url}analyze/{text}"
    try:
        response = requests.get(request_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Sentiment analysis error: {e}")
        return None


def post_review(data_dict):
    """
    Post review data to the backend review insertion endpoint.
    """
    request_url = f"{backend_url}/insert_review"
    try:
        response = requests.post(request_url, json=data_dict)
        response.raise_for_status()
        print(response.json())
        return response.json()
    except requests.RequestException as e:
        print(f"Review post error: {e}")
        return None


def searchcars_request(endpoint, **kwargs):
    params = ""
    if (kwargs):
        for key, value in kwargs.items():
            params = params+key + "=" + value + "&"

    request_url = searchcars_url+endpoint+"?"+params

    print("GET from {} ".format(request_url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except:
        # If any error occurs
        print("Network exception occurred")
    finally:
        print("GET request call complete!")
