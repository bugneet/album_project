import re
from django.shortcuts import render , HttpResponseRedirect
from rest_framework import status, mixins, generics
from .models import PhotoTable, Board, Reply
from .serializers import PhotoTableSerializer, BoardSerializer, ReplySerializer
import os
import torch
from PIL import Image
from datetime import datetime
from ultralytics import YOLO
import torchvision.transforms as transforms
from operator import itemgetter
import imagehash
from rest_framework.decorators import api_view   
from rest_framework.response import Response
from django.contrib import messages


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

    # 2개 변수 필요 // 임시로 10개만 가져오기 [:10]
    queryset = PhotoTable.objects.all()[:10]
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
class MyBoard(generics.ListAPIView):
    serializer_class = BoardSerializer
    
    # 로그인 정보에서 유저 id 가져오기
    userid = "1111"

    def get_queryset(self):
        return Board.objects.filter(id=self.userid) # 완전일치 검색
   
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class MyReply(generics.ListAPIView):
    serializer_class = ReplySerializer
    
    # 로그인 정보에서 유저 id 가져오기
    userid = "1111"

    def get_queryset(self):
        return Reply.objects.filter(id=self.userid) # 완전일치 검색
   
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


def calculate_image_hash(file_path):
    with Image.open(file_path) as img:
        hash_value = imagehash.average_hash(img)
    return hash_value