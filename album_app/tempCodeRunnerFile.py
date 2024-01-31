import re
from django.shortcuts import render , redirect,  HttpResponseRedirect, get_object_or_404
from rest_framework import status, mixins, generics
from .models import *
from .serializers import PhotoTableSerializer, BoardSerializer, ReplySerializer, LikedSerializer
import os
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from PIL import Image
from datetime import datetime
from operator import itemgetter
from collections import Counter
from rest_framework.response import Response 
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView, View
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.http import JsonResponse
all_phototags = (
    PhotoTable.objects
    .values_list('board_photo_tag', flat=True)
    .distinct()
        )
print(all_phototags)