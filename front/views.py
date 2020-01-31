from django.shortcuts import render, get_object_or_404

from django.views.generic import TemplateView
from front.models import Menu, Page
from shopapp.models import Category
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def login(request):
    return render(request, 'enter.html')

@login_required
def home(request):
    return render(request, 'home.html')


class PageView(TemplateView):
    template_name = "page.html"

    def get(self, request, *args, **kwargs):
        p = get_object_or_404(Page, id=kwargs["id"])
        return render(request, self.template_name, {'page': p})
    

def menu(request):
    return {'topmenu': Menu.objects.filter(parent=None), 'Category_0': Category.objects.filter(parent=None)}