from rest_framework import serializers
from .models import LinkPreviewContent
from utils import validators


# Link Preview serializer
class LinkPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkPreviewContent
        fields = ['url']
    
    def validate(self, attrs):
        url = attrs.get('url')

        if not validators.is_url(url):
            raise serializers.ValidationError({'url': 'Invalid Url.'})

        return attrs