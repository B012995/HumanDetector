# -*- coding: utf-8 -*-
'''
Created on 2017/10/25

@author: CSYSBP01
'''

from rest_framework import serializers

from .models import Count

class CountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Count
        fields = ('cnt', 'created_at')