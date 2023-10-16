from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apiauth.models import Farmer
from apicore.models import Task, Animal, Costs
from django.db.models import Q
from apicore.serializers import AnimalCostsSerializer, AnimalSerializer, CostsSerializer
from django.db.models import Sum
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import FileResponse, HttpResponse
from io import BytesIO


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
    

class HealthRatioAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        condition1 = Q(owner=pk)
        condition2 = Q(status=False)
        condition3 = Q(status=True)
        combined_conditions_animals_healthy = condition1 & condition3
        combined_conditions_animals_ill = condition1 & condition2
        animals_healthy = Animal.objects.filter(combined_conditions_animals_healthy).distinct()
        animals_ill = Animal.objects.filter(combined_conditions_animals_ill).distinct()
        counted_healthy = animals_healthy.count()
        counted_ill = animals_ill.count()
        return Response({
            'healthy': counted_healthy,
            'ill': counted_ill
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

class CategoryCostAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        ownerAnimals = Animal.objects.filter(owner=pk)
        serializer = AnimalSerializer(ownerAnimals, many=True)
        animal_ids = [animal['id'] for animal in serializer.data]
        category_summary = {}
        queryset = Costs.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                queryset = Costs.objects.filter(animal=int(id))
                category_summary_query = queryset.values('category__name').annotate(total_cost=Sum('amount'))
                for entry in category_summary_query:
                    category_name = entry['category__name']
                    total_cost = entry['total_cost']

                    if category_name in category_summary:
                        category_summary[category_name] += total_cost
                    else:
                        category_summary[category_name] = total_cost

        else:
            worker = Farmer.objects.get(id=pk)
            owner = worker.id_owner
            workerAnimals = Animal.objects.filter(owner=owner)
            serializerWorker = AnimalSerializer(workerAnimals, many=True)
            animalWorker_ids = [animal['id'] for animal in serializerWorker.data]
            if not len(animalWorker_ids) == 0:
                for id in animalWorker_ids:
                    queryset = Costs.objects.filter(animal=int(id))
                    category_summary_query = queryset.values('category__name').annotate(total_cost=Sum('amount'))
                    for entry in category_summary_query:
                        category_name = entry['category__name']
                        total_cost = entry['total_cost']

                        if category_name in category_summary:
                            category_summary[category_name] += total_cost
                        else:
                            category_summary[category_name] = total_cost

        result = [{'name': key, 'total_costs': value} for key, value in category_summary.items()]
        return(Response(result))

class CostFromLastSixMonthsAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')  


        owner_animals = Animal.objects.filter(owner=pk)

        data = []
        today = datetime.now()

        for i in range(6):
            end_date = today - timedelta(days=30 * i)
            start_date = end_date - timedelta(days=30)
            month_name = end_date.strftime("%B") 

            # Filter costs within the current month
            costs_in_month = Costs.objects.filter(
                created_at__gte=start_date,
                created_at__lt=end_date + timedelta(days=1), 
                animal__in=owner_animals
            ).aggregate(total_cost=Sum('amount'))['total_cost']

            if costs_in_month is None:
                costs_in_month = 0

            data.append({'name': month_name, 'sum': costs_in_month})
        data.reverse()
        return Response({
                'monthly_costs': data
        })
    
class PdfReportAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        owner = Farmer.objects.filter(id=pk).first()
        user_animals = Animal.objects.filter(owner=pk)
        employees = Farmer.objects.filter(id_owner=pk, id_owner__isnull=False)
        

    # Create a PDF document in memory using BytesIO
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Add content to the PDF
        c.drawString(100, 750, f"Zwierzeta uzytkownika {owner.first_name} {owner.last_name}")
        y = 720  # Initial y-coordinate for the list

        for animal in user_animals:
            c.drawString(100, y, f"Animal Name: {animal.name}")
            # Add other animal details as needed
            y -= 20  # Adjust the y-coordinate for the next entry
        
        y-= 50
        c.drawString(100,  y, 'Pracownicy')
        y -=20
        for farmer in employees:
            c.drawString(100, y, f"Imie pracownika: {farmer.first_name}")
            # Add other animal details as needed
            y -= 20  # Adjust the y-coordinate for the next entry


        c.showPage()
        c.save()

        buffer.seek(0)  # Reset buffer position

        # Create a new HttpResponse with the PDF content
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_animals_report.pdf"'

        buffer.close()  # Close the buffer to release resources

        return response