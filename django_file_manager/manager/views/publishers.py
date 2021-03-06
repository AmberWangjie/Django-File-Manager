from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.views.generic.edit import FormView
from django.core.files.storage import FileSystemStorage
from ..decorators import publisher_required
from ..forms import BaseAnswerInlineFormSet, QuestionForm, PublishersSignUpForm, DocumentForm, FileFieldForm
from ..models import Answer, Question, Quiz, User, Document, History, SubFile
import logging

logger = logging.getLogger(__name__)


class PublisherSignUpView(CreateView):
    model = User
    form_class = PublishersSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'publisher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('publishers:quiz_change_list')


@method_decorator([login_required, publisher_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'manager/publishers/quiz_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .select_related('subject') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_quizzes', distinct=True))
        return queryset


@method_decorator([login_required, publisher_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name', 'subject', )
    template_name = 'manager/publishers/quiz_add_form.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(self.request, 'The quiz was created with success! Go ahead and add some questions now.')
        return redirect('publishers:quiz_change', quiz.pk)


@method_decorator([login_required, publisher_required], name='dispatch')
class FileListView(ListView):
    model = Document
    ordering = ('-uploaded_at',)
    context_object_name = 'files'
    template_name = 'manager/publishers/file_change_list.html'

    # def get_queryset(self):
    #     queryset = self.request.user.documents \
    #         .select_related('publisher') \
    #         .annotate(subscriber_count=Count('subscriber', distinct=True))
    #     return queryset


@login_required
@publisher_required
def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        logger.info('File' + filename + 'at' + uploaded_file_url + 'uploaded!')
        return render(request, 'manager/publishers/simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'manager/publishers/simple_upload.html')


@login_required
@publisher_required
def FileCreateView(request):
    if request.method == 'POST':
        documentForm = DocumentForm(request.POST, request.FILES)
        #historyForm = HistoryForm()
        if documentForm.is_valid():
            document = documentForm.save()
            document.publisher = request.user
            #document.subject = 
            document.save()
            messages.success(request, 'You have successfully uploaded your file.')
            #history = historyForm.save()
            #history.operation = 'c'
            #history.performer = request.user
            #history.document = document
            history = History(operation='c', performer=request.user, document=document)
            history.save()
            #history.date = 
            #logger.info('File' + filename + 'at' + uploaded_file_url + 'uploaded!')
            return redirect('publishers:file_change_list')
    else:
        documentForm = DocumentForm()
    return render(request, 'manager/publishers/file_upload.html', {
            'form' : documentForm
    })


@method_decorator([login_required, publisher_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name', 'subject', )
    context_object_name = 'quiz'
    template_name = 'manager/publishers/quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('publishers:quiz_change', kwargs={'pk': self.object.pk})



# @method_decorator([login_required, publisher_required], name='dispatch')
# class FileUpdateView(UpdateView):
#     model = Document
#     fields = ('description', 'document.name', 'uploaded_at', 'subject', )
#     context_object_name = 'files'
#     template_name = 'manager/publishers/file_change_form.html'

#     # def get_context_data(self, **kwargs):
#     #     kwargs['subscriber'] = self.get_object().subscriber.annotate(subscriber_count=Count('subscriber'))
#     #     return super().get_context_data(**kwargs)

#     def get_queryset(self):
#         '''
#         This method is an implicit object-level permission management
#         This view will only match the ids of existing quizzes that belongs
#         to the logged in user.
#         '''
#         #return self.request.user.file.all()
#         return self.objects.all()

#     def get_success_url(self):
#         return reverse('publishers:file_change', kwargs={'pk' : self.object.pk})



@method_decorator([login_required, publisher_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'manager/publishers/quiz_delete_confirm.html'
    success_url = reverse_lazy('publishers:quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()



@method_decorator([login_required, publisher_required], name='dispatch')
class FileDeleteView(DeleteView):
    model = Document
    context_object_name = 'file'
    template_name = 'manager/publishers/file_delete_confirm.html'
    success_url = reverse_lazy('publishers:file_change_list')

    def delete(self, request, *args, **kwargs):
        file = self.get_object()
        messages.success(request, 'The file %s was deleted successfully!' %file.document.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.documents.all()



@method_decorator([login_required, publisher_required], name='dispatch')
class QuizResultsView(DetailView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'manager/publishers/quiz_results.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related('subscriber__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@method_decorator([login_required, publisher_required], name='dispatch')
class FileResultsView(DetailView):
    
    #model = History
    #context_object_name = 'histories'
    model = Document
    context_object_name = 'file'
    template_name = 'manager/publishers/file_results.html'
    #pk_url_kwarg = 'document_pk'
    # def get_context_data(self, **kwargs):
    #     history = self.get_object()
    #     histories = history.select_related('document').order_by('-date')
    #     total_histories = histories.count()
      #  histories = file.history.select_related('document').order_by('-date')
        #one file - n histories, count how many of each operation, also show the time, better in range(in the last xx days)
    def get_context_data(self, **kwargs):
        #document = self.get_object()
        #history = self.get_object()
        #kwargs['file'] = history.document
        #return super().get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)
        context['file'] = self.get_object().document.name
        context['histories'] = History.objects.filter(document=self.get_object())
        return context
    # def get_queryset(self):
    #     queryset = self.get_object().histories \
    #         .select_related('document') \
    #         .order_by('-date') 
    #         #.annotate(subscriber_count=Count('subscriber', distinct=True))
    #     return queryset
    #def get_queryset(self):
        #document = self.get_object()
        #return History.objects.filter(history__document=document).order_by(-date)


@login_required
@publisher_required
def question_add(request, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # quiz will be able to add questions to it.
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('publishers:question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'manager/publishers/question_add_form.html', {'quiz': quiz, 'form': form})


@login_required
@publisher_required
def question_change(request, quiz_pk, question_pk):
    # Simlar to the `question_add` view, this view is also managing
    # the permissions at object-level. By querying both `quiz` and
    # `question` we are making sure only the owner of the quiz can
    # change its details and also only questions that belongs to this
    # specific quiz can be changed via this url (in cases where the
    # user might have forged/player with the url params.
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    AnswerFormSet = inlineformset_factory(
        Question,  # parent model
        Answer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'),
        min_num=2,
        validate_min=True,
        max_num=10,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('publishers:quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'manager/publishers/question_change_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'formset': formset
    })


@method_decorator([login_required, publisher_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'manager/publishers/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('publishers:quiz_change', kwargs={'pk': question.quiz_id})
