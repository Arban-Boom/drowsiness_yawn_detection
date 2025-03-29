# from django.urls import path
# from .views import home, home_view, login_view, register_view, logout_view, run_drowsiness_detection

# urlpatterns = [
#     path('', home, name='index'),
#     path('home/', home_view, name='home'),
#     path('login/', login_view, name='login'),
#     path('register/', register_view, name='register'),
#     path('logout/', logout_view, name='logout'),
#     path('run/', run_drowsiness_detection, name='run_drowsiness'),
# ]
from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("driver_dashboard/", views.driver_view, name="driver_dashboard"),
    path('update-settings/', views.update_settings, name='update_settings'),
    path('toggle-monitoring/', views.toggle_monitoring, name='toggle_monitoring'),
    path('update-profile/', views.update_profile, name='update_profile'),

]
