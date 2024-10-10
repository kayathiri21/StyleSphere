from django.shortcuts import render, get_object_or_404,redirect
from .models import MainCategory, Product,SubCategory,Cart, CartItem ,Order,OrderItem
from django.core.mail import send_mail
from django.contrib import messages
from .forms import ContactForm, SignUpForm
from django.contrib.auth import login as auth_login,logout
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from datetime import timedelta
from django.contrib.auth.decorators import login_required
import razorpay
# Create your views here.
def home(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)  # Ensure the cart exists
        cart_count = cart.items.count() 
    # Get the current date and time
    now = timezone.now()

    # Get trendy products (with discounts)
    trendy_products = Product.objects.filter(discount_price__isnull=False, is_active=True, stock__gt=0).order_by('-discount_price')[:10]

    # Get just arrived products (created within the last 7 days)
    just_arrived_products = Product.objects.filter(created_at__gte=now - timedelta(days=7), is_active=True, stock__gt=0).order_by('-created_at')[:10]
    # main_categories = MainCategory.objects.prefetch_related('subcategories').all()
    context = {
        'trendy_products': trendy_products,
        'just_arrived_products': just_arrived_products,
        'main_categories': MainCategory.objects.all(),
        'cart_count': cart_count
       
    }
   
   
    return render(request,'app/home.html', context)
def shop(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)  # Ensure the cart exists
        cart_count = cart.items.count() 
    products = Product.objects.filter(is_active=True)  # Only active products
    
 
    
    context = {
        'products': products,
        'main_categories': MainCategory.objects.all(),
        'cart_count': cart_count

    }
    return render(request, 'app/shop.html', context)
def search(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)  # Ensure the cart exists
        cart_count = cart.items.count() 
    query = request.GET.get('query')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.none()
    main_categories = MainCategory.objects.all()
    return render(request, 'app/search.html', {
        'products': products,
        'query': query,
        'main_categories': main_categories,
        'cart_count': cart_count
    })
def detail(request, product_slug): 
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)  # Ensure the cart exists
        cart_count = cart.items.count() 
    product = get_object_or_404(Product, slug=product_slug)
    context = {
        'product': product,
        'main_categories': MainCategory.objects.all(),
        'cart_count': cart_count
    }
    return render(request, 'app/detail.html', context)
def contact(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)  # Ensure the cart exists
        cart_count = cart.items.count() 
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email (replace with your settings)
            send_mail(
                f"Query from {name}: {subject}",
                message,
                email,
               [settings.DEFAULT_FROM_EMAIL], # Replace with your recipient email
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # Redirect after POST
    else:
        form = ContactForm()
    context = {
        'form': form,
        'main_categories': MainCategory.objects.all(),
        'cart_count': cart_count
     }
    return render(request,'app/contact.html',context)
# @login_required
# def add_to_cart(request, slug):
#     product = get_object_or_404(Product, slug=slug, is_active=True)

#     if not product.is_stock_available():
#         messages.error(request, f"Sorry, {product.name} is out of stock.")
#         return redirect('shop')

#     # Get or create the user's cart
#     cart, created = Cart.objects.get_or_create(user=request.user)

#     # Handle the quantity (default to 1 if not specified)
#     quantity = int(request.POST.get('quantity', 1))

#     # Check if the product is already in the cart
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

#     if not created:
#         if cart_item.quantity + quantity <= product.stock:
#             cart_item.quantity += quantity
#             cart_item.save()
#             messages.success(request, f"Updated quantity of {product.name} in your cart.")
#         else:
#             messages.warning(request, f"Cannot add more of {product.name}. Stock limit reached.")
#     else:
#         if quantity <= product.stock:
#             cart_item.quantity = quantity
#             cart_item.save()
#             messages.success(request, f"Added {product.name} to your cart.")
#         else:
#             messages.warning(request, f"Cannot add {quantity} of {product.name}. Only {product.stock} in stock.")

#     return redirect('cart')



@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user) 
    cart_items = cart.items.all()
    total_price = cart.get_total_price()  # Calculate total price from the cart items
    
    shipping_cost= Decimal('50.00')  # Flat shipping charge
    cart_count = 0
    if request.user.is_authenticated:
         cart, created = Cart.objects.get_or_create(user=request.user)  # Ensure the cart exists
         cart_count = cart.items.count() 
    context =  {
        'cart_items': cart_items,
        'total_price': cart.get_total_price(),
        'shipping_cost':shipping_cost,
        'cart_count': cart_count,  # Pass the cart count to the template
        'main_categories': MainCategory.objects.all(),
    }
    
    return render(request, 'app/cart.html',context )


