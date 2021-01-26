from django.urls import path, include
from api import views

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('checkuser/', views.check_user),
    path('stops', views.get_stops),
    path('stops/', views.get_stop_by_id),
    path('routes/', views.get_routes_by_stop),
    path('destinations/', views.get_destinations),
    path('prediction/', views.get_prediction_time),
    path('leapcard/', views.get_leapcard_info),
    path('saveleapinfo/', views.save_leap_card),
    path('getleapauthinfo/', views.get_leap_auth_detail),
    path('removeleapauthinfo/', views.remove_leap_authinfo),
    path('realtimeinfo/', views.get_real_time_information),

    # Favorite routes
    path('favorite-routes/', views.favorite_route),
]
