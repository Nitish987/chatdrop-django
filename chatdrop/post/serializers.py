from rest_framework import serializers
from .models import Post, PostComment, PostLike, PostCommentLike
from utils import validators


# Add Post - Text
class TextPostSerializer(serializers.ModelSerializer):
    '''This serializer is deprecated, must use V2.'''
    hashtags = serializers.CharField(max_length=100, allow_blank=True)

    class Meta:
        model = Post
        fields = ['hashtags', 'text']

    def validate(self, attrs):
        text = attrs.get('text')

        # validation
        if validators.is_empty(text) or not validators.atmost_length(text, 10000):
            raise serializers.ValidationError({'text': 'Invalid content.'})

        return attrs
    
class TextPostSerializerV2(serializers.ModelSerializer):
    hashtags = serializers.CharField(max_length=100, allow_blank=True)

    class Meta:
        model = Post
        fields = ['hashtags', 'text', 'visibility']

    def validate(self, attrs):
        text = attrs.get('text')
        visibility = attrs.get('visibility')

        # validation
        if validators.is_empty(text) or not validators.atmost_length(text, 10000):
            raise serializers.ValidationError({'text': 'Invalid content.'})
        
        if visibility is None:
            raise serializers.ValidationError({'photos', 'No visibility Selected.'})

        return attrs
    

# Add Post - Photo
class PhotoPostSerializer(serializers.ModelSerializer):
    '''This serializer is deprecated, must use V2.'''
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = Post
        fields = ['hashtags', 'photos']

    def validate(self, attrs):
        photos = attrs.get('photos')

        # validation
        if photos is None:
            raise serializers.ValidationError({'photos', 'No Photo Selected.'})

        return attrs

class PhotoPostSerializerV2(serializers.ModelSerializer):
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)
    aspect_ratios = serializers.ListField(child=serializers.FloatField(), write_only=True)

    class Meta:
        model = Post
        fields = ['hashtags', 'photos', 'visibility', 'aspect_ratios']

    def validate(self, attrs):
        photos = attrs.get('photos')
        visibility = attrs.get('visibility')
        aspect_ratios = attrs.get('aspect_ratios')

        # validation
        if photos is None:
            raise serializers.ValidationError({'photos', 'No Photo Selected.'})
        
        if visibility is None:
            raise serializers.ValidationError({'photos', 'No visibility Selected.'})
        
        if aspect_ratios is None:
            raise serializers.ValidationError({'photos', 'No aspect ratio Selected.'})

        return attrs
    


# Add Post - Video
class VideoPostSerializer(serializers.ModelSerializer):
    '''This serializer is deprecated, must use V2.'''
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    video = serializers.FileField()

    class Meta:
        model = Post
        fields = ['hashtags', 'video']

    def validate(self, attrs):
        video = attrs.get('video')

        # validation
        if video is None:
            raise serializers.ValidationError({'video', 'No Video Selected.'})

        return attrs

class VideoPostSerializerV2(serializers.ModelSerializer):
    '''This Serializer is deprecated, must use v3'''
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    video = serializers.FileField()
    aspect_ratio = serializers.FloatField()

    class Meta:
        model = Post
        fields = ['hashtags', 'video', 'visibility', 'aspect_ratio']

    def validate(self, attrs):
        video = attrs.get('video')
        visibility = attrs.get('visibility')
        aspect_ratio = attrs.get('aspect_ratio')

        # validation
        if video is None:
            raise serializers.ValidationError({'video', 'No Video Selected.'})
        
        if visibility is None:
            raise serializers.ValidationError({'photos', 'No visibility Selected.'})
        
        if aspect_ratio is None:
            raise serializers.ValidationError({'photos', 'No aspect ratio Selected.'})

        return attrs

class VideoPostSerializerV3(serializers.ModelSerializer):
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    video = serializers.FileField()
    aspect_ratio = serializers.FloatField()
    thumbnail = serializers.ImageField()

    class Meta:
        model = Post
        fields = ['hashtags', 'video', 'visibility', 'aspect_ratio', 'thumbnail']

    def validate(self, attrs):
        video = attrs.get('video')
        visibility = attrs.get('visibility')
        aspect_ratio = attrs.get('aspect_ratio')
        thumbnail = attrs.get('thumbnail')

        # validation
        if video is None:
            raise serializers.ValidationError({'video', 'No Video Selected.'})
        
        if thumbnail is None:
            raise serializers.ValidationError({'thumbnail', 'No thumbnail Selected.'})
        
        if visibility is None:
            raise serializers.ValidationError({'photos', 'No visibility Selected.'})
        
        if aspect_ratio is None:
            raise serializers.ValidationError({'photos', 'No aspect ratio Selected.'})

        return attrs



