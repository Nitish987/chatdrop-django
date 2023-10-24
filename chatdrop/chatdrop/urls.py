from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # WEB
    path('', include('web.web_urls')),
    path('web/account/', include('account.web_urls')),
    path('web/notifier/', include('notifier.web_urls')),
    path('web/post/', include('post.web_urls')),
    path('web/friend/', include('friends.web_urls')),
    path('web/story/', include('stories.web_urls')),
    path('web/fanfollowing/', include('fanfollowing.web_urls')),
    path('web/feeds/', include('feeds.web_urls')),
    path('web/search/', include('search.web_urls')),
    path('web/privacy/', include('privacy.web_urls')),
    path('web/reel/', include('reel.web_urls')),
    path('web/facility/', include('facility.web_urls')),

    # REST
    path('api/account/', include('account.urls')),
    path('api/notifier/', include('notifier.urls')),
    path('api/post/', include('post.urls')),
    path('api/friend/', include('friends.urls')),
    path('api/story/', include('stories.urls')),
    path('api/fanfollowing/', include('fanfollowing.urls')),
    path('api/feeds/', include('feeds.urls')),
    path('api/search/', include('search.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/privacy/', include('privacy.urls')),
    path('api/reel/', include('reel.urls')),
    path('api/facility/', include('facility.urls')),
]