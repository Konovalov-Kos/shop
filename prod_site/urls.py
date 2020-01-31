"""prod_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from shopapp.views import MainView, CategoriesView, ProductView, KorzinaView
from front.views import PageView, login, home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view()),
    path('page/<int:id>', PageView.as_view()),
    path('category/<int:id>', CategoriesView.as_view(), name='one_category'),
    path('product/<int:id>', ProductView.as_view(), name="one_product"),
    path('', include('social_django.urls', namespace='social')),
    path("login/", login, name="login"),
    path("home/", home, name="home"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("cart/", KorzinaView.as_view(), name="korzina"),

]
