from django.urls import path
from . import web_views

urlpatterns = [
    path('v2/story/add/', web_views.AddStoryV2.as_view(), name='web-add-story-v2'),
    path('v1/story/list/', web_views.ListStory.as_view(), name='web-list-story'),
    path('v1/story/<str:story_id>/viewer/', web_views.StoryViewer.as_view(), name='web-story-viewer'),
    path('v1/story/<str:story_id>/delete/', web_views.DeleteStory.as_view(), name='web-delete-story'),
]