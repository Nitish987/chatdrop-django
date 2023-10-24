from rest_framework import serializers
from .models import Reel, ReelComment, ReelLike, ReelCommentLike, Audio
from utils import validators


# Reel
class ReelSerializer(serializers.ModelSerializer):
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    video = serializers.FileField()
    audio_id = serializers.IntegerField(default=0)
    aspect_ratio = serializers.FloatField()
    thumbnail = serializers.ImageField()

    class Meta:
        model = Reel
        fields = ['audio_id', 'text', 'hashtags', 'video', 'visibility', 'aspect_ratio', 'thumbnail']

    def validate(self, attrs):
        text = attrs.get('text')
        video = attrs.get('video')
        audio_id = attrs.get('audio_id')
        visibility = attrs.get('visibility')
        aspect_ratio = attrs.get('aspect_ratio')
        thumbnail = attrs.get('thumbnail')

        # validation
        if text is None:
            raise serializers.ValidationError({'text', 'no description provided'})
        
        if audio_id is None or type(audio_id) is not int:
            raise serializers.ValidationError({'audio_id', 'Invalid audio selected.'})
        
        if video is None:
            raise serializers.ValidationError({'video', 'No Video Selected.'})
        
        if visibility is None:
            raise serializers.ValidationError({'visibility', 'No visibility Selected.'})
        
        if aspect_ratio is None:
            raise serializers.ValidationError({'aspect_ratio', 'No aspect ratio Selected.'})
        
        if thumbnail is None:
            raise serializers.ValidationError({'thumbnail', 'No thumbnail specified.'})

        return attrs



# Add Comment
class AddCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReelComment
        fields = ['text']

    def validate(self, attrs):
        text = attrs.get('text')

        # validation
        if validators.is_empty(text) or not validators.atmost_length(text, 10000):
            raise serializers.ValidationError({'text': 'Invalid Comment.'})
        
        return attrs


# Add Like
class AddLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReelLike
        fields = ['type']

    def validate(self, attrs):
        type = attrs.get('type')

        # validation
        if validators.is_empty(type) or type not in ['LIKE', 'LOVE', 'HAHA', 'YAY', 'WOW', 'SAD', 'ANGRY']:
            raise serializers.ValidationError({'type': 'Invalid Like.'})
        
        return attrs


# Add Comment Like
class AddCommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReelCommentLike
        fields = ['type']

    def validate(self, attrs):
        type = attrs.get('type')

        # validation
        if validators.is_empty(type) or type not in ['LIKE', 'LOVE', 'HAHA', 'YAY', 'WOW', 'SAD', 'ANGRY']:
            raise serializers.ValidationError({'type': 'Invalid Like.'})
        
        return attrs




# Audio
class AudioSerailzer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = ['name', 'audio', 'duration']
    
    def validate(self, attrs):
        name = attrs.get('name')
        audio = attrs.get('audio')
        duration = attrs.get('duration')

        # validate
        if name is None or validators.is_empty(name):
            raise serializers.ValidationError({'name': 'Audio name not specified.'})

        if audio is None:
            raise serializers.ValidationError({'audio': 'No audio selected.'})
        
        if duration is None:
            raise serializers.ValidationError({'duration': 'Audio duration not specified.'})
        
        return attrs