from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from rest_framework.views import APIView
from rest_framework.response import Response
import googleapiclient.discovery

# Create your views here.

from pathlib import Path

import os
import json

BASE_DIR = Path(__file__).resolve().parent.parent

class GoogleCalendarInitView(APIView):
    def get(self, request):
        client_secrets_path = 'client_secrets.json'
        with open(client_secrets_path, 'r') as f:
            client_secrets = json.load(f)


        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes=settings.GOOGLE_CALENDAR_SCOPE, redirect_uri=settings.GOOGLE_REDIRECT_URI)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
        )
        request.session['state'] = state
        return redirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        state = request.session.pop('state', None)
        if not state:
            return Response({'error': 'Invalid state parameter'})

        client_secrets_path = os.path.join(BASE_DIR, 'client_secrets.json')
        with open(client_secrets_path, 'r') as f:
            client_secrets = json.load(f)

        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes=settings.GOOGLE_CALENDAR_SCOPE, redirect_uri=settings.GOOGLE_REDIRECT_URI)

        flow.fetch_token(authorization_response=request.build_absolute_uri(), state=state)

        credentials = flow.credentials

        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

        events = service.events().list(calendarId='primary').execute()

        return Response(events)




        