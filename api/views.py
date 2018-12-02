from rest_framework import viewsets,status
from rest_framework.views import APIView, Response
from .models import Panel, OneHourElectricity
from .serializers import PanelSerializer, OneHourElectricitySerializer
import pandas as pd

from datetime import date, datetime, timedelta

class PanelViewSet(viewsets.ModelViewSet):
    queryset = Panel.objects.all()
    serializer_class = PanelSerializer
    def create(self, request):
        serializer = PanelSerializer(data=request.data)
        if float(request.data['longitude']) < -180 or float(request.data['longitude']) > 180:
            return Response("longitude should be -180 .. 180", status=status.HTTP_400_BAD_REQUEST)
        if float(request.data['latitude']) < -90 or float(request.data['latitude']) > 90:
            return Response("latitude should be -90 .. 90", status=status.HTTP_400_BAD_REQUEST)
        if len(request.data['serial']) != 16:
            return Response("serial should be 16 characters length", status=status.HTTP_400_BAD_REQUEST)

        queryset = Panel.objects.filter(serial=request.data['serial'])
        items = PanelSerializer(queryset, many=True)
        if len(items.data) > 0:
            return Response("serial {} already exists".format(request.data['serial']),
                            status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HourAnalyticsView(APIView):
    serializer_class = OneHourElectricitySerializer
    def get(self, request, panelid):
        panelid = int(self.kwargs.get('panelid', 0))
        queryset = OneHourElectricity.objects.filter(panel_id=panelid)
        items = OneHourElectricitySerializer(queryset, many=True)
        return Response(items.data)

    def post(self, request, panelid):
        panelid = int(self.kwargs.get('panelid', 0))
        serializer = OneHourElectricitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DayAnalyticsView(APIView):
    def get(self, request, panelid):
        # Please implement this method to return Panel's daily analytics data
        panelid = int(self.kwargs.get('panelid', 0))
        queryset = OneHourElectricity.objects.filter(panel_id=panelid)
        items = OneHourElectricitySerializer(queryset, many=True)

        data = []
        for item in items.data[:]:
            data.append({'id': item['id'], 'date':  datetime.strptime(item['date_time'][:10], '%Y-%m-%d').date(), 'value': item['kilo_watt']})
        df = pd.DataFrame(data=data)
        sum = df.groupby(['date'])['value'].agg([('sum', 'sum'), ('average', 'mean'), ('minimum' , 'min'), ('maximum', 'max')]).reset_index()
        sum.columns = ['date_time', 'sum', 'average', 'minimum', 'maximum']
        sum.sort_index()
        return Response(sum.T.to_dict().values())