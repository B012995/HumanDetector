from django.apps import AppConfig
# from .thread import WriteThread

class ApiConfig(AppConfig):
    name = 'api'

#     def ready(self):
#         w = WriteThread(10)