@login_required
@require_POST
def update_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    action = request.POST.get('action')
    item_id = request.POST.get('item_id')

    try:
        cart_item = CartItem.objects.get(cart=cart, id=item_id)
    except CartItem.DoesNotExist:
        messages.error(request, "Item not found in your cart.")
        return redirect('cart')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Increased quantity of {cart_item.product.name}.")
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f"Decreased quantity of {cart_item.product.name}.")
        else:
            cart_item.delete()
            messages.success(request, f"Removed {cart_item.product.name} from your cart.")
    elif action == 'remove':
        cart_item.delete()
        messages.success(request, f"Removed {cart_item.product.name} from your cart.")

    return redirect('cart')


# @login_required
# def checkout(request):
#     cart, created = Cart.objects.get_or_create(user=request.user)  # Ensure the cart exists
#     cart_items = cart.items.select_related('product').all()  # Get cart items
#     total_price = cart.get_total_price()  # Calculate total price from the cart items
#     shipping_cost = 10  # Flat shipping cost

#     if request.method == 'POST':
#         # Collect billing info from form
#         billing_first_name = request.POST.get('billing_first_name')
#         billing_last_name = request.POST.get('billing_last_name')
#         billing_email = request.POST.get('billing_email')
#         billing_mobile = request.POST.get('billing_mobile')
#         billing_address_line1 = request.POST.get('billing_address_line1')
#         billing_address_line2 = request.POST.get('billing_address_line2', '')
#         billing_country = request.POST.get('billing_country')
#         billing_city = request.POST.get('billing_city')
#         billing_state = request.POST.get('billing_state')
#         billing_zip_code = request.POST.get('billing_zip_code')

#         # Validate required billing fields
#         required_billing_fields = [
#             billing_first_name, billing_last_name, billing_email, billing_mobile,
#             billing_address_line1, billing_country, billing_city, billing_state, billing_zip_code
#         ]

#         if not all(required_billing_fields):
#             messages.error(request, "Please fill in all required billing fields.")
#             return redirect('checkout')

#         # Check if shipping address is different
#         shipto = request.POST.get('shipto')
#         if shipto:
#             shipping_first_name = request.POST.get('shipping_first_name')
#             shipping_last_name = request.POST.get('shipping_last_name')
#             shipping_email = request.POST.get('shipping_email', billing_email)
#             shipping_mobile = request.POST.get('shipping_mobile', billing_mobile)
#             shipping_address_line1 = request.POST.get('shipping_address_line1')
#             shipping_address_line2 = request.POST.get('shipping_address_line2', '')
#             shipping_country = request.POST.get('shipping_country')
#             shipping_city = request.POST.get('shipping_city')
#             shipping_state = request.POST.get('shipping_state')
#             shipping_zip_code = request.POST.get('shipping_zip_code')

#             # Validate required shipping fields
#             required_shipping_fields = [
#                 shipping_first_name, shipping_last_name, shipping_email, shipping_mobile,
#                 shipping_address_line1, shipping_country, shipping_city, shipping_state, shipping_zip_code
#             ]

#             if not all(required_shipping_fields):
#                 messages.error(request, "Please fill in all required shipping fields.")
#                 return redirect('checkout')
#         else:
#             # If shipping address is the same as billing
#             shipping_first_name = billing_first_name
#             shipping_last_name = billing_last_name
#             shipping_email = billing_email
#             shipping_mobile = billing_mobile
#             shipping_address_line1 = billing_address_line1
#             shipping_address_line2 = billing_address_line2
#             shipping_country = billing_country
#             shipping_city = billing_city
#             shipping_state = billing_state
#             shipping_zip_code = billing_zip_code

#         # Create the Order
#         order = Order.objects.create(
#             user=request.user,
#             billing_first_name=billing_first_name,
#             billing_last_name=billing_last_name,
#             billing_email=billing_email,
#             billing_mobile=billing_mobile,
#             billing_address_line1=billing_address_line1,
#             billing_address_line2=billing_address_line2,
#             billing_country=billing_country,
#             billing_city=billing_city,
#             billing_state=billing_state,
#             billing_zip_code=billing_zip_code,
#             shipping_first_name=shipping_first_name,
#             shipping_last_name=shipping_last_name,
#             shipping_email=shipping_email,
#             shipping_mobile=shipping_mobile,
#             shipping_address_line1=shipping_address_line1,
#             shipping_address_line2=shipping_address_line2,
#             shipping_country=shipping_country,
#             shipping_city=shipping_city,
#             shipping_state=shipping_state,
#             shipping_zip_code=shipping_zip_code,
#             total_amount=total_price + shipping_cost,
#             created_at=timezone.now(),
#             status='Pending',
#         )

