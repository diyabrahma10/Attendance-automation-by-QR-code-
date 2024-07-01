from email.message import EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from miniProject import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
import qrcode
from datetime import datetime
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def registerProf(request):
    if request.method == "POST":
        # username = request.POST.get("username")
        username = request.POST["username"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        # we are creating the names of the variable same as the name given in the labels in the input hence here the lhs username is the variable we created here in the python file and the username inside the request.POSt function is the one we created in the html file as name to the label

        if User.objects.filter(username = username):
            messages.error(request, "Username Already Exists. Please try some other username")
            return redirect('home')
        
        # if User.objects.filter(email = email):
        #     messages.error(request, "Email already in use")
        #     return redirect('home')
        
        if len(username)>10:
            messages.error(request, "Username must be under 10 characters")
            return redirect('registerProf')
        if pass1!=pass2:
            messages.error(request, "Passwords didn't match")
            return redirect('registerProf')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha Numeric")
            return redirect("registerProf")

        myuser = User.objects.create(username=username,email=email)
        myuser.set_password(pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        
        myuser.save()

        messages.success(request,"Your Account Have been Successfully Created, We also have sent you a confirmation email, Please confirm your your email in order to activate your account")

        # Welcome email

        # subject = "Welcome to Mini Project group one Professors Login"
        # message = "Hello " + myuser.first_name+ "!!\n" + "Welcome to our website!!\nWe have sent you this confirmation email to confirm your email address\nPlease confirm your email address to activate your account\n\nThanking you\nDiya Brahma"  #myuser is the object name 
        # from_email = settings.EMAIL_HOST_USER
        # to_list = [myuser.email]
        # send_mail(subject, message, from_email, to_list)

        #email address confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirm your email email Id for miniproject site"
        message2 = render_to_string("email_confirmation.html", {
            'name': myuser.first_name,
            'domain' : current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('loginProf')

    return render(request, "authentication/signup.html")

def loginProf(request):
    if request.method == 'POST':
        username = request.POST["username"]
        pass1 = request.POST["pass1"]
        

        user = authenticate(username = username, password = pass1)
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html", {'fname':fname})
        else:
            messages.error(request, "Bad Credentials")
            return redirect('loginProf')

    return render(request, "authentication/signin.html")

def logoutProf(request):
    logout(request)
    messages.success(request, " Logged Out successfully")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)

    except(TypeError,ValueError,OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activationFailed.html')
    
@login_required(login_url='/loginProf')
def qrCodeForm(request):
    if request.method == 'POST':
        try:
            pName = request.POST["pName"]
            department = request.POST["department"]
            semester = request.POST["semester"]
            subject = request.POST["subject"]
            subcode = request.POST["subcode"]
            email = request.POST["email"]
            duration = request.POST["duration"]
            
            
            #code to create qr code from the given data
            currentTime = datetime.now()
            timeStamp = currentTime.strftime("%Y-%m-%d %H:%M:%S")
            data = pName + " " + department + " " + semester + " " + subject + " " + subcode  + " " + email + " " + timeStamp + " " + duration
            qrCode = qrcode.make(data)
            filename = "newQR.png"
            qrCode.save(filename)

            #sending the mail
            emailSubject = "The generated qr code for the respective class"
            textMessage = "This is your respective qr code for your class of " + subject + "for the department of " + department + ":" 
            fromEmail = settings.EMAIL_HOST_USER
            recipientList = [email]
            # send_mail(emailSubject, textMessage, fromEmail, recipientList)
            email = EmailMessage(emailSubject, textMessage, fromEmail,recipientList )       #this EmailMessage is a class
            filePath = f"{settings.BASE_DIR}\\newQR.png"
            print(filePath)
            with open(filePath,'rb') as file:
                email.attach('newQR.png', file.read(), 'image/png')
            
            email.send()
            messages.success(request, 'QR code for the particular class have been sent to your registered email id')
        except:
            messages.error(request, 'Could not generate and send the QR code. Try again')
        return redirect('home')

     
    return render(request,'qrCode/qrCodeForm.html' )