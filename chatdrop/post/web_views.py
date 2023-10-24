from rest_framework.views import APIView
from utils.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from account.throttling import AuthenticatedUserThrottling
from account.authentication import UserWebAuthentication
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from . import serializers
from .services import PostService, CommentService, LikeService, CommentLikeService
from utils.debug import debug_print




# Add Post
@method_decorator(csrf_protect, name='dispatch')
class AddPostV3(APIView):
    parser_classes = [FormParser, MultiPartParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            content_type = request.query_params.get('content_type')
            serializer = None

            if content_type == 'TEXT':
                serializer = serializers.TextPostSerializerV2(data=request.data)

            elif content_type == 'PHOTO':
                serializer = serializers.PhotoPostSerializerV2(data=request.data)
            
            elif content_type == 'VIDEO':
                serializer = serializers.VideoPostSerializerV3(data=request.data)
            
            elif content_type == 'TEXT_PHOTO':
                serializer = serializers.TextPhotoPostSerializerV2(data=request.data)
            
            elif content_type == 'TEXT_VIDEO':
                serializer = serializers.TextVideoPostSerializerV3(data=request.data)

            # validating serializer
            if serializer is not None and serializer.is_valid():
                # saving post
                post = PostService.add_post_v3(
                    auth_user=request.user,
                    content_type=content_type,
                    data=serializer.validated_data
                )
                
                if post is not None:
                    # sending response
                    return Response.success({
                        'message': 'Posted Successfully',
                        'post': PostService.to_json_v3(post, auth_user=request.user)
                    })
                
                return Response.error(error='Unable to create post.')

            return Response.errors(serializer.errors)
        
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()




# post view
@method_decorator(csrf_protect, name='dispatch')
class SinglePostViewV2(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request, post_id):
        try: 
            post = PostService.view_post_v2(
                auth_user=request.user,
                post_id=post_id,
            )
            
            return Response.success({
                'message': 'post',
                'post': post,
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()




# Change post visibility
@method_decorator(csrf_protect, name='dispatch')
class ChangePostVisilibity(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def put(self, request, post_id):
        try: 
            visibility = request.query_params.get('vbt')

            PostService.change_visibility(
                auth_user=request.user,
                post_id=post_id,
                visibility=visibility,
            )
            
            return Response.success({
                'message': f'Visibility changed to {visibility}',
            })
        except:
            return Response.something_went_wrong()





# List Post
@method_decorator(csrf_protect, name='dispatch')
class ListPostV3(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try: 
            posts, has_next = PostService.list_all_v3(
                auth_user=request.user,
                uid=request.query_params.get('of'),
                page=request.query_params.get('page'),
            )
            
            return Response.success({
                'message': 'All Post.',
                'posts': posts,
                'has_next': has_next
            })
        except:
            return Response.something_went_wrong()






# Delete Post
@method_decorator(csrf_protect, name='dispatch')
class DeletePost(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def delete(self, request, post_id):
        try:
            PostService.delete_post(
                auth_user=request.user,
                post_id=post_id,
            )

            # sending response
            return Response.success({
                'message': 'Post deleted Successfully.'
            })
        except:
            return Response.something_went_wrong()





# Add Comment
@method_decorator(csrf_protect, name='dispatch')
class Comment(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request, post_id):
        try: 
            serializer = serializers.AddCommentSerializer(data=request.data)

            if serializer.is_valid():
                response = CommentService.add_comment(
                    auth_user=request.user,
                    post_id=post_id,
                    data=serializer.validated_data,
                )
                
                # sending response
                return Response.success(response)
            
            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()
        

    def get(self, request, post_id):
        try:
            comments = CommentService.list_all(request.user, post_id)
            
            return Response.success({
                'message': 'All Comments.',
                'comments': comments
            })
        except:
            return Response.something_went_wrong()
        





# Delete Comment
@method_decorator(csrf_protect, name='dispatch')
class DeleteComment(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def delete(self, request, post_id, comment_id):
        try:
            CommentService.delete_comment(
                auth_user=request.user,
                post_id=post_id,
                comment_id=comment_id,
            )

            # sending response
            return Response.success({
                'message': 'comment deleted Successfully.'
            })
        except:
            return Response.something_went_wrong()





# Add Like
@method_decorator(csrf_protect, name='dispatch')
class Like(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    # Like
    def post(self, request, post_id):
        try:
            serializer = serializers.AddLikeSerializer(data=request.data)

            if serializer.is_valid():
                # posting like
                LikeService.like_post(
                    auth_user=request.user, 
                    post_id=post_id,
                    data=serializer.validated_data,
                )
                
                # sending response
                return Response.success({
                    'message': 'Liked Successfully.'
                })
            
            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()


    # List Like
    def get(self, request, post_id):
        try:
            likes = LikeService.list_all(post_id)
            
            return Response.success({
                'message': 'All Likes.',
                'likes': likes
            })
        except:
            return Response.something_went_wrong()


    # Dislike
    def delete(self, request, post_id):
        try:
            LikeService.dislike_post(
                auth_user=request.user,
                post_id=post_id,
            )

            # sending response
            return Response.success({
                'message': 'Like deleted Successfully.'
            })
        except:
            return Response.something_went_wrong()






# Comment Like
@method_decorator(csrf_protect, name='dispatch')
class CommentLike(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    # Comment Like
    def post(self, request, comment_id):
        try:
            serializer = serializers.AddCommentLikeSerializer(data=request.data)

            if serializer.is_valid():
                # posting like
                CommentLikeService.like_comment(
                    auth_user=request.user,
                    comment_id=comment_id,
                    data=serializer.validated_data
                )
                
                # sending response
                return Response.success({
                    'message': 'Liked Successfully.'
                })
            
            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()


    # List Comment Likes
    def get(self, request, comment_id):
        try:
            likes = CommentLikeService.list_all(comment_id)
            
            return Response.success({
                'message': 'All Comment Likes.',
                'likes': likes
            })
        except:
            return Response.something_went_wrong()
        

    # Comment dislike
    def delete(self, request, comment_id):
        try:
            CommentLikeService.dislike_comment(
                auth_user=request.user,
                comment_id=comment_id,
            )

            # sending response
            return Response.success({
                'message': 'Like deleted Successfully.'
            })
        except:
            return Response.something_went_wrong()

