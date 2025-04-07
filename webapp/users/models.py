from django.db import models
from django.contrib.auth.models import AbstractUser

#? Reimplement, add CuOOra context
class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
     
class Vote(models.Model):
    is_positive_vote = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    #...
    def is_like(self):
        return self.is_positive_vote
    
    def get_user(self):
        pass #* First, assign foreign key

    def like(self):
        self.is_positive_vote = True

    def dislike(self):
        self.is_positive_vote = False