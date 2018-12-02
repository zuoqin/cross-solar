from rest_framework import serializers
from .models import Panel, OneHourElectricity

class PanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panel
        fields = ('id', 'brand', 'serial', 'latitude', 'longitude')

class OneHourElectricitySerializer(serializers.ModelSerializer):
    class Meta:
        panel = serializers.PrimaryKeyRelatedField(queryset=Panel.objects.all())
        model = OneHourElectricity
        fields = ('id', 'panel', 'kilo_watt','date_time')