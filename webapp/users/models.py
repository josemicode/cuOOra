from django.db import models
from django.contrib.auth.models import AbstractUser

#? Reimplement, add CuOOra context
class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    #...
    #* votes is referenced
    #* questions is referenced

class Answer(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    #? Autoset...
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    #* votes is referenced
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="answers", null=True)

    def _filter_votes(self, positive):
        return [vote for vote in self.votes if vote.is_like() == positive]

    def positive_votes(self):
        return self._filter_votes(True)
    
    def negative_votes(self):
        return self._filter_votes(False)

    def get_question(self):
        return self.question
		
    def get_user(self):
        return self.user

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description
	
    def get_timestamp(self):
        return self.timestamp

    def add_vote(self, a_vote):
        if any(vote.user == a_vote.user for vote in self.votes):
            raise ValueError("Este usuario ya ha votado")
        self.votes.append(a_vote)

    def get_votes(self):
        return self.votes

class Topic(models.Model):
    name = models.CharField(max_length=75)
    description = models.TextField()
    #* questions is referenced

    def add_question(self, a_question):
        self.questions.append(a_question)

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_questions(self):
        return self.questions

class Question(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    #* answers is referenced
    #* votes is referenced
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    topics = models.ManyToManyField(Topic, related_name="questions")

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def _filter_votes(self, positive: bool):
        return [vote for vote in self.votes if vote.is_like() == positive]

    def positive_votes(self):
        return self._filter_votes(True)
    
    def negative_votes(self):
        return self._filter_votes(False)

    def get_topics(self):
        return self.topics

    def get_title(self):
        return self.title
    
    def set_title(self, a_title):
        self.title = a_title

    def get_user(self):
        return self.user

    def get_timestamp(self):
        return self.timestamp

    def get_votes(self):
        return self.votes

    def add_vote(self, a_vote):
        if any(vote.user == a_vote.user for vote in self.votes): 
            raise ValueError("Este usuario ya ha votado")
        self.votes.append(a_vote)

    def add_topic(self, a_topic):
        if a_topic in self.topics:
            raise ValueError("El topico ya esta agregado.")
        self.topics.append(a_topic)
        a_topic.add_question(self)

    def add_answer(self, answer):
        self.answers.append(answer)

    def get_best_answer(self):
        if not self.answers:
            return None
        
        return sorted(self.answers, key=lambda a: len(a.positive_votes()) - len(a.negative_votes()), reverse=True)[0]

class Vote(models.Model):
    is_positive_vote = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    answer = models.ForeignKey(Answer , on_delete=models.CASCADE, related_name="votes")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="votes", null=True)

    #...
    def is_like(self):
        return self.is_positive_vote
    
    def get_user(self):
        return self.user

    def like(self):
        self.is_positive_vote = True

    def dislike(self):
        self.is_positive_vote = False