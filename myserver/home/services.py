from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = 'authentication.User'
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        