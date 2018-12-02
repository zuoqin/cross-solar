from rest_framework.test import APITestCase
from rest_framework import status
from .models import Panel, OneHourElectricity
from datetime import datetime

class PanelTestCase(APITestCase):
    def setUp(self):
        panel = Panel.objects.create(brand="Areva", serial="AAAA1111BBBB2222", latitude=12.345678, longitude=98.7655432)
        OneHourElectricity.objects.create(panel=panel, kilo_watt=11, date_time=datetime(2018,1,1,9) )
        OneHourElectricity.objects.create(panel=panel, kilo_watt=12, date_time=datetime(2018, 1, 1, 10))
        OneHourElectricity.objects.create(panel=panel, kilo_watt=20, date_time=datetime(2018, 1, 2, 11))
        OneHourElectricity.objects.create(panel=panel, kilo_watt=30, date_time=datetime(2018, 1, 2, 12))

    def test_panel_listing(self):
        response = self.client.get('/panel/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_panel_get(self):
        response = self.client.get('/panel/1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["serial"], "AAAA1111BBBB2222")


    def test_panel_analytics_get(self):
        response = self.client.get('/panel/1/analytics/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(list(response.data)[0]['kilo_watt'], 11)


    def test_panel_analytics_day_get(self):
        response = self.client.get('/panel/1/analytics/day/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(list(response.data)[0]['sum'], 23)
        self.assertEqual(list(response.data)[0]["average"], 11.5)
        self.assertEqual(list(response.data)[0]["minimum"], 11)
        self.assertEqual(list(response.data)[0]["maximum"], 12)


        self.assertEqual(list(response.data)[1]['sum'], 50)
        self.assertEqual(list(response.data)[1]["average"], 25)
        self.assertEqual(list(response.data)[1]["minimum"], 20)
        self.assertEqual(list(response.data)[1]["maximum"], 30)

    def test_panel_post_serial_exists(self):
        response = self.client.post('/panel/', {'brand': 'New Barand', 'serial': 'AAAA1111BBBB2222', 'latitude': 67, 'longitude': 45}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_panel_post_serial_16(self):
        response = self.client.post('/panel/', {'brand': 'New Barand', 'serial': 'AAAA1111BBBB222', 'latitude': 67, 'longitude': 45}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_panel_post_bad_latitude(self):
        response = self.client.post('/panel/', {'brand': 'New Barand', 'serial': 'AAAA1111BBBB2227', 'latitude': 97, 'longitude': 45}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_panel_post_bad_longitude(self):
        response = self.client.post('/panel/', {'brand': 'New Barand', 'serial': 'AAAA1111BBBB2227', 'latitude': 67, 'longitude': 245}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_panel_post_ok(self):
        response = self.client.post('/panel/', {'brand': 'New Barand', 'serial': 'AAAA1111BBBB2227', 'latitude': 67, 'longitude': 45}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
