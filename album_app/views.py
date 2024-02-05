
from django.shortcuts import render , redirect,  HttpResponseRedirect, get_object_or_404
from rest_framework import status, mixins, generics
from .models import *
from .serializers import PhotoTableSerializer, BoardSerializer, ReplySerializer, LikedSerializer, RecommendContentsSerializer
import os
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from typing import List, Dict
from datetime import datetime

# import torchvision.transforms as transforms
from operator import itemgetter

from collections import Counter
from rest_framework.response import Response 
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView, View
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .modules.yolo_detection import detect

from uuid import uuid4
from django.core.files.storage import FileSystemStorage


# Create your views here.
def index(request):
    return render(request, 'album_app/index.html')

def mypage_album(request):
    return render(request, 'album_app/mypage_album.html')

def mypage_mypost(request):
    return render(request, 'album_app/mypage_mypost.html')

def mypage_myreply(request):
    return render(request, 'album_app/mypage_myreply.html')

# def classification(request):    
#     file_names = ['2004-01-01_17.jpg','2004-04-01_21.jpg','2004-06-01_6.jpg']

#     # 객체 탐지 함수 호출
#     items = detect(file_names) # 이미지 파일명 전달 
    
#     return render(request, 'album_app/classification.html', {'items' : items, 'alltags' : alltags})

class Classification(generics.ListAPIView):
    serializer_class = PhotoTableSerializer
    
    def get_queryset(self):        
        fileNames = self.request.GET.getlist('fileNames[]')
        items = detect(fileNames) # 이미지 파일명 전달 
        return items
    
    def get(self, request, *args, **kwargs):    
             
        # print(request.session.items())    
        return self.list(request, *args, **kwargs)
    
@api_view(['POST'])
def save_data(request, username):
    if request.method == 'POST':
        
        # Serializer 객체 생성
        serializer = PhotoTableSerializer()        
       
        user = UsersAppUser.objects.filter(username=username) 

        data_list = []
        
        for data in request.data:
            # 원하는 id 값을 data에 추가
            data['id'] = user[0].id 
            # Serializer에 데이터를 직접 전달하여 객체 생성
            serializer = PhotoTableSerializer(data=data)

            if serializer.is_valid():
                # 데이터 유효성 검사 후 저장
                serializer.save()
                data_list.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(data_list, status=status.HTTP_201_CREATED)
    
class PhotoTableAPIMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    serializer_class = PhotoTableSerializer
    
    def get_queryset(self):
        # username = request.query_params.get('username')        
        username = self.kwargs.get('username')
        user = UsersAppUser.objects.filter(username=username) 

        return PhotoTable.objects.filter(id=user[0].id).order_by('-photodate').all()  # 완전일치 검색
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class MyAlbumDel(mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = PhotoTable.objects.all()
    serializer_class = PhotoTableSerializer
    lookup_field = "photoid"  # 기본키

    # DELETE : bookno 전달 받고, bookno에 해당되는 1개의 도서 정보 삭제 (destroy)
    def delete(self, request, *args, **kwargs):  # DELETE 메소드 처리 함수 (1권 삭제)
        return self.destroy(request, *args, **kwargs)  # mixins.DestroyModelMixin와 연결

# 사진 1장 수정
class MyAlbumUpdate(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = PhotoTable.objects.all()
    serializer_class = PhotoTableSerializer
    lookup_field = "photoid"  # 기본키

    # GET : bookno 전달 받고, bookno에 해당되는 1개의 도서 정보 반환 (retrieve)
    def get(self, request, *args, **kwargs):  # GET 메소드 처리 함수 (1권 조회)
        return self.retrieve(request, *args, **kwargs)  # mixins.RetrieveModelMixin와 연결

    # PUT : bookno 전달 받고, bookno에 해당되는 1개의 도서 정보 수정 (update)
    def put(self, request, *args, **kwargs):  # PUT 메소드 처리 함수 (1권 수정)        
        return self.update(request, *args, **kwargs)  # mixins.UpdateModelMixin와 연결

    # DELETE : bookno 전달 받고, bookno에 해당되는 1개의 도서 정보 삭제 (destroy)
    def delete(self, request, *args, **kwargs):  # DELETE 메소드 처리 함수 (1권 삭제)
        return self.destroy(request, *args, **kwargs)  # mixins.DestroyModelMixin와 연결

@api_view(['PUT'])
def album_update(request, photoid):
    try:
        instance = PhotoTable.objects.get(photoid=photoid)
    except PhotoTable.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = PhotoTableSerializer(instance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# 유저에 맞는 컨텐츠 출력
@api_view(['GET'])
def combined_api_view(request, **kwargs):
    username = kwargs.get('username')

    # 사용자 정보 가져오기
    user = UsersAppUser.objects.filter(username=username).first()

    if user:
        # 해당 사용자의 ID 가져오기
        user_id = user.id

        # 연도별 태그별 이미지 카운트
        data = (
            PhotoTable.objects
            .filter(id=user_id, uploaddate__year=2023)
            .values('phototag')
        )

        # 2023년 태그 추출
        tags_2023 = []
        for entry in data:
            tags = entry['phototag'].split('#')
            for tag in tags:
                tagname = tag.strip()
                if tagname:
                    tags_2023.append(tagname)
        tag_counts = Counter(tags_2023)

        top_tags_2023 = tag_counts.most_common(4)
        
        recommend_contents_data = []

        for tag, _ in top_tags_2023:
            tag_data = RecommendContents.objects.filter(phototag__contains=tag)
            recommend_contents_data.extend(tag_data[:4])  # 상위 3개의 데이터만 추가
        
        # Serialize 데이터
        serializer = RecommendContentsSerializer(recommend_contents_data, many=True)

        return Response(serializer.data)
    
    return Response([])


# 개인 분석차트 
@api_view(['GET'])
def personal_chart(request, **kwargs):
    # login_id= request.user.id # 로그인한 id 불러오기 
    # print(login_id)
    username= kwargs.get('username')
    
    result= UsersAppUser.objects.filter(username=username)
    ls= result.values_list('id',flat=True)
    id = ls[0] if ls else None
    print(id)

    name_list =[ '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트',
          '벤치', '새', '고양이', '강아지', '양', '소', '코끼리', '곰', '얼룩말', '기린',
            '가방', '우산', '핸드백', '넥타이', '캐리어', '스키', '스노우보드', '공', '야구배트',
          '야구글러브', '스케이트보드', '테니스라켓', '물병', '와인잔', '컵', '포크', 
          '나이프', '숟가락', '접시', '바나나', '사과', '샌드위치', '오렌지', '브로콜리',
            '당근', '핫도그', '피자', '도넛', '케이크', '소파', '화분', '침대', '식탁', 
            '텔레비전', '컴퓨터', '마우스', '키보드', '전화기', '전자레인지', '오븐', 
            '토스터기', '싱크대', '냉장고', '책', '꽃병', '곰인형',
            '장신구', '에어프라이어', '비행기날개', '백팩', '풍선','아이들' 
            '맥주잔', '카메라', '양초', '건배', '전시된옷', '화장품', '십자가', 
            '에펠탑', '안경', '등대', '바베큐고기', '원판(덤벨 및 바벨)',
            '포장고기','바지', '휴대폰뒷면', '턱걸이', '케이블카', 
            '러닝머신', '신발','소주잔', '선글라스', '일출(일몰)', 
            '사원', '상의', '손목시계']
    data_dict = {}
    data_list = []    
    

    for i, name in enumerate(name_list):
        count = len(PhotoTable.objects.filter(phototag__contains=name, id=id)) # 특정 id에 해당
        data_dict['tagname'] = name_list[i]
        data_dict['tagcount'] = count
        # data_dict['login_id']= id      
        data_list.append(data_dict)
        data_dict = {}    

    # tag가 하나 이상 존재하는 것만 뽑아서 내림차순으로 정렬함 
    filtered_list = [item for item in data_list if item['tagcount'] != 0]
    result_top10 = sorted(filtered_list, key=lambda x: x['tagcount'], reverse=True)
    
    return Response(result_top10)

# 개인분석 -연도별
@api_view(['GET'])
def personal_chart_yearly(request, **kwargs):
    username = kwargs.get('username')

    # 사용자 정보 가져오기
    user = UsersAppUser.objects.filter(username=username).first()
    name_list =[ '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트',
          '벤치', '새', '고양이', '강아지', '양', '소', '코끼리', '곰', '얼룩말', '기린',
            '가방', '우산', '핸드백', '넥타이', '캐리어', '스키', '스노우보드', '공', '야구배트',
          '야구글러브', '스케이트보드', '테니스라켓', '물병', '와인잔', '컵', '포크', 
          '나이프', '숟가락', '접시', '바나나', '사과', '샌드위치', '오렌지', '브로콜리',
            '당근', '핫도그', '피자', '도넛', '케이크', '소파', '화분', '침대', '식탁', 
            '텔레비전', '컴퓨터', '마우스', '키보드', '전화기', '전자레인지', '오븐', 
            '토스터기', '싱크대', '냉장고', '책', '꽃병', '곰인형',
            '장신구', '에어프라이어', '비행기날개', '백팩', '풍선','아이들' 
            '맥주잔', '카메라', '양초', '건배', '전시된옷', '화장품', '십자가', 
            '에펠탑', '안경', '등대', '바베큐고기', '원판(덤벨 및 바벨)',
            '포장고기','바지', '휴대폰뒷면', '턱걸이', '케이블카', 
            '러닝머신', '신발','소주잔', '선글라스', '일출(일몰)', 
            '사원', '상의', '손목시계']

    if user:
        # 해당 사용자의 ID 가져오기
        user_id = user.id

        # 2004년부터 2009년까지 연도별 태그별 이미지 카운트
        data = (
            PhotoTable.objects
            .filter(id=user_id, uploaddate__year__range=(2004, 2024))
            .values('phototag', 'uploaddate__year')
        )

        # 결과를 딕셔너리 형태로 구성
        result_dict = {}
        for entry in data:
            year = entry['uploaddate__year']
            tags = entry['phototag'].split('#')  # #으로 구분된 태그 파싱
            for tag in tags:
                tagname = tag.strip()  # 태그 양쪽의 공백 제거
                if not tagname:
                    continue  # 빈 문자열이면 스킵

                if tagname in name_list:
                    if year not in result_dict:
                        result_dict[year] = {}

                    if tagname not in result_dict[year]:
                        result_dict[year][tagname] = 1
                    else:
                        result_dict[year][tagname] += 1

        # 연도별 리스트로 구성
        result_list = []
        for year, tags in result_dict.items():
            tags_list = [{'tagname': tagname, 'tagcount': tagcount} for tagname, tagcount in tags.items()]
            result_list.append({'year': year, 'tags': tags_list})

        return Response(result_list)

# 연도별 개인분석 top3
@api_view(['GET'])
def personal_chart_yearly_top3(request, **kwargs):
    username = kwargs.get('username')

    # 사용자 정보 가져오기
    user = UsersAppUser.objects.filter(username=username).first()
    name_list =[ '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트',
          '벤치', '새', '고양이', '강아지', '양', '소', '코끼리', '곰', '얼룩말', '기린',
            '가방', '우산', '핸드백', '넥타이', '캐리어', '스키', '스노우보드', '공', '야구배트',
          '야구글러브', '스케이트보드', '테니스라켓', '물병', '와인잔', '컵', '포크', 
          '나이프', '숟가락', '접시', '바나나', '사과', '샌드위치', '오렌지', '브로콜리',
            '당근', '핫도그', '피자', '도넛', '케이크', '소파', '화분', '침대', '식탁', 
            '텔레비전', '컴퓨터', '마우스', '키보드', '전화기', '전자레인지', '오븐', 
            '토스터기', '싱크대', '냉장고', '책', '꽃병', '곰인형',
            '장신구', '에어프라이어', '비행기날개', '백팩', '풍선','아이들' 
            '맥주잔', '카메라', '양초', '건배', '전시된옷', '화장품', '십자가', 
            '에펠탑', '안경', '등대', '바베큐고기', '원판(덤벨 및 바벨)',
            '포장고기','바지', '휴대폰뒷면', '턱걸이', '케이블카', 
            '러닝머신', '신발','소주잔', '선글라스', '일출(일몰)', 
            '사원', '상의', '손목시계']

    if user:
        # 해당 사용자의 ID 가져오기
        user_id = user.id

        # 연도별 태그별 이미지 카운트
        data = (
            PhotoTable.objects
            .filter(id=user_id, uploaddate__year__range=(2018, 2024))
            .values('uploaddate__year', 'phototag')
        )

        # 결과를 딕셔너리 형태로 구성
        result_dict = {}
        for entry in data:
            year = entry['uploaddate__year']
            tags = entry['phototag'].split('#')  # #으로 구분된 태그 파싱
            for tag in tags:
                tagname = tag.strip()  # 태그 양쪽의 공백 제거
                if not tagname or tagname not in name_list:
                    continue  # 빈 문자열이거나 지정된 태그가 아니면 스킵

                if year not in result_dict:
                    result_dict[year] = {}

                if tagname not in result_dict[year]:
                    result_dict[year][tagname] = 1
                else:
                    result_dict[year][tagname] += 1

        # 연도별 Top 3 태그 구성
        result_list = []
        for year, tags in result_dict.items():
            sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:3]
            tags_list = [{'tagname': tagname, 'tagcount': tagcount} for tagname, tagcount in sorted_tags]
            result_list.append({'year': year, 'top_tags': tags_list})

        return Response(result_list)

    


# 전체 분석 차트 
@api_view(['GET'])
def tag_chart(request):
    name_list =[ '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트',
          '벤치', '새', '고양이', '강아지', '양', '소', '코끼리', '곰', '얼룩말', '기린',
            '가방', '우산', '핸드백', '넥타이', '캐리어', '스키', '스노우보드', '공', '야구배트',
          '야구글러브', '스케이트보드', '테니스라켓', '물병', '와인잔', '컵', '포크', 
          '나이프', '숟가락', '접시', '바나나', '사과', '샌드위치', '오렌지', '브로콜리',
            '당근', '핫도그', '피자', '도넛', '케이크', '소파', '화분', '침대', '식탁', 
            '텔레비전', '컴퓨터', '마우스', '키보드', '전화기', '전자레인지', '오븐', 
            '토스터기', '싱크대', '냉장고', '책', '꽃병', '곰인형',
            '장신구', '에어프라이어', '비행기날개', '백팩', '풍선','아이들' 
            '맥주잔', '카메라', '양초', '건배', '전시된옷', '화장품', '십자가', 
            '에펠탑', '안경', '등대', '바베큐고기', '원판(덤벨 및 바벨)',
            '포장고기','바지', '휴대폰뒷면', '턱걸이', '케이블카', 
            '러닝머신', '신발','소주잔', '선글라스', '일출(일몰)', 
            '사원', '상의', '손목시계']
    data_dict = {}
    data_list = []    
    

    for i, name in enumerate(name_list):
        count = len(PhotoTable.objects.filter(phototag__contains=name)) # 특정 id에 해당
        data_dict['tagname'] = name_list[i]
        data_dict['tagcount'] = count
        # data_dict['login_id']= id      
        data_list.append(data_dict)
        data_dict = {}    

    # tag가 하나 이상 존재하는 것만 뽑아서 내림차순으로 정렬함 
    filtered_list = [item for item in data_list if item['tagcount'] != 0]
    result_top10 = sorted(filtered_list, key=lambda x: x['tagcount'], reverse=True)
    
    return Response(result_top10)

# 최근 5개년 연도별 top3
@api_view(['GET'])
def tag_chart_yearly_top3(request):
    lis=[ '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트',
          '벤치', '새', '고양이', '강아지', '양', '소', '코끼리', '곰', '얼룩말', '기린',
            '가방', '우산', '핸드백', '넥타이', '캐리어', '스키', '스노우보드', '공', '야구배트',
          '야구글러브', '스케이트보드', '테니스라켓', '물병', '와인잔', '컵', '포크', 
          '나이프', '숟가락', '접시', '바나나', '사과', '샌드위치', '오렌지', '브로콜리',
            '당근', '핫도그', '피자', '도넛', '케이크', '소파', '화분', '침대', '식탁', 
            '텔레비전', '컴퓨터', '마우스', '키보드', '전화기', '전자레인지', '오븐', 
            '토스터기', '싱크대', '냉장고', '책', '꽃병', '곰인형',
            '장신구', '에어프라이어', '비행기날개', '백팩', '풍선','아이들' ,
            '맥주잔', '카메라', '양초', '건배', '전시된옷', '화장품', '십자가', 
            '에펠탑', '안경', '등대', '바베큐고기', '원판(덤벨 및 바벨)',
            '포장고기','바지', '휴대폰뒷면', '턱걸이', '케이블카', 
            '러닝머신', '신발','소주잔', '선글라스', '일출(일몰)', 
            '사원', '상의', '손목시계']

    data_list = []

    for year in range(2019, 2024):
        top3_for_year = []
        for i, name in enumerate(lis):
            tag_count = (
                PhotoTable.objects
                .filter(phototag__contains=name, uploaddate__year=year)
                .count()
            )

            data_dict = {
                'tagname': name,
                'tagcount': tag_count
            }
            top3_for_year.append(data_dict)

        sorted_top3_for_year = sorted(top3_for_year, key=lambda x: x['tagcount'], reverse=True)[:3]
        result_dict = {
            'year': year,
            'top3_tags': sorted_top3_for_year
        }
        data_list.append(result_dict)


    return Response(data_list)



# 전체 분석 차트 - 연도별 분석
@api_view(['GET'])
def tag_chart_yearly(request):
    lis=[ '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트',
          '벤치', '새', '고양이', '강아지', '양', '소', '코끼리', '곰', '얼룩말', '기린',
            '가방', '우산', '핸드백', '넥타이', '캐리어', '스키', '스노우보드', '공', '야구배트',
          '야구글러브', '스케이트보드', '테니스라켓', '물병', '와인잔', '컵', '포크', 
          '나이프', '숟가락', '접시', '바나나', '사과', '샌드위치', '오렌지', '브로콜리',
            '당근', '핫도그', '피자', '도넛', '케이크', '소파', '화분', '침대', '식탁', 
            '텔레비전', '컴퓨터', '마우스', '키보드', '전화기', '전자레인지', '오븐', 
            '토스터기', '싱크대', '냉장고', '책', '꽃병', '곰인형',
            '장신구', '에어프라이어', '비행기날개', '백팩', '풍선','아이들' ,
            '맥주잔', '카메라', '양초', '건배', '전시된옷', '화장품', '십자가', 
            '에펠탑', '안경', '등대', '바베큐고기', '원판(덤벨 및 바벨)',
            '포장고기','바지', '휴대폰뒷면', '턱걸이', '케이블카', 
            '러닝머신', '신발','소주잔', '선글라스', '일출(일몰)', 
            '사원', '상의', '손목시계']
    
    try:
        result=[]
        

        for year in range(2004, 2024):
            start_month = 1 
            end_month = 12  

            for month in range(start_month, end_month + 1):
                    monthly_data = PhotoTable.objects.filter(uploaddate__year=year, uploaddate__month=month)

                    tag_counter = Counter(tag for data in monthly_data for tag in data.phototag.split('#') if tag in lis)

                    monthly_result = [{'tagname': tag, 'tagcount': tag_counter[tag]} for tag in lis]

                    final_result=[tag for tag in monthly_result if tag['tagcount'] != 0]

                    result_sorted= sorted(final_result, key=lambda x: x['tagcount'], reverse=True)


                    result.append({'year': year, 'month': month, 'tags': result_sorted})
                    

        return Response(result, status=status.HTTP_200_OK)

    except PhotoTable.DoesNotExist:
        return Response({'error': 'No data found for the specified month range'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 전체 분석 - 태그별 연도 당 갯수 
@api_view(['GET'])
def tag_count_yearly_chart(request):
    lis=[ '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트',
          '벤치', '새', '고양이', '강아지', '양', '소', '코끼리', '곰', '얼룩말', '기린',
            '가방', '우산', '핸드백', '넥타이', '캐리어', '스키', '스노우보드', '공', '야구배트',
          '야구글러브', '스케이트보드', '테니스라켓', '물병', '와인잔', '컵', '포크', 
          '나이프', '숟가락', '접시', '바나나', '사과', '샌드위치', '오렌지', '브로콜리',
            '당근', '핫도그', '피자', '도넛', '케이크', '소파', '화분', '침대', '식탁', 
            '텔레비전', '컴퓨터', '마우스', '키보드', '전화기', '전자레인지', '오븐', 
            '토스터기', '싱크대', '냉장고', '책', '꽃병', '곰인형',
            '장신구', '에어프라이어', '비행기날개', '백팩', '풍선','아이들' ,
            '맥주잔', '카메라', '양초', '건배', '전시된옷', '화장품', '십자가', 
            '에펠탑', '안경', '등대', '바베큐고기', '원판(덤벨 및 바벨)',
            '포장고기','바지', '휴대폰뒷면', '턱걸이', '케이블카', 
            '러닝머신', '신발','소주잔', '선글라스', '일출(일몰)', 
            '사원', '상의', '손목시계']   
    data_list = []

    for name in lis:
        tag_data = {'tagname': name, 'tagcount_by_year': []}
        for year in range(2004, 2024):
            count = PhotoTable.objects.filter(
                phototag__contains=name,
                uploaddate__year=year
            ).count()
            tag_data['tagcount_by_year'].append({'year': year, 'tagcount': count})

        data_list.append(tag_data)
        
    return Response(data_list)



# 유저에 맞는 컨텐츠 출력
@api_view(['GET'])
def total_combined_api_view(request):

        # 연도별 태그별 이미지 카운트
        data = (
            PhotoTable.objects
            .filter(uploaddate__year=2023)
            .values('phototag')
        ) 

        # 2023년 태그 추출
        tags_2023 = []
        for entry in data:
            tags = entry['phototag'].split('#')
            for tag in tags:
                tagname = tag.strip()
                if tagname:
                    tags_2023.append(tagname)
        tag_counts = Counter(tags_2023)

        top_tags_2023 = tag_counts.most_common(5)
        print(top_tags_2023)
        recommend_contents_data = []

        for tag, _ in top_tags_2023:
            tag_data = RecommendContents.objects.filter(phototag__contains=tag)
            recommend_contents_data.extend(tag_data[:5])  # 상위 3개의 데이터만 추가
        
        # Serialize 데이터
        serializer = RecommendContentsSerializer(recommend_contents_data, many=True)

        return Response(serializer.data)

# 전체 분석- 행동분석 
# 비행기 버스 기차 => 전국여행  => 연도별로 태그를 모두 갖고 있는 사람의 수 count 
@api_view(['GET'])
def custom_tags_count_yearly_chart(request):
    lis = [{'애견가': ['강아지', '사람']}, {'전국여행': ['버스', '사람']},{'해외여행': ['비행기', '사람']},
           {'기차여행': ['기차', '사람']},{'육아': ['아이들', '사람']},{'캠핑': ['바베큐고기', '사람']},
           {'sns사용자': ['휴대폰뒷면', '사람']},{'피트니스': ['러닝머신', '사람']},{'건강식': ['당근', '브로콜리']},
          {'스포츠인': ['공', '사람']},
           {'시네필': ['텔레비전', '사람']},{'애서가': ['책', '사람']},{'애주가': ['건배', '소주잔']},
           {'테니스인': ['테니스라켓', '사람']},{'뷰티': ['화장품', '사람']},{'신발수집가': ['사람', '신발']},
           {'포토그래퍼': ['카메라', '사람']},{'게임 및 엔터테인먼트': ['컴퓨터', '키보드']},{'기독교인': ['사람', '십자가']},
           {'불교인': ['사람', '사원']}, {'시계수집가': ['사람', '손목시계']},{'와인수집가': ['사람', '와인잔']},{'애묘가': ['사람', '고양이']},
        
           ]
    data_list = []

    for year in range(2004, 2024):
        year_data = {'year': year, 'user_tags': {}}

        for category in lis:
            category_name, tags = list(category.items())[0]
            user_count = 0

            # Count users who have all tags in the current category for the current year
            users_with_tags = PhotoTable.objects.filter(uploaddate__year=year)

            for tag in tags:
                users_with_tags = users_with_tags.filter(phototag__contains=tag)

            user_count = len(set(user.id for user in users_with_tags))

            year_data['user_tags'][category_name] = user_count

        data_list.append(year_data)

    return Response(data_list)

    
class Recommendtable(generics.ListAPIView):
    queryset = RecommendContents.objects.all()
    serializer_class = RecommendContentsSerializer



class BoardAPIMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    # 2개 변수 필요
    queryset = Board.objects.all()


# 내 (userid) 게시글 보기  
class MyPost(generics.ListAPIView):
    serializer_class = BoardSerializer  

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = UsersAppUser.objects.filter(username=username) 
        return Board.objects.filter(id=user[0].id).select_related('photoid').order_by('-created_time').all() 

   
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class MyReply(generics.ListAPIView):
    serializer_class = ReplySerializer
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        user = UsersAppUser.objects.filter(username=username) 
        return Reply.objects.filter(id=user[0].id).select_related('board_no').order_by('-regdate').all()  # 완전일치 검색
   
    def get(self, request, *args, **kwargs):
        print(request.user)
        return self.list(request, *args, **kwargs)

class MyReplyDel(mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    lookup_field = "rno"  # 기본키

    # DELETE : bookno 전달 받고, bookno에 해당되는 1개의 도서 정보 삭제 (destroy)
    def delete(self, request, *args, **kwargs):  # DELETE 메소드 처리 함수 (1권 삭제)
        return self.destroy(request, *args, **kwargs)  # mixins.DestroyModelMixin와 연결


    
class MyLiked(generics.ListAPIView):
    serializer_class = LikedSerializer
   
    def get_queryset(self):
        # username = request.query_params.get('username')        
        username = self.kwargs.get('username')
        user = UsersAppUser.objects.filter(username=username) 

        return Liked.objects.filter(id=user[0].id).select_related('board_no').order_by('-likedate').all()  # 완전일치 검색    
    
    def get(self, request, *args, **kwargs):    
             
        print(request.session.items())    
        return self.list(request, *args, **kwargs)

class MyLikedDel(mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Liked.objects.all()
    serializer_class = LikedSerializer
    lookup_field = "likeno"  # 기본키

    # DELETE : bookno 전달 받고, bookno에 해당되는 1개의 도서 정보 삭제 (destroy)
    def delete(self, request, *args, **kwargs):  # DELETE 메소드 처리 함수 (1권 삭제)
        return self.destroy(request, *args, **kwargs)  # mixins.DestroyModelMixin와 연결

class LikedAPIMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Liked.objects.all()
    serializer_class = LikedSerializer

    def get(self, request, *args, **kwargs):        
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# def calculate_image_hash(file_path):
#     with Image.open(file_path) as img:
#         hash_value = imagehash.average_hash(img)
#     return hash_value

BASE_DIR = settings.BASE_DIR

@csrf_exempt
def upload_photo(request):
    if request.method == 'POST':
        if not request.POST.get('csrfmiddlewaretoken'):
            return JsonResponse({'error': 'CSRF 토큰이 누락되었거나 잘못되었습니다.'}, status=400)

        title = request.POST['title']
        description = request.POST['description']
        photo = request.FILES['imgFile0']

        if photo.content_type not in ['image/jpeg', 'image/png']:
            return JsonResponse({'error': '허용된 파일 형식이 아닙니다.'}, status=400)

        if not photo.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return JsonResponse({'error': '허용된 파일 확장자가 아닙니다.'}, status=400)

        # 원하는 경로에 이미지 저장
        upload_path = os.path.join('media', 'Upload')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        photo_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_img.jpg"
        photo_path = os.path.join(upload_path, photo_name)

        with open(photo_path, 'wb') as f:
            for chunk in photo.chunks():
                f.write(chunk)

        # 이미지 정보 반환
        response_data = {
            'title': title,
            'description': description,
            'photo_path': photo_path,
            'photo_name': photo_name,
        }

        return JsonResponse(response_data, status=200)

    return JsonResponse({'error': '올바른 요청이 아닙니다.'}, status=400)


def generate_new_filename(original_filename):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    name, extension = os.path.splitext(original_filename)
    return f"{timestamp}_{name}{extension}"

class TagSearch(generics.ListAPIView):
    serializer_class = PhotoTableSerializer

    def get_queryset(self):
        return PhotoTable.objects.filter(phototag__contains=self.kwargs["keyword"]) # 와일드 검색
   
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ExhibitionAPI(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.order_by('-created_time')
    
    def get_likes_and_replies(self, boards):
        boards = Board.objects.all()

        likes_and_replies = []
        for board in boards:
            likes_count = Liked.objects.filter(board_no=board.board_no).count()
            replies = Reply.objects.filter(board_no=board.board_no)
            reply_list = [{'rno': reply.rno, 'id': reply.id.username, 'replytext': reply.replytext, 'regdate': reply.regdate} for reply in replies]
            sorted_replies = sorted(reply_list, key=lambda x: x['regdate'], reverse=True)
            likes_and_replies.append({
                'board_no' : board.board_no,
                'likes_count' : likes_count,
                'replies': sorted_replies,
            })
        return likes_and_replies

    def get(self, request, *args, **kwargs):
        boards = self.get_queryset()
        
        all_phototags = (
            Board.objects
            .values_list('board_photo_tag', flat=True)
        )

        tag_counter = Counter(tag for phototag in all_phototags for tag in phototag.split('#') if tag)
        tag_frequency_list = [(tag, count) for tag, count in tag_counter.items()]
        tag_frequency_list.sort(key=lambda x: x[1], reverse=True)

        serializer = BoardSerializer(boards, many=True)

        response_data = {
            'boards': serializer.data,
            'all_phototags': tag_frequency_list,
        }

        likes_and_replies = self.get_likes_and_replies(boards)
        response_data['likes_and_replies'] = likes_and_replies

        return Response(response_data)

    def post(self, request, *args, **kwargs):
        selected_tags = request.data.get('selectedtags', [])

        if selected_tags:
            tag_queries = [Q(board_photo_tag__contains=tag) for tag in selected_tags]

            combined_query = tag_queries.pop()
            for query in tag_queries:
                combined_query &= query

            boards = Board.objects.filter(combined_query).order_by('-created_time')
        else:
            boards = Board.objects.all().order_by('-created_time')


        likes_and_replies = self.get_likes_and_replies(boards)

        serializer = BoardSerializer(boards, many=True)

        response_data = {
            'boards': serializer.data,
            'likes_and_replies': likes_and_replies,
        }

        return Response(response_data)

class LikeBoardView(APIView):
    def post(self, request, board_no, format=None):
        user = get_object_or_404(UsersAppUser, username=request.data.get('username'))
        board = get_object_or_404(Board, board_no=board_no)

        try:
            like = Liked.objects.get(board_no=board, id=user.id)
            like.delete()
            liked = False
        except Liked.DoesNotExist:
            new_like = Liked(board_no=board, id=user, likedate=timezone.now())
            new_like.save()
            liked = True

        return Response({'liked': liked}, status=status.HTTP_201_CREATED)

class AddReply(APIView):
    def post(self, request, board_no):
        try:
            board = Board.objects.get(board_no=board_no)
            user = get_object_or_404(UsersAppUser, username=request.data.get('username', ''))
            reply_text = request.data.get('comment', '')
            Reply.objects.create(board_no=board, id=user, replytext=reply_text, regdate=timezone.now())

            return Response({'message' : '댓글이 추가되었습니다.'})
        
        except Board.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        
class UserLikesView(APIView):
    def get(self, request, username, format=None):
        user = get_object_or_404(UsersAppUser, username=username)
        try:
            user_likes = Liked.objects.filter(id=user)
            liked_boards = [liked.board_no.board_no for liked in user_likes]
            return Response({'liked_boards': liked_boards}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BoardWritingView(APIView):
    def post(self, request, format=None):
        title = request.data.get('title', '')
        contents = request.data.get('contents', '')
        created_time = request.data.get('created_time', None)
        tags = request.data.get('tags')
        photoid = request.data.get('photoid')
        username = request.data.get('username')
        photo_instance = PhotoTable.objects.get(photoid=int(photoid))

        user = get_object_or_404(UsersAppUser, username=username)

        new_board = Board(title=title, contents=contents, board_photo_tag=tags, created_time=created_time, id=user, photoid=photo_instance)
        new_board.save()

        serializer = BoardSerializer(new_board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PhotoListView(APIView):
    def get(self, request, username, **kwargs):
        print(username)
        user = get_object_or_404(UsersAppUser, username=username)
        print(user)
        photos = PhotoTable.objects.filter(id=user)
        print(photos)
        serializer_photos = PhotoTableSerializer(photos, many=True).data

        return Response({'photos': serializer_photos}, status=status.HTTP_200_OK)

class BoardUpdate(APIView):
    def get(self, request, board_no, format=None):
        board = get_object_or_404(Board, board_no=board_no)
        serializer = BoardSerializer(board)
        return Response(serializer.data)
    
    def post(self, request, board_no, format=None):
        title = request.data.get('title', '')
        contents = request.data.get('contents', '')
        created_time = request.data.get('created_time', None)
        tags = request.data.get('tags')
        photoid = request.data.get('photoid')
        username = request.data.get('username')
        photo_instance = PhotoTable.objects.get(photoid=int(photoid))

        user = get_object_or_404(UsersAppUser, username=username)

        new_board = Board(board_no=board_no, title=title, contents=contents, board_photo_tag=tags, created_time=created_time, id=user, photoid=photo_instance)
        new_board.save()

        serializer = BoardSerializer(new_board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class BoardDelete(
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    lookup_field = "board_no"

    def delete(self, request, *args, **kwargs):
        board = self.get_object()
        board.liked_posts.all().delete()
        board.replies.all().delete()

        return self.destroy(request, *args, **kwargs)

class ReplyDelete(
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Reply.objects.all()
    lookup_field = 'rno'

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecommendTags(APIView):
    def get(self, request, username, **kwargs):
        users = UsersAppUser.objects.all()
        user_data_list = []
        current_user = UsersAppUser.objects.filter(username=username).first()

        for user in users:
            user_data = {
                "user_id": user.id,
                "username": user.username,
                "tags": set(),
                "tag_count": {},
            }

            user_photos = PhotoTable.objects.filter(id=user.id)
            for photo in user_photos:
                tags = photo.phototag.split('#')[1:]

                for tag in tags:
                    user_data['tag_count'][tag] = user_data['tag_count'].get(tag, 0) + 1

                sorted_tag_counts = sorted(user_data['tag_count'].items(), key=lambda x: x[1], reverse=True)
                top_5_tags = dict(sorted_tag_counts[:5])

                user_data['tag_count'] = top_5_tags
                user_data['tags'].update(top_5_tags.keys())

            user_data_list.append(user_data)        
            users_df = pd.DataFrame(user_data_list)

            users_df['tags_literal'] = users_df['tags'].apply(lambda tags_list: ' '.join(tag for tag in tags_list))
        
        corpus = users_df['tags_literal'].astype(str).tolist()
        vectorizer = CountVectorizer(min_df=0.0, ngram_range=(1,2))
        tag_vector = vectorizer.fit_transform(corpus)

        tag_matrix = pd.DataFrame(tag_vector.toarray(), columns=vectorizer.get_feature_names_out())
        
        tag_similarity = cosine_similarity(tag_matrix, tag_matrix)

        tag_similarity_arg = tag_similarity.argsort()[:, ::-1]

        similar_user = users_df.iloc[tag_similarity_arg[current_user.id-1][1:6]]
        current_user = users_df.iloc[tag_similarity_arg[current_user.id-1][0]]

        response_data = {
            'similar_user' : similar_user,
            'current_user' : current_user,
            'user_df': users_df,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def recommend_content(self, df):
        recommended_content = df['tag'].value_counts().idxmax()
        return {'recommended_content': recommended_content}

class UserAnalysis(APIView):
    @login_required
    def get(self, request, username, **kwargs):
        # 로그인한 사용자의 username을 가져옵니다.
        username = request.user.username

        # 해당 사용자가 올린 사진의 태그 수와 상위 3개 태그를 가져옵니다.
        user = get_object_or_404(UsersAppUser, username=username)
        user_photos = PhotoTable.objects.filter(id=user)
        user_tags = user_photos.values('phototag').annotate(tag_count=Count('phototag')).order_by('-tag_count')[:3]

        # 가져온 태그 데이터를 리스트로 변환
        user_tags_list = list(user_tags.values('phototag', 'tag_count'))

        # 해당 사용자의 전체 이미지 수를 가져옵니다.
        total_images_count = PhotoTable.objects.filter(id=user).count()

        # 사용자 분석 페이지에 필요한 정보를 JSON 형식으로 생성합니다.
        user_data = {
            'username': username,
            'total_images_count': total_images_count,
            'user_tags': user_tags_list,
            # 추가적인 필요한 정보가 있다면 여기에 추가
        }

        # JsonResponse를 사용하여 JSON 응답을 생성합니다.
        return JsonResponse(user_data)
    
    def get_matching_activities(request):
        user_selected_tags = request.data.get('user_selected_tags', [])
        predefined_activities = {
            '운동': [
                {'name': '자전거 타기', 'tags': ['자전거', '벤치', '공원']},
                {'name': '야구', 'tags': ['야구배트', '야구글러브', '야구공']},
                { 'name': '스키', 'tags': ['스키', '스노우보드', '겨울'] },
                { 'name': '공놀이', 'tags': ['공', '야구배트', '야구장'] },
                { 'name': '롤러블레이딩', 'tags': ['스케이트보드', '롤러블레이드', '공원'] },
                { 'name': '수영', 'tags': ['물병', '수영복', '수영장'] },
                { 'name': '요가', 'tags': ['요가 매트', '스트레칭', '명상'] },
                { 'name': '필라테스', 'tags': ['필라테스 매트', '덤벨', '스트레칭'] },
                { 'name': '헬스', 'tags': ['덤벨', '바벨', '운동복'] },
            ],
            '레저': [
                { 'name': '피크닉', 'tags': ['바구니', '샌드위치', '공원'] },
                { 'name': '등산', 'tags': ['등산화', '등산 배낭', '산'] },
                { 'name': '낚시', 'tags': ['낚싯대', '낚시 미끼', '강'] },
                { 'name': '캠핑', 'tags': ['텐트', '취사 도구', '캠핑장'] },
                { 'name': '게임', 'tags': ['컴퓨터', '게임 패드', '게임'] },
                { 'name': '영화 감상', 'tags': ['팝콘', '콜라', '영화관'] },
                { 'name': '음악 감상', 'tags': ['헤드폰', '음악 스트리밍 서비스', '공연장'] },
                { 'name': '독서', 'tags': ['책', '커피', '도서관'] },
            ],
            '기타': [
                { 'name': '여행', 'tags': ['여권', '비행기표', '숙소'] },
                { 'name': '학습', 'tags': ['책', '노트', '강의실'] },
                { 'name': '취미', 'tags': ['악기', '도구', '동호회'] },
                { 'name': '일', 'tags': ['컴퓨터', '휴대폰', '사무실'] },
            ],
            '추가 액티비티': [
                { 'name': '자전거 여행', 'tags': ['자전거', '텐트', '캠핑장'] },
                { 'name': '야구 경기 관람', 'tags': ['야구장', '야구팬', '응원'] },
                { 'name': '스키 여행', 'tags': ['스키', '숙소', '스키장'] },
                { 'name': '공놀이 대회', 'tags': ['공', '야구배트', '야구장'] },
                { 'name': '롤러블레이딩 대회', 'tags': ['롤러블레이드', '공원'] },
                { 'name': '수영 대회', 'tags': ['물병', '수영복', '수영장'] },
                { 'name': '요가 수업', 'tags': ['요가 매트', '스트레칭', '명상'] },
                { 'name': '필라테스 수업', 'tags': ['필라테스 매트', '덤벨', '스트레칭'] },
                { 'name': '헬스장 이용', 'tags': ['덤벨', '바벨', '운동복'] },
                { 'name': '피크닉 데이트', 'tags': ['바구니', '샌드위치', '공원'] },
                { 'name': '등산 여행', 'tags': ['등산화', '등산 배낭', '산'] },
                { 'name': '낚시 여행', 'tags': ['낚싯대', '낚시 미끼', '강'] },
                { 'name': '캠핑 여행', 'tags': ['텐트', '취사 도구', '캠핑장'] },
                { 'name': '게임 대회', 'tags': ['컴퓨터', '게임 패드', '게임'] },
                { 'name': '영화 관람', 'tags': ['팝콘', '콜라', '영화관'] },
                { 'name': '음악 감상', 'tags': ['헤드폰', '음악 스트리밍 서비스', '공연장'] },
                { 'name': '독서', 'tags': ['책', '커피', '도서관'] },
                { 'name': '여행 준비', 'tags': ['여권', '비행기표', '숙소'] },
                { 'name': '학습 준비', 'tags': ['책', '노트', '강의실'] },
                { 'name': '취미 활동', 'tags': ['악기', '도구', '동호회'] },
                { 'name': '일상 생활', 'tags': ['컴퓨터', '휴대폰', '사무실'] },
            ],
        }
        matching_activities = []

        for activity_category, activities in predefined_activities.items():
            for activity in activities:
                if all(tag in user_selected_tags for tag in activity['tags']):
                    matching_activities.append({'name': activity['name']})

        return Response(matching_activities, status=status.HTTP_200_OK)

@api_view(['POST'])
def file_upload(request):
    if request.method == "POST" and request.FILES.getlist('imgFiles'):
        files = request.FILES.getlist('imgFiles')
        fs = FileSystemStorage()

        saved_files = []

        for file in files:
            # 파일명 중복되지 않도록 uuid 사용해서 파일명 변경
            uuid = uuid4().hex
            file_name = uuid + '_' +  file.name  
            fs.save(file_name, file)
            saved_files.append(file_name)

        return JsonResponse({'fileNames':saved_files})

    return JsonResponse({'message': 'No files were uploaded.'}, status=400)

from functools import reduce
class RecommendContent(APIView):
    def get(self, request, *args, **kwargs):
        user_tags = request.GET.get('user_tags').split(',')
        recommend_tags = request.GET.get('recommend_tags').split(',')

        user_tags = [tag.strip() for tag in user_tags]
        
        user_content = RecommendContents.objects.filter(
            reduce(lambda x, y: x | y, (Q(phototag__icontains=tag) for tag in user_tags))
        )

        recommend_content = RecommendContents.objects.filter(
            reduce(lambda x, y: x | y, (Q(phototag__icontains=tag) for tag in recommend_tags))
        )

        user_content_serializer = RecommendContentsSerializer(user_content, many=True)
        recommend_content_serializer = RecommendContentsSerializer(recommend_content, many=True)

        response_data = {
            'user_content': user_content_serializer.data,
            'recommend_content': recommend_content_serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
       
