from rest_framework.serializers import ModelSerializer
from .models import Note, Task, TaskComment

class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TaskCommentSerializer(ModelSerializer):
    class Meta:
        model = TaskComment
        fields = '__all__'