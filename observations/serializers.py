from rest_framework import serializers
from .models import Observation

class ObservationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Observation
        fields = '__all__'
        read_only_fields = ('user', 'ai_suggestion', 'ai_confidence', 'created_at') 