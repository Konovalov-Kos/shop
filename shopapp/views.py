from django.http import Http404, JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Category, Product, Order, ProductsInOrders, News
import json, os, base64
from liqpay.liqpay import LiqPay

class MainView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat_pc = get_object_or_404(Category, name='Ноутбуки, ПК')
        cat_phones = get_object_or_404(Category, name='Смартфоны')
        cat_kitchen = get_object_or_404(Category, name='Техника для кухни')
        cat_childs = get_object_or_404(Category, name='Товары для детей')
        context['cat_pc'] = cat_pc
        context['cat_phones'] = cat_phones
        context['cat_kitchen'] = cat_kitchen
        context['cat_childs'] = cat_childs
        context['prods'] = Product.objects.order_by('-add_date')[:8]
        context['novosti'] = News.objects.order_by('-news_date')[:2]
        return context


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
        if "action" in request.POST:
            if request.POST['action'] == "add_to_cart":
                if "cart" not in request.session:
                    request.session["cart"] = {}
                if "product_id" in request.POST:
                    if request.session["cart"].get(request.POST["product_id"]):
                        request.session["cart"][request.POST.get("product_id")] += 1
                    else:
                        request.session["cart"][request.POST.get("product_id")] = 1

        else:
            return redirect(reverse("one_product", kwargs=kwargs))
        return render(request, self.template_name, self.get_context_data(**kwargs))

class KorzinaView(TemplateView):
    template_name = 'korzina.html'

    def get(self, request, *args, **kwargs):
        if not request.session.get("cart"):
            return render(request, self.template_name)
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
        request.session['summary_p'] = str(summary_p)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        if request.body and "action" not in request.POST:
            deistvie = json.loads(request.body)
            if request.session["cart"]:
                if str(deistvie.get('id')) in request.session["cart"]:
                    k = int(request.session["cart"][str(deistvie.get('id'))])
                else:
                    proverka1 = get_object_or_404(Product, pk=deistvie.get('id'))
                    k = 1
                    request.session['cart'][str(deistvie.get('id'))] = 1
            else:
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
        return redirect(reverse("korzina", kwargs=kwargs))


class PayView(TemplateView):
    template_name = 'oplata.html'

    def get(self, request, *args, **kwargs):
        if request.session.get('order'):
            order_id = request.session['order'][0]
            order_price = str(request.session['order'][1])
            if Order.objects.filter(pk=int(order_id)).exists():
                liqpay = LiqPay(os.getenv('LIQPAY_PUBLIC_KEY'), os.getenv('LIQPAY_PRIVATE_KEY'))
                params = {
                    'action': 'pay',
                    'amount': str(order_price),
                    'currency': 'UAH',
                    'description': f'Payment for order № {order_id}',
                    'order_id': str(order_id),
                    'version': '3',
                    'sandbox': 1, # sandbox mode, set to 1 to enable it
                    'server_url': 'https://localhost:8008/payback/', # url to callback view
                }
                signature = liqpay.cnb_signature(params)
                data = liqpay.cnb_form(params)
                st = data.find('value=')+7
                data2 = data[st:]
                end = data2.find('/>')-1
                data = data2[:end]
                signature = data2[end:]
                st = signature.find('value=')+7
                signature = signature[st:]
                end = signature.find('/>') - 1
                signature = signature[:end]
                return render(request, self.template_name, {'signature': signature, 'data': data})
        raise Http404

@method_decorator(csrf_exempt, name='dispatch')
class PayCallbackView(TemplateView):
    def post(self, request, *args, **kwargs):
        liqpay = LiqPay(os.getenv('LIQPAY_PUBLIC_KEY'), os.getenv('LIQPAY_PRIVATE_KEY'))
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        sign = liqpay.str_to_sign(os.getenv('LIQPAY_PRIVATE_KEY') + data + os.getenv('LIQPAY_PRIVATE_KEY'))
        if sign == signature:
            print('callback is valid')
        response = ''
        base64.b64decode(data, response)
        print('callback data', response)
        if request.session.get('order'):
            request.session.pop('order')
        return HttpResponse()

class OrderView(TemplateView):
    template_name = 'order.html'

    def get(self, request, *args, **kwargs):
        if not request.session.get("cart") or not request.session.get("summary_p"):
            return redirect(reverse('korzina'))
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        if not request.session.get("cart") or not request.session.get("summary_p"):
            return redirect(reverse('korzina'))
        if 'action' in request.POST and 'phone' in request.POST and 'adress' in request.POST:
             if request.POST['phone'] != '' and request.POST['adress'] != 0:
                phone = request.POST['phone'].replace(' ', '')
                if phone[0] == '+':
                    phone = request.POST['phone'][1:]
                if phone.isnumeric():
                    new_order = Order.objects.create(
                                                        user=request.user,
                                                        delivery_adress=request.POST.get('adress'),
                                                        phone=phone,
                                                        comment=request.POST.get('comment'),
                                                        price_to_pay=float(request.session['summary_p'])
                                                    )
                    for product_id, kvo in request.session["cart"].items():
                        prod = get_object_or_404(Product, pk=product_id)
                        ProductsInOrders.objects.create(order=new_order, product=prod, kvo=kvo, price=prod.price)
                    request.session.pop('cart')
                    request.session.pop('summary_p')
                    request.session['order'] = [new_order.id, new_order.price_to_pay]
                    return redirect(reverse('oplata'))

        return redirect(reverse('order'))

class OrderdetailView(TemplateView):
    template_name = 'one_order.html'

    def get(self, request, *args, **kwargs):
        ord = get_object_or_404(Order, pk=kwargs["id"])
        prods_in_order = ProductsInOrders.objects.filter(order=ord)
        return render(request, self.template_name, {'prods_in_order': prods_in_order, 'order': ord})

class ProductsView(TemplateView):
    template_name = 'show_prods.html'