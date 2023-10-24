import reel.services as reel_services

from django.db.models import Q
from account.models import User
from reel.models import Audio
from django.core.paginator import Paginator
from privacy.services import BlockedUserService


# Search
class SearchService:
    @staticmethod
    def query_profiles(auth_user, q, page):
        q = q.strip()
        query_list = q.split(' ')

        profiles = User.objects.filter(
            Q(location__in=query_list) | 
            Q(interest__in=query_list) | 
            Q(first_name__in=query_list) | 
            Q(last_name__in=query_list) | 
            Q(username__in=query_list)
        )

        pagination = Paginator(profiles, 100)
        paginated_profiles = pagination.get_page(int(page))

        result = []
        for profile in paginated_profiles.object_list:

            if not profile.is_admin and not BlockedUserService.is_blocked(user=profile ,blocked_user=auth_user):
                
                result.append({
                    'uid': profile.uid,
                    'name': profile.full_name,
                    'username': profile.username,
                    'gender': profile.gender,
                    'photo': profile.photo_cdn_url,
                    'message': profile.message,
                })
        
        return result
    
    @staticmethod
    def query_audios(auth_user, q, page):
        q = q.strip()
        query_list = q.split(' ')

        audios = Audio.objects.filter(Q(name__in=query_list))

        pagination = Paginator(audios, 100)
        paginated_audios = pagination.get_page(int(page))

        result = []

        audio_service = reel_services.AudioService
        for audio in paginated_audios.object_list:
            result.append(audio_service.to_json(audio=audio))
        
        return result
            