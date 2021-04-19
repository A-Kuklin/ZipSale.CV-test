from django.contrib import admin

from .models import GitUser


class GitUserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'GitHubUser')
    search_fields = ('GitHubUser',)
    list_filter = ('GitHubUser',)
    empty_value_display = "-пусто-"


admin.site.register(GitUser, GitUserAdmin)
