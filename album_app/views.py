import re
from rest_framework import status, mixins, generics
from .models import PhotoTable, Board, Reply, Liked, Photo
from .serializers import PhotoTableSerializer, BoardSerializer, ReplySerializer, LikedSerializer
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from PIL import Image
from datetime import datetime
from ultralytics import YOLO
import torchvision.transforms as transforms
from operator import itemgetter
import imagehash

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
    
class BoardAPIMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    # 2개 변수 필요
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
class ReplyAPIMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    # 2개 변수 필요
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer

    def get(self, request, *args, **kwargs):        
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
class TagSearch(generics.ListAPIView):
    serializer_class = PhotoTableSerializer

    def get_queryset(self):
        return PhotoTable.objects.filter(phototag__contains=self.kwargs["keyword"]) # 와일드 검색
   
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

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

    # 2개 변수 필요
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

        try:
            photo = Photo.objects.create(
                title=title,
                description=description,
                image=photo_path.replace(os.path.sep, '/'),
            )
        except ValidationError as e:
            return HttpResponseBadRequest(', '.join(e.messages))

        return redirect('classification.html')

    return render(request, 'upload.html')


def analysis_results_view(request):
    return render(request, 'classfication.html')

