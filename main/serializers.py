from rest_framework import serializers

from .models import Post, Category

class PostSerializer(serializers.ModelSerializer):
    '''
    Serializer for Post model
    id, name, description, short_description, image
    '''
    category_id = serializers.CharField(source='category.id')
    # category_name = serializers.ReadOnlyField(source='category')
    class Meta:
        model = Post
        fields = ["id", "name", "description", "short_description", "image", "category_id"]
    
class CategorySerializer(serializers.ModelSerializer):
    '''
    Category and posts in this category
    id, name, posts
    '''
    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "posts"]

    def delete(self, validated_data):
        Post.objects.filter(id=validated_data['pk']).delete()