#         # Create OrderItems with selected color and size
#         for cart_item in cart_items:
#             selected_color = request.POST.get(f'color_{cart_item.id}', 'N/A')  # Default to 'N/A' if not provided
#             selected_size = request.POST.get(f'size_{cart_item.id}', 'N/A')    # Default to 'N/A' if not provided
#             OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.quantity,
#                 selected_color=cart_item.selected_color,  # Copy the color
#                 selected_size=cart_item.selected_size,  
#             )
#             # Optionally, reduce stock
#             cart_item.product.stock -= cart_item.quantity
#             cart_item.product.save()

#         # Clear the cart after the order is placed
#         cart.items.all().delete()

#         # Optional: Send confirmation email
#         try:
#             send_mail(
#                 f"Order Confirmation - #{order.id}",
#                 f"Thank you for your order, {order.billing_first_name}!\n\n"
#                 f"Your order ID is {order.id}.\n\n"
#                 f"Total Amount: Rs{order.total_amount}\n"
#                 f"Status: {order.status}",
#                 settings.DEFAULT_FROM_EMAIL,
#                 [order.billing_email],
#                 fail_silently=False,
#             )
#         except Exception as e:
#             # Log the exception or handle it as needed
#             print(f"Error sending email: {e}")

#         messages.success(request, "Your order has been placed successfully!")
#         return redirect('order_confirmation', order_id=order.id)  # Redirect to order confirmation page

#     context = {
#         'cart_items': cart_items,
#         'total_price': total_price,
#         'total_price_with_shipping': total_price + shipping_cost,
#         'main_categories': MainCategory.objects.all(),
#     }
#     return render(request, 'app/checkout.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            
            return redirect('home')  # Redirect to home after successful registration
        
    else:
        form = SignUpForm()

    context = {
        'form': form,
        
    }
    return render(request, 'app/signup.html', context)

def logout_view(request):
    logout(request)  # This logs the user out by terminating the session
    return redirect('home')



def subcategory_products(request, subcategory_slug):
    subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
    products = Product.objects.filter(sub_category=subcategory, is_active=True)
    context = {
        'products': products,
        'main_categories': MainCategory.objects.all(),
        'current_subcategory': subcategory,  # For optional breadcrumb or header
    }
    return render(request, 'app/shop.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'main_categories': MainCategory.objects.all(),
    }
    return render(request, 'app/order_confirmation.html', context)
@login_required
def my_orders(request):
    """
    Display the current and previous orders of the logged-in user.
    """
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)  # Ensure the cart exists
        cart_count = cart.items.count() 
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    current_orders = orders.filter(status='Pending')
    previous_orders = orders.exclude(status='Pending')
    
    context = {
        'current_orders': current_orders,
        'previous_orders': previous_orders,
        'main_categories': MainCategory.objects.all(),
        'cart_count':cart_count,
    }

    return render(request, 'app/my_orders.html', context)


