import notifier.services as notifier_services
import friends.services as friend_services
import fanfollowing.services as fan_services
import privacy.services as privacy_services

from .models import Reel, ReelVideo, ReelHashTag, ReelComment, ReelLike, ReelCommentLike, Audio, ReelView
from utils import generator, time
from django.utils import timezone
from account.services import UserService
from .exceptions import ReelError, CommentError, LikeError, AudioError
from django.core.paginator import Paginator
from utils.image_processing import ImageDetection



# Reel Services
class ReelService:
    '''ReelService for posting, deleting and listing reels.'''

    @staticmethod
    def is_reel_exists(id):
        return Reel.objects.filter(id=id).exists()

    @staticmethod
    def get_reel(id):
        return Reel.objects.get(id=id)
    
    @staticmethod
    def add_reel(auth_user, data):
        reel = None

        contains_hashtags = False
        if data.get('hashtags') != '':
            contains_hashtags = True
        
        posted_on = timezone.now()

        prediction = ImageDetection.process(image_bytes=data.get('thumbnail'))
        labels = prediction.labels
        if not prediction.is_safe:
            raise ReelError('Nude Video found.')

        reel = Reel.objects.create(
            id=generator.generate_identity(), 
            user=auth_user, 
            text=data.get('text'), 
            contains_hashtags=contains_hashtags,
            visibility=data.get('visibility'),
            posted_on=posted_on,
        )

        audio = None
        if data.get('audio_id') != 0 and data.get('audio_id') != None:
            audio = Audio.objects.get(id=data.get('audio_id'))

        ReelVideo.objects.create(
            reel=reel, 
            video=data.get('video'), 
            thumbnail=data.get('thumbnail'), 
            labels=labels,
            audio=audio, 
            aspect_ratio=data.get('aspect_ratio')
        )

        if reel is not None:
            user_tags = data.get('hashtags').split(',')
            for hashtag in user_tags:
                hashtag = str(hashtag)
                if hashtag.startswith('@'):
                    try:
                        user = UserService.get_user_by_username(username=hashtag[1:])
                        ReelHashTag.objects.create(reel=reel, type='USER', tag=f'@{user.username}::{user.uid}')
                    except:
                        pass
                elif hashtag.startswith('#'):
                    ReelHashTag.objects.create(reel=reel, type='TAG', tag=hashtag[1:])
                elif hashtag.startswith('https://') or hashtag.startswith('http://'):
                    ReelHashTag.objects.create(reel=reel, type='URL', tag=hashtag)
            
            auth_user.reel_count += 1
            auth_user.save()

        return reel
    
    @staticmethod
    def change_visibility(auth_user, reel_id, visibility):
        reel = ReelService.get_reel(id=reel_id)
        
        if reel.user.uid != auth_user.uid:
            raise ReelError('No permission to change visibility of this reel.')
        
        reel.visibility = visibility
        reel.save()
    
    @staticmethod
    def add_reel_view(auth_user, reel_id):
        reel = ReelService.get_reel(reel_id)

        # adding view to a story
        if not ReelView.objects.filter(reel=reel, seen_by=auth_user).exists():
            ReelView.objects.create(reel=reel, seen_by=auth_user)

            reel.views_count += 1
            reel.save()

    @staticmethod
    def delete_reel(auth_user, reel_id):
        reel = ReelService.get_reel(id=reel_id)

        if reel.user.uid != auth_user.uid:
            raise ReelError('No permission to delete post.')
        
        reel.delete()

        auth_user.reel_count -= 1
        auth_user.save()
    
    @staticmethod
    def to_json(reel: Reel, auth_user):
        # Profile
        profile = reel.user

        # calculating ago time
        time_ago = time.caltime_string(reel.posted_on)

        reel_json = {
            'id': reel.id,
            'user': {
                'uid': profile.uid,
                'name': profile.full_name,
                'photo': profile.photo_cdn_url,
                'username': profile.username,
                'gender': profile.gender,
                'message': profile.message,
            },
            'type': reel.reel_type,
            'visibility': reel.visibility,
            'posted_on': time_ago,
            'contains_hashtags': reel.contains_hashtags,
            'is_following': False,
            'views_count': reel.views_count,
            'likes_count': reel.likes_count,
            'comments_count': reel.comments_count,
            'hashtags': [],
            'text': reel.text,
            'video': None,
            'liked': None,
            'auth_user': {
                'uid': auth_user.uid,
                'name': auth_user.full_name,
                'photo': auth_user.photo_cdn_url,
                'username': auth_user.username,
                'gender': auth_user.gender,
                'message': auth_user.message,
            }
        }

        if auth_user.uid != profile.uid and fan_services.FollowService.is_following_exists(user=auth_user, follow=profile):
            reel_json['is_following'] = True

        try:
            like = ReelLike.objects.get(reel=reel, by=auth_user)
            reel_json['liked'] = like.type
        except:
            pass

        if reel.contains_hashtags:
            hashtags = ReelHashTag.objects.filter(reel=reel)
            
            reel_json['hashtags'] = []

            for tag in hashtags:
                reel_json['hashtags'].append({
                    'type': tag.type,
                    'tag': tag.tag
                })

        video = ReelVideo.objects.get(reel=reel)
        
        reel_json['video'] = {
            'url': video.cdn_url,
            'thumbnail': video.cdn_thumbnail_url,
            'labels': video.labels,
            'audio': None if video.audio == None else AudioService.to_json(video.audio),
            'aspect_ratio': video.aspect_ratio,
        }

        return reel_json
    
    @staticmethod
    def view_reel(auth_user, reel_id):
        reel = ReelService.get_reel(id=reel_id)

        if privacy_services.BlockedUserService.is_blocked(user=reel.user, blocked_user=auth_user):
            return None

        if reel.is_private and auth_user.uid != reel.user.uid:
            return None

        if reel.is_only_friends and auth_user.uid != reel.user.uid:
            if not friend_services.FriendService.is_friend_exists(user=auth_user, friend=reel.user):
                return None

        reel_json = ReelService.to_json(reel=reel, auth_user=auth_user)
        return reel_json

    @staticmethod
    def list_all(auth_user, uid, page):
        user = UserService.get_user(uid)

        reels = Reel.objects.filter(user=user).order_by('-posted_on')

        pagination = Paginator(reels, 100)
        paginated_reels = pagination.get_page(int(page))
        
        reel_list = []
        for reel in paginated_reels.object_list:
            if privacy_services.BlockedUserService.is_blocked(user=reel.user, blocked_user=auth_user):
                continue
            
            if reel.is_private and auth_user.uid != user.uid:
                continue

            if reel.is_only_friends and auth_user.uid != user.uid:
                if not friend_services.FriendService.is_friend_exists(user=auth_user, friend=user):
                    continue

            reel_json = ReelService.to_json(reel=reel, auth_user=auth_user)
            reel_list.append(reel_json)
        
        return reel_list
    

