from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib import auth
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from .forms import *
from polls.models import *
from django.template import RequestContext
from django.core.mail import send_mail
import hashlib, datetime, random
from django.utils import timezone
from django.contrib.auth.views import password_reset, password_reset_confirm



def login(request):
    c={}
    c.update(csrf(request))
    return render_to_response('polls/login.html', c)
    
    

def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return redirect('/')
        else:
            return HttpResponse('user not active')
    else:
        return redirect('/accounts/invalid')
 

def logout(request):
    auth.logout(request)
    return render_to_response('polls/index.html')


def invalid_login(request):
    return redirect('/authentication/')


def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid(): 
            form.save()  # save user to database if form is valid

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            random_string = str(random.random()).encode('utf8')
            salt = hashlib.sha1(random_string).hexdigest()[:5]
            salted = (salt + email).encode('utf8')
            activation_key = hashlib.sha1(salted).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(7) # 7 days

            #Get user by username
            user=User.objects.get(username=username)

            # Create and save user profile                                                                                                                                  
            new_profile = UserProfile(user=user, activation_key=activation_key, 
                key_expires=key_expires)
            new_profile.save()

            # Send email with activation key
            email_subject = 'Account confirmation'
            email_body = "Hey %s, thanks for signing up. To activate your account, click this link within \
            7 days http://127.0.0.1:8000/confirm/%s" % (username, activation_key) #### https://localhost/

            send_mail(email_subject, email_body, None,
                [email], fail_silently=False)

            return redirect('/register_success')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form':form})



def register_confirm(request, activation_key):
    #check if user is already logged in and if he is redirect him to some other url, e.g. home
    if request.user.is_authenticated():
        HttpResponseRedirect('/')

    # check if there is UserProfile which matches the activation key (if not then display 404)
    user_profile = get_object_or_404(UserProfile, activation_key=activation_key)

    #check if the activation key has expired, if it hase then render confirm_expired.html
    if user_profile.key_expires < timezone.now():
        return HttpResponse('expired')
    #if the key hasn't expired save user and set him as active and render some template to confirm activation
    user = user_profile.user
    user.is_active = True
    user.save()
    return render_to_response('registration/confirm.html')



def register_success(request):
    return render(request, 'registration/success.html')
    

def reset_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, template_name='registration/reset_confirm.html',
        uidb64=uidb64, token=token, post_reset_redirect='/')


def reset(request):
    return password_reset(request, template_name='registration/reset.html',
        email_template_name='registration/reset_email.html',
        post_reset_redirect='/')
    
    
 
 
 
 
 
 
 
 
 
 
 
    
    
    