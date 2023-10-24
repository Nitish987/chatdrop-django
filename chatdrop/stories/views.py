from rest_framework.views import APIView
from utils.response import Response
from utils.debug import debug_print
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsRequestValid
from account.throttling import AuthenticatedUserThrottling
from . import serializers
from .services import StoryService


# Add Story

# deprecated
class AddStory(APIView):
    '''This api is deprecated, must use v2.'''
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            content_type = request.query_params.get('content_type')
            serializer = None

            if content_type == 'TEXT':
                serializer = serializers.TextStorySerializer(data=request.data)
            
            elif content_type == 'PHOTO':
                serializer = serializers.PhotoStorySerializer(data=request.data)
            
            elif content_type == 'VIDEO':
                serializer = serializers.VideoStorySerializer(data=request.data)
            
            # validating serializer
            if serializer is not None and serializer.is_valid():

                # saving story
                StoryService.add_story(
                    auth_user=request.user,
                    content_type=content_type,
                    data=serializer.validated_data,
                )

                # sending response
                return Response.success({
                    'message': 'Story added Successfully'
                })

            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()


class AddStoryV2(APIView):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            content_type = request.query_params.get('content_type')
            serializer = None

            if content_type == 'TEXT':
                serializer = serializers.TextStorySerializerV2(data=request.data)
            
            elif content_type == 'PHOTO':
                serializer = serializers.PhotoStorySerializerV2(data=request.data)
            
            elif content_type == 'VIDEO':
                serializer = serializers.VideoStorySerializerV2(data=request.data)
            
            # validating serializer
            if serializer is not None and serializer.is_valid():

                # saving story
                StoryService.add_story_v2(
                    auth_user=request.user,
                    content_type=content_type,
                    data=serializer.validated_data,
                )

                # sending response
                return Response.success({
                    'message': 'Story added Successfully'
                })

            return Response.errors(serializer.errors)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# List Story
class ListStory(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            # listing stories
            stories = StoryService.list_all_with_checks(
                auth_user=request.user,
                uid=request.query_params.get('of')
            )

            return Response.success({
                'message': 'All Story.',
                'stories': stories
            })
        except:
            return Response.something_went_wrong()


# Delete Story
class DeleteStory(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def delete(self, request, story_id):
        try:
            StoryService.delete_story(
                auth_user=request.user,
                story_id=story_id,
            )

            # sending response
            return Response.success({
                'message': 'Story deleted Successfully.'
            })
        except:
            return Response.something_went_wrong()




# Story Viewer
class StoryViewer(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request, story_id):
        try:
            # adding story view
            StoryService.add_story_view(
                auth_user=request.user,
                story_id=story_id
            )

            return Response.success({
                'message': 'Story view added.'
            })
        except:
            return Response.something_went_wrong()

    def get(self, request, story_id):
        try:
            # listing story viewers
            viewers = StoryService.list_all_story_views(
                auth_user=request.user,
                story_id=story_id
            )

            return Response.success({
                'message': 'All story viewers.',
                'viewers': viewers
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()