# Comment Paginator
class CommentService:
    '''Comment service for commenting on reel.'''
    @staticmethod
    def is_comment_exists(id, reel):
        return ReelComment.objects.filter(id=id, reel=reel).exists()

    @staticmethod
    def get_comment_on_reel(id, reel):
        return ReelComment.objects.get(id=id, reel=reel)
    
    @staticmethod
    def get_comment_by_id(id):
        return ReelComment.objects.get(id=id)
    
    @staticmethod
    def add_comment(auth_user, reel_id, data):
        reel = ReelService.get_reel(reel_id)

        comment = ReelComment.objects.create(
            reel=reel,
            by=auth_user,
            text=data.get('text')
        )

        # upgrading comment counts
        reel.comments_count += 1
        reel.save()

        if reel.user.uid != auth_user.uid:
            # sending user a notification
            notifier_services.NotificationChannelService.push_notification(
                from_user=auth_user,
                to_user=reel.user,
                refer=reel.id,
                subject='Reel',
                body='comment on your reel.',
                type='REEL_COMMENT'
            )

        # calculating ago time
        time_ago = time.caltime_string(comment.commented_on)

        return {
            'message': 'Commented Successfully.',
            'comment': {
                'id': comment.id,
                'reel_id': comment.reel.id,
                'user': {
                    'uid': auth_user.uid,
                    'name': auth_user.full_name,
                    'photo': auth_user.photo_cdn_url,
                    'username': auth_user.username,
                    'gender': auth_user.gender,
                },
                'text': comment.text,
                'likes_count': comment.likes_count,
                'commented_on': time_ago,
                'liked': None,
            }
        }

    @staticmethod
    def delete_comment(auth_user, reel_id, comment_id):
        reel = ReelService.get_reel(reel_id)
        comment = CommentService.get_comment_on_reel(comment_id, reel)

        if comment.by.uid == auth_user.uid or reel.user.uid == auth_user.uid:
            comment.delete()

            # downgrading comment counts
            reel.comments_count -= 1
            reel.save()
        else:
            raise CommentError('No permission for deleting comment')

    @staticmethod
    def list_all(user, reel_id):
        reel = Reel.objects.get(id=reel_id)
        comments = ReelComment.objects.filter(reel=reel)

        comments_list = []
        for comment in comments:
            if privacy_services.BlockedUserService.is_blocked(user=comment.by, blocked_user=user):
                continue
            
            # Profile
            profile = comment.by

            # calculating ago time
            time_ago = time.caltime_string(comment.commented_on)

            comment_json = {
                'id': comment.id,
                'reel_id': comment.reel.id,
                'user': {
                    'uid': profile.uid,
                    'name': profile.full_name,
                    'photo': profile.photo_cdn_url,
                    'username': profile.username,
                    'gender': profile.gender,
                    'message': profile.message,
                },
                'text': comment.text,
                'likes_count': comment.likes_count,
                'commented_on': time_ago,
                'liked': None,
            }

            try:
                like = ReelCommentLike.objects.get(comment=comment, by=user)
                comment_json['liked'] = like.type
            except:
                pass

            comments_list.append(comment_json)

        return comments_list


