from rest_framework import serializers
from .models import Story


# Add Story - Text
class TextStorySerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=1000, allow_blank=True)
    photo = serializers.ImageField()

    class Meta:
        model = Story
        fields = ['text', 'photo']

    def validate(self, attrs):
        text = attrs.get('text')
        photo = attrs.get('photo')

        # validation
        if text is None:
            raise serializers.ValidationError({'text': 'Invalid content.'})
        
        if photo is None:
            raise serializers.ValidationError({'photo', 'No Photo Selected.'})

        return attrs



class TextStorySerializerV2(serializers.ModelSerializer):
    photo = serializers.ImageField()

    class Meta:
        model = Story
        fields = ['photo']

    def validate(self, attrs):
        photo = attrs.get('photo')

        # validation
        if photo is None:
            raise serializers.ValidationError({'photo', 'No Photo Selected.'})

        return attrs
    



# Add Story - Photo
class PhotoStorySerializer(serializers.ModelSerializer):
    '''This serializer is deprecated, must use v2.'''
    photo = serializers.ImageField()

    class Meta:
        model = Story
        fields = ['photo']

    def validate(self, attrs):
        photo = attrs.get('photo')

        # validation
        if photo is None:
            raise serializers.ValidationError({'photo', 'No Photo Selected.'})

        return attrs


class PhotoStorySerializerV2(serializers.ModelSerializer):
    text = serializers.CharField(max_length=1000, allow_blank=True)
    photo = serializers.ImageField()

    class Meta:
        model = Story
        fields = ['text', 'photo']

    def validate(self, attrs):
        text = attrs.get('text')
        photo = attrs.get('photo')

        # validation
        if text is None:
            raise serializers.ValidationError({'text': 'Invalid content.'})
        
        if photo is None:
            raise serializers.ValidationError({'photo', 'No Photo Selected.'})

        return attrs
    



# Add Story - Video
class VideoStorySerializer(serializers.ModelSerializer):
    '''This serializer is deprecated, must use v2.'''
    video = serializers.FileField()

    class Meta:
        model = Story
        fields = ['video']

    def validate(self, attrs):
        video = attrs.get('video')

        # validation
        if video is None:
            raise serializers.ValidationError({'video', 'No Video Selected.'})

        return attrs
        

class VideoStorySerializerV2(serializers.ModelSerializer):
    text = serializers.CharField(max_length=1000, allow_blank=True)
    video = serializers.FileField()

    class Meta:
        model = Story
        fields = ['text', 'video']

    def validate(self, attrs):
        text = attrs.get('text')
        video = attrs.get('video')

        # validation
        if text is None:
            raise serializers.ValidationError({'text': 'Invalid content.'})
        
        if video is None:
            raise serializers.ValidationError({'video', 'No Video Selected.'})

        return attrs