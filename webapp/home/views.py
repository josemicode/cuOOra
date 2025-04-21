from django.shortcuts import render, get_object_or_404, redirect
from users.models import Question, SocialRetriever, PopularTodayRetriever, TopicRetriever, NewsRetriever, Topic, Answer
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from users.models import Vote
from django.db.models import Count, Q




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

@login_required(login_url='login')
def questions_list_view(request):
    preguntas = (
        Question.objects
        .select_related("user")
        .prefetch_related("topics")
        .annotate(
            positive_votes_count=Count(
                'votes',
                filter=Q(votes__is_positive_vote=True)
            ),
            negative_votes_count=Count(
                'votes',
                filter=Q(votes__is_positive_vote=False)
            )
        )
        .order_by("-timestamp")
    )
    return render(request, "questions_list.html", {"preguntas": preguntas})

@api_view(['GET'])
@login_required
def pregunta_detalle_api(request, id):
    pregunta = get_object_or_404(Question, id=id)

    # Averiguamos si este usuario ya votó aquí
    content_type = ContentType.objects.get_for_model(Question)
    try:
        vote = Vote.objects.get(
            user=request.user,
            specific_subclass=content_type,
            object_id=pregunta.id
        )
        user_vote = 'like' if vote.is_positive_vote else 'dislike'
    except Vote.DoesNotExist:
        user_vote = None

    data = {
        'title': pregunta.title,
        'description': pregunta.description,
        'username': pregunta.user.username,
        'timestamp': pregunta.timestamp.strftime('%d %B %Y %H:%M'),
        'topics': [t.name for t in pregunta.topics.all()],
        'positive_votes': pregunta.positive_votes().count(),
        'negative_votes': pregunta.negative_votes().count(),
        'user_vote': user_vote,
    }
    return JsonResponse(data)

@login_required(login_url='login')
def topics(request):
    topics = Topic.objects.all()
    return render(request, "topics.html", {"topics": topics})

@login_required(login_url='login')
def responder_pregunta(request, pk):
    question = get_object_or_404(Question, pk=pk)
    respuestas = Answer.objects.filter(question=question)

    if request.method == 'POST':
        contenido = request.POST.get('description')
        if contenido:
            Answer.objects.create(
                user=request.user,
                question=question,
                description=contenido
            )
            return redirect('responder_pregunta', pk=question.pk)

    return render(request, 'responder_pregunta.html', {
        'question': question,
        'respuestas': respuestas,
    })
    
@login_required
def update_username(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu nombre de usuario ha sido actualizado.")
            return redirect('home')  # O la página a la que quieras redirigir después
    else:
        form = UserChangeForm(instance=request.user)
    
    return render(request, 'update_username.html', {'form': form})


class CustomLogoutView(LogoutView):
    next_page = '/home/'  # Redirigir al home después de cerrar sesión
    

class CustomLoginView(LoginView):
    template_name = 'login.html'  # Ruta a tu template
    redirect_authenticated_user = True


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')
    
def test_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            return render(request, 'success.html', {'user': user})
        else:
            return render(request, 'error.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'login_test.html')

# views.py


def home_view(request):
    user = request.user
    recommender = request.GET.get("recommender", "general")

    # 1️⃣ Construyo la queryset base anotada con los conteos de votos
    preguntas_base = (
        Question.objects
        .select_related('user')
        .prefetch_related('topics')
        .annotate(
            positive_votes_count=Count(
                'votes', filter=Q(votes__is_positive_vote=True)
            ),
            negative_votes_count=Count(
                'votes', filter=Q(votes__is_positive_vote=False)
            )
        )
    )

    # 2️⃣ Aplico el recommender sobre esa queryset anotada
    if recommender == "popular":
        preguntas = PopularTodayRetriever().retrieve_questions(preguntas_base, user)
    elif recommender == "reciente":
        preguntas = NewsRetriever().retrieve_questions(preguntas_base, user)
    elif recommender == "relevante":
        preguntas = TopicRetriever().retrieve_questions(preguntas_base, user)
    elif recommender == "social":
        preguntas = SocialRetriever().retrieve_questions(preguntas_base, user)
    else:
        # “general”: convierto en lista para conservar las anotaciones
        preguntas = list(preguntas_base)

    # 3️⃣ Topics destacados (igual que antes)
    topic_order = request.GET.get("topic_order", "popular")
    if topic_order == "recientes":
        topics = Topic.objects.order_by('-created_at')[:4]
    elif topic_order == "alfabetico":
        topics = Topic.objects.order_by('name')[:4]
    else:
        topics = Topic.objects.order_by('-num_questions')[:4]

    return render(request, "home.html", {
        "preguntas": preguntas,
        "topics": topics,
        "active_recommender": recommender,
        "active_topic_order": topic_order,
    })



def topic_detail(request, id):
    topic = get_object_or_404(Topic, id=id)
    return JsonResponse({
        "id": topic.id,
        "name": topic.name,
        "description": topic.description,
    })
    
@login_required
@require_POST
def vote_pregunta_api(request, id):
    pregunta = get_object_or_404(Question, id=id)
    voto_tipo = request.POST.get('vote')       # “like” o “dislike”
    is_like = voto_tipo == 'like'

    vote, created = Vote.objects.update_or_create(
        user=request.user,
        specific_subclass=ContentType.objects.get_for_model(Question),
        object_id=pregunta.id,
        defaults={'is_positive_vote': is_like}
    )

    return JsonResponse({
        'positive_votes': pregunta.positive_votes().count(),
        'negative_votes': pregunta.negative_votes().count(),
    })