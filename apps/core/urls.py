from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('quote-request/', views.QuoteRequestView.as_view(), name='quote_request'),
    path('thank-you/', views.ThankYouView.as_view(), name='thank_you'),
    path('api/ip-lookup/', views.ip_lookup_proxy, name='ip_lookup'),
] 