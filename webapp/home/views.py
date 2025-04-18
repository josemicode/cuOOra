from django.shortcuts import render
from users.models import Question, SocialRetriever, Topic

def home(request):
    preguntas = Question.objects.select_related('user').all()
    return render(request, 'home.html', {'preguntas': preguntas})

def socials(request):
    user = request.user
    questions = Question.objects.all()
    retrieved_questions = SocialRetriever().retrieve_questions(questions, user)
    context = {"questions": retrieved_questions}
    return render(request, 'recommended.html', context)

def questions_list_view(request):
    preguntas = Question.objects.select_related("user").prefetch_related("topics").all().order_by("-timestamp")
    return render(request, "questions_list.html", {"preguntas": preguntas})

def topics(request):
    topics = Topic.objects.all()
    return render(request, "topics.html", {"topics": topics})