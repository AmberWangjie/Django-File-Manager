from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_publisher:
            return redirect('publishers:quiz_change_list')
        else:
            return redirect('subscribers:quiz_list')
    return render(request, 'manager/home.html')
