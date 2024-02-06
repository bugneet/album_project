import re
from django.shortcuts import render , redirect,  HttpResponseRedirect, get_object_or_404
from rest_framework import status, mixins, generics
from .models import *
from .serializers import PhotoTableSerializer, BoardSerializer, ReplySerializer, LikedSerializer, RecommendContentsSerializer
import os
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from PIL import Image
from datetime import datetime
# from ultralytics import YOLO
# import torchvision.transforms as transforms
from operator import itemgetter
# import imagehash
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

# Create your views here.
def index(request):
    return render(request, 'album_app/index.html')

def mypage_album(request):
    return render(request, 'album_app/mypage_album.html')

def mypage_mypost(request):
    return render(request, 'album_app/mypage_mypost.html')

def mypage_myreply(request):
    return render(request, 'album_app/mypage_myreply.html')


def classification(request):
    
    model_path = './static/model/best1.pt'

    # YOLO 모델 로드
    model2 = YOLO('yolov8n.pt')

    # 커스텀 로드
    model = YOLO(model_path)

    # 이미지 로드
    img_folder_path = "./static/img/2011-01-01"

    img_paths = []

    file_list = os.listdir(img_folder_path)

    for file_name in file_list: 
        # print(file_name)
        img_paths.append(f"{img_folder_path}/{file_name}")
    
    # imgs = [Image.open(img_path) for img_path in img_paths]

    # 이미지 640으로 변환
    # resize_transform = transforms.Resize((640, 640))
    # 이미지를 YOLO 모델의 입력으로 변환
    # img_tensors = [transforms.ToTensor()(resize_transform(img)).unsqueeze_(0) for img in imgs]

    items = []
    all_tag_dict = {}
    for idx, img in enumerate(img_paths):
        
        # 이미지 객체 검출 실행
        
        # 원본
        results = model(img)

        pred_labels = []
        # 검출 결과를 레이블로 변환
        for i, result in enumerate(results):
            if result.__len__() == 0:
                break
            for box in result.boxes.cls:                
                pred_labels.append(result.names[int(box.item())])
                # print(f"Label: {model.names[int(class_id)]}, Box: {x.item(), y.item(), w.item(), h.item()}, Confidence: {conf.item()}")
        
        tag_dict = {}
        # 태그 저장 
        for label in pred_labels:                      
            if label in tag_dict:
                # 이미 존재하는 키인 경우, 해당 키의 값을 1 증가시킴
                tag_dict[label] += 1
            else:
                # 새로운 키인 경우, 해당 키를 추가하고 값을 1로 설정
                tag_dict[label] = 1     
                # 사진당 감지된 최초 오브젝트 저장 
                if label in all_tag_dict:
                    all_tag_dict[label] += 1
                else:
                    all_tag_dict[label] = 1              
             
        tags = ("#" + "#".join(tag_dict.keys())).replace(' ', '')     

        # 원본
        results2 = model2(img)

        pred_labels = []
        # 검출 결과를 레이블로 변환
        for i, result in enumerate(results2):
            if result.__len__() == 0:
                break
            for box in result.boxes.cls:                
                pred_labels.append(result.names[int(box.item())])
                # print(f"Label: {model.names[int(class_id)]}, Box: {x.item(), y.item(), w.item(), h.item()}, Confidence: {conf.item()}")
        
        tag_dict = {}
        # 태그 저장 
        for label in pred_labels:                      
            if label in tag_dict:
                # 이미 존재하는 키인 경우, 해당 키의 값을 1 증가시킴
                tag_dict[label] += 1
            else:
                # 새로운 키인 경우, 해당 키를 추가하고 값을 1로 설정
                tag_dict[label] = 1     
                # 사진당 감지된 최초 오브젝트 저장 
                if label in all_tag_dict:
                    all_tag_dict[label] += 1
                else:
                    all_tag_dict[label] = 1              
             
        tags2 = ("#" + "#".join(tag_dict.keys())).replace(' ', '')  

        tags += tags2
        # print(f"{idx}번째 사진 태그 = {tags.replace(' ', '')}")
        
        ############ 임시로 #일상 태그 넣기###################
        tags += "#일상"
        ######################################################
        tags = re.sub(r'#+', '#', tags)
        # tags = tags.replace("##", "#") 
        
        ############사진 파일 안에 날짜정보가 없을 경우############
        # 현재 날짜 및 시간 받아오기
        current_date_time = datetime.now()
        # 날짜만 받아오기
        current_date = current_date_time.date()
        # print(current_date)
        items.append({'title':idx, 'date':current_date, 'tags':tags, 'img_path':file_list[idx]})    
    
    # 딕셔너리 value값으로 정렬
    sorted_items = sorted(all_tag_dict.items(), key=itemgetter(1), reverse=True)
    sorted_dict = dict(sorted_items)

    alltags = ""
    for key, value in sorted_dict.items():         
        alltags += f"#{key}({value})" 

    # alltags_set = {f"{key}({value})" for key, value in sorted_dict.items()}
    # alltags = '#{}'.format('#'.join(str(item) for item in alltags_set))
    return render(request, 'album_app/classification.html', {'items' : items, 'alltags' : alltags})


class PhotoTableAPIMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    userid = "1"
    # 2개 변수 필요 // 임시로 10개만 가져오기 [:10]
    # queryset = PhotoTable.objects.all()[:30000] # 전체 가져오기
    queryset = PhotoTable.objects.filter(id=userid).order_by('-photodate').all() # 해당userid 가져오기

    serializer_class = PhotoTableSerializer

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
    
    # 로그인 정보에서 유저 id 가져오기
    userid = "1"

    def get_queryset(self):
        return Board.objects.filter(id=self.userid).select_related('photoid').all() 
   
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class MyReply(generics.ListAPIView):
    serializer_class = ReplySerializer
    
    # 로그인 정보에서 유저 id 가져오기
    userid = "1"

    def get_queryset(self):
        return Reply.objects.filter(id=self.userid).select_related('board_no').all()  # 완전일치 검색
   
    def get(self, request, *args, **kwargs):
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
    
    # 로그인 정보에서 유저 id 가져오기
    userid = "1"

    def get_queryset(self):
        return Liked.objects.filter(id=self.userid).select_related('board_no').all()  # 완전일치 검색
   
    def get(self, request, *args, **kwargs):
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

def calculate_image_hash(file_path):
    with Image.open(file_path) as img:
        hash_value = imagehash.average_hash(img)
    return hash_value

BASE_DIR = settings.BASE_DIR

def upload_photo(request):
    if request.method == 'POST':
        if not request.POST.get('csrfmiddlewaretoken'):
            return HttpResponseForbidden('CSRF 토큰이 누락되었거나 잘못되었습니다.')

        title = request.POST['title']
        description = request.POST['description']
        photo = request.FILES['imgFile']

        if photo.content_type not in ['image/jpeg', 'image/png']:
            return HttpResponseBadRequest('허용된 파일 형식이 아닙니다.')

        if not photo.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return HttpResponseBadRequest('허용된 파일 확장자가 아닙니다.')

        photo_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        photo_path = os.path.join('Uploads', f'{photo_name}.jpg')

        with photo.open('wb') as f:
            f.write(photo.read())
      
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
                
                if '' in tags:
                    tags = [tag for tag in tags if tag != '']
                    
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
        current_user_info = users_df.iloc[tag_similarity_arg[current_user.id-1][0]]
        response_data = {
            'similar_user' : similar_user,
            'current_user' : current_user_info,
        }
        return Response(response_data, status=status.HTTP_200_OK)

from functools import reduce
class RecommendContent(APIView):
    def get(self, request, *args, **kwargs):
        user_tags = request.GET.get('user_tags').split(',')
        recommend_tags = request.GET.get('recommend_tags').split(',')

        user_tags = [tag.strip() for tag in user_tags]
        print('유저 태그: ', user_tags)
        print('추천 태그', recommend_tags)
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