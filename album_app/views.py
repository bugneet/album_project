from collections import Counter
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response 
from rest_framework import mixins, generics, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from .serializers import BoardSerializer, PhotoTableSerializer

# Create your views here.
def index(request):
    return render(request, 'album_app/index.html')

class ExhibitionAPI(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.order_by('-created_time')

    def get_paginated_boards(self, queryset, page, board_per_page):
        paginator = Paginator(queryset, board_per_page)

        try:
            boards = paginator.page(page)
        except PageNotAnInteger:
            boards = paginator.page(1)
        except EmptyPage:
            boards = paginator.page(paginator.num_pages)

        return boards, paginator.num_pages

    def get_likes_and_replies(self, boards):
        likes_and_replies = []
        for board in boards:
            likes_count = Liked.objects.filter(board_no=board.board_no).count()
            replies = Reply.objects.filter(board_no=board.board_no)
            likes_and_replies.append({
                'id' : board.board_no,
                'likes_count' : likes_count,
                'replies': [{'id': reply.rno, 'replytext': reply.replytext, 'regdate': reply.regdate} for reply in replies],
            })
        return likes_and_replies

    def get(self, request, *args, **kwargs):
        board_per_page = 5
        page = request.query_params.get('page', 1)

        queryset = self.get_queryset()
        boards, last_pages = self.get_paginated_boards(queryset, page, board_per_page)

        all_phototags = (
            PhotoTable.objects
            .filter(photoid__in=Board.objects.values('photoid'))
            .values_list('phototag', flat=True)
            .distinct()
        )

        tag_counter = Counter(tag for phototag in all_phototags for tag in phototag.split('#') if tag)
        # print(tag_counter)
        tag_frequency_list = [(tag, count) for tag, count in tag_counter.items()]
        tag_frequency_list.sort(key=lambda x: x[1], reverse=True)

        serializer = BoardSerializer(boards, many=True)

        response_data = {
            'boards': serializer.data,
            'all_phototags': tag_frequency_list,
            'last_pages': last_pages
        }

        likes_and_replies = self.get_likes_and_replies(boards)
        response_data['likes_and_replies'] = likes_and_replies

        return Response(response_data)

    def post(self, request, *args, **kwargs):
        selected_tags = request.data.get('selectedtags', [])
        print(selected_tags)

        if selected_tags:
            tag_queries = [Q(photoid__phototag__contains=tag) for tag in selected_tags]

            combined_query = tag_queries.pop()
            for query in tag_queries:
                combined_query |= query

            queryset = Board.objects.filter(combined_query).order_by('-created_time')
        else:
            queryset = Board.objects.all().order_by('-created_time')

        boards, last_pages = self.get_paginated_boards(queryset, 1, 5)

        likes_and_replies = self.get_likes_and_replies(boards)

        serializer = BoardSerializer(boards, many=True)

        response_data = {
            'boards': serializer.data,
            'last_pages': last_pages,
            'likes_and_replies': likes_and_replies,
        }

        return Response(response_data)

class CurrentUserView(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        response_data = {
            'username': user.username,
            'id': user.id,
        }
        return Response(response_data)

class BoardWritingView(APIView):
    def post(self, request, format=None):
        title = request.data.get('title', '')
        contents = request.data.get('contents', '')
        created_time = request.data.get('created_time', None)
        photoid = request.data.get('photoid')
        
        photo_instance = PhotoTable.objects.get(photoid=int(photoid))
        user_id = 1
    
        user = get_object_or_404(UsersAppUser, pk=user_id)

        new_board = Board(title=title, contents=contents, created_time=created_time, id=user, photoid=photo_instance)
        new_board.save()

        serializer = BoardSerializer(new_board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PhotoListView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = 1
        user = get_object_or_404(UsersAppUser, pk=user_id)
        photos = PhotoTable.objects.filter(id=user)
        serializer_photos = PhotoTableSerializer(photos, many=True).data

        return Response({'photos': serializer_photos}, status=status.HTTP_200_OK)

class LikeBoard(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_no):
        try:
            board = Board.objects.get(board_no=board_no)
            user = request.user

            if Liked.objects.filter(board_no=board.board_no, id=user.id).exists():
                Liked.objects.filter(board_no=board.board_no, id=user.id).delete()
                message = '좋아요 취소'
            else:
                Liked.objects.create(board_no=board.board_no, id=user.id)
                message = '좋아요 추가'

            return Response({'message': message})

        except Board.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

class AddReply(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_no):
        try:
            board = Board.objects.get(board_no=board_no)
            user = request.user
            reply_text = request.data.get('replytext', '')

            Reply.objects.create(board_no=board.board_no, id=user.id, replytext=reply_text)

            return Response({'message' : '댓글이 추가되었습니다.'})
        
        except Board.DoesNotExist:
            return Response({'error': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

class BoardAPIMixins(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    lookup_field = "board_no"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# def board_detail(request, board_no):
#     board = get_object_or_404(Board, board_no=board_no)
#     comments = Reply.objects.filter(board_no=board)
#     likes = Liked.objects.filter(board_no=board)

#     context = {
#         'board' : board,
#         'comments' : comments,
#         'likes' : likes
#     }
#     return render(request, 'album_app/board_detail.html', context)

# @login_required
# def board_like(request, board_no):
#     board = get_object_or_404(Board, board_no=board_no)
#     user = request.user

#     if Liked.objects.filter(board_no=board, id=user).exists():
#         Liked.objects.filter(board_no=board, id=user).delete()
#     else:
#         Liked.objects.create(board_no=board, id=user)

#     return redirect('board_detail', board_no=board_no)