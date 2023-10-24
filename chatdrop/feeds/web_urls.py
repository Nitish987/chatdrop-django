from django.urls import path
from . import web_views

urlpatterns = [
    path('v3/feeds/timeline/', web_views.TimeLineFeedsV3.as_view(), name='web-timeline-v3'),
    path('v1/feeds/storyline/', web_views.StoryLineFeeds.as_view(), name='web-storyline'),
    path('v1/feeds/reelline/', web_views.ReelLineFeeds.as_view(), name='web-reelline'),
]
