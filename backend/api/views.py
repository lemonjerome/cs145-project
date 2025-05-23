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

        # Find stoplight groups within a 20-meter radius
        stoplight_groups = []
        stoplights = []
        closest_stoplights = {}  # Store the closest stoplight for each group

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

            # Find the closest stoplight for this group
            if group_stoplights:
                closest_stoplight = min(
                    group_stoplights,
                    key=lambda s: geodesic(
                        (group.lat, group.lng), (s.lookahead_lat, s.lookahead_lng)
                    ).meters
                )
                closest_stoplights[group.id] = {
                    "stoplightID": closest_stoplight.id,
                    "lookahead_lat": closest_stoplight.lookahead_lat,
                    "lookahead_lng": closest_stoplight.lookahead_lng,
                }

        # Serialize the stoplight group details and store them in the session
        serialized_groups = [
            {"groupID": group.id, "lat": group.lat, "lng": group.lng}
            for group in stoplight_groups
        ]

        serialized_stoplights = [
            {
                "stoplightID": stoplight.id,
                "groupID": stoplight.group.id,
                "lookahead_lat": stoplight.lookahead_lat,
                "lookahead_lng": stoplight.lookahead_lng,
            }
            for stoplight in stoplights
        ]

        request.session["stoplight_groups"] = serialized_groups
        request.session["stoplights"] = serialized_stoplights
        request.session["closest_stoplights"] = closest_stoplights  # Store closest stoplights
        request.session.save()
        return Response({"success": True})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
def get_stoplights(request):
    # Retrieve the stoplight groups from the session
    stoplight_groups = request.session.get('stoplight_groups', [])
    stoplights = request.session.get('stoplights', [])
    return Response({"stoplight_groups": stoplight_groups, "stoplights": stoplights}, status=200)
