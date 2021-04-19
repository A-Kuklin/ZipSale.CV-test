from django.db import models


class GitUser(models.Model):
    GitHubUser = models.CharField(max_length=39, blank=True, null=True)