# Add Post - Text Photo
class TextPhotoPostSerializer(serializers.ModelSerializer):
    '''This serializer is deprecated, must use V2.'''
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = Post
        fields = ['hashtags', 'text', 'photos']

    def validate(self, attrs):
        text = attrs.get('text')
        photos = attrs.get('photos')

        # validation
        if validators.is_empty(text) or not validators.atmost_length(text, 10000):
            raise serializers.ValidationError({'text': 'Invalid content.'})
        
        if photos is None:
            raise serializers.ValidationError({'photos', 'No Photo Selected.'})

        return attrs

class TextPhotoPostSerializerV2(serializers.ModelSerializer):
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)
    aspect_ratios = serializers.ListField(child=serializers.FloatField(), write_only=True)

    class Meta:
        model = Post
        fields = ['hashtags', 'text', 'photos', 'visibility', 'aspect_ratios']

    def validate(self, attrs):
        text = attrs.get('text')
        photos = attrs.get('photos')
        visibility = attrs.get('visibility')
        aspect_ratios = attrs.get('aspect_ratios')

        # validation
        if validators.is_empty(text) or not validators.atmost_length(text, 10000):
            raise serializers.ValidationError({'text': 'Invalid content.'})
        
        if photos is None:
            raise serializers.ValidationError({'photos', 'No Photo Selected.'})
        
        if visibility is None:
            raise serializers.ValidationError({'photos', 'No visibility Selected.'})
        
        if aspect_ratios is None:
            raise serializers.ValidationError({'photos', 'No aspect ratio Selected.'})

        return attrs


# Add Post - Text Video
class TextVideoPostSerializer(serializers.ModelSerializer):
    '''This serializer is deprecated, must use V2.'''
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    video = serializers.FileField()

    class Meta:
        model = Post
        fields = ['hashtags', 'text', 'video']

    def validate(self, attrs):
        text = attrs.get('text')
        video = attrs.get('video')

        # validation
        if validators.is_empty(text) or not validators.atmost_length(text, 10000):
            raise serializers.ValidationError({'text': 'Invalid content.'})
        
        if video is None:
            raise serializers.ValidationError({'video', 'No Video Selected.'})

        return attrs

class TextVideoPostSerializerV2(serializers.ModelSerializer):
    '''This serializer is deprecated, must use v3.'''
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    video = serializers.FileField()
    aspect_ratio = serializers.FloatField()

    class Meta:
        model = Post
        fields = ['hashtags', 'text', 'video', 'visibility', 'aspect_ratio']

    def validate(self, attrs):
        text = attrs.get('text')
        video = attrs.get('video')
        visibility = attrs.get('visibility')
        aspect_ratio = attrs.get('aspect_ratio')

        # validation
        if validators.is_empty(text) or not validators.atmost_length(text, 10000):
            raise serializers.ValidationError({'text': 'Invalid content.'})
        
        if video is None:
            raise serializers.ValidationError({'video', 'No Video Selected.'})
        
        if visibility is None:
            raise serializers.ValidationError({'photos', 'No visibility Selected.'})
        
        if aspect_ratio is None:
            raise serializers.ValidationError({'photos', 'No aspect ratio Selected.'})

        return attrs

class TextVideoPostSerializerV3(serializers.ModelSerializer):
    hashtags = serializers.CharField(max_length=100, allow_blank=True)
    video = serializers.FileField()
    aspect_ratio = serializers.FloatField()
    thumbnail = serializers.ImageField()

    class Meta:
        model = Post
        fields = ['hashtags', 'text', 'video', 'visibility', 'aspect_ratio', 'thumbnail']

    def validate(self, attrs):
        text = attrs.get('text')
        video = attrs.get('video')
        visibility = attrs.get('visibility')
        aspect_ratio = attrs.get('aspect_ratio')
        thumbnail = attrs.get('thumbnail')

        # validation
        if validators.is_empty(text) or not validators.atmost_length(text, 10000):
            raise serializers.ValidationError({'text': 'Invalid content.'})
        
        if video is None:
            raise serializers.ValidationError({'video', 'No Video Selected.'})
        
        if thumbnail is None:
            raise serializers.ValidationError({'thumbnail', 'No thumbnail Selected.'})
        
        if visibility is None:
            raise serializers.ValidationError({'photos', 'No visibility Selected.'})
        
        if aspect_ratio is None:
            raise serializers.ValidationError({'photos', 'No aspect ratio Selected.'})

        return attrs



# Add Comment
class AddCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
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
        model = PostLike
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
        model = PostCommentLike
        fields = ['type']

    def validate(self, attrs):
        type = attrs.get('type')

        # validation
        if validators.is_empty(type) or type not in ['LIKE', 'LOVE', 'HAHA', 'YAY', 'WOW', 'SAD', 'ANGRY']:
            raise serializers.ValidationError({'type': 'Invalid Like.'})
        
        return attrs

        