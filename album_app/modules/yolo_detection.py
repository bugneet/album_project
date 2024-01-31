import imagehash
from ultralytics import YOLO
from operator import itemgetter
from PIL import Image
import os
from datetime import datetime
import re

def detect(imgnames):
    
    yolo_label_kor = {0: '사람', 1: '자전거', 2: '자동차', 3: '오토바이', 4: '비행기', 5: '버스', 
                  6: '기차', 7: '트럭', 8: '보트', 9: '', 10: '', 11: '', 12: '', 13: '벤치', 14: '새', 
                  15: '고양이', 16: '강아지', 17: '말', 18: '양', 19: '소', 20: '코끼리', 21: '곰', 22: '얼룩말',
                  23: '기린', 24: '가방', 25: '우산', 26: '핸드백', 27: '넥타이', 28: '캐리어', 29: '', 30: '스키', 
                  31: '스노우보드', 32: '공', 33: '', 34: '야구배트', 35: '야구글러브', 36: '스케이트보드', 37: '', 
                  38: '테니스라켓', 39: '물병', 40: '와인잔', 41: '컵', 42: '포크', 43: '나이프', 44: '숟가락', 45: '접시',
                  46: '바나나', 47: '사과', 48: '샌드위치', 49: '오렌지', 50: '브로콜리', 51: '당근', 52: '핫도그',
                  53: '피자', 54: '도넛', 55: '케이크', 56: '', 57: '소파', 58: '화분', 59: '침대', 60: '식탁', 61: '',
                  62: '텔레비전', 63: '컴퓨터', 64: '마우스', 65: '', 66: '키보드', 67: '전화기', 68: '전자레인지', 
                  69: '오븐', 70: '토스터기', 71: '싱크대', 72: '냉장고', 73: '책', 74: '', 75: '꽃병', 76: '', 
                  77: '곰인형', 78: '', 79: ''}

    yolo_custom_label_kor = {0: '장신구', 1: '에어프라이어', 2: '비행기날개', 3: '백팩', 4: '풍선', 5: '맥주잔', 6: '카메라', 
    7: '양초', 8: '건배', 9: '아이들' ,10: '전시된옷', 11: '화장품', 12: '십자가', 13: '에펠탑', 14: '안경', 15: '등대',
    16: '바베큐고기', 17: '포장고기', 18: '바지', 19: '휴대폰 뒷면', 20: '원판(덤벨 및 바벨)', 
    21: '철봉', 22: '케이블카', 23: '러닝머신', 24: '신발', 25: '소주잔', 26: '선글라스', 27: '일출(일몰)', 28: '사원', 29: '상의', 30: '손목시계'} 

    model_path = './static/model/best.pt'

    # YOLO 모델 로드
    model2 = YOLO('yolov8n.pt')

    # 커스텀 로드
    model = YOLO(model_path)

    # 이미지 폴더
    img_folder_path = '../upload/'

    img_paths = []

    for file_name in imgnames: 
        # print(file_name)
        img_paths.append(f"{img_folder_path}/{file_name}")
    
    items = []
    all_tag_dict = {}
    for idx, img in enumerate(img_paths):
        
        print(f"img : {img}")
        # 이미지 객체 검출 실행
        
        # 원본
        results = model(img)

        pred_labels = []
        # 검출 결과를 레이블로 변환
        for i, result in enumerate(results):
            if result.__len__() == 0:
                break
            for box in result.boxes.cls:                
                pred_labels.append(yolo_custom_label_kor[int(box.item())])
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
                pred_labels.append(yolo_label_kor[int(box.item())])
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
        # tags += "#일상"
        ######################################################
        tags = re.sub(r'#+', '#', tags)
        # tags = tags.replace("##", "#") 
        if tags.endswith('#'):
            tags = tags[:-1]
        
        ############사진 파일 안에 날짜정보가 없을 경우############
        # 현재 날짜 및 시간 받아오기
        current_date_time = datetime.now()
        # 날짜만 받아오기
        current_date = str(current_date_time.date())
        # print(current_date)
        img_hash = str(calculate_image_hash(img))

        items.append(
            {'photohash':img_hash, 
             'phototag':tags, 
             'photodate':current_date, 
             'uploaddate':current_date, 
             'image':imgnames[idx]})    
    
    # 딕셔너리 value값으로 정렬
    sorted_items = sorted(all_tag_dict.items(), key=itemgetter(1), reverse=True)
    sorted_dict = dict(sorted_items)

    alltags = ""
    for key, value in sorted_dict.items():         
        alltags += f"#{key}({value})" 

    # alltags_set = {f"{key}({value})" for key, value in sorted_dict.items()}
    # alltags = '#{}'.format('#'.join(str(item) for item in alltags_set))
    # return render(request, 'album_app/classification.html', {'items' : items, 'alltags' : alltags})
    
    # 이미지 감지 한 데이터셋 리턴
    
    print(f"items : {items}")

    return items

def calculate_image_hash(file_path):
    with Image.open(file_path) as img:
        hash_value = imagehash.average_hash(img)
    return hash_value
