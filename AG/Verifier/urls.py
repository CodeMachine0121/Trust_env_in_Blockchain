"""AG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views


urlpatterns = [
    path("Parameters/", views.get_shortTerm_SystemParameters),
    path("Register/", views.registerReqeust),
    path("SessionKey/", views.sessionKey_exchange),
    path("updateSessionKey/", views.updateSessionKey),
    path("clientAvailability/", views.find_Client_available),
    path("quit_AG/", views.quit_this_AG),
    path('askTransactions/', views.createTransaction),
    path("payment/", views.makePayment),
    path("getBalance/", views.getContractBalance),
    path("getPublicKey/", views.getPubKeyFromRContract),
    path("getChameleonHash/", views.getChameleonHash),
]
