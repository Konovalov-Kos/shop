from django.http import Http404, JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Category, Product
import json


class MainView(TemplateView):
    template_name = "index.html"

class CategoriesView(TemplateView):
    template_name = 'categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = get_object_or_404(Category, pk=kwargs["id"])
        if cat.has_childs:
            context['cat'] = cat
        else:
            self.template_name = 'product_list.html'
            context['cat'] = cat
        return context

class ProductView(TemplateView):
    template_name = 'one_full_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prod = get_object_or_404(Product, pk=kwargs["id"])
        context['product'] = prod
        return context

    def post(self, request, *args, **kwargs):
        print(request.POST)
        if "action" in request.POST:
            if request.POST['action'] == "add_to_cart":
                if "cart" not in request.session:
                    request.session["cart"] = {}
                if "product_id" in request.POST:
                    if request.session["cart"].get(request.POST["product_id"]):
                        request.session["cart"][request.POST.get("product_id")] += 1
                    else:
                        request.session["cart"][request.POST.get("product_id")] = 1
                    print("BLABLABLA", request.session["cart"])

        else:
            return redirect(reverse("one_product", kwargs=kwargs))
        return render(request, self.template_name, self.get_context_data(**kwargs))

class KorzinaView(TemplateView):
    template_name = 'korzina.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["prod_in_cart"] = []
        prods_incart = Product.objects.filter(id__in=request.session["cart"].keys())
        summary_p = 0
        for key, val in request.session["cart"].items():
            for obj in prods_incart:
                if str(obj.id) == str(key):
                    summary_p += obj.price*int(val)
                    context["prod_in_cart"].append({'tovar': obj, 'kol_vo': val, 'total_price': obj.price*int(val)})
        context['summary_price'] = summary_p
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        if request.body:
            deistvie = json.loads(request.body)
            print("MI TYT")
            if request.session["cart"]:
                print(deistvie.get('id'))
                if str(deistvie.get('id')) in request.session["cart"]:
                    k = int(request.session["cart"][str(deistvie.get('id'))])
                else:
                    proverka1 = get_object_or_404(Product, pk=deistvie.get('id'))
                    k = 1
                    request.session['cart'][str(deistvie.get('id'))] = 1
            else:
                print("BLAKAKAKAKAK")
                raise Http404
            if deistvie.get('do') == 'increase':
                request.session["cart"][str(deistvie.get('id'))] = k + 1
            elif deistvie.get('do') == 'decrease':
                if k - 1 == 0:
                    request.session["cart"].pop(str(deistvie.get('id')))
                else:
                    request.session["cart"][str(deistvie.get('id'))] = k - 1
            elif deistvie.get('do') == 'remove':
                request.session["cart"].pop(str(deistvie.get('id')))
            return JsonResponse({'status': True})

        if "action" in request.POST:
            if request.POST['action'] == "modify_count":
                for keys in request.POST:
                    if "prod_" in keys:
                        tovar_id = keys[5:]
                        if Product.objects.filter(pk=tovar_id).exists():
                            request.session["cart"][tovar_id] = request.POST[keys]
        print(request.POST.getlist("prod[]"))
        return redirect(reverse("korzina", kwargs=kwargs))