from rest_framework import serializers

from user.models import User
from user.serializers import UserSerializer

from .models import Category, Product, Image, Color, Size


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_value']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name', 'description']


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'is_active',
            'created_at',
            'parent',
            'children',
        ]

    def get_children(self, obj):
        children = Category.objects.filter(parent=obj)
        return CategorySerializer(children, many=True).data


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    def get_category(self, obj):
        return obj.category.name

    def get_image(self, obj):
        first_image = obj.images.first()
        return f"http://127.0.0.1:8000{first_image.image.url}" if first_image else None

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'seller',
            'title',
            'description',
            'price',
            'image',
            'quantity',
            'views'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    images = ImageSerializer(many=True)
    colors = ColorSerializer(many=True)
    sizes = SizeSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'seller',
            'title',
            'description',
            'price',
            'images',
            'colors',
            'sizes',
            'quantity',
            'views'
        ]


class CreateProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    colors = ColorSerializer(many=True, required=False, write_only=True)
    sizes = SizeSerializer(many=True, required=False, write_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'seller',
            'category',
            'title',
            'description',
            'price',
            'uploaded_images',
            'colors',
            'sizes',
            'quantity',
            'images'
        ]
        extra_kwargs = {
            'seller': {'read_only': True},
        }

    def create_or_get_colors(self, color_data):
        colors = []
        for color_info in color_data:
            color_name = color_info['name'].lower()
            hex_value = color_info['hex_value'].lower()

            color, created = Color.objects.get_or_create(
                name=color_name,
                defaults={'hex_value': hex_value}
            )

            if not created and color.hex_value != hex_value:
                color.hex_value = hex_value
                color.save()

            colors.append(color)
        return colors

    def create_or_get_sizes(self, size_data):
        sizes = []
        for size_info in size_data:
            size_name = size_info['name'].lower()
            description = size_info.get('description', '').lower()

            size, created = Size.objects.get_or_create(
                name=size_name,
                defaults={'description': description}
            )

            if not created and size.description != description:
                size.description = description
                size.save()

            sizes.append(size)
        return sizes

    def create(self, validated_data):
        color_data = validated_data.pop('colors', [])
        size_data = validated_data.pop('sizes', [])
        uploaded_images = validated_data.pop('uploaded_images', [])

        product = Product.objects.create(**validated_data)

        colors = self.create_or_get_colors(color_data)
        sizes = self.create_or_get_sizes(size_data)
        product.colors.set(colors)
        product.sizes.set(sizes)

        for image in uploaded_images:
            Image.objects.create(product=product, image=image)

        return product

    def update(self, instance, validated_data):
        color_data = validated_data.pop('colors', None)
        size_data = validated_data.pop('sizes', None)
        uploaded_images = validated_data.pop('uploaded_images', [])

        instance = super().update(instance, validated_data)

        if color_data is not None:
            colors = self.create_or_get_colors(color_data)
            instance.colors.set(colors)

        if size_data is not None:
            sizes = self.create_or_get_sizes(size_data)
            instance.sizes.set(sizes)

        for image in uploaded_images:
            Image.objects.create(product=instance, image=image)

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data
        representation['colors'] = ColorSerializer(instance.colors.all(), many=True).data
        representation['sizes'] = SizeSerializer(instance.sizes.all(), many=True).data
        return representation
