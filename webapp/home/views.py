from django.shortcuts import render, get_object_or_404
from users.models import Question, SocialRetriever, Topic
from django.http import JsonResponse

def home(request):
    preguntas = Question.objects.select_related('user').all()[:4]
    topics = Topic.objects.all()[:4]
    return render(request, 'home.html', {'preguntas': preguntas, 'topics':topics})

def socials(request):
    user = request.user
    questions = Question.objects.all()
    retrieved_questions = SocialRetriever().retrieve_questions(questions, user)
    context = {"questions": retrieved_questions}
    return render(request, 'recommended.html', context)

def questions_list_view(request):
    preguntas = Question.objects.select_related("user").prefetch_related("topics").all().order_by("-timestamp")
    return render(request, "questions_list.html", {"preguntas": preguntas})


def pregunta_detalle_api(request, id):
    pregunta = get_object_or_404(Question, id=id)
    data = {
        'title': pregunta.title,
        'description': pregunta.description,
        'username': pregunta.user.username,
        'timestamp': pregunta.timestamp.strftime('%d %B %Y %H:%M'),
        'topics': [t.name for t in pregunta.topics.all()]
    }
    return JsonResponse(data)

def topics(request):
    topics = Topic.objects.all()
    return render(request, "topics.html", {"topics": topics})