from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apiauth.models import Farmer
from apicore.models import Task, Animal
from django.db.models import Q
from apicore.serializers import AnimalCostsSerializer
from django.db.models import Sum


class WorkerCountAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        employees = Farmer.objects.filter(id_owner=pk, id_owner__isnull=False)
        counted_employees = employees.count()
        return Response(counted_employees)
    
class TaskRatioAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        condition1 = Q(owner=pk)
        condition2 = Q(worker=pk)
        condition3 = Q(status=False)
        condition4 = Q(status=True)
        combined_conditionsComplete = (condition1 | condition2) & condition4
        combined_conditionsInProgres = (condition1 | condition2) & condition3
        tasksInProgres = Task.objects.filter(combined_conditionsInProgres).distinct()
        tasksCompleted = Task.objects.filter(combined_conditionsComplete).distinct()
        countedInProgres = tasksInProgres.count()
        countedComplete = tasksCompleted.count()
        return Response({
            'inProgres': countedInProgres,
            'complete': countedComplete
        })

class AnimalCostSumAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        animals = Animal.objects.filter(owner=pk)
        serializer = AnimalCostsSerializer(animals, many=True)
        return Response(serializer.data)

class AnimalCostByCategoryAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        animal = Animal.objects.filter(id=pk).first()
        animal_costs_by_category = animal.animal_costs.values('category__name').annotate(value=Sum('amount'))
        return Response(animal_costs_by_category)