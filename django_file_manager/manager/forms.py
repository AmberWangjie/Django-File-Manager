from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
#from validatedfile import QuotaValidator
from manager.models import (Answer, Question, Subscriber, SubscribeAnswer,
                              Subject, User, Document, SubFile)


class PublishersSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_publisher = True
        if commit:
            user.save()
        return user


class SubscribersSignUpForm(UserCreationForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_subscriber = True
        user.save()
        subscirber = Subscriber.objects.create(user=user)
        subscirber.interests.add(*self.cleaned_data.get('interests'))
        return user


class SubscriberInterestsForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ('interests', )
        widgets = {
            'interests': forms.CheckboxSelectMultiple
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', )


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError('Mark at least one answer as correct.', code='no_correct_answer')


class TakeQuizForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = SubscribeAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('description', 'document', 'subject')
        widgets = {
            'subjects': forms.CheckboxSelectMultiple
        }


class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
   # file_field = forms.FileField(validators=[QuotaValidator(max_usage=102400)], widget=forms.ClearableFileInput(attrs={'multiple': True}))

#     class Meta:
#         model = Document
#         fields = ['document']

#     def __init__(self, user, *args, **kwargs):
#         super(FileFieldForm.self).__init__(*args, **kwargs)
#         self.user = user
#         self.fields['document'].validators[0].update_quota(items=self.user.documents.all(), attr_name='document',)

#     def exceeds_quota(self):
#         return self.fields['document'].validators[0].quota.exceeds()

#     def save(self, *args, **kwargs):
#         model = super(FileFieldForm, self).save(commit=False)
#         model.user=self.user
#         model.save()

# class HistoryForm(forms.Form):
#     class Meta:
#         model = History
#         fields = ('operation', 'performer', 'date') 


# class SubFileForm(forms.ModelForm):
#     OPTIONS = (('1', 'Subscribe'), ('2', 'Nevermind'))
#     submission = forms.ChoiceField(choices=OPTIONS)
#     #class Meta:
#      #   model = SubFile
#       #  fields = ('answer', )
#     def __init__(self, *args, **kwargs):
#         super(SubFileForm, self).__init__(*args, **kwargs)
#         self.fields['submission'].choices = list(self.fields['submission'].choices)

#     def clean_submission(self):
#         data = self.cleaned_data.get('submission')
#         if data in OPTIONS:
#             try:
#                 data = SubFile.objects.get()
#             except 
        
