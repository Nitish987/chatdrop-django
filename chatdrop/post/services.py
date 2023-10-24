import notifier.services as notifier_services
import friends.services as friend_services
import privacy.services as privacy_services

from .models import Post, PostPhoto, PostVideo, PostHashTag, PostComment, PostLike, PostCommentLike
from utils import generator, time
from django.utils import timezone
from account.services import UserService
from .exceptions import PostError, CommentError, LikeError
from django.core.paginator import Paginator
from utils.image_processing import ImageDetection, InvalidImageError
from deprecated.sphinx import deprecated


# Post Paginator
class PostService:
    '''Post Service for posting, deleting and listing posts.'''

    @staticmethod
    def is_post_exists(id):
        return Post.objects.filter(id=id).exists()

    @staticmethod
    def get_post(id):
        return Post.objects.get(id=id)
    
    @deprecated(version='2', reason='This method is deprecated, must use v3.')
    @staticmethod
    def add_post_v2(auth_user, content_type, data):
        '''This method is deprecated, must use v3.'''
        post = None

        contains_hashtags = False
        if data.get('hashtags') != '':
            contains_hashtags = True
        
        posted_on = timezone.now()


        if content_type == 'TEXT':
            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user,
                text=data.get('text'),
                content_type=content_type,
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

        elif content_type == 'PHOTO':
            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user, 
                content_type=content_type, 
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

            aspect_ratios = data.get('aspect_ratios')
            for i, photo in enumerate(data.get('photos')):
                PostPhoto.objects.create(post=post, photo=photo, aspect_ratio=aspect_ratios[i])

        elif content_type == 'VIDEO':
            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user, 
                content_type=content_type, 
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

            PostVideo.objects.create(post=post, video=data.get('video'), aspect_ratio=data.get('aspect_ratio'))

        elif content_type == 'TEXT_PHOTO':
            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user, 
                text=data.get('text'), 
                content_type=content_type, 
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

            aspect_ratios = data.get('aspect_ratios')
            for i, photo in enumerate(data.get('photos')):
                PostPhoto.objects.create(post=post, photo=photo, aspect_ratio=aspect_ratios[i])

        elif content_type == 'TEXT_VIDEO':
            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user, 
                text=data.get('text'), 
                content_type=content_type, 
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

            PostVideo.objects.create(post=post, video=data.get('video'), aspect_ratio=data.get('aspect_ratio'))

        if post is not None:
            user_tags = data.get('hashtags').split(',')
            for hashtag in user_tags:
                hashtag = str(hashtag)
                if hashtag.startswith('@'):
                    try:
                        user = UserService.get_user_by_username(username=hashtag[1:])
                        PostHashTag.objects.create(post=post, type='USER', tag=f'@{user.username}::{user.uid}')
                    except:
                        pass
                elif hashtag.startswith('#'):
                    PostHashTag.objects.create(post=post, type='TAG', tag=hashtag[1:])
                elif hashtag.startswith('https://') or hashtag.startswith('http://'):
                    PostHashTag.objects.create(post=post, type='URL', tag=hashtag)
            
            auth_user.post_count += 1
            auth_user.save()

        return post
    
    @staticmethod
    def add_post_v3(auth_user, content_type, data):
        post = None

        contains_hashtags = False
        if data.get('hashtags') != '':
            contains_hashtags = True
        
        posted_on = timezone.now()


        if content_type == 'TEXT':
            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user,
                text=data.get('text'),
                content_type=content_type,
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

        elif content_type == 'PHOTO':
            labels = []
            for photo in data.get('photos'):
                prediction = ImageDetection.process(image_bytes=photo.file)
                labels.append(prediction.labels)
                if not prediction.is_safe:
                    raise InvalidImageError('Nude Image found')
            
            if len(labels) != len(data.get('photos')) or len(labels) != len(data.get('aspect_ratios')):
                raise PostError('something went wrong in posting.')


            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user, 
                content_type=content_type, 
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

            aspect_ratios = data.get('aspect_ratios')
            for i, photo in enumerate(data.get('photos')):
                PostPhoto.objects.create(post=post, photo=photo, labels=labels[i], aspect_ratio=aspect_ratios[i])

        elif content_type == 'VIDEO':
            thumbnail = data.get('thumbnail')
            prediction = ImageDetection.process(image_bytes=thumbnail.file)
            labels = prediction.labels
            if not prediction.is_safe:
                raise InvalidImageError('Nude Video found')
            
            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user, 
                content_type=content_type, 
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

            PostVideo.objects.create(
                post=post, 
                video=data.get('video'), 
                thumbnail=data.get('thumbnail'), 
                labels=labels, 
                aspect_ratio=data.get('aspect_ratio'),
            )

        elif content_type == 'TEXT_PHOTO':
            labels = []
            for photo in data.get('photos'):
                prediction = ImageDetection.process(image_bytes=photo.file)
                labels.append(prediction.labels)
                if not prediction.is_safe:
                    raise InvalidImageError('Nude Image found')
            
            if len(labels) != len(data.get('photos')) or len(labels) != len(data.get('aspect_ratios')):
                raise PostError('something went wrong in posting.')
            
            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user, 
                text=data.get('text'), 
                content_type=content_type, 
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

            aspect_ratios = data.get('aspect_ratios')
            for i, photo in enumerate(data.get('photos')):
                PostPhoto.objects.create(post=post, photo=photo, labels=labels[i], aspect_ratio=aspect_ratios[i])

        elif content_type == 'TEXT_VIDEO':
            thumbnail = data.get('thumbnail')
            prediction = ImageDetection.process(image_bytes=thumbnail.file)
            labels = prediction.labels
            if not prediction.is_safe:
                raise InvalidImageError('Nude Video found')
            
            post = Post.objects.create(
                id=generator.generate_identity(), 
                user=auth_user, 
                text=data.get('text'), 
                content_type=content_type, 
                contains_hashtags=contains_hashtags,
                visibility=data.get('visibility'),
                posted_on=posted_on,
            )

            PostVideo.objects.create(
                post=post, 
                video=data.get('video'), 
                thumbnail=data.get('thumbnail'), 
                labels=labels, 
                aspect_ratio=data.get('aspect_ratio'),
            )

        if post is not None:
            user_tags = data.get('hashtags').split(',')
            for hashtag in user_tags:
                hashtag = str(hashtag)
                if hashtag.startswith('@'):
                    try:
                        user = UserService.get_user_by_username(username=hashtag[1:])
                        PostHashTag.objects.create(post=post, type='USER', tag=f'@{user.username}::{user.uid}')
                    except:
                        pass
                elif hashtag.startswith('#'):
                    PostHashTag.objects.create(post=post, type='TAG', tag=hashtag[1:])
                elif hashtag.startswith('https://') or hashtag.startswith('http://'):
                    PostHashTag.objects.create(post=post, type='URL', tag=hashtag)
            
            auth_user.post_count += 1
            auth_user.save()

        return post

    @staticmethod
    def change_visibility(auth_user, post_id, visibility):
        post = PostService.get_post(id=post_id)
        
        if post.user.uid != auth_user.uid:
            raise PostError('No permission to delete post.')
        
        post.visibility = visibility
        post.save()


    @staticmethod
    def delete_post(auth_user, post_id):
        post = PostService.get_post(id=post_id)

        if post.user.uid != auth_user.uid:
            raise PostError('No permission to delete post.')
        
        post.delete()

        auth_user.post_count -= 1
        auth_user.save()

    @deprecated(version='2', reason='This method is deprecated, must use to_json_v3 method')
    @staticmethod
    def form_post_content_json_v2(post, auth_user):
        '''This method is deprecated. must use to_json v3 method'''
        # Profile
        profile = post.user

        # calculating ago time
        time_ago = time.caltime_string(post.posted_on)

        post_json = {
            'id': post.id,
            'user': {
                'uid': profile.uid,
                'name': profile.full_name,
                'photo': profile.photo_cdn_url,
                'username': profile.username,
                'gender': profile.gender,
                'message': profile.message,
            },
            'type': post.post_type,
            'visibility': post.visibility,
            'content_type': post.content_type,
            'posted_on': time_ago,
            'contains_hashtags': post.contains_hashtags,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'hashtags': [],
            'text': None,
            'photos': [],
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

        try:
            like = PostLike.objects.get(post=post, by=auth_user)
            post_json['liked'] = like.type
        except:
            pass

        if post.contains_hashtags:
            hashtags = PostHashTag.objects.filter(post=post)
            
            post_json['hashtags'] = []

            for tag in hashtags:
                post_json['hashtags'].append({
                    'type': tag.type,
                    'tag': tag.tag
                })
            
        if post.content_type == 'TEXT' or post.content_type == 'TEXT_PHOTO' or post.content_type == 'TEXT_VIDEO' or post.content_type == 'TEXT_PDF':
            post_json['text'] = post.text
            
        if post.content_type == 'PHOTO' or post.content_type == 'TEXT_PHOTO':
            photos = PostPhoto.objects.filter(post=post)
            
            post_json['photos'] = []

            for photo in photos:
                post_json['photos'].append({
                    'url': photo.cdn_url,
                    'aspect_ratio': photo.aspect_ratio,
                })

        if post.content_type == 'VIDEO' or post.content_type == 'TEXT_VIDEO':
            video = PostVideo.objects.get(post=post)
            
            post_json['video'] = {
                'url': video.cdn_url,
                'aspect_ratio': video.aspect_ratio,
            }

        return post_json
    
    @staticmethod
    def to_json_v3(post, auth_user):
        # Profile
        profile = post.user

        # calculating ago time
        time_ago = time.caltime_string(post.posted_on)

        post_json = {
            'id': post.id,
            'user': {
                'uid': profile.uid,
                'name': profile.full_name,
                'photo': profile.photo_cdn_url,
                'username': profile.username,
                'gender': profile.gender,
                'message': profile.message,
            },
            'type': post.post_type,
            'visibility': post.visibility,
            'content_type': post.content_type,
            'posted_on': time_ago,
            'contains_hashtags': post.contains_hashtags,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'hashtags': [],
            'text': None,
            'photos': [],
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

        try:
            like = PostLike.objects.get(post=post, by=auth_user)
            post_json['liked'] = like.type
        except:
            pass

        if post.contains_hashtags:
            hashtags = PostHashTag.objects.filter(post=post)
            
            post_json['hashtags'] = []

            for tag in hashtags:
                post_json['hashtags'].append({
                    'type': tag.type,
                    'tag': tag.tag
                })
            
        if post.content_type == 'TEXT' or post.content_type == 'TEXT_PHOTO' or post.content_type == 'TEXT_VIDEO':
            post_json['text'] = post.text
            
        if post.content_type == 'PHOTO' or post.content_type == 'TEXT_PHOTO':
            photos = PostPhoto.objects.filter(post=post)
            
            post_json['photos'] = []

            for photo in photos:
                post_json['photos'].append({
                    'url': photo.cdn_url,
                    'aspect_ratio': photo.aspect_ratio,
                    'labels': photo.labels,
                })

        if post.content_type == 'VIDEO' or post.content_type == 'TEXT_VIDEO':
            video = PostVideo.objects.get(post=post)
            
            post_json['video'] = {
                'url': video.cdn_url,
                'aspect_ratio': video.aspect_ratio,
                'thumbnail': video.cdn_thumbnail_url,
                'labels': video.labels,
            }

        return post_json
    
    @deprecated(version='1', reason='This method is deprecated, must use v2.')
    @staticmethod
    def view_post(auth_user, post_id):
        '''This method is deprecated, must use v2'''
        post = PostService.get_post(id=post_id)

        if privacy_services.BlockedUserService.is_blocked(user=post.user, blocked_user=auth_user):
            return None

        if post.is_private and auth_user.uid != post.user.uid:
            return None

        if post.is_only_friends and auth_user.uid != post.user.uid:
            if not friend_services.FriendService.is_friend_exists(user=auth_user, friend=post.user):
                return None

        post_json = PostService.form_post_content_json_v2(post=post, auth_user=auth_user)
        return post_json
    
    @staticmethod
    def view_post_v2(auth_user, post_id):
        post = PostService.get_post(id=post_id)

        if privacy_services.BlockedUserService.is_blocked(user=post.user, blocked_user=auth_user):
            return None

        if post.is_private and auth_user.uid != post.user.uid:
            return None

        if post.is_only_friends and auth_user.uid != post.user.uid:
            if not friend_services.FriendService.is_friend_exists(user=auth_user, friend=post.user):
                return None

        post_json = PostService.to_json_v3(post=post, auth_user=auth_user)
        return post_json
    
    @deprecated(version='2', reason='This method is deprecated, must use v3.')
    @staticmethod
    def list_all_v2(auth_user, uid, page):
        '''This method is deprecated, must use v3'''
        user = UserService.get_user(uid)

        posts = Post.objects.filter(user=user).order_by('-posted_on')

        pagination = Paginator(posts, 100)
        paginated_posts = pagination.get_page(int(page))
        
        post_list = []
        for post in paginated_posts.object_list:
            if privacy_services.BlockedUserService.is_blocked(user=post.user, blocked_user=auth_user):
                continue
            
            if post.is_private and auth_user.uid != user.uid:
                continue

            if post.is_only_friends and auth_user.uid != user.uid:
                if not friend_services.FriendService.is_friend_exists(user=auth_user, friend=user):
                    continue

            post_json = PostService.form_post_content_json_v2(post=post, auth_user=auth_user)
            post_list.append(post_json)
        
        return post_list

    @staticmethod
    def list_all_v3(auth_user, uid, page):
        user = UserService.get_user(uid)

        posts = Post.objects.filter(user=user).order_by('-posted_on')

        pagination = Paginator(posts, 100)
        paginated_posts = pagination.get_page(int(page))
        
        post_list = []
        for post in paginated_posts.object_list:
            if privacy_services.BlockedUserService.is_blocked(user=post.user, blocked_user=auth_user):
                continue
            
            if post.is_private and auth_user.uid != user.uid:
                continue

            if post.is_only_friends and auth_user.uid != user.uid:
                if not friend_services.FriendService.is_friend_exists(user=auth_user, friend=user):
                    continue

            post_json = PostService.to_json_v3(post=post, auth_user=auth_user)
            post_list.append(post_json)
        
        return post_list, paginated_posts.has_next()
    

# Comment Paginator
class CommentService:
    '''Comment service for commenting on post.'''
    @staticmethod
    def is_comment_exists(id, post):
        return PostComment.objects.filter(id=id, post=post).exists()

    @staticmethod
    def get_comment_on_post(id, post):
        return PostComment.objects.get(id=id, post=post)
    
    @staticmethod
    def get_comment_by_id(id):
        return PostComment.objects.get(id=id)
    
    @staticmethod
    def add_comment(auth_user, post_id, data):
        post = PostService.get_post(post_id)

        comment = PostComment.objects.create(
            post=post,
            by=auth_user,
            text=data.get('text')
        )

        # upgrading comment counts
        post.comments_count += 1
        post.save()

        if post.user.uid != auth_user.uid:
            # sending user a notification
            notifier_services.NotificationChannelService.push_notification(
                from_user=auth_user,
                to_user=post.user,
                refer=post.id,
                subject='Comment',
                body='comment on your post.',
                type='POST_COMMENT'
            )

        # calculating ago time
        time_ago = time.caltime_string(comment.commented_on)

        return {
            'message': 'Commented Successfully.',
            'comment': {
                'id': comment.id,
                'post_id': comment.post.id,
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
    def delete_comment(auth_user, post_id, comment_id):
        post = PostService.get_post(post_id)
        comment = CommentService.get_comment_on_post(comment_id, post)

        if comment.by.uid == auth_user.uid or post.user.uid == auth_user.uid:
            comment.delete()

            # downgrading comment counts
            post.comments_count -= 1
            post.save()
        else:
            raise CommentError('No permission for deleting comment')

    @staticmethod
    def list_all(user, post_id):
        post = Post.objects.get(id=post_id)
        comments = PostComment.objects.filter(post=post)

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
                'post_id': comment.post.id,
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
                like = PostCommentLike.objects.get(comment=comment, by=user)
                comment_json['liked'] = like.type
            except:
                pass

            comments_list.append(comment_json)

        return comments_list


# Like Paginator
class LikeService:
    '''Like Service for like and dislike the post'''
    @staticmethod
    def get_like_on_post(post, by):
        return PostLike.objects.get(post=post, by=by)

    @staticmethod
    def like_post(auth_user, post_id, data):
        post = PostService.get_post(post_id)

        try:
            like = PostLike.objects.get(post=post, by=auth_user)
            like.type = data.get('type')
            like.save()
        except:
            like = PostLike.objects.create(
                post=post, 
                by=auth_user, 
                type=data.get('type'),
            )
        
            # upgrading like counts
            post.likes_count += 1
            post.save()
        
        if post.user.uid != auth_user.uid:
            # sending user a notification
            notifier_services.NotificationChannelService.push_notification(
                from_user=auth_user,
                to_user=post.user,
                refer=post.id,
                subject='Like',
                body='liked your post.',
                type='POST_LIKE'
            )

        return like
    
    @staticmethod
    def dislike_post(auth_user, post_id):
        post = PostService.get_post(post_id)
        like = LikeService.get_like_on_post(post, auth_user)

        if like.by.uid != auth_user.uid:
            raise LikeError('No permission for dislike this post')
        
        like.delete()

        post.likes_count -= 1
        post.save()

    @staticmethod
    def list_all(post_id):
        post = Post.objects.get(id=post_id)
        likes = PostLike.objects.filter(post=post)

        likes_list = []
        for like in likes:
            likes_list.append({
                'id': like.id,
                'post_id': like.post.id,
                'by': like.by.uid,
                'type': like.type
            })

        return likes_list


# Like Paginator
class CommentLikeService:
    '''Comment like service for like and dislike comments on post.'''

    @staticmethod
    def get_comment_like_on_comment(comment, by):
        return PostCommentLike.objects.get(comment=comment, by=by)

    @staticmethod
    def like_comment(auth_user, comment_id, data):
        comment = CommentService.get_comment_by_id(comment_id)

        try:
            like = PostCommentLike.objects.get(comment=comment, by=auth_user)
            like.type = data.get('type')
            like.save()
        except:
            like = PostCommentLike.objects.create(
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
                refer=comment.post.id,
                subject='Like',
                body='liked your comment.',
                type='POST_COMMENT_LIKE',
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
        comment = PostComment.objects.get(id=comment_id)
        likes = PostCommentLike.objects.filter(comment=comment)

        likes_list = []
        for like in likes:
            likes_list.append({
                'id': like.id,
                'comment_id': like.comment.id,
                'by': like.by.uid,
                'type': like.type
            })

        return likes_list

                
