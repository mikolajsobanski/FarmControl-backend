from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Note, Task, TaskComment, Species, Animal, CostsCategory, Vaccination, Health, Costs
from django.db.models import Sum

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

class SpeciesSerializer(ModelSerializer):
    class Meta:
        model = Species
        fields = '__all__'
        
class AnimalSerializer(ModelSerializer):
    class Meta:
        model = Animal
        fields = '__all__'

class AnimalCostsSerializer(ModelSerializer):
    total_costs = SerializerMethodField()

    class Meta:
        model = Animal
        fields = ['name', 'total_costs']

    def get_total_costs(self, obj):
        return obj.animal_costs.aggregate(total=Sum('amount'))['total']

class CostsCategorySerializer(ModelSerializer):
    class Meta:
        model = CostsCategory
        fields = '__all__'

class VaccinationSerializer(ModelSerializer):
    class Meta:
        model = Vaccination
        fields = '__all__'

class HealthSerializer(ModelSerializer):
    class Meta:
        model = Health
        fields = '__all__'

class CostsSerializer(ModelSerializer):
    class Meta:
        model = Costs
        fields = '__all__'