# Like Paginator
class LikeService:
    '''Like Service for like and dislike the reel'''
    @staticmethod
    def get_like_on_reel(reel, by):
        return ReelLike.objects.get(reel=reel, by=by)

    @staticmethod
    def like_reel(auth_user, reel_id, data):
        reel = ReelService.get_reel(reel_id)

        try:
            like = ReelLike.objects.get(reel=reel, by=auth_user)
            like.type = data.get('type')
            like.save()
        except:
            like = ReelLike.objects.create(
                reel=reel, 
                by=auth_user, 
                type=data.get('type'),
            )
        
            # upgrading like counts
            reel.likes_count += 1
            reel.save()
        
        if reel.user.uid != auth_user.uid:
            # sending user a notification
            notifier_services.NotificationChannelService.push_notification(
                from_user=auth_user,
                to_user=reel.user,
                refer=reel.id,
                subject='Like',
                body='liked your reel.',
                type='REEL_LIKE'
            )

        return like
    
    @staticmethod
    def dislike_reel(auth_user, reel_id):
        reel = ReelService.get_reel(reel_id)
        like = LikeService.get_like_on_reel(reel, auth_user)

        if like.by.uid != auth_user.uid:
            raise LikeError('No permission for dislike this reel')
        
        like.delete()

        reel.likes_count -= 1
        reel.save()

    @staticmethod
    def list_all(reel_id):
        reel = Reel.objects.get(id=reel_id)
        likes = ReelLike.objects.filter(reel=reel)

        likes_list = []
        for like in likes:
            likes_list.append({
                'id': like.id,
                'reel_id': like.reel.id,
                'by': like.by.uid,
                'type': like.type
            })

        return likes_list


# Like Paginator
class CommentLikeService:
    '''Comment like service for like and dislike comments on reel.'''

    @staticmethod
    def get_comment_like_on_comment(comment, by):
        return ReelCommentLike.objects.get(comment=comment, by=by)

    @staticmethod
    def like_comment(auth_user, comment_id, data):
        comment = CommentService.get_comment_by_id(comment_id)

        try:
            like = ReelCommentLike.objects.get(comment=comment, by=auth_user)
            like.type = data.get('type')
            like.save()
        except:
            like = ReelCommentLike.objects.create(
                comment=comment, 
                by=auth_user, 
                type= data.get('type'),
            )
        
            # upgrading like counts
            comment.likes_count += 1
            comment.save()
        
        if comment.by.uid != auth_user.uid:
            # sending user a notification
            notifier_services.NotificationChannelService.push_notification(
                from_user=auth_user,
                to_user=comment.by,
                refer=comment.reel.id,
                subject='Like',
                body='liked your comment.',
                type='REEL_COMMENT_LIKE',
            )

        return like

    @staticmethod
    def dislike_comment(auth_user, comment_id):
        comment = CommentService.get_comment_by_id(comment_id)
        like = CommentLikeService.get_comment_like_on_comment(comment, auth_user)

        if like.by.uid != auth_user.uid:
            raise LikeError('No permission for dislike this comment')
        
        like.delete()

        comment.likes_count -= 1
        comment.save()

    @staticmethod
    def list_all(comment_id):
        comment = ReelComment.objects.get(id=comment_id)
        likes = ReelCommentLike.objects.filter(comment=comment)

        likes_list = []
        for like in likes:
            likes_list.append({
                'id': like.id,
                'comment_id': like.comment.id,
                'by': like.by.uid,
                'type': like.type
            })

        return likes_list





# Audio Service
class AudioService:
    @staticmethod
    def add_audio(auth_user, data: dict):
        audio = Audio.objects.create(
            user=auth_user,
            name=data.get('name'),
            audio=data.get('audio'),
            duration=data.get('duration'),
        )

        return AudioService.to_json(audio)
    
    @staticmethod
    def delete_audio(auth_user, audio_id):
        audio = Audio.objects.get(id=audio_id)

        if audio.user.uid != auth_user.uid:
            raise AudioError('No Permission to delete this audio.')
    
        audio.delete()
    
    @staticmethod
    def to_json(audio: Audio):
        return {
            'id': audio.id,
            'name': audio.name,
            'filename': audio.filename,
            'url': audio.cdn_url,
            'duration': audio.duration,
            'from_user': {
                'uid': audio.user.uid,
                'name': audio.user.full_name,
                'photo': audio.user.photo_cdn_url,
                'username': audio.user.username,
                'gender': audio.user.gender,
                'message': audio.user.message,
            },
        }
    
    @staticmethod
    def list_all(auth_user):
        audios = Audio.objects.filter(user=auth_user)
        return [AudioService.to_json(audio) for audio in audios]
