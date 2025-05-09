from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import StoplightGroup
from geopy.distance import geodesic


@api_view(['POST'])
def post_route(request):
    try:
        # Parse the JSON body
        coordinates = request.data.get("coordinates", [])

        if not coordinates:
            return Response({"error": "No coordinates provided."}, status=400)

        # Process the coordinates
        print("Received coordinates:", coordinates)

        # Find stoplight groups within a 10-meter radius
        stoplight_groups = []
        for coord in coordinates:
            lat, lng = coord
            for group in StoplightGroup.objects.all():
                group_location = (group.lat, group.lng)
                distance = geodesic((lat, lng), group_location).meters
                if distance <= 10 and group not in stoplight_groups:
                    stoplight_groups.append(group)

        # Serialize the stoplight group details and store them in the session
        serialized_groups = [
            {"groupID": group.id, "lat": group.lat, "lng": group.lng}
            for group in stoplight_groups
        ]
        request.session['stoplight_groups'] = serialized_groups

        return Response({"message": "Coordinates processed successfully."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
def get_stoplights(request):
    # Retrieve the stoplight groups from the session
    stoplight_groups = request.session.get('stoplight_groups', [])
    return Response({"stoplight_groups": stoplight_groups}, status=200)
