from .models import Tweet
from .forms import TweetForm,UserRegistrationForm,CommentForm,CustomPasswordChangeForm
from django.shortcuts import get_object_or_404,redirect,render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import random
from django.contrib.auth.views import PasswordChangeView,LoginView, LogoutView
from django.core.mail import send_mail
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.conf import settings
from .models import Profile
from django.db.models import Q
from django.urls import reverse
from django.utils.html import strip_tags

# Create your views here.


def homes(request):
    return render(request,'tweets/index.html')

def tweet_list(request):
    user = request.user
    user_gener = None  # Default for anonymous users

    if user.is_authenticated:
        try:
            profile = user.profile
            user_gener = profile.gener
        except:
            user_gener = None  # Optional: Handle if profile doesn't exist

    tweets = Tweet.objects.all().order_by('-created_at')
    return render(request, 'tweets/tweet_list.html', {
        'tweets': tweets,
        'user_gener': user_gener
    })

@login_required
@login_required
def tweet_create(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()

            tweet_gener = tweet.gener

            users = User.objects.exclude(pk=request.user.pk).select_related('profile')

            for user in users:
                user_gener = user.profile.gener if hasattr(user, 'profile') else []
                if set(tweet_gener) & set(user_gener):
                    excerpt = tweet.text[:100] + ("..." if len(tweet.text) > 100 else "")
                    url = request.build_absolute_uri(reverse('tweet_detail', kwargs={'pk': tweet.pk}))
                    
                    email_subject = f"🔥 A Post Picked Just for You – Don’t Miss This!"

                    email_html_message = f"""
                        <html>
                        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 30px;">
                            <div style="max-width: 640px; margin: auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); padding: 30px;">
                            
                            <h2 style="color: #1d3557; margin-top: 0; font-size: 26px;">🌟 You might love this: <br> <span style="color: #457B9D;">{tweet.title}</span></h2>

                            <p style="color: #333333; font-size: 17px; line-height: 1.7; margin-top: 20px;">
                                {excerpt}
                            </p>

                            <div style="text-align: center; margin: 40px 0;">
                                <a href="{url}" target="_blank" style="
                                    display: inline-block;
                                    background: linear-gradient(135deg, #1d3557, #457B9D);
                                    color: #ffffff !important;
                                    text-decoration: none;
                                    padding: 14px 30px;
                                    border-radius: 8px;
                                    font-weight: bold;
                                    font-size: 16px;
                                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                                    transition: background 0.3s ease;
                                " onmouseover="this.style.background='linear-gradient(135deg, #2c5282, #5a91bd)';" onmouseout="this.style.background='linear-gradient(135deg, #1d3557, #457B9D)';">
                                🔗 See More
                                </a>
                            </div>

                            <p style="color: #888; font-size: 13px; text-align: center;">
                                You’re receiving this because you subscribed to updates in your favorite genres.<br>
                                Don’t want these? You can manage preferences in your profile.
                            </p>
                            </div>
                        </body>
                        </html>
                        """
                    send_mail(
                        subject=email_subject,
                        message=strip_tags(email_html_message),  # plain text fallback
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                        html_message=email_html_message,
                    )

            messages.success(request, "Post Created Successfully!")
            return redirect('tweet_list')
    else:
        form = TweetForm()

    return render(request, 'tweets/tweet_form.html', {'form': form})

@login_required
def tweet_edit(request,tweet_id):
    tweet=get_object_or_404(Tweet,pk=tweet_id,user=request.user)
    if request.method=="POST":
        form=TweetForm(request.POST,request.FILES,instance=tweet)
        if form.is_valid():
            tweet=form.save(commit=False)
            tweet.user=request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form=TweetForm(instance=tweet)
    return render(request,'tweets/tweet_form.html',{'form':form})

@login_required
def tweet_delete(request,tweet_id):
    tweet=get_object_or_404(Tweet,pk=tweet_id,user=request.user)
    if request.method=="POST":
        tweet.delete()
        return redirect('tweet_list')
    return render(request,'tweets/tweet_confirm_deletion.html',{'tweet':tweet})

def register(request):
    otp_required = False

    if request.method == "POST":
        if 'otp' in request.POST:
            entered_otp = request.POST.get('otp')
            if entered_otp == request.session.get('otp'):
                form_data = request.session.get('user_data')

                # Create user
                user = User.objects.create_user(
                    username=form_data['username'],
                    email=form_data['email'],
                    password=form_data['password1']
                )

                # Save Profile with gener (MultiSelectField expects a comma-separated string)
                gener = form_data.get('gener', [])
                profile = Profile.objects.create(user=user)
                if gener:
                    profile.gener = ','.join(gener)  # assign comma-separated string
                profile.save()

                login(request, user)
                messages.success(request, "Registration successful!")
                request.session.pop('otp', None)
                request.session.pop('user_data', None)
                return redirect('tweet_list')

            else:
                messages.error(request, "Invalid OTP. Try again.")
                otp_required = True
                form = UserRegistrationForm(request.session.get('user_data'))
        else:
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                otp = str(random.randint(100000, 999999))
                request.session['otp'] = otp

                # Save form data including selected gener values as a list
                request.session['user_data'] = {
                    'username': form.cleaned_data['username'],
                    'email': form.cleaned_data['email'],
                    'password1': form.cleaned_data['password1'],
                    'gener': request.POST.getlist('gener')  # get list of selected choices
                }

                send_mail(
                    subject="🔐 Your OTP Code for VloggyNepal",
                    message=f"Your OTP is: {otp}",
                    from_email='Vloggylogin@gmail.com',
                    recipient_list=[form.cleaned_data['email']],
                    fail_silently=False,
                    html_message=f"""
                        <html>
                        <body>
                            <h2>🔐 VloggyNepal OTP Verification</h2>
                            <p>Your OTP is:</p>
                            <div style="font-size: 24px; font-weight: bold;">{otp}</div>
                            <p>This code will expire in <strong>10 minutes</strong>.</p>
                        </body>
                        </html>
                    """
                )

                messages.info(request, "An OTP has been sent to your email.")
                otp_required = True
            else:
                otp_required = False
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {
        'form': form,
        'otp_required': otp_required
    })

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        form_data = request.session.get('form_data')

        if entered_otp == session_otp and form_data:
            # Create user
            user = User.objects.create_user(
                username=form_data['username'],
                email=form_data['email'],
                password=form_data['password1']
            )
            login(request, user)

            # Clear session
            del request.session['otp']
            del request.session['form_data']

            return redirect('tweet_list')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'registration/verify_otp.html')



