
from django.shortcuts import render , redirect,  HttpResponseRedirect, get_object_or_404
from rest_framework import status, mixins, generics
from .models import *
from .serializers import PhotoTableSerializer, BoardSerializer, ReplySerializer, LikedSerializer
import os
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login

from datetime import datetime

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
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .modules.yolo_detection import detect


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
        
        file_names = ['2004-01-01_17.jpg','2004-04-01_21.jpg','2004-06-01_6.jpg']
        items = detect(file_names) # 이미지 파일명 전달 
        return items
    
    def get(self, request, *args, **kwargs):    
             
        print(request.session.items())    
        return self.list(request, *args, **kwargs)
    
@api_view(['POST'])
def save_data(request):   

    if request.method == 'POST':
        print(request.data)
        serializer = PhotoTableSerializer(data=request.data, many=True)        

        if serializer.is_valid():
            # 데이터 유효성 검사 후 저장
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
    
@api_view(['GET'])
def tagChart_test(request):
    id= request.user.id # 로그인한 id 불러오기 
    
    name_list = ['프로그래밍', '안드로이드']
    data_dict = {}
    data_list = []    
    

    for i, name in enumerate(name_list):
        count = len(PhotoTable.objects.filter(phototag__contains=name, userid=id)) # 특정 id에 해당
        data_dict['tagname'] = name_list[i]
        data_dict['tagcount'] = count        
        data_list.append(data_dict)
        data_dict = {}    

    print(data_list)
    return Response(data_list)


@api_view(['GET'])
def tag_chart(request):
    lis=[ '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트',
          '벤치', '새', '고양이', '강아지', '양', '소', '코끼리', '곰', '얼룩말', '기린',
            '가방', '우산', '핸드백', '넥타이', '캐리어', '스키', '스노우보드', '공', '야구배트',
          '야구글러브', '스케이트보드', '테니스라켓', '물병', '와인잔', '컵', '포크', 
          '나이프', '숟가락', '접시', '바나나', '사과', '샌드위치', '오렌지', '브로콜리',
            '당근', '핫도그', '피자', '도넛', '케이크', '소파', '화분', '침대', '식탁', 
            '텔레비전', '컴퓨터', '마우스', '키보드', '전화기', '전자레인지', '오븐', 
            '토스터기', '싱크대', '냉장고', '책', '꽃병', '곰인형',
            '장신구', '에어프라이어', '비행기날개', '아기', '백팩', '풍선', '바벨', 
            '맥주잔', '카메라', '양초', '건배', '전시된옷', '화장품', '십자가', '덤벨', 
            '귀걸이', '에펠탑', '운동기구', '안경', '말', '아이', '등대', '바베큐고기', 
            '포장고기', '목걸이', '바지', '휴대폰뒷면', '턱걸이', '리프트(케이블카)', 
            '반지', '러닝머신', '신발', '쇼핑백', '소주잔', '선글라스', '일출(일몰)', 
            '사원', '상의', '손목시계']
    tag_count=[]

    for x in lis:
        count= len(PhotoTable.objects.filter(phototag__contains=x))
        tag_count.append(count)
    # tag_count= sorted(tag_count, reverse=True)[:10]
    result=[]
    for y in range(len(lis)):
        result.append({"tagname":lis[y], "tagcount":tag_count[y]})
    
    result_top10 = sorted(result, key=lambda x: x['tagcount'], reverse=True)[:10]

    return Response(result_top10)


@api_view(['GET'])
def tag_chart_personal(request):

    if request.user.is_authenticated:

        id= request.user.id # 로그인한 id 불러오기 

    # p_count = len(PhotoTable.objects.filter(phototag__contains='프로그래밍', bookno='1003'))
        p_count = len(PhotoTable.objects.filter(phototag__contains='사람' ,userid=id))
        print(p_count)

        a_count = len(PhotoTable.objects.filter(phototag__contains='일상' ,userid=id))
        print(a_count)       

        b_count = len(PhotoTable.objects.filter(phototag__contains='아기' ,userid=id))
        print(b_count) 

        c_count = len(PhotoTable.objects.filter(phototag__contains='운동기구', userid=id))
        print(c_count) 
        d_count = len(PhotoTable.objects.filter(phototag__contains='비행기' , userid=id))
        print(d_count) 

        result = [
            {"tagname":'사람', "tagcount":p_count},
            {"tagname":'일상', "tagcount":a_count},
            {"tagname":'운동기구', "tagcount":b_count},
            {"tagname":'아기', "tagcount":c_count},
            {"tagname":'비행기', "tagcount":d_count},

            ]  

        return Response(result)
    else:
        messages.warning(request, '로그인이 필요합니다.')
        return HttpResponseRedirect('http://127.0.0.1:8000/chart_db/')


class BoardAPIMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    # 2개 변수 필요
    queryset = Board.objects.all()


# 내 (userid) 게시글 보기  
class MyPost(generics.ListAPIView):
    serializer_class = BoardSerializer  

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = UsersAppUser.objects.filter(username=username) 
        return Board.objects.filter(id=user[0].id).select_related('photoid').all() 
   
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class MyReply(generics.ListAPIView):
    serializer_class = ReplySerializer
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        user = UsersAppUser.objects.filter(username=username) 
        return Reply.objects.filter(id=user[0].id).select_related('board_no').all()  # 완전일치 검색
   
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

        return Liked.objects.filter(id=user[0].id).select_related('board_no').all()  # 완전일치 검색    
    
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

    # 2개 변수 필요
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
            reply_list = [{'id': reply.id.username, 'replytext': reply.replytext, 'regdate': reply.regdate} for reply in replies]
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
            .distinct()
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

import pandas as pd
class RecommendContents(APIView):
    def get(self, request, *args, **kwargs):
        all_photos = PhotoTable.objects.all()
        data_list = []

        user_tags={}
        for photo in all_photos:
            username = photo.id.username
            phototag = photo.phototag

            if username not in user_tags:
                user_tags[username] = set()
            
            user_tags[username].add(phototag)

        for username, tags in user_tags.items():
            for tag in tags:
                data_list.append({
                    'username' : username,
                    'tag' : tag
                })

        df = pd.DataFrame(data_list)
        recomment_content = self.recommend_content(df)

        print(recomment_content)
        response_data = {
            'recomment_content':df,
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
    
    def get_matching_activities(self, user_selected_tags):
        predefinedActivities ={}
        matching_activities = []
        
        for activity_category, activities in predefinedActivities.items():
            for activity in activities:
                if all(tag in user_selected_tags for tag in activity['tags']):
                    matching_activities.append(activity)
                    break

        return matching_activities