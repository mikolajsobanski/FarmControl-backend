from rest_framework.serializers import ModelSerializer
from .models import Farmer

class FarmerSerializer(ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'is_owner', 'id_owner', 'photo']
        extra_kwargs = {
            'password' : {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance