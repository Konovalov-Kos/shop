from django.shortcuts import render, get_object_or_404

from django.utils.crypto import pbkdf2
from django.contrib.auth import authenticate
from django.contrib.auth import login as d_login
from django.contrib.auth.forms import UserCreationForm, User


from django.views.generic import TemplateView
from front.models import Menu, Page
from shopapp.models import Category, Order
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

class LoginView(TemplateView):
    template_name = 'enter.html'

    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, 'enter.html', {'form': form})

    def post(self, request, *args, **kwargs):
        try:
            if User.objects.get(username=request.POST.get('username')):
                print('HERE1')
                if request.POST.get('password1') == request.POST.get('password2'):
                    print('HERE2')
                    old_user = User.objects.get(username=request.POST.get('username'))
                    print(old_user.password)
                    t_user = authenticate(username=request.POST.get('username'), password=request.POST.get('password1'))
                    if t_user:
                        d_login(request, t_user)
                        return redirect('home')
        except:
            pass
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print('VALID!')
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            d_login(request, user)
            return redirect('home')
        return render(request, self.template_name, {'form': form, 'msg': 'Поля заполнены неверно'})

def login(request):
    return render(request, 'enter.html')

@login_required
def home(request):
    person_orders = Order.objects.filter(user=request.user)
    return render(request, 'home.html', {'person_orders': person_orders})


class PageView(TemplateView):
    template_name = "page.html"

    def get(self, request, *args, **kwargs):
        p = get_object_or_404(Page, id=kwargs["id"])
        return render(request, self.template_name, {'page': p})
    

def menu(request):
    return {'topmenu': Menu.objects.filter(parent=None), 'Category_0': Category.objects.filter(parent=None)}