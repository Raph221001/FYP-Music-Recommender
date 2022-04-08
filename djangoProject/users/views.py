from django.shortcuts import  render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate #add this
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm #add this
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from .models import *
from .forms import CreateUserForm

def homepage(request):
	return render(request=request, template_name='users/homepage.html')

def register_request(request):
	if request.user.is_authenticated:
		return redirect('users:homepage')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + user)

				return redirect('users:login')

		context = {'form': form}
		return render(request, 'users/register.html', context)

def login_request(request):
	if request.user.is_authenticated:
		return redirect('users:homepage')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('users:homepage')
			else:
				messages.info(request, 'Username OR password is incorrect')

		context = {}
		return render(request, 'users/login.html', context)

def logout_request(request):
	logout(request)
	form = AuthenticationForm(request, data=request.POST)
	messages.info(request, "You have successfully logged out.")
	return render(request=request, template_name='users/logout.html', context={"login_form":form})

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "users/password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Title',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'raphofeimu@gmail.com' , ['raphofeimu@gmail.com'], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')

					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return redirect ("users:homepage")
				messages.error(request, 'An invalid email has been entered.')
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="users/password/password_reset.html", context={"password_reset_form":password_reset_form})