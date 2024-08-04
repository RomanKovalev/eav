from rest_framework import serializers
from .models import Row, Attribute, ChildAttribute, AttributeValue


class RowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Row
        fields = ['id', 'hash', 'table']


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name', 'row']


class ChildAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildAttribute
        fields = ['id', 'name', 'row']


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = serializers.PrimaryKeyRelatedField(queryset=Attribute.objects.all(), required=False)
    child_attribute = serializers.PrimaryKeyRelatedField(queryset=ChildAttribute.objects.all(), required=False)

    class Meta:
        model = AttributeValue
        fields = ['id', 'row', 'attribute', 'child_attribute', 'value']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Example of dynamic fields
        request = self.context.get('request')
        if request and request.query_params.get('include_attribute_name') == 'true':
            representation['attribute_name'] = instance.attribute.name if instance.attribute else None

        if request and request.query_params.get('include_child_attribute_name') == 'true':
            representation['child_attribute_name'] = instance.child_attribute.name if instance.child_attribute else None

        return representation
