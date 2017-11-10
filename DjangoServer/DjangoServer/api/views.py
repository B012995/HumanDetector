# -*- coding: utf-8 -*-
#from django.shortcuts import render

from rest_framework.generics import ListAPIView

from .models import Count
from .serializer import CountSerializer  # @UnresolvedImport
# Create your views here.

class CountListAPIView(ListAPIView):
#    queryset = Count.objects.all().order_by('-created_at')

    def get_queryset(self):

        if 'latest' in self.request.GET:    #指定した分だけ直近の人数を取得
            latest_value = int(self.request.GET.get(key="latest", default=1))
            return Count.objects.all().order_by('-created_at')[:latest_value]

        elif 'from' in self.request.GET and 'to' in self.request.GET:   #指定した期間の人数を取得
            from_value = self.request.GET.get(key="from")
            to_value = self.request.GET.get(key="to")
            return Count.objects.all().filter(created_at__gte=from_value,created_at__lte=to_value)

    serializer_class = CountSerializer
#     queryset = Count.objects.all()


# class CountDetailAPIView(RetrieveAPIView):
#     queryset = Count.objects.all()
#     serializer_class = CountSerializer
#     lookup_field = 'cnt'


# class CountViewSet(viewsets.ModelViewSet):
#
#     def get(self, request):
#         if 'latest' in request.GET:
#             latest_value = request.GET.get(key="latest", default=10)
#             queryset = Count.objects.all().order_by('-created_at')[:latest_value]
#         elif ('from' in request.GET) and ('to' in request.GET):
#             from_value = request.GET.get('from')
#             to_value = request.GET.get('to')
# #         else:
#
#     queryset = Count.objects.all()
#     serializer_class = CountSerializer
# #     filter_fields = ('cnt', 'created_at')