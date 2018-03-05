from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView

from ..decorators import subscriber_required
from ..forms import SubscriberInterestsForm, SubscribersSignUpForm, TakeQuizForm, DocumentForm, FileFieldForm
from ..models import Quiz, Subscriber, TakenQuiz, User, Document, SubFile


class SubscriberSignUpView(CreateView):
    model = User
    form_class = SubscribersSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'subscriber'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('subscribers:quiz_list')


@method_decorator([login_required, subscriber_required], name='dispatch')
class SubscriberInterestsView(UpdateView):
    model = Subscriber
    form_class = SubscriberInterestsForm
    template_name = 'manager/subscribers/interests_form.html'
    success_url = reverse_lazy('subscribers:quiz_list')

    def get_object(self):
        return self.request.user.subscriber

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)



@method_decorator([login_required, subscriber_required], name='dispatch')
class SubscriberFileInterestsView(UpdateView):
    model = Subscriber
    form_class = SubscriberInterestsForm
    template_name = 'manager/subscribers/file_interests_form.html'
    success_url = reverse_lazy('subscribers:sub_file_list')

    def get_object(self):
        return self.request.user.subscriber

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)



@method_decorator([login_required, subscriber_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'manager/subscribers/quiz_list.html'

    def get_queryset(self):
        subscriber = self.request.user.subscriber
        subscriber_interests = subscriber.interests.values_list('pk', flat=True)
        taken_quizzes = subscriber.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=subscriber_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, subscriber_required], name='dispatch')
class RelateFileListView(ListView):
    model = Document
    ordering = ('document', )
    context_object_name = 'files'
    template_name = 'manager/subscribers/related_file_list.html'

    def get_queryset(self):
        subscriber = self.request.user.subscriber
        subscriber_interests = subscriber.interests.values_list('pk', flat=True)
        sub_files = subscriber.documents.values_list('pk', flat=True)
        queryset = Document.objects.filter(subject__in=subscriber_interests) \
                    .exclude(pk__in=sub_files)
        return queryset


@method_decorator([login_required, subscriber_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'manager/subscribers/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.subscriber.taken_quizzes \
            .select_related('quiz', 'quiz__subject') \
            .order_by('quiz__name')
        return queryset


@method_decorator([login_required, subscriber_required], name='dispatch')
class SubFilesListView(ListView):
    model = SubFile
    context_object_name = 'sub_files'
    template_name = 'manager/subscribers/sub_file_list.html'

    def get_queryset(self):
        queryset = self.request.user.subscriber.sub_files \
                    .select_related('document', 'document__subject') \
                    .order_by('document__description')
        return queryset


@login_required
@subscriber_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    subscriber = request.user.subscriber

    if subscriber.quizzes.filter(pk=pk).exists():
        return render(request, 'subscribers/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = subscriber.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                subscriber_answer = form.save(commit=False)
                subscriber_answer.subscriber = subscriber
                subscriber_answer.save()
                if subscriber.get_unanswered_questions(quiz).exists():
                    return redirect('subscribers:take_quiz', pk)
                else:
                    correct_answers = subscriber.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(subscriber=subscriber, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                    return redirect('subscribers:quiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'manager/subscribers/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })
