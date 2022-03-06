from django.apps import AppConfig


class BookclubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookclub'

class HumanizeConfig(AppConfig):
    name = 'django.contrib.humanize'
    verbose_name = ("Humanize")