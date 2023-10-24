from .models import Story, StoryView
from django.utils import timezone
from datetime import timedelta
from utils import generator, time
from account.services import UserService
from .exceptions import StoryError
from friends.services import FriendService
from deprecated.sphinx import deprecated


# Story Service
class StoryService:
    '''Story Service for post and deleting stories.'''

    def get_story(id):
        return Story.objects.get(id=id)

    @deprecated(version='1', reason='This add story function is depreated, must use v2.')
    @staticmethod
    def add_story(auth_user, content_type, data):
        '''This add story function is deprecated, must use v2.'''
        story = None

        posted_on = timezone.now()
        active_until = posted_on + timedelta(days=1)

        if content_type == 'TEXT':
            story = Story.objects.create(
                id=generator.generate_identity(),
                user=auth_user, 
                content_type=content_type, 
                text=data.get('text'),
                content=data.get('photo'),
                posted_on=posted_on,
                active_until=active_until
            )
            
        elif content_type == 'PHOTO':
            story = Story.objects.create(
                id=generator.generate_identity(),
                user=auth_user, 
                content_type=content_type, 
                content=data.get('photo'),
                posted_on=posted_on,
                active_until=active_until
            )
        
        elif content_type == 'VIDEO':
            story = Story.objects.create(
                id=generator.generate_identity(),
                user=auth_user, 
                content_type=content_type, 
                content=data.get('video'),
                posted_on=posted_on,
                active_until=active_until
            )
       
        return story
    
    @staticmethod
    def add_story_v2(auth_user, content_type, data):
        story = None

        posted_on = timezone.now()
        active_until = posted_on + timedelta(days=1)

        if content_type == 'TEXT':
            story = Story.objects.create(
                id=generator.generate_identity(),
                user=auth_user, 
                content_type=content_type,
                content=data.get('photo'),
                posted_on=posted_on,
                active_until=active_until
            )
            
        elif content_type == 'PHOTO':
            story = Story.objects.create(
                id=generator.generate_identity(),
                user=auth_user, 
                content_type=content_type, 
                content=data.get('photo'),
                text=data.get('text'),
                posted_on=posted_on,
                active_until=active_until
            )
        
        elif content_type == 'VIDEO':
            story = Story.objects.create(
                id=generator.generate_identity(),
                user=auth_user, 
                content_type=content_type, 
                content=data.get('video'),
                text=data.get('text'),
                posted_on=posted_on,
                active_until=active_until
            )
       
        return story
    
    @staticmethod
    def delete_story(auth_user, story_id):
        story = StoryService.get_story(story_id)

        if story.user.uid != auth_user.uid:
            raise StoryError('No Permission to delete this story.')
            
        # deleting story
        story.delete() 
    
    @staticmethod
    def list_all(user):
        stories = Story.objects.filter(user=user).order_by('posted_on')

        story_list = []
        for story in stories:
            # checking story active state
            
            if story.is_active:

                # calculating ago time
                time_ago = time.caltime_string(posted_on=story.posted_on)

                story_json = {
                    'id': story.id,
                    'content_type': story.content_type,
                    'content': story.content_cdn_url,
                    'text': story.text,
                    'posted_on': time_ago,
                    'likes_count': story.likes_count
                }

                story_list.append(story_json)

        return story_list

    @staticmethod
    def list_all_with_checks(auth_user, uid):
        if auth_user.uid == uid:
            user = auth_user
        else:
            user = UserService.get_user(uid)
        
        # checking whether the user is same user or user is friend of the user of which stories are requested
        if auth_user.uid == user.uid or FriendService.is_friend_exists(user=auth_user, friend=user):

            return StoryService.list_all(user)
        
        raise StoryError('No permission to list stories.')
    
    @staticmethod
    def add_story_view(auth_user, story_id):
        story = StoryService.get_story(story_id)

        # adding view to a story
        if not StoryView.objects.filter(story=story, seen_by=auth_user).exists():
            StoryView.objects.create(story=story, seen_by=auth_user)

            story.views_count += 1
            story.save()
    
    @staticmethod
    def list_all_story_views(auth_user, story_id):
        story = StoryService.get_story(story_id)

        # throwing error if story is not uploaded by the auth user
        if story.user.uid != auth_user.uid:
            raise StoryError('No Permission to view this.')

        viewers_list = []
        viewers = StoryView.objects.filter(story=story)
        
        for viewer in viewers:
            user_json = {
                'uid': viewer.seen_by.uid,
                'name': viewer.seen_by.full_name,
                'photo': viewer.seen_by.photo_cdn_url,
                'username': viewer.seen_by.username,
                'gender': viewer.seen_by.gender,
                'message': viewer.seen_by.message,
            }

            viewers_list.append(user_json)

        return viewers_list
