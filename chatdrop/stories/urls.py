from django.urls import path
from . import views

urlpatterns = [
    path('v1/story/add/', views.AddStory.as_view(), name='add-story'), # deprecated
    path('v2/story/add/', views.AddStoryV2.as_view(), name='add-story-v2'),
    
    path('v1/story/list/', views.ListStory.as_view(), name='list-story'),
    path('v1/story/<str:story_id>/viewer/', views.StoryViewer.as_view(), name='story-viewer'),
    path('v1/story/<str:story_id>/delete/', views.DeleteStory.as_view(), name='delete-story'),
]
