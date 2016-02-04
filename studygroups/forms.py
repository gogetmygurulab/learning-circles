from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail

from localflavor.us.forms import USPhoneNumberField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML

import pytz, datetime, json

import twilio

from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import StudyGroup
from studygroups.models import StudyGroupMeeting
from studygroups.models import Feedback
from studygroups.sms import send_message

import logging

logger = logging.getLogger(__name__)


class ApplicationForm(forms.ModelForm):
    COMPUTER_ACCESS = (
        ('Both', 'Both'),
        ('Just a laptop', 'Just a laptop'),
        ('Just headphones', 'Just headphones'),
        ('Neither', 'Neither'),
    )
    DIGITAL_LITERACY_CHOICES = (
        ('0', _(u'Can\'t do')), 
        ('1', _(u'Need help doing')),
        ('2', _(u'Can do with difficulty')), 
        ('3', _(u'Can do')),
        ('4', _(u'Expert (can teach others)')),
    )

    mobile = USPhoneNumberField(required=False, label=_('Phone Number for SMS'), help_text=_('if no email available (currently US numbers only)'))
    computer_access = forms.ChoiceField(
        choices=COMPUTER_ACCESS,
        label=_('Can you bring a laptop and headphones to the Learning Circle each week?')
    )
    goals = forms.CharField(
        label=_('In one sentence, please explain your goals for taking this course.')
    )
    support = forms.CharField(
        label=_('A successful study group requires the support of all of its members. How will you help your peers achieve their goals?')
    )

    send_email = forms.ChoiceField(label=_('Send an email'), choices=DIGITAL_LITERACY_CHOICES)
    delete_spam = forms.ChoiceField(label=_('Delete spam email'), choices=DIGITAL_LITERACY_CHOICES)
    search_online = forms.ChoiceField(label=_('Find stuff online using Google'), choices=DIGITAL_LITERACY_CHOICES)
    browse_video = forms.ChoiceField(label=_('Watch a video on Youtube'), choices=DIGITAL_LITERACY_CHOICES)
    online_shopping = forms.ChoiceField(label=_('Fill out an application form or buy something online'), choices=DIGITAL_LITERACY_CHOICES)
    mobile_apps = forms.ChoiceField(label=_('Use a mobile app'), choices=DIGITAL_LITERACY_CHOICES)
    web_safety = forms.ChoiceField(label=_('Evaluate whether a website is safe/can be trusted'), choices=DIGITAL_LITERACY_CHOICES)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'study_group', 'name', 'email', 'mobile', 'goals', 'support', 'computer_access',
            Fieldset(
                _(u'How comfortable are you doing the following tasks?'),
                'send_email', 'delete_spam', 'search_online', 'browse_video', 'online_shopping', 'mobile_apps', 'web_safety'
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))
        super(ApplicationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        signup_questions = {}
        questions = ['computer_access', 'goals', 'support', 'send_email', 'delete_spam', 'search_online', 'browse_video', 'online_shopping', 'mobile_apps', 'web_safety']
        for question in questions:
            signup_questions[question] = self.cleaned_data[question]
        self.instance.signup_questions = json.dumps(signup_questions)
        return super(ApplicationForm, self).save(commit)

    def clean(self):
        cleaned_data = super(ApplicationForm, self).clean()
        contact_method = cleaned_data.get("contact_method")

        if not cleaned_data.get('mobile') and not cleaned_data.get('email'):
            self.add_error('email', _('Please provide your email address or a US mobile number to sign up.'))

    class Meta:
        model = Application
        fields = ['study_group', 'name', 'email', 'mobile']
        widgets = {'study_group': forms.HiddenInput} 


class OptOutForm(forms.Form):
    email = forms.EmailField(help_text=_('Email address used to sign up.'), required=False)
    mobile = USPhoneNumberField(required=False, label=_('Phone Number for SMS'), help_text=_('Phone number used to sign up.'))

    def clean(self):
        cleaned_data = super(OptOutForm, self).clean()
        email = cleaned_data['email']
        mobile = cleaned_data['mobile']

        if not email and not mobile:
            self.add_error('email', _('Please provide either the email address or the phone number used to sign up.'))

        conditions = [
            not email or Application.objects.active().filter(email=email).count() == 0,
            not mobile or Application.objects.active().filter(mobile=mobile).count() == 0,
            email or mobile
        ]

        if all(conditions):
            raise forms.ValidationError(_('Could not find any signup matching your email address or phone number. Please make sure to enter the email or phone number you used to sign up.'))

    def send_optout_message(self):
        email = self.cleaned_data['email']
        mobile = self.cleaned_data['mobile']
        if email:
            for application in Application.objects.active().filter(email=email):
                # send opt-out email
                context = { 'application': application }
                subject = render_to_string('studygroups/optout_confirm_email_subject.txt', context).strip('\n')
                html_body = render_to_string('studygroups/optout_confirm_email.html', context)
                text_body = render_to_string('studygroups/optout_confirm_email.txt', context)
                notification = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [application.email])
                notification.attach_alternative(html_body, 'text/html')
                notification.send()
 

        # Find all signups with mobile with email and delete
        if mobile:
            applications = Application.objects.active().filter(mobile=mobile)
            if email:
                # don't send text to applications with a valid email in opt out form
                applications = application.exclude(email=email)
            for application in applications:
                context = { 'application': application }
                message = render_to_string('studygroups/optout_confirm_text.txt', context)
                try:
                    send_message(application.mobile, message)
                except twilio.TwilioRestException as e:
                    logger.exception(u"Could not send text message to %s", to, exc_info=e)
                application.delete()


