import friends.services as friend_services
import reel.services as reel_services
import privacy.services as privacy_services

from friends.models import Friend
from fanfollowing.models import Following
from post.models import Post, PostHashTag
from account.services import UserService
from random import shuffle
from stories.services import StoryService
from django.core.paginator import Paginator
from django.db.models import Q
from post.services import PostService
from reel.models import Reel
from deprecated.sphinx import deprecated


# TimeLine Paginator
class TimeLineService:
    @deprecated(version='2', reason='This method is deprecated, must use v3')
    @staticmethod
    def serialize_post_v2(user, posts):
        '''This method is deprecated, must use v3.'''
        post_list = []

        counted = []
        for post in posts:
            if privacy_services.BlockedUserService.is_blocked(user=post.user, blocked_user=user):
                continue

            if post.id in counted or (post.is_private and post.user.uid != user.uid):
                continue

            if post.is_only_friends and user.uid != post.user.uid:
                if not friend_services.FriendService.is_friend_exists(user=user, friend=post.user):
                    continue

            counted.append(post.id)
            
            post_json = PostService.form_post_content_json_v2(post=post, auth_user=user)
            post_list.append(post_json)
        
        return post_list
    
    @staticmethod
    def serialize_post_v3(user, posts):
        post_list = []

        counted = []
        for post in posts:
            if privacy_services.BlockedUserService.is_blocked(user=post.user, blocked_user=user):
                continue

            if post.id in counted or (post.is_private and post.user.uid != user.uid):
                continue

            if post.is_only_friends and user.uid != post.user.uid:
                if not friend_services.FriendService.is_friend_exists(user=user, friend=post.user):
                    continue

            counted.append(post.id)
            
            post_json = PostService.to_json_v3(post=post, auth_user=user)
            post_list.append(post_json)
        
        return post_list

    
    @deprecated(version='2', reason='This method is deprecated, must use v3')
    @staticmethod
    def generate_timeline_feeds_v2(user, page):
        '''This method is deprecated, must use v3.'''
        feeds_query = []

        friends = Friend.objects.filter(user=user)
        for friend in friends:
            feeds_query += Post.objects.filter(user=friend.friend).order_by('-posted_on')
        
        followings = Following.objects.filter(user=user)
        for following in followings:
            feeds_query += Post.objects.filter(user=following.follow).order_by('-posted_on')

        feeds_query += Post.objects.filter(user=user).order_by('-posted_on')

        q = user.interest.strip().split(',') + [user.location, f'@{user.username}::{user.uid}']
        hashtags = PostHashTag.objects.filter(Q(tag__in=q))
        for hashtag in hashtags:
            feeds_query.append(hashtag.post)

        feeds_query += Post.objects.filter(visibility='PUBLIC')

        pagination = Paginator(feeds_query, 50)
        paginated_posts = pagination.get_page(int(page))

        feed_json = TimeLineService.serialize_post_v2(user, paginated_posts.object_list)

        shuffle(feed_json)

        return feed_json, paginated_posts.has_next()

    @staticmethod
    def generate_timeline_feeds_v3(user, page):
        feeds_query = []

        friends = Friend.objects.filter(user=user)
        for friend in friends:
            feeds_query += Post.objects.filter(user=friend.friend).order_by('-posted_on')
        
        followings = Following.objects.filter(user=user)
        for following in followings:
            feeds_query += Post.objects.filter(user=following.follow).order_by('-posted_on')

        feeds_query += Post.objects.filter(user=user).order_by('-posted_on')

        q = user.interest.strip().split(',') + [user.location, f'@{user.username}::{user.uid}']
        hashtags = PostHashTag.objects.filter(Q(tag__in=q))
        for hashtag in hashtags:
            feeds_query.append(hashtag.post)

        feeds_query += Post.objects.filter(visibility='PUBLIC')

        pagination = Paginator(feeds_query, 50)
        paginated_posts = pagination.get_page(int(page))

        feed_json = TimeLineService.serialize_post_v3(user, paginated_posts.object_list)

        shuffle(feed_json)

        return feed_json, paginated_posts.has_next()


# Story Feeds
class StoryLineFeedsService:
    @staticmethod
    def list_all(user):
        feed_list = [{
            'user': {
                'uid': user.uid,
                'name': user.full_name,
                'photo': user.photo_cdn_url,
                'username': user.username,
                'gender': user.gender, 
                'message': user.message,
            },
            'stories': StoryService.list_all(user)
        }]

        friends = Friend.objects.filter(user=user)
        for friend in friends:
            stories = StoryService.list_all(friend.friend)

            # Profile
            profile = UserService.get_user(uid=friend.friend.uid)


            if len(stories) > 0:
                feed_list.append({
                    'user': {
                        'uid': profile.uid,
                        'name': profile.full_name,
                        'photo': profile.photo_cdn_url,
                        'username': profile.username,
                        'gender': profile.gender,
                        'message': profile.message,
                        'chatroom': friend.chat_room,
                    },
                    'stories': stories
                })

        return feed_list
                
            


            

# reel line feeds
class ReelLineService:
    @staticmethod
    def list_all(auth_user, page):
        feed_list = []
        reels = Reel.objects.all()

        pagination = Paginator(reels, 100)
        paginated_reels = pagination.get_page(int(page))

        reel_service = reel_services.ReelService

        counted = []
        for reel in paginated_reels.object_list:
            if privacy_services.BlockedUserService.is_blocked(user=reel.user, blocked_user=auth_user):
                continue

            if reel.id in counted or (reel.is_private and reel.user.uid != auth_user.uid):
                continue

            if reel.is_only_friends and auth_user.uid != reel.user.uid:
                if not friend_services.FriendService.is_friend_exists(user=auth_user, friend=reel.user):
                    continue

            feed_list.append(reel_service.to_json(reel, auth_user=auth_user))
        
        shuffle(feed_list)
        
        return feed_list, paginated_reels.has_next()

