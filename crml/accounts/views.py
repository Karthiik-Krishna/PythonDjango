from django.shortcuts import render, redirect 
from django.http import HttpResponse

from django.forms import inlineformset_factory #For multiple forms in a form

from django.contrib.auth.forms import UserCreationForm #For login pages,django provides default forms with this
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required #For restrictions 
from django.contrib.auth.models import Group

from django.contrib import messages

# Create your views here.
from .models import *
from .forms import OrderForm,CreateUserForm,CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user,allowed_users,admin_only




@unauthenticated_user
def registerPage(request):
		#form = UserCreationForm() This gives default django form
		form = CreateUserForm() #Our customized form 
		if request.method == 'POST':
			#form = UserCreationForm(request.POST)
			form = CreateUserForm(request.POST)
			if form.is_valid():
				#form.save()
				user = form.save()  
				#user = form.cleaned_data.get('username') 
				username = form.cleaned_data.get('username') #To get corresponding user
				
				group = Group.objects.get(name = 'customer')
				user.groups.add(group)
				#The above two lines will add the registered user to customer group
				
				Customer.objects.create(
					user=user,
					)
				messages.success(request,'Account was created for ' +username) #To display the success message
				return redirect('login')
		context = {'form':form}
		return render(request,'accounts/register.html',context)




@unauthenticated_user
def loginPage(request):
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')	
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('home')
			else:
				messages.info(request,'Incorrect Usename or Password')
				#return render(request,'accounts/login.html', context)

		context={}
		return render(request,'accounts/login.html', context)





def logoutUser(request):
	logout(request)
	return redirect('login')





@login_required(login_url = 'login')
#@allowed_users(allowed_roles = ['admin'])
@admin_only
def home(request):
	orders = Order.objects.all()
	customers = Customer.objects.all()

	total_customers = customers.count()

	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	pending = orders.filter(status='Pending').count()

	context = {'orders':orders, 'customers':customers,
	'total_orders':total_orders,'delivered':delivered,
	'pending':pending }

	return render(request, 'accounts/dashboard.html', context)


@login_required
@allowed_users(allowed_roles = ['customer'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)

	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES ,instance=customer)
		if form.is_valid():
			form.save()
	context = {'form':form}
	return render(request,'accounts/account_settings.html',context)


@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['customer'])
def userPage(request):
	orders = request.user.customer.order_set.all()
	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	pending = orders.filter(status='Pending').count()
	print('Orders:',orders)
	context = {'orders':orders,'total_orders':total_orders,'delivered':delivered,
	'pending':pending}
	return render(request,'accounts/user.html',context)

	

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def products(request):
	products = Product.objects.all()

	return render(request, 'accounts/products.html', {'products':products})




@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def customer(request, pk_test):
	customer = Customer.objects.get(id=pk_test)
	orders = customer.order_set.all()
	order_count = orders.count()
	#myFilter = OrderFilter() #This is for getting the attributes on the page at search in customer.html
	myFilter = OrderFilter(request.GET, queryset=orders)
	orders = myFilter.qs
	context = {'customer':customer, 'orders':orders, 'order_count':order_count,'myFilter':myFilter}
	return render(request, 'accounts/customer.html',context)





@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def createOrder(request,pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product','status'), extra=6 )
	customer = Customer.objects.get(id=pk)
	#To get the form with no pre values use below none()
	formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
	#customer=Customer.objects.get(id=pk)
	#form = OrderForm(initial={'customer':customer})
	if request.method == 'POST':
		#print('Printing POST:', request.POST)
		#form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST,instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	context = {'formset':formset}
	return render(request, 'accounts/order_form.html', context)





@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def updateOrder(request, pk):

	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)

	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}
	return render(request, 'accounts/order_form.html', context)





@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == "POST":
		order.delete()
		return redirect('/')

	context = {'item':order}
	return render(request, 'accounts/delete.html', context)

def setcookie(request):
	html = HttpResponse("<h1>Data flair tutorial</>")
	html.setcookie('dataflair','Hello this your cookie', max_age = None)
	return html