# Only details of that particular tweets
def tweet_detail(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    comments = tweet.comments.order_by('created_at')
    has_reacted = False
    if request.user.is_authenticated:
        has_reacted = tweet.reactions.filter(user=request.user).exists()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Redirect to login or show error
            return redirect('login')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tweet = tweet
            comment.user = request.user
            comment.save()
            return redirect('tweet_detail', pk=tweet.pk)
    else:
        form = CommentForm()

    context = {
        'tweet': tweet,
        'comments': comments,
        'form': form,
        'has_reacted': has_reacted,
    }
    return render(request, 'tweets/tweet_detail.html', context)

@login_required
def my_tweets(request):
    tweets = Tweet.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tweets/my_tweets.html', {'tweets': tweets})


@login_required
def toggle_reaction(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    existing_reaction = tweet.reactions.filter(user=request.user).first()

    if existing_reaction:
        existing_reaction.delete()
    else:
        tweet.reactions.create(user=request.user)

    return redirect('tweet_detail', pk=tweet.id)




class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('tweet_list') # redirect after logout


@login_required
def custom_password_change(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    from django.contrib import messages

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important, keeps user logged in
            messages.success(request, 'Password changed successfully.')
            return render(request, 'registration/password_change_form.html', {'form': form, 'password_changed': True})
        else:
            # form invalid, show errors including "old password incorrect"
            pass
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'registration/password_change_form.html', {'form': form})


def forgot_password_view(request):
    if request.method == 'POST':
        step = request.POST.get('step')

        if step == 'email':
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                otp = str(random.randint(100000, 999999))
                request.session['reset_email'] = email
                request.session['reset_otp'] = otp
                print(user)
                send_mail(
                subject='🔐 Password Reset Code - VloggyNepal',
                message='Use the code below to reset your password.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
                html_message=f"""
                    <html>
                    <head>
                    <style>
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                            background-color: #f4f4f4;
                            border-radius: 10px;
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            color: #333;
                        }}
                        .header {{
                            text-align: center;
                            padding-bottom: 10px;
                            border-bottom: 2px solid #ccc;
                        }}
                        .otp {{
                            background-color: #e63946;
                            color: #fff;
                            font-size: 24px;
                            font-weight: bold;
                            padding: 12px 20px;
                            display: inline-block;
                            border-radius: 8px;
                            margin: 20px 0;
                        }}
                        .footer {{
                            margin-top: 30px;
                            font-size: 14px;
                            text-align: center;
                            color: #777;
                        }}
                        .highlight {{
                            color: #2a9d8f;
                            font-weight: bold;
                        }}
                    </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h2>🔐 VloggyNepal Password Reset</h2>
                            </div>

                            <p>Hi <strong>{user.username}</strong>,</p>

                            <p>We received a request to reset your password. If this was you, use the code below:</p>

                            <div class="otp">{otp}</div>

                            <p>This code is valid for the next <span class="highlight">10 minutes</span>.</p>

                            <p>If you didn't request this, you can safely ignore the message. Your account remains secure.</p>

                            <p>Need help? Just reply to this email — we're here for you!</p>

                            <div class="footer">
                                Stay safe & secure,<br>
                                <strong>VloggyNepal Team</strong>
                            </div>
                            </div>
                    </body>
                    </html>
                """
    )
                messages.success(request, 'OTP has been sent to your email.')
                return render(request, 'forgot_password.html', {'otp_sent': True})

            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')

        elif step == 'otp':
            entered_otp = request.POST.get('otp')
            if entered_otp == request.session.get('reset_otp'):
                messages.success(request, 'OTP verified. Please set your new password.')
                return render(request, 'forgot_password.html', {'otp_verified': True})
            else:
                messages.error(request, 'Invalid OTP.')
                return render(request, 'forgot_password.html', {'otp_sent': True})

        elif step == 'new_password':
            new_pass = request.POST.get('new_password')
            confirm_pass = request.POST.get('confirm_password')

            if new_pass == confirm_pass:
                email = request.session.get('reset_email')
                try:
                    user = User.objects.get(email=email)
                    user.set_password(new_pass)
                    user.save()
                    messages.success(request, 'Password changed successfully. You can now log in.')
                    request.session.flush()
                    return redirect('login')
                except User.DoesNotExist:
                    messages.error(request, 'User session expired or invalid. Try again.')
                    return redirect('forgot_password')
            else:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'forgot_password.html', {'otp_verified': True})

    # GET or default render
    return render(request, 'forgot_password.html')
