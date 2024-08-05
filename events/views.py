from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponse, JsonResponse
from .models import Event, Feedback, FrontPageVideo, Registration, TeamMember, ContactMessage
from .forms import EventForm, FeedbackForm, RegistrationForm, EventRegistrationForm, SignUpForm, TeamMemberForm
import random
import string
from django.template.loader import render_to_string
from calendar import HTMLCalendar
from django.utils.safestring import mark_safe
from datetime import datetime, timedelta
from django.contrib.admin.views.decorators import staff_member_required



def index(request):
    login_form = AuthenticationForm()
    signup_form = SignUpForm()
    videos = FrontPageVideo.objects.all()  # Assuming FrontPageVideo is your model
    return render(request, 'index.html', {'login_form': login_form, 'signup_form': signup_form, 'videos': videos})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after successful signup
            return redirect('login')  # Redirect to login page
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('event_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def custom_logout(request):
    logout(request)
    return redirect(reverse('index'))


def about(request):
    team_members = TeamMember.objects.all()
    for member in team_members:
        print(member.image.url)  # Use 'image' if the field is named 'image'
    return render(request, 'events/about.html', {'team_members': team_members})

def contact(request):
    return render(request, 'contact.html')

@login_required
def event_list(request):
    current_time = timezone.now()
    upcoming_events = Event.objects.filter(registration_start__gt=current_time)
    current_events = Event.objects.filter(registration_start__lte=current_time)
    posters = CollegePoster.objects.all()
    return render(request, 'events/event_list.html', {
        'upcoming_events': upcoming_events,
        'current_events': current_events,
        'events': Event.objects.all(),
        'posters': posters  # Ensure all events are available in the context
    })

# @login_required
# def event_list(request):
#     current_time = timezone.now()
    
#     upcoming_events = Event.objects.filter(registration_start__gt=current_time)
#     current_events = Event.objects.filter(registration_start__lte=current_time)
    
#     posters = CollegePoster.objects.all()  # Fetch posters for the template

#     return render(request, 'events/event_list.html', {
#         'upcoming_events': upcoming_events,
#         'current_events': current_events,
#         'posters': posters  # Add posters to the context
#     })

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    registration_form = EventRegistrationForm(initial={'event_id': event_id})
    return render(request, 'events/event_detail.html', {'event': event, 'registration_form': registration_form})


@login_required
def registration_closed(request):
    return render(request, 'events/registration_closed.html')


@login_required
def already_registered(request):
    return render(request, 'events/already_registered.html')


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if registration period has started
    if timezone.now() < event.registration_start:
        return redirect('registration_not_started')

    # Check if the user has already registered for this event
    if Registration.objects.filter(event=event, user=request.user).exists():
        return redirect('already_registered')

    # Check if event is full
    if event.is_full():
        return redirect('registration_closed')

    # Check if the current time is after the event start time
    current_time = timezone.now()
    event_datetime = datetime.combine(event.date, event.time)
    event_datetime = timezone.make_aware(event_datetime)
    if current_time > event_datetime:
        return redirect('registration_closed')

    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            token = generate_token()

            registration = Registration.objects.create(
                event=event,
                user=request.user,
                name=name,
                email=email,
                token=token
            )

            # Decrease the event capacity
            event.capacity -= 1
            event.save()

            # Prepare the email content
            email_subject = 'Event Registration Confirmation'
            email_body = render_to_string('emails/registration_confirmation.html', {'registration': registration})

            email_message = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            email_message.content_subtype = 'html'  # Set the content type to HTML
            email_message.send(fail_silently=False)

            return redirect('registration_detail', registration_id=registration.id)
    else:
        form = EventRegistrationForm()

    return render(request, 'events/register_for_event.html', {'event': event, 'form': form})



@login_required
def registration_detail(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    return render(request, 'events/registration_detail.html', {'registration': registration})

def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@login_required
def download_token(request, registration_id):
    registration = get_object_or_404(Registration, pk=registration_id, user=request.user)
    registration.generate_token_pdf()

    # Serve the PDF for download
    response = HttpResponse(registration.token_pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{registration.token}.pdf"'
    return response


@login_required
def user_registration_history(request):
    registrations = Registration.objects.filter(user=request.user)
    return render(request, 'events/user_registration_history.html', {'registrations': registrations})





class EventCalendar(HTMLCalendar):
    def __init__(self, events):
        super().__init__()
        self.events = self.group_by_day(events)

    def group_by_day(self, events):
        grouped_events = {}
        for event in events:
            day = event.date.day
            if day not in grouped_events:
                grouped_events[day] = []
            grouped_events[day].append(event)
        return grouped_events

    def formatday(self, day, weekday):
        events_from_day = self.events.get(day, [])
        events_html = '<ul>'
        for event in events_from_day:
            events_html += f'<li><a href="{reverse("event_detail", args=[event.id])}">{event.title}</a></li>'
        events_html += '</ul>'
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if events_from_day:
                cssclass += ' event-day'
            return f"<td class='{cssclass}'><span class='day'>{day}</span> {events_html}</td>"
        return '<td></td>'

    def formatmonth(self, year, month, withyear=True):
        events = Event.objects.filter(date__year=year, date__month=month)
        self.events = self.group_by_day(events)
        return super().formatmonth(year, month, withyear)

    def get_previous_month(self, date):
        first_day = date.replace(day=1)
        prev_month = first_day - timedelta(days=1)
        return prev_month.year, prev_month.month

    def get_next_month(self, date):
        last_day = date.replace(day=28) + timedelta(days=4)  # This will always get the next month
        next_month = last_day.replace(day=1)
        return next_month.year, next_month.month



def calendar_view(request, year=datetime.now().year, month=datetime.now().strftime('%m')):
    year = int(year)
    month = int(month)
    date = datetime(year, month, 1)
    cal = EventCalendar(Event.objects.filter(date__year=year, date__month=month))
    html_cal = cal.formatmonth(year, month)
    prev_year, prev_month = cal.get_previous_month(date)
    next_year, next_month = cal.get_next_month(date)
    prev_url = reverse('calendar_view', kwargs={'year': prev_year, 'month': prev_month})
    next_url = reverse('calendar_view', kwargs={'year': next_year, 'month': next_month})
    context = {
        'calendar': mark_safe(html_cal),
        'prev_url': prev_url,
        'next_url': next_url,
        'year': year,
        'month': month,
    }
    return render(request, 'events/calendar.html', context)


def events_on_day(request, year, month, day):
    events = Event.objects.filter(date__year=year, date__month=month, date__day=day)
    events_list = [{'title': event.title, 'description': event.description, 'time': event.time.strftime('%H:%M')} for event in events]
    return JsonResponse(events_list, safe=False)

@login_required
def feedback(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if the event has ended
    if not event.has_ended():
        return redirect('event_list')  # Redirect to event list if feedback is not available

    # Check if the user has registered for this event
    if not Registration.objects.filter(event=event, user=request.user).exists():
        return redirect('event_list')  # Redirect to event list if the user has not registered

    # Check if the user has already provided feedback for this event
    if Feedback.objects.filter(event=event, user=request.user).exists():
        return redirect('feedback_thanks')  # Redirect to thank you page if feedback is already provided

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Save the feedback
            feedback = Feedback(
                event=event,
                user=request.user,
                overall_rating=form.cleaned_data['overall_rating'],
                content_relevance=form.cleaned_data['content_relevance'],
                speaker_evaluation=form.cleaned_data['speaker_evaluation'],
                organization_rating=form.cleaned_data['organization_rating'],
                suggestions=form.cleaned_data['suggestions']
            )
            feedback.save()
            return redirect('feedback_thanks')  # Redirect after successful feedback submission
    else:
        form = FeedbackForm()

    return render(request, 'events/feedback.html', {'form': form, 'event': event})



def feedback_thanks(request):
    return render(request, 'events/feedback_thanks.html')


@login_required
def event_feedback_report(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    feedback_list = Feedback.objects.filter(event=event)

    # Calculate statistics (e.g., average ratings)
    ratings = {
        'overall_rating': {'Excellent': 0, 'Good': 0, 'Average': 0, 'Poor': 0},
        'content_relevance': {'Very relevant': 0, 'Somewhat relevant': 0, 'Neutral': 0, 'Not very relevant': 0, 'Not relevant at all': 0},
        'speaker_evaluation': {'Excellent': 0, 'Good': 0, 'Average': 0, 'Poor': 0},
        'organization_rating': {'Very well organized': 0, 'Well organized': 0, 'Neutral': 0, 'Poorly organized': 0, 'Very poorly organized': 0},
    }

    for feedback in feedback_list:
        ratings['overall_rating'][feedback.overall_rating] += 1
        ratings['content_relevance'][feedback.content_relevance] += 1
        ratings['speaker_evaluation'][feedback.speaker_evaluation] += 1
        ratings['organization_rating'][feedback.organization_rating] += 1

    context = {
        'event': event,
        'feedback_list': feedback_list,
        'ratings': ratings
    }
    return render(request, 'events/feedback_report.html', context)


def results_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Check if the event has ended
    if not event.has_ended():
        return render(request, 'error.html', {'message': 'Results are not available for ongoing events.'})
    
    # Get registrations with prizes
    registrations = Registration.objects.filter(event=event).exclude(prize='')

    # Define a sorting order for prizes
    prize_order = {'1st': 1, '2nd': 2, '3rd': 3}
    
    # Sort registrations by prize level
    sorted_registrations = sorted(registrations, key=lambda r: prize_order.get(r.prize, 999))

    # Pass the sorted registrations to the template
    return render(request, 'results_page.html', {
        'event': event,
        'registrations': sorted_registrations,
        'no_results': not sorted_registrations,
        'current_year': timezone.now().year  # For footer year
    })
    



def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            contact_message = ContactMessage.objects.create(name=name, email=email, message=message)
            send_mail(
                'Contact Form Submission',
                f'Name: {name}\nEmail: {email}\nMessage: {message}',
                email,
                ['alvinksabu200115@gmail.com']  # Replace with your admin email
            )
            return redirect('contact_success')
        else:
            # Handle the case where one or more fields are missing
            return render(request, 'contact.html', {'error': 'Please fill in all fields'})
    return render(request, 'contact.html')
def contact_success(request):
    return render(request, 'contact_success.html')



@staff_member_required
def contact_message_list(request):
    messages = ContactMessage.objects.all()
    return render(request, 'admin/contactmessage/contact_message_list.html', {'messages': messages})

@staff_member_required
def ContactMessageAdminView(request):
    contact_messages = ContactMessage.objects.all()
    return render(request, 'admin/contactmessage/changelist.html', {'contact_messages': contact_messages})





def upload_team_member(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('about')
    else:
        form = TeamMemberForm()
    return render(request, 'upload_team_member.html', {'form': form})


from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
        profile.save()
        
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'events/profile.html', context)

def create_event(request):
    # Your view logic here
    return render(request, 'events/create_event.html')


from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
@login_required
def profile_edit(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        try:
            user = User.objects.get(id=request.user.id)
            user.username = username
            user.email = email
            user.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
    return render(request, 'events/profile_edit.html')

from .models import CollegePoster

def home(request):
    posters = CollegePoster.objects.all()
    return render(request, 'event.html', {'posters': posters})