from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Event, Registration, TeamMember
from django.core.exceptions import ValidationError

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'capacity']

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['event', 'user', 'name', 'email', 'token', 'prize']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and not self.instance.event.has_ended():
            self.fields['prize'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        prize = cleaned_data.get('prize')
        event = cleaned_data.get('event')

        # Check if registration period has started
        if event and timezone.now() < event.registration_start:
            raise ValidationError("Registration has not started for this event yet.")

        if prize and event:
            if prize != '':
                if not event.can_award_prizes():
                    raise ValidationError("Cannot award more prizes. The event already has 3 prizes assigned.")
                if event.registrations.filter(prize=prize).exists():
                    raise ValidationError(f"The prize '{prize}' has already been awarded.")

        return cleaned_data

class EventRegistrationForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your Name')
    email = forms.EmailField(label='Your Email')

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class FeedbackForm(forms.Form):
    overall_rating = forms.ChoiceField(
        choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')],
        widget=forms.RadioSelect,
        label='How would you rate the overall quality of the event?'
    )
    content_relevance = forms.ChoiceField(
        choices=[('Very relevant', 'Very relevant'), ('Somewhat relevant', 'Somewhat relevant'), ('Neutral', 'Neutral'), ('Not very relevant', 'Not very relevant'), ('Not relevant at all', 'Not relevant at all')],
        widget=forms.RadioSelect,
        label='How relevant was the content of the event to your interests or needs?'
    )
    speaker_evaluation = forms.ChoiceField(
        choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')],
        widget=forms.RadioSelect,
        label='How would you rate the speaker(s)/presenter(s) in terms of knowledge and presentation skills?'
    )
    organization_rating = forms.ChoiceField(
        choices=[('Very well organized', 'Very well organized'), ('Well organized', 'Well organized'), ('Neutral', 'Neutral'), ('Poorly organized', 'Poorly organized'), ('Very poorly organized', 'Very poorly organized')],
        widget=forms.RadioSelect,
        label='How well was the event organized? (e.g., scheduling, venue, materials)'
    )
    suggestions = forms.CharField(
        widget=forms.Textarea,
        label='What suggestions do you have for improving future events? (Please provide details)',
        required=False
    )

class ReplyForm(forms.Form):
    reply_message = forms.CharField(widget=forms.Textarea, label='Reply Message')

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'role', 'bio', 'image']


from django.contrib.auth.models import User
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']