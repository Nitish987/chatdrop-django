from rest_framework.views import APIView
from utils.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsRequestValid
from account.throttling import AuthenticatedUserThrottling
from . import serializers
from .services import ReelService, CommentService, LikeService, CommentLikeService, AudioService
from utils.debug import debug_print




# Add Reel
class AddReel(APIView):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            serializer = serializers.ReelSerializer(data=request.data)

            # validating serializer
            if serializer is not None and serializer.is_valid():
                # saving reel
                ReelService.add_reel(
                    auth_user=request.user,
                    data=serializer.validated_data
                )
                # sending response
                return Response.success({
                    'message': 'Posted Successfully'
                })

            return Response.errors(serializer.errors)
        
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Reel Viewer
class ReelViewer(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request, reel_id):
        try:
            # adding story view
            ReelService.add_reel_view(
                auth_user=request.user,
                reel_id=reel_id
            )

            return Response.success({
                'message': 'Reel view added.'
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Single Reel view
class SingleReelView(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request, reel_id):
        try: 
            reel = ReelService.view_reel(
                auth_user=request.user,
                reel_id=reel_id,
            )
            
            return Response.success({
                'message': 'reel',
                'reel': reel,
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Change reel visibility
class ChangeReelVisilibity(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def put(self, request, reel_id):
        try: 
            visibility = request.query_params.get('vbt')

            ReelService.change_visibility(
                auth_user=request.user,
                reel_id=reel_id,
                visibility=visibility,
            )
            
            return Response.success({
                'message': f'Visibility changed to {visibility}',
            })
        except:
            return Response.something_went_wrong()



        

class ListReel(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try: 
            reels = ReelService.list_all(
                auth_user=request.user,
                uid=request.query_params.get('of'),
                page=request.query_params.get('page'),
            )
            
            return Response.success({
                'message': 'All reel.',
                'reels': reels
            })
        except:
            return Response.something_went_wrong()
        




# Delete Reel
class DeleteReel(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def delete(self, request, reel_id):
        try:
            ReelService.delete_reel(
                auth_user=request.user,
                reel_id=reel_id,
            )

            # sending response
            return Response.success({
                'message': 'Reel deleted Successfully.'
            })
        except:
            return Response.something_went_wrong()
        




# Add Comment
class Comment(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request, reel_id):
        try: 
            serializer = serializers.AddCommentSerializer(data=request.data)

            if serializer.is_valid():
                response = CommentService.add_comment(
                    auth_user=request.user,
                    reel_id=reel_id,
                    data=serializer.validated_data,
                )
                
                # sending response
                return Response.success(response)
            
            return Response.errors(serializer.errors)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()
        

    def get(self, request, reel_id):
        try:
            comments = CommentService.list_all(request.user, reel_id)
            
            return Response.success({
                'message': 'All Comments.',
                'comments': comments
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()
        




# Delete Comment
class DeleteComment(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def delete(self, request, reel_id, comment_id):
        try:
            CommentService.delete_comment(
                auth_user=request.user,
                reel_id=reel_id,
                comment_id=comment_id,
            )

            # sending response
            return Response.success({
                'message': 'comment deleted Successfully.'
            })
        except:
            return Response.something_went_wrong()





# Add Like
class Like(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    # Like
    def post(self, request, reel_id):
        try:
            serializer = serializers.AddLikeSerializer(data=request.data)

            if serializer.is_valid():
                # posting like
                LikeService.like_reel(
                    auth_user=request.user, 
                    reel_id=reel_id,
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
    def get(self, request, reel_id):
        try:
            likes = LikeService.list_all(reel_id)
            
            return Response.success({
                'message': 'All Likes.',
                'likes': likes
            })
        except:
            return Response.something_went_wrong()


    # Dislike
    def delete(self, request, reel_id):
        try:
            LikeService.dislike_reel(
                auth_user=request.user,
                reel_id=reel_id,
            )

            # sending response
            return Response.success({
                'message': 'Reel Like deleted Successfully.'
            })
        except:
            return Response.something_went_wrong()






# Comment Like
class CommentLike(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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





# Add Audio
class AddAudio(APIView):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            serializer = serializers.AudioSerailzer(data=request.data)

            if serializer.is_valid():
                audio_json = AudioService.add_audio(
                    auth_user=request.user,
                    data=serializer.validated_data,
                )
            
                return Response.success({
                    'message': 'Audio added sucessfully.',
                    'audio': audio_json,
                })
            
            return Response.errors(serializer.errors)
        
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()
    



# List Audio
class ListAudio(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try: 
            audios = AudioService.list_all(auth_user=request.user)
            
            return Response.success({
                'message': 'All audio.',
                'audios': audios,
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()




# Delete Audio
class DeleteAudio(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def delete(self, request, audio_id):
        try: 
            AudioService.delete_audio(
                auth_user=request.user,
                audio_id=audio_id,
            )
            
            return Response.success({
                'message': 'Audio deleted.'
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()
