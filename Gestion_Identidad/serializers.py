from rest_framework import serializers

class SearchSerializer(serializers.Serializer):
    text = serializers.CharField()
    dropdown1 = serializers.CharField()
    dropdown2 = serializers.CharField()
    selectedOption1 = serializers.CharField()
    selectedOption2 = serializers.CharField()