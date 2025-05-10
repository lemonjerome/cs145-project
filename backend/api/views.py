from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import StoplightGroup, Stoplight
from geopy.distance import geodesic


@api_view(['POST'])
def post_route(request):
    try:
        # Parse the JSON body
        coordinates = request.data.get("coordinates", [])

        if not coordinates:
            return Response({"error": "No coordinates provided."}, status=400)

        # Find stoplight groups within a 10-meter radius
        stoplight_groups = []
        stoplights = []
        for coord in coordinates:
            lat, lng = coord
            for group in StoplightGroup.objects.all():
                group_location = (group.lat, group.lng)
                distance = geodesic((lat, lng), group_location).meters
                if distance <= 20 and group not in stoplight_groups:
                    stoplight_groups.append(group)

        # Collect only the stoplights that belong to the stoplight_groups 
        for group in stoplight_groups:
          group_stoplights = Stoplight.objects.filter(group=group)
          stoplights.extend(group_stoplights)

        # Serialize the stoplight group details and store them in the session
        serialized_groups = [
            {"groupID": group.id, "lat": group.lat, "lng": group.lng}
            for group in stoplight_groups
        ]

        serialized_stoplights = [
            {
                "stoplightID": stoplight.id,
                "groupID": stoplight.group.id, 
                "local_id": stoplight.local_id,
                "lat": stoplight.lat,
                "lng": stoplight.lng,
                "lookahead_lat": stoplight.lookahead_lat,
                "lookahead_lng": stoplight.lookahead_lng
            }
            for stoplight in stoplights
        ]

        request.session['stoplight_groups'] = serialized_groups
        request.session['stoplights'] = serialized_stoplights
        request.session.modified = True
        return Response({"message": "Coordinates processed successfully."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
def get_stoplights(request):
    # Retrieve the stoplight groups from the session
    stoplight_groups = request.session.get('stoplight_groups', [])
    return Response({"stoplight_groups": stoplight_groups}, status=200)
