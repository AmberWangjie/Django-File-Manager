from django.urls import include, path
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from .views import manager, subscribers, publishers

urlpatterns = [
    path('', manager.home, name='home'),

    path('subscribers/', include(([
        path('', subscribers.QuizListView.as_view(), name='quiz_list'),
        path('relate-files/', subscribers.RelateFileListView.as_view(), name='related_file_list'),
        path('sub-files/', subscribers.SubFilesListView.as_view(), name='sub_file_list'),
        path('interests/', subscribers.SubscriberInterestsView.as_view(), name='subscriber_interests'),
        path('file-interests/', subscribers.SubscriberFileInterestsView.as_view(), name='subscriber_file_interests'),
        path('taken/', subscribers.TakenQuizListView.as_view(), name='taken_quiz_list'),
        path('quiz/<int:pk>/', subscribers.take_quiz, name='take_quiz'),
    ], 'manager'), namespace='subscribers')),

    path('publishers/', include(([
        path('file/', publishers.FileListView.as_view(), name='file_change_list'),
        path('quiz/', publishers.QuizListView.as_view(), name='quiz_change_list'),
        path('quiz/add/', publishers.QuizCreateView.as_view(), name='quiz_add'),
        path('quiz/<int:pk>/', publishers.QuizUpdateView.as_view(), name='quiz_change'),
        path('quiz/<int:pk>/delete/', publishers.QuizDeleteView.as_view(), name='quiz_delete'),
        path('quiz/<int:pk>/results/', publishers.QuizResultsView.as_view(), name='quiz_results'),
        path('quiz/<int:pk>/question/add/', publishers.question_add, name='question_add'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/', publishers.question_change, name='question_change'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', publishers.QuestionDeleteView.as_view(), name='question_delete'),
       # path('file/', publishers.FileListView.as_view(), name='file_change_list'),
        #path('file/upload/', publishers.simple_upload, name='simple_upload'),
        path('file/upload/', publishers.form_upload, name='form_upload'),
        #path('file/<int:pk>/', publishers.FileUpdateView.as_view(), name='file_change'),
        path('file/<int:pk>/', publishers.FileUpdateView.as_view(), name='file_change'),
        path('file/<int:pk>/results/', publishers.FileResultsView.as_view(), name='file_results'),
    ], 'manager'), namespace='publishers')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
