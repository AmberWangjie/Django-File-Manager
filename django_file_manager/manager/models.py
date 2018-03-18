from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver
#import magic
#from validatedfile import ValidatedFileField

class User(AbstractUser):
    is_subscriber = models.BooleanField(default=False)
    is_publisher = models.BooleanField(default=False)


class Subject(models.Model):
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default='#007bff')

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)


class Quiz(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')

    def __str__(self):
        return self.name



class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class Document(models.Model):
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='document_publisher')
    #subscriber = models.ManyToManyField(Subscriber, through='SubFile')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, related_name='document_subject')
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/%Y/%m/%d')
 #   document = ValidatedFileField(null=True, blank=True, uploaded_to='documents/%Y/%m/%d', max_uploaded_size=10240, content_types=['application/pdf', 'image/png'])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #history = models.ForeignKey(History, on_delete=models.CASCADE, null=True, related_name='document_history')

    def __str__(self):
        return self.document.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)


class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    documents = models.ManyToManyField(Document)
    interests = models.ManyToManyField(Subject, related_name='interested_students')


    def get_unanswered_questions(self, quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    def __str__(self):
        return self.user.username


class TakenQuiz(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)


class SubFile(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='sub_files')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='sub_files')
    date = models.DateTimeField(auto_now_add=True)


class History(models.Model):
#    v = 'R'
 #   e = 'W'
    OPERATION_OPTIONS = (('c', 'Create'), ('m', 'Modify'), ('s', 'Subscribe'))
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='file_history')
    operation = models.CharField(max_length=10, choices=OPERATION_OPTIONS, default='c')
    date = models.DateTimeField(auto_now_add=True)
    performer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_performer')
    #sub_count = models.IntegerField(default=0)


class SubscribeAnswer(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')
