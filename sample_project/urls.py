from django.urls import include, path


urlpatterns = [
    path('api/', include('turngeneration.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
