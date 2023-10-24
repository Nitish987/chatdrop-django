from django.urls import path
from . import views

urlpatterns = [
    # path('v1/feeds/timeline/', views.TimeLineFeeds.as_view(), name='timeline'), # removed
    path('v2/feeds/timeline/', views.TimeLineFeedsV2.as_view(), name='timeline-v2'), # deprecated
    path('v3/feeds/timeline/', views.TimeLineFeedsV3.as_view(), name='timeline-v3'),

    path('v1/feeds/storyline/', views.StoryLineFeeds.as_view(), name='storyline'),
    path('v1/feeds/reelline/', views.ReelLineFeeds.as_view(), name='reelline'),
]
