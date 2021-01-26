import json
import pickle
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import BusStop, RouteProgram, PlannedStopInterval, UserSavedRoutes, SaveLeapCardDetails
from datetime import datetime
from django.contrib.auth.hashers import make_password
# For leapcard information
from pyleapcard import *


# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user(request, *args, **kwargs):
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message = 'Clock in server current time is for check_user is: '
    return Response(data=message + date, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_stops(request, *args, **kwargs):
    bus_stops = BusStop.objects.all().values()
    return JsonResponse({'results': list(bus_stops)})


@api_view(['POST'])
def get_stop_by_id(request, *args, **kwargs):
    body = json.loads(request.body)
    stop_id = body.get('stop_id', None)
    bus_stops = BusStop.objects.filter(stop_id=stop_id).values()
    return JsonResponse({'results': list(bus_stops)})


@api_view(['POST'])
def get_routes_by_stop(request, *args, **kwargs):
    body = json.loads(request.body)
    stop_id = body.get('stop_id', None)
    route_program_set = list()
    if stop_id is not None:
        route_program_set = RouteProgram.objects.filter(stop_id=stop_id).values(
            'direction', 'line_id', 'program_number').distinct()
    return JsonResponse({'results': list(route_program_set)})


@api_view(['POST'])
def get_destinations(request, *args, **kwargs):
    content = []
    body = json.loads(request.body)
    line_id = body.get('line_id', None)
    direction = body.get('direction', None)
    program_number = body.get('program_number', None)

    if None in (line_id, direction, program_number):
        return JsonResponse({'results': content}, status=status.HTTP_400_BAD_REQUEST)

    route_program_set = RouteProgram.objects.filter(line_id=line_id,
                                                    direction=direction,
                                                    program_number__gt=program_number).values('stop_id').distinct()
    return JsonResponse({'results': list(route_program_set)})


def get_day_type(timestamp):
    weekday = datetime.fromtimestamp(timestamp).weekday()
    if weekday == 6:
        return 2
    elif weekday == 5:
        return 1
    else:
        return 0


def get_forecast_weather_info_by_time(dt_timestamp):
    endpoint = "http://api.openweathermap.org/data/2.5/forecast"
    key = "0cf61b96be769935320ea4795e6b0bab"
    id_dublin_city = "7778677"
    response = requests.get(
        url=endpoint,
        params={"id": id_dublin_city, "appid": key}
    )

    data = dict()
    weather = json.loads(response.text)
    for daily_weather in weather['list']:
        if daily_weather['dt'] > dt_timestamp:
            data = daily_weather
            break

    rain_1h = data.get('rain', {}).get('1h')
    rain_3h = data.get('rain', {}).get('3h')
    snow_1h = data.get('snow', {}).get('1h')
    snow_3h = data.get('snow', {}).get('3h')

    rain = 0
    if rain_1h is not None:
        rain = rain_1h
    if rain_3h is not None:
        rain = rain_3h

    snow = 0
    if snow_1h is not None:
        snow = snow_1h
    if snow_3h is not None:
        snow = snow_3h

    feels_like = data.get('main', {}).get('feels_like', 0)
    wind_speed = data.get('wind', {}).get('speed', 0)

    return feels_like, rain, snow, wind_speed


def predict_with_model(**parameters):
    path = "/home/student/models/"
    model_name = parameters['model_name']
    origin_id = parameters['origin_id']
    destination_id = parameters['destination_id']
    planned_interval = parameters['planned_interval']
    day_type = parameters['day_type']
    feels_like = parameters['feels_like']
    rain = parameters['rain']
    snow = parameters['snow']
    wind_speed = parameters['wind_speed']

    prediction_time = -1
    try:
        with open(path + model_name, 'rb') as handle:
            model = pickle.load(handle)
            data = [[origin_id, destination_id, planned_interval, day_type, feels_like, rain, snow, wind_speed]]
            result = model.predict(data)
            prediction_time = result[0][0]
    finally:
        return prediction_time


@api_view(['POST'])
def get_prediction_time(request, *args, **kwargs):
    data = dict()
    body = json.loads(request.body)
    timestamp = body.get('timestamp', None)
    origin_id = body.get('origin_id', None)
    destination_id = body.get('destination_id', None)
    line_id = body.get('line_id', None)
    direction = body.get('direction', None)

    if None in (timestamp, origin_id, destination_id, line_id, direction):
        return JsonResponse({'results': data}, status=status.HTTP_400_BAD_REQUEST)

    interval_set = PlannedStopInterval.objects.filter(origin_id=origin_id,
                                                      destination_id=destination_id,
                                                      line_id=line_id,
                                                      direction=direction).values('planned_interval')

    _feels_like, _rain, _snow, _wind_speed = get_forecast_weather_info_by_time(timestamp)
    data['feels_like'] = _feels_like
    data['rain'] = _rain
    data['snow'] = _snow
    data['wind_speed'] = _wind_speed
    data['model_name'] = f"{line_id}_{direction}.pkl"
    data['origin_id'] = int(origin_id)
    data['destination_id'] = int(destination_id)
    data['day_type'] = int(get_day_type(timestamp))
    data['planned_interval'] = -1
    if len(interval_set) > 0:
        data['planned_interval'] = interval_set[0].get('planned_interval', 0)
        return JsonResponse({'results': predict_with_model(**data)}, safe=False)
    else:
        return JsonResponse({'results': -1}, safe=False)


# Leap card information
@api_view(['GET'])
def get_leapcard_info(request, *args, **kwargs):
    result = {}
    leap_username = request.query_params.get('leap_username', '')
    leap_password = request.query_params.get('leap_password', '')
    if '' in (leap_username, leap_password):
        return JsonResponse({'results': []}, status=status.HTTP_400_BAD_REQUEST)
    session = LeapSession()
    try:
        session.try_login(leap_username, leap_password)
        leap_card_info = session.get_card_overview()
        leap_card_info = vars(leap_card_info)
        if leap_card_info:
            result['leap_card_info'] = leap_card_info
        else:
            return JsonResponse({'results': 'Please check your credential'}, status=status.HTTP_204_NO_CONTENT)

        # Get leap card history
        events = session.get_events()
        leapcard_history = []
        for item in events:
            item = vars(item)
            leapcard_history.append(item)
        result['leapcard_history'] = leapcard_history

        return JsonResponse({'results': result}, safe=False)
    except:
        return JsonResponse({'results': 'Please check your credential'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_leap_card(request, *args, **kwargs):
    request.body = json.loads(request.body)
    leap_user_email = request.body['username']
    leap_password = request.body['password']
    user_reg_email = request.user

    if '' in (leap_user_email, leap_password):
        return JsonResponse({'results': 'Sorry invalid request'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        isFound = SaveLeapCardDetails.objects.filter \
            (leap_user_email=leap_user_email
             ).values()

        if len(isFound) > 0:
            return JsonResponse({'results': 'User is already registered'}, status=status.HTTP_302_FOUND)

        # commented out make_password as to retrive hashing password is not working need to work on this.
        save_leap_info = SaveLeapCardDetails.objects.create \
                (
                leap_user_email=leap_user_email,
                leap_password=leap_password,
                user_reg_email=user_reg_email
            )
        if save_leap_info:
            return JsonResponse({'results': 'Leap details saved'}, status=status.HTTP_201_CREATED)
        return JsonResponse({'results': 'Invalid request, please try again'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print('e', e)
    return JsonResponse({'results': 'Invalid request, please try again'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leap_auth_detail(request, *args, **kwargs):
    user_reg_email = request.user
    leap_auth_detail = SaveLeapCardDetails.objects.filter(user_reg_email=user_reg_email).values()
    try:
        if len(leap_auth_detail) > 0:
            result = {}
            leap_username = leap_auth_detail[0]['leap_user_email']
            leap_password = leap_auth_detail[0]['leap_password']
            if '' in (leap_username, leap_password):
                return JsonResponse({'results': []}, status=status.HTTP_400_BAD_REQUEST)
            session = LeapSession()
            session.try_login(leap_username, leap_password)
            leap_card_info = session.get_card_overview()
            leap_card_info = vars(leap_card_info)
            if leap_card_info:
                result['leap_card_info'] = leap_card_info
            else:
                return JsonResponse({'results': 'Please check your credential'}, status=status.HTTP_204_NO_CONTENT)

            # Get leap card history
            events = session.get_events()
            leapcard_history = []
            for item in events:
                item = vars(item)
                leapcard_history.append(item)
            result['leapcard_history'] = leapcard_history

            return JsonResponse({'results': result}, safe=False)
        else:
            return JsonResponse({'results': []}, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return JsonResponse({'results': 'Invalid request, please try again'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def remove_leap_authinfo(request, *args, **kwargs):
    user_reg_email = request.user
    try:
        isDelete = SaveLeapCardDetails.objects.filter \
            (user_reg_email=user_reg_email,
             ).delete()
        if isDelete[0] != 0:
            return JsonResponse({'results': 'Leap details removed successfully'}, status=status.HTTP_200_OK)

        return JsonResponse({'results': 'Invalid request, please try again'}, status=status.HTTP_400_BAD_REQUEST)


    except Exception as e:
        print('ee', e)
        return JsonResponse({'results': 'Invalid request, please try again'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_route(request, *args, **kwargs):
    if request.method == 'GET':
        return get_fav_route(request)
    elif request.method == 'POST':
        return add_fav_route(request)
    elif request.method == 'DELETE':
        return delete_fav_route(request)


def add_fav_route(request):
    user_email = request.user
    request.body = request.body.decode('UTF-8')
    request.body = json.loads(request.body)
    origin_stop_id = request.body['origin_stop_id']
    origin_stop_name = request.body['origin_stop_name']
    destination_stop_id = request.body['destination_stop_id']
    destination_stop_name = request.body['destination_stop_name']
    line_id = request.body['line_id']
    direction = request.body['direction']
    if '' in (user_email, origin_stop_id, destination_stop_id, line_id, direction):
        return JsonResponse({'results': 'Sorry invalid request some parameter missing'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        isFound = UserSavedRoutes.objects.filter \
            (user_email=user_email,
             origin_stop_id=origin_stop_id,
             destination_stop_id=destination_stop_id
             ).values()

        if len(isFound) > 0:
            return JsonResponse({'results': 'Selected route is already saved'}, status=status.HTTP_302_FOUND)

        save_route = UserSavedRoutes.objects.create \
                (
                user_email=user_email,
                origin_stop_id=origin_stop_id,
                origin_stop_name=origin_stop_name,
                destination_stop_id=destination_stop_id,
                destination_stop_name=destination_stop_name,
                line_id=line_id,
                direction=direction,
            )
        if save_route:
            return JsonResponse({'results': 'Route is saved'}, status=status.HTTP_201_CREATED)
        return JsonResponse({'results': 'Invalid request, please try again'}, status=status.HTTP_400_BAD_REQUEST)


    except Exception as e:
        print('ee', e)
        return JsonResponse({'results': 'Invalid request, please try again'}, status=status.HTTP_400_BAD_REQUEST)


def delete_fav_route(request):
    user_email = request.user
    request.body = request.body.decode('UTF-8')
    request.body = json.loads(request.body)
    origin_stop_id = request.body['origin_stop_id']
    destination_stop_id = request.body['destination_stop_id']
    if '' in (user_email, origin_stop_id, destination_stop_id):
        return JsonResponse({'results': 'Sorry invalid request some parameter missing'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        isDelete = UserSavedRoutes.objects.filter \
            (user_email=user_email,
             origin_stop_id=origin_stop_id,
             destination_stop_id=destination_stop_id
             ).delete()
        if isDelete[0] != 0:
            return JsonResponse({'results': 'Selected route removed successfully'}, status=status.HTTP_200_OK)

        return JsonResponse({'results': 'Invalid request, please try again'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print('ee', e)
        return JsonResponse({'results': 'Invalid request, please try again'}, status=status.HTTP_400_BAD_REQUEST)


def get_fav_route(request):
    user_email = request.user
    saved_routes = UserSavedRoutes.objects.filter(user_email=user_email).values()
    if saved_routes:
        return JsonResponse({'results': list(saved_routes)}, safe=False)

    return JsonResponse({'results': []}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_real_time_information(request, *args, **kwargs):
    stop_id = request.query_params.get('stopId', '')
    response = requests.get('https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid=' + stop_id +'&format=json')
    if response:
        return JsonResponse({'results':  response.json()}, safe=False)
    return JsonResponse({'results': []}, status=status.HTTP_204_NO_CONTENT)
