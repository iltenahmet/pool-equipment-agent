import json
import requests
from dotenv import load_dotenv
import os

BASE_URL = "https://candidate-onsite-study-srs-712206638513.us-central1.run.app"

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def search_products_klevu(term, page_size=5, page=1):
    try:
        endpoint = f"{BASE_URL}/api/search"
        params = {"term": term, "page_size": page_size, "page": page}

        response = requests.get(endpoint, params=params)
        response.raise_for_status()

        result = response.json()
        print("klevu returns " + json.dumps(result, indent=4))
        return result
    except requests.RequestException as e:
        print("Error in search_products_klevu:", str(e))
        return {"error": str(e)}


def search_products_azure(query, limit=3):
    try:
        endpoint = f"{BASE_URL}/api/products/search"
        params = {"query": query, "limit": limit}

        response = requests.get(endpoint, params=params)
        response.raise_for_status()

        result = response.json()
        print("azure returns " + json.dumps(result, indent=4))
        return result
    except requests.RequestException as e:
        print("Error in search_products_azure:", str(e))
        return {"error": str(e)}


def get_product_details(part_number):
    try:
        endpoint = f"{BASE_URL}/api/products/{part_number}"
        response = requests.get(endpoint)
        response.raise_for_status()

        result = response.json()
        print("product details api returns " + json.dumps(result, indent=4))
        return result
    except requests.RequestException as e:
        print("Error in get_product_details:", str(e))
        return {"error": str(e)}


def get_pricing(items: list):
    """
    Calls the /api/pricing endpoint to retrieve pricing information for multiple items.

    :param items: A list of dictionaries, each containing at least:
        {
          "item_code": "string",
        }
    :return: The JSON response from the API, which includes pricing information.
    """
    # For each item, automatically add the unit "EA"
    for item in items:
        item["unit"] = "EA"

    try:
        endpoint = f"{BASE_URL}/api/pricing"
        payload = {"items": items}
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Error in get_pricing:", str(e))
        return {"error": str(e)}


def search_stores(location: str, radius=50, page_size=5, page=1):
    """
    Search for stores near a location using coordinates.

    Parameters:
        latitude (float): Latitude coordinate (required).
        longitude (float): Longitude coordinate (required).
        radius (int, optional): Search radius in miles. Default is 50.
        page_size (int, optional): Number of results per page. Default is 10.
        page (int, optional): Page number. Default is 1.

    Returns:
        dict: The JSON response from the API, including search results and pagination info.
    """
    location_data = get_coordinates(location)
    try:
        endpoint = f"{BASE_URL}/api/stores/search"
        params = {
            "latitude": location_data["lat"],
            "longitude": location_data["lng"],
            "radius": radius,
            "page_size": page_size,
            "page": page,
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Error in search_stores:", str(e))
        return {"error": str(e)}


def get_coordinates(location):
    try:
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": location, "key": GOOGLE_API_KEY}
        geo_response = requests.get(geocode_url, params=params)
        geo_response.raise_for_status()
        data = geo_response.json()

        # Check if the geocoding API returned a valid response.
        if data.get("status") != "OK" or not data.get("results"):
            return {"error": "Location not found."}

        # Extract latitude and longitude from the first result.
        location_data = data["results"][0]["geometry"]["location"]
        return location_data
    except requests.RequestException as e:
        print("Error in geocoding:", str(e))
        return {"error": str(e)}


def get_store_details(store_id):
    """
    Get detailed information about a specific store.

    :param store_id: The identifier for the store.
    :return: The JSON response with store details.
    """
    try:
        endpoint = f"{BASE_URL}/api/stores/{store_id}"
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Error in get_store_details:", str(e))
        return {"error": str(e)}


def check_health():
    try:
        endpoint = f"{BASE_URL}/health"
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Error in get_store_details:", str(e))
        return {"error": str(e)}
