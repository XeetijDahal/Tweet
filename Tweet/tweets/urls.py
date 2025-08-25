from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.tweet_list,name="tweet_list"),
    path('create/',views.tweet_create,name="tweet_create"),
    path('<int:tweet_id>/delete/',views.tweet_delete,name="tweet_delete"),
    path('<int:tweet_id>/edit/',views.tweet_edit,name="tweet_edit"),
    path('register/',views.register,name="register"),
    path('tweet/<int:pk>/', views.tweet_detail, name='tweet_detail'),
    path('login/',auth_views.LoginView.as_view(template_name='registration/login.html'),name="login"),
    path('my-tweets/', views.my_tweets, name='my_tweets'),
    path('tweet/<int:tweet_id>/react/', views.toggle_reaction, name='tweet_react'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('change-password/', views.custom_password_change, name='change_password'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)