@login_required
def cancel_order(request, order_id):
    """
    Allow the user to cancel an order within 3 hours of its creation.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.can_cancel():
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} has been successfully cancelled.")
    else:
        messages.error(request, "Order cannot be cancelled. Either it's already processed or the cancellation window has passed.")
    
    return redirect('my_orders')



@login_required
def add_to_cart(request, slug):
    if not request.user.is_authenticated:
        # If the user is not authenticated, show an error message and redirect to the login page
        messages.error(request, "You must be logged in to add products to your cart.")
        return redirect('login')  # Redirect to the login page  # Redirect to login page

    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        # Retrieve selected size, color, and quantity from the form
        selected_size = request.POST.get('size')
        selected_color = request.POST.get('color')
        quantity = int(request.POST.get('quantity', 1))

        # Get the user's cart or create it if it doesn't exist
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if a CartItem with the same product, size, and color exists in the cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            selected_size=selected_size,
            selected_color=selected_color
        )

        if not created:
            # If the CartItem already exists, increase the quantity
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # If the CartItem is newly created, set the quantity and save it
            cart_item.quantity = quantity
            cart_item.save()

        # Send a success message and redirect the user to the cart page
        messages.success(request, "Product added to cart successfully!")
        return redirect('cart')  # Redirect to the cart page after adding the product

    return redirect('detail', slug=slug)























# stock: This refers to the field in your Product model that holds the stock quantity.
# __gt: This is a field lookup that means "greater than". So stock__gt=0 checks for products where the stock field is greater than zero.
@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)  # Ensure the cart exists
    cart_items = cart.items.select_related('product').all()  # Get cart items
    total_price = cart.get_total_price()  # Calculate total price from the cart items
    gst_rate = Decimal('0.18')  # 18% GST
    gst_amount = round(total_price  * gst_rate, 2)
    shipping_cost= Decimal('50.00')  # Flat shipping charge
    total_amount_with_gst = round(total_price + gst_amount + shipping_cost, 2)
   
    
    if request.method == 'POST':
        # Collect billing info from form
        billing_first_name = request.POST.get('billing_first_name')
        billing_last_name = request.POST.get('billing_last_name')
        billing_email = request.POST.get('billing_email')
        billing_mobile = request.POST.get('billing_mobile')
        billing_address_line1 = request.POST.get('billing_address_line1')
        billing_address_line2 = request.POST.get('billing_address_line2', '')
        billing_country = request.POST.get('billing_country')
        billing_city = request.POST.get('billing_city')
        billing_state = request.POST.get('billing_state')
        billing_zip_code = request.POST.get('billing_zip_code')

        # Validate required billing fields
        required_billing_fields = [
            billing_first_name, billing_last_name, billing_email, billing_mobile,
            billing_address_line1, billing_country, billing_city, billing_state, billing_zip_code
        ]

        if not all(required_billing_fields):
            messages.error(request, "Please fill in all required billing fields.")
            return redirect('checkout')

        # Check if shipping address is different
        shipto = request.POST.get('shipto')
        if shipto:
            shipping_first_name = request.POST.get('shipping_first_name')
            shipping_last_name = request.POST.get('shipping_last_name')
            shipping_email = request.POST.get('shipping_email', billing_email)
            shipping_mobile = request.POST.get('shipping_mobile', billing_mobile)
            shipping_address_line1 = request.POST.get('shipping_address_line1')
            shipping_address_line2 = request.POST.get('shipping_address_line2', '')
            shipping_country = request.POST.get('shipping_country')
            shipping_city = request.POST.get('shipping_city')
            shipping_state = request.POST.get('shipping_state')
            shipping_zip_code = request.POST.get('shipping_zip_code')

            # Validate required shipping fields
            required_shipping_fields = [
                shipping_first_name, shipping_last_name, shipping_email, shipping_mobile,
                shipping_address_line1, shipping_country, shipping_city, shipping_state, shipping_zip_code
            ]

            if not all(required_shipping_fields):
                messages.error(request, "Please fill in all required shipping fields.")
                return redirect('checkout')
        else:
            # If shipping address is the same as billing
            shipping_first_name = billing_first_name
            shipping_last_name = billing_last_name
            shipping_email = billing_email
            shipping_mobile = billing_mobile
            shipping_address_line1 = billing_address_line1
            shipping_address_line2 = billing_address_line2
            shipping_country = billing_country
            shipping_city = billing_city
            shipping_state = billing_state
            shipping_zip_code = billing_zip_code
        payment_method = request.POST.get('payment_method')
        order = Order.objects.create(
            user=request.user,
            billing_first_name=billing_first_name,
            billing_last_name=billing_last_name,
            billing_email=billing_email,
            billing_mobile=billing_mobile,
            billing_address_line1=billing_address_line1,
            billing_address_line2=billing_address_line2,
            billing_country=billing_country,
            billing_city=billing_city,
            billing_state=billing_state,
            billing_zip_code=billing_zip_code,
            shipping_first_name=shipping_first_name,
            shipping_last_name=shipping_last_name,
            shipping_email=shipping_email,
            shipping_mobile=shipping_mobile,
            shipping_address_line1=shipping_address_line1,
            shipping_address_line2=shipping_address_line2,
            shipping_country=shipping_country,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_zip_code=shipping_zip_code,
            total_amount=total_amount_with_gst ,
            created_at=timezone.now(),
            status='Pending',
            payment_method=payment_method,  # Store payment method
        )
        order.save()

        # Create OrderItems with selected color and size
        for cart_item in cart_items:
            selected_color = cart_item.selected_color if cart_item.selected_color else 'N/A'
            selected_size = cart_item.selected_size if cart_item.selected_size else 'N/A'
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                selected_color=selected_color,  # Copy the selected color
                selected_size=selected_size,  
            )
            
            # Optionally, reduce stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # Clear the cart after the order is placed
        cart.items.all().delete()  # Clear cart items

        # Send order confirmation email
        try:
            send_mail(
                f"Order Confirmation - #{order.id}",
                f"Thank you for your order, {order.billing_first_name}!\n\n"
                f"Your order ID is {order.id}.\n\n"
                f"Total Amount: Rs {order.total_amount}\n"
                f"Payment Method: {payment_method}\n"
                f"Status:{order.status}",
                settings.DEFAULT_FROM_EMAIL,
                [order.billing_email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the exception or handle it as needed
            print(f"Error sending email: {e}")
        if payment_method == 'card':
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_TEST_KEY_ID, settings.RAZORPAY_TEST_KEY_SECRET))
                razorpay_order = client.order.create({
                    'amount':int(total_amount_with_gst  * 100),
                    'currency': 'INR',
                     "receipt": str(order.id),
                    'payment_capture': '1',
                })
                order.razorpay_order_id = razorpay_order['id']  # Use the correct field
                order.save()
                request.session['razorpay_order_id'] = razorpay_order['id']
                # Store Razorpay Order ID in session to retrieve later in payment_success
               

                context = {
                    'cart_items': cart_items,
                    'gst_amount': gst_amount,
                'shipping_cost': shipping_cost,
                    'order_id': order.id,
                    'total_price': total_price,
                    'total_price_with_shipping':total_amount_with_gst ,
                    'razorpay_order_id': razorpay_order['id'],
                     'razorpay_order_amount': razorpay_order['amount'],
                    'main_categories': MainCategory.objects.all(),
                    'payment':True,
                     'payment_method': 'card',    # Indicate payment method
                    'billing_first_name': billing_first_name,
                    'billing_last_name': billing_last_name,
                    'billing_email': billing_email,
                    'billing_mobile': billing_mobile,
                }
                return render(request, 'app/checkout.html', context)

            except Exception as e:
                messages.error(request, f"Error processing payment.{e}")
                print(e)
                return redirect('checkout')

        elif payment_method == 'cod':
            # Redirect to the order confirmation page
            return redirect('order_confirmation', order_id=order.id)
    else: 
        context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'gst_amount': gst_amount,
        'shipping_cost': shipping_cost,
        'total_amount_with_gst': total_amount_with_gst ,
        'main_categories': MainCategory.objects.all(),
    }
    return render(request, 'app/checkout.html', context)
# views.py
@login_required
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    razorpay_signature = request.GET.get('razorpay_signature')
    razorpay_order_id = request.GET.get('razorpay_order_id')  # Updated to retrieve from GET

    if not razorpay_order_id or not payment_id or not razorpay_signature:
        messages.error(request, "Invalid payment attempt.")
        return redirect('checkout')

    try:
        order = Order.objects.get(razorpay_order_id=razorpay_order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('checkout')

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_TEST_KEY_ID, settings.RAZORPAY_TEST_KEY_SECRET))

    # Verify the payment signature
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, "Payment signature verification failed.")
        return redirect('checkout')

    # Update the order with payment details
    order.razorpay_payment_id = payment_id
    order.razorpay_signature = razorpay_signature
    order.status = 'In Process'
    order.save()

    # Fetch order items and calculate totals
    order_items = OrderItem.objects.filter(order=order)
    total_amount = sum(item.product.price * item.quantity for item in order_items)
    gst_rate = Decimal('0.18')
    gst_amount = round(total_amount * gst_rate, 2)
    shipping_cost = Decimal('50.00')
    total_amount_with_gst = round(total_amount + gst_amount + shipping_cost, 2)

    # Clear the user's cart
    Cart.objects.filter(user=request.user).delete()

    # Send confirmation email
    try:
        send_mail(
            f"Order Confirmation - #{order.id}",
            f"Dear {order.billing_first_name},\n\n"
            f"Thank you for your purchase! Your order #{order.id} has been successfully placed.\n\n"
            f"Order Details:\n"
            f"Total Amount: ₹{order.total_amount}\n"
            f"Payment Method: {order.get_payment_method_display()}\n"
            f"Status: {order.status}\n\n"
            f"Thank you for shopping with us!",
            settings.DEFAULT_FROM_EMAIL,
            [order.billing_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending confirmation email: {e}")

    context = {
        'order': order,
        'order_items': order_items,
        'total_amount': total_amount,
        'gst_amount': gst_amount,
        'shipping_cost': shipping_cost,
        'total_amount_with_gst': total_amount_with_gst
    }

    # Render the invoice page with the updated context
    return render(request, 'app/invoice.html', context)