class MessageForm(forms.ModelForm):
    class Meta:
        model = Reminder
        exclude = ['study_group_meeting', 'created_at', 'sent_at']
        widgets = {'study_group': forms.HiddenInput} 


class StudyGroupForm(forms.ModelForm):
    meeting_time = forms.TimeField(input_formats=['%I:%M %p'])
    weeks = forms.IntegerField(min_value=1, label=_('How many weeks will your learning circle run?'))
    timezone = forms.ChoiceField(choices=zip(pytz.common_timezones, pytz.common_timezones))

    def __init__(self, *args, **kwargs):
        super(StudyGroupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.layout.insert(1, HTML("""<p><a href="{% url 'studygroups_course_create' %}">Add course</a></p>"""))

        if self.instance.pk:
            self.fields['weeks'].initial = self.instance.studygroupmeeting_set.active().count()

    def save(self, commit=True):
        self.instance.end_date = self.cleaned_data['start_date'] + datetime.timedelta(weeks=self.cleaned_data['weeks'] - 1)
        return super(StudyGroupForm, self).save(commit)

    class Meta:
        model = StudyGroup
        fields = [
            'course',
            'venue_name',
            'venue_address',
            'venue_details',
            'venue_website',
            'facilitator',
            'start_date',
            'weeks',
            'meeting_time',
            'duration',
            'timezone',
            'image',
        ]


class FacilitatorForm(forms.ModelForm):
    username = forms.EmailField(required=True, label=_('Email'))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class StudyGroupMeetingForm(forms.ModelForm):
    meeting_time = forms.SplitDateTimeField(input_time_formats=['%I:%M %p'])
    class Meta:
        model = StudyGroupMeeting
        fields = ['meeting_time', 'study_group']
        widgets = {'study_group': forms.HiddenInput} 


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['study_group_meeting', 'feedback', 'reflection', 'attendance', 'rating']
        labels = {
            'feedback': _('For learners: Write a brief summary of this week\'s Learning Circle.'),
            'attendance': _('How many people attended?'),
            'reflection': _('Between us: Is there anything you want to let us know?'),
            'rating': _('Overall, how would you say this week went?')
        }
        help_texts = {
            'feedback': _('You may want to include your impressions of how it went, plus/delta feedback, and anything the group agreed on having completed before the next meeting. This will be automatically sent to learners two days before next week\'s meeting.'),
            'reflection': _('You can use this space for reflections, concerns, and anything else you think might help us improve Learning Circles. We won\'t share anything here without contacting you first.'),
        }
        widgets = {'study_group_meeting': forms.HiddenInput} 
