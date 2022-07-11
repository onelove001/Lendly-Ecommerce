from django.shortcuts import *
from django.urls import reverse
from django.views.generic import *
from .forms import BillingForm
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


# Payment
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import requests
import socket


class home(ListView):
    model = Product
    template_name = "App/home.html"


class product_details(DetailView):
    model = Product
    template_name = "App/product_details.html"


@login_required
def add_to_cart(request, product_id):
    item  = get_object_or_404(Product, id=product_id)
    order_item=Cart.objects.get_or_create(item=item, user=request.user, purchase=False)
    order_qs = Order.objects.filter(user = request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.order_items.filter(item=item).exists():
            order_item[0].quantity += 1
            order_item[0].save()
            messages.info(request, "Item quantity is updated")
            return redirect("cart")
        else:
            order.order_items.add(order_item[0])
            messages.info(request, "A new item has been added to your cart")
            return redirect("cart")
    else:
        order = Order(user=request.user)
        order.save()
        order.order_items.add(order_item[0])
        messages.info(request, "A new item has been added to your cart")
        return redirect("cart")


@login_required
def cart(request):
    cart = Cart.objects.filter(user = request.user, purchase = False)
    orders = Order.objects.filter(user=request.user, ordered=False)
    if cart.exists() and orders.exists():
        order = orders[0]
        context = {"order":order, "orders":orders, "cart":cart}
        return render(request, "App/cart.html", context)
    else:
        messages.warning(request, "No item in cart! ")
    return render(request, "App/cart.html", context = {})


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(Product, id=item_id)
    order_qs = Order.objects.filter(user = request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.order_items.filter(item=item).exists():
            order_item = Cart.objects.filter(item = item, user=request.user, purchase=False)[0]
            order.order_items.remove(order_item)
            order_item.delete()
            messages.success(request, "Item successfully Removed")
            return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.error(request, "Item not in your cart")
            return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.error(request, "No active order")
        return redirect("home")


@login_required
def increase_item(request, item_id):
    item = get_object_or_404(Product, id=item_id)
    order_qs = Order.objects.filter(user = request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.order_items.filter(item=item).exists():
            order_item = Cart.objects.filter(item = item, user = request.user, purchase=False)[0]
            order_item.quantity += 1
            order_item.save()
            messages.success(request, f"{item.name} Item Updated")
            return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.error(request, f"{item.name} Not In your cart")
            return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.success(request, f"You don't have an active order")
        return redirect("home")


@login_required
def decrease_item(request, item_id):
    item = get_object_or_404(Product, id=item_id)
    order_qs = Order.objects.filter(user = request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.order_items.filter(item=item).exists():
            order_item = Cart.objects.filter(item = item, user = request.user, purchase=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.success(request, f"{item.name} Item successfully Updated")
                return redirect(request.META.get("HTTP_REFERER"))
            else:
                order.order_items.remove(order_item)
                order_item.delete()
                messages.error(request, f"{item.name} Has been removed")
                return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.error(request, f"{item.name} Not In your cart")
            return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.success(request, f"You don't have an active order")
        return redirect("home")



@login_required
def payment_checkout(request):  
    saved_address = BillingAddress.objects.get_or_create(user = request.user)
    saved_address  = saved_address[0]
    form = BillingForm(instance = saved_address)
    if request.method=="POST":
        form = BillingForm(data = request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated billing address successfully")
            form = BillingForm(instance=saved_address)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order_items = order_qs[0].order_items.all()
    order_total = order_qs[0].get_total_amount()
    return render(request, "App/payment_checkout.html", context = {"saved_address":saved_address, "form":form, "order_items":order_items, "order_total":order_total})



@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user = request.user)
    savedd_address = saved_address[0]
    if not saved_address[0].is_fully_filled():
        messages.info(request, "Please complete shipping address")
        return redirect("payment_checkout")
    if not request.user.profile.is_fully_filled():
        messages.info(request, "Please complete profile details")
        return redirect("change_profile")

    STORE_ID = "abcco62cb2aa9aec48"
    API_KEY = "abcco62cb2aa9aec48@ssl"
    status_url = request.build_absolute_uri(reverse("complete_payment_success"))
    mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=STORE_ID, sslc_store_pass=API_KEY)
    mypayment.set_urls(success_url=status_url, fail_url=status_url, cancel_url=status_url, ipn_url=status_url)
    order_qs = Order.objects.filter(user=request.user, ordered = False)
    order_items=order_qs[0].order_items.all()
    orders=order_qs[0].order_items.count()
    order_total = order_qs[0].get_total_amount()
    mypayment.set_product_integration(total_amount=Decimal(order_total), currency='USD', product_category='Mixed', 
    product_name=order_items, num_of_item=orders, shipping_method='YES', product_profile='None')
    
    user = request.user
    mypayment.set_customer_info(name=user.proifle.last_name, email=user.email, address1=user.profile.address, 
    address2='', city=user.profile.city, postcode=user.profile.zip_code, country=user.profile.country, phone=user.profile.phone)

    mypayment.set_shipping_info(shipping_to=user.profile.full_name, address=savedd_address.address, city=savedd_address.city, 
    postcode=savedd_address.zip_code, country=savedd_address.country)
    response_data = mypayment.init_payment()
    print(response_data)
    return redirect(response_data["GatewayPageURL"])



@csrf_exempt
@login_required
def complete_payment_success(request):
    if request.method == "POST" or request.method=="post":
        payment_data = request.POST
        status = payment_data['status']
        if status == "VALID":
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request, "Payment Successfull")
            return redirect("purchased", kwargs={"val_id":val_id, "tran_id":tran_id})
        elif status == "failed":
            messages.warning(request, "Payment Failed, Please try again")
        
    return render(request, "App/complete_payment_success.html", {})


@login_required
def purchased(request, val_id, tran_id):
    order_qs = Order.objects.filter(user = request.user, ordered = False)
    order = order_qs[0]
    order_id = tran_id
    order.ordered = True
    order.order_id = order_id
    order.payment_id = val_id
    order.save()
    cart_items = Cart.objects.filter(user = request.user, purchased=False)
    for item in cart_items:
        item.purchased = True
        item.save()
    return redirect("home")


@login_required
def orders(request):
    try:
        orders = Order.objects.filter(user = request.user, ordered = True)
        context = {"orders":orders}
    except:
        messages.warning(request, "You do not have an active order")
        return redirect("home")
    return render(request, "App/orders.html", context)