from operator import itemgetter
import textwrap
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apiauth.models import Farmer
from apicore.models import Task, Animal, Costs, Vaccination, Health
from django.db.models import Q
from apicore.serializers import AnimalCostsSerializer, AnimalSerializer, CostsSerializer, VaccinationSerializer, HealthSerializer
from django.db.models import Sum
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak
from reportlab.pdfgen import canvas
from django.http import FileResponse, HttpResponse
from io import BytesIO
from .reportsSupportFile import changeDateFormat, create_table, getAnimalName, remove_diacritics, getCostCategoryName, getSpeciesName, displayAnimalStatus


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
    
class PdfFullReportAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        owner = Farmer.objects.filter(id=pk).first()
        user_animals = Animal.objects.filter(owner=pk)
        employees = Farmer.objects.filter(id_owner=pk, id_owner__isnull=False)
        serializer = AnimalSerializer(user_animals, many=True)
        animal_ids = [animal['id'] for animal in serializer.data]
        costs = []
        queryset = Costs.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                queryset = Costs.objects.filter(animal=int(id))
                serializer = CostsSerializer(queryset, many=True)
                costs.extend(serializer.data)
        costs = sorted(costs, key=itemgetter('created_at'), reverse=True)
        # vaccination
        vaccinations = []
        querysetVaccinations = Vaccination.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                querysetVaccinations = Vaccination.objects.filter(animal=int(id))
                serializerVaccination = VaccinationSerializer(querysetVaccinations, many=True)
                vaccinations.extend(serializerVaccination.data)
        #health
        health = []
        querysetHealth = Health.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                querysetHealth = Health.objects.filter(animal=int(id))
                serializerHealth = HealthSerializer(querysetHealth, many=True)
                health.extend(serializerHealth.data)
        


    # Create a PDF document in memory using BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add content to the PDF
        elements.append(Paragraph("Pelen raport", getSampleStyleSheet()['Title']))

        # Add the costs data to the PDF as a table
        elements.append(Paragraph("Zwierzeta", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if user_animals:
            animal_data = [["Nazwa", "Gatunek", "Data urodzenia", "Status"]]
            for animal in user_animals:
                animal_data.append([remove_diacritics(animal.name), remove_diacritics(getSpeciesName(str(animal.species))), remove_diacritics(changeDateFormat(str(animal.dob))),displayAnimalStatus(animal.status)])
            animals_table = create_table(animal_data, [150, 150, 150, 150])
            elements.append(animals_table)
        else:
            elements.append(Paragraph("No animalss data available.", getSampleStyleSheet()['Normal']))
        
        elements.append(Paragraph("Pracownicy", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if employees:
            farmer_data = [["Imie", "Nazwisko", "Data dolaczenia"]]
            for farmer in employees:
                farmer_data.append([remove_diacritics(farmer.first_name), remove_diacritics(farmer.last_name), remove_diacritics(changeDateFormat(str(farmer.date_joined)))])
            farmers_table = create_table(farmer_data, [200, 200, 200])
            elements.append(farmers_table)
        else:
            elements.append(Paragraph("No farmers data available.", getSampleStyleSheet()['Normal']))


        #print costs
        # Add the costs data to the PDF as a table
        elements.append(Paragraph("Koszty", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if costs:
            cost_data = [["Zwierze", "Nazwa", "Data", "Kategoria", "Kwota"]]
            for cost in costs:
                cost_data.append([remove_diacritics(getAnimalName(cost["animal"])), remove_diacritics(cost["name"]), remove_diacritics(changeDateFormat(cost["created_at"])),remove_diacritics(getCostCategoryName(cost["category"])), cost["amount"]])
            costs_table = create_table(cost_data, [100, 100, 150, 150, 100])
            elements.append(costs_table)
        else:
            elements.append(Paragraph("No costs data available.", getSampleStyleSheet()['Normal']))
        
        #print vaccination
         # Add the vaccination data to the PDF as a table
        elements.append(Paragraph("Szczepionki", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if vaccinations:
            vaccination_data = [["Zwierze", "Szczepionka", "Podana", "Wazna do"]]
            for vaccination in vaccinations:
                vaccination_data.append([remove_diacritics(getAnimalName(vaccination["animal"])), remove_diacritics(vaccination["name"]), remove_diacritics(changeDateFormat(vaccination["created_at"])),remove_diacritics(changeDateFormat(vaccination["expiration_date"]))])
            vaccination_table = create_table(vaccination_data, [100, 100, 200, 200])
            elements.append(vaccination_table)
        else:
            elements.append(Paragraph("No vaccination data available.", getSampleStyleSheet()['Normal']))

        #print health
        elements.append(Paragraph("Historia zdrowia", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if health:
            health_data = [["Zwierze", "Choroba", "Data"]]
            for animalHealth in health:
                health_data.append([remove_diacritics(getAnimalName(animalHealth["animal"])), remove_diacritics(animalHealth["name"]),remove_diacritics(changeDateFormat(animalHealth["created_at"]))])


            health_table = create_table(health_data, [200, 200, 200])
            elements.append(health_table)
        else:
            elements.append(Paragraph("No health data available.", getSampleStyleSheet()['Normal']))

        doc.build(elements)

        buffer.seek(0)  # Reset buffer position

        # Create a new HttpResponse with the PDF content
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_animals_report.pdf"'

        buffer.close()  # Close the buffer to release resources

        return response
    
class PdfFullCostsReportAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        user_animals = Animal.objects.filter(owner=pk)
        serializer = AnimalSerializer(user_animals, many=True)
        animal_ids = [animal['id'] for animal in serializer.data]
        costs = []
        queryset = Costs.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                queryset = Costs.objects.filter(animal=int(id))
                serializer = CostsSerializer(queryset, many=True)
                costs.extend(serializer.data)
        costs = sorted(costs, key=itemgetter('created_at'), reverse=True)

         # Create a PDF document in memory using BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add content to the PDF
        elements.append(Paragraph("Pelen raport kosztow ", getSampleStyleSheet()['Title']))

        # Add the costs data to the PDF as a table
        elements.append(Paragraph("Koszty", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if costs:
            cost_data = [["Zwierze", "Nazwa", "Data", "Kategoria", "Kwota"]]
            for cost in costs:
                cost_data.append([remove_diacritics(getAnimalName(cost["animal"])), remove_diacritics(cost["name"]), remove_diacritics(changeDateFormat(cost["created_at"])),remove_diacritics(getCostCategoryName(cost["category"])), cost["amount"]])
            costs_table = create_table(cost_data, [100, 100, 150, 150, 100])
            elements.append(costs_table)
        else:
            elements.append(Paragraph("No costs data available.", getSampleStyleSheet()['Normal']))

        doc.build(elements)

        buffer.seek(0)  # Reset buffer position

        # Create a new HttpResponse with the PDF content
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_animals_report.pdf"'

        buffer.close()  # Close the buffer to release resources

        return response
    
class PdfFullHealthReportAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        user_animals = Animal.objects.filter(owner=pk)
        serializer = AnimalSerializer(user_animals, many=True)
        animal_ids = [animal['id'] for animal in serializer.data]
        # vaccination
        vaccinations = []
        querysetVaccinations = Vaccination.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                querysetVaccinations = Vaccination.objects.filter(animal=int(id))
                serializerVaccination = VaccinationSerializer(querysetVaccinations, many=True)
                vaccinations.extend(serializerVaccination.data)
        #health
        health = []
        querysetHealth = Health.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                querysetHealth = Health.objects.filter(animal=int(id))
                serializerHealth = HealthSerializer(querysetHealth, many=True)
                health.extend(serializerHealth.data)

    
        # Create a PDF document in memory using BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add content to the PDF
        elements.append(Paragraph("Pelen raport zdrowia", getSampleStyleSheet()['Title']))

        # Add the vaccination data to the PDF as a table
        elements.append(Paragraph("Szczepionki", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if vaccinations:
            vaccination_data = [["Zwierze", "Szczepionka", "Podana", "Wazna do"]]
            for vaccination in vaccinations:
                vaccination_data.append([remove_diacritics(getAnimalName(vaccination["animal"])), remove_diacritics(vaccination["name"]), remove_diacritics(changeDateFormat(vaccination["created_at"])),remove_diacritics(changeDateFormat(vaccination["expiration_date"]))])
            vaccination_table = create_table(vaccination_data, [100, 100, 200, 200])
            elements.append(vaccination_table)
        else:
            elements.append(Paragraph("No vaccination data available.", getSampleStyleSheet()['Normal']))

        #elements.append(PageBreak())

        # Add the health data to the PDF as a table
        elements.append(Paragraph("Historia zdrowia", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if health:
            health_data = [["Zwierze", "Choroba", "Data"]]
            for animalHealth in health:
                health_data.append([remove_diacritics(getAnimalName(animalHealth["animal"])), remove_diacritics(animalHealth["name"]),remove_diacritics(changeDateFormat(animalHealth["created_at"]))])


            health_table = create_table(health_data, [200, 200, 200])
            elements.append(health_table)
        else:
            elements.append(Paragraph("No health data available.", getSampleStyleSheet()['Normal']))

        doc.build(elements)
        buffer.seek(0)  # Reset buffer position

        # Create a new HttpResponse with the PDF content
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_animals_report.pdf"'

        buffer.close()  # Close the buffer to release resources

        return response
    
class PdfMonthlyReportAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
         #time manipulation
        today = datetime.now()
        end_date = today 
        start_date = end_date - timedelta(days=30)
        owner = Farmer.objects.filter(id=pk).first()
        user_animals = Animal.objects.filter(owner=pk)
        employees = Farmer.objects.filter(id_owner=pk, id_owner__isnull=False,
            date_joined__gte=start_date,
            date_joined__lt=end_date + timedelta(days=1) )
        serializer = AnimalSerializer(user_animals, many=True)
       
        #
        animal_ids = [animal['id'] for animal in serializer.data]
        costs = []
        queryset = Costs.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                queryset = Costs.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date + timedelta(days=1),
                    animal=int(id))
                serializer = CostsSerializer(queryset, many=True)
                costs.extend(serializer.data)
        costs = sorted(costs, key=itemgetter('created_at'), reverse=True)

        # vaccination
        vaccinations = []
        querysetVaccinations = Vaccination.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                querysetVaccinations = Vaccination.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date + timedelta(days=1),
                    animal=int(id))
                serializerVaccination = VaccinationSerializer(querysetVaccinations, many=True)
                vaccinations.extend(serializerVaccination.data)
        #health
        health = []
        querysetHealth = Health.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                querysetHealth = Health.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date + timedelta(days=1),
                    animal=int(id))
                serializerHealth = HealthSerializer(querysetHealth, many=True)
                health.extend(serializerHealth.data)

        # Create a PDF document in memory using BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add content to the PDF
        elements.append(Paragraph("Pelen raport z ostatnich 30 dni", getSampleStyleSheet()['Title']))
        elements.append(Paragraph(f"Od: {remove_diacritics(changeDateFormat(str(start_date)))} Do: {remove_diacritics(changeDateFormat(str(end_date)))}", getSampleStyleSheet()['Normal']))

        elements.append(Paragraph("Nowi pracownicy", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if employees:
            farmer_data = [["Imie", "Nazwisko", "Data dolaczenia"]]
            for farmer in employees:
                farmer_data.append([remove_diacritics(farmer["first_name"]), remove_diacritics(farmer["last_name"]), remove_diacritics(changeDateFormat(farmer["date_joined"]))])
            farmers_table = create_table(farmer_data, [200, 200, 200])
            elements.append(farmers_table)
        else:
            elements.append(Paragraph("No farmers data available.", getSampleStyleSheet()['Normal']))


        #print costs
        # Add the costs data to the PDF as a table
        elements.append(Paragraph("Koszty", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if costs:
            cost_data = [["Zwierze", "Nazwa", "Data", "Kategoria", "Kwota"]]
            for cost in costs:
                cost_data.append([remove_diacritics(getAnimalName(cost["animal"])), remove_diacritics(cost["name"]), remove_diacritics(changeDateFormat(cost["created_at"])),remove_diacritics(getCostCategoryName(cost["category"])), cost["amount"]])
            costs_table = create_table(cost_data, [100, 100, 150, 150, 100])
            elements.append(costs_table)
        else:
            elements.append(Paragraph("No costs data available.", getSampleStyleSheet()['Normal']))
        
        #print vaccination
         # Add the vaccination data to the PDF as a table
        elements.append(Paragraph("Szczepionki", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if vaccinations:
            vaccination_data = [["Zwierze", "Szczepionka", "Podana", "Wazna do"]]
            for vaccination in vaccinations:
                vaccination_data.append([remove_diacritics(getAnimalName(vaccination["animal"])), remove_diacritics(vaccination["name"]), remove_diacritics(changeDateFormat(vaccination["created_at"])),remove_diacritics(changeDateFormat(vaccination["expiration_date"]))])
            vaccination_table = create_table(vaccination_data, [100, 100, 200, 200])
            elements.append(vaccination_table)
        else:
            elements.append(Paragraph("No vaccination data available.", getSampleStyleSheet()['Normal']))

        #print health
        elements.append(Paragraph("Historia zdrowia", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if health:
            health_data = [["Zwierze", "Choroba", "Data"]]
            for animalHealth in health:
                health_data.append([remove_diacritics(getAnimalName(animalHealth["animal"])), remove_diacritics(animalHealth["name"]),remove_diacritics(changeDateFormat(animalHealth["created_at"]))])


            health_table = create_table(health_data, [200, 200, 200])
            elements.append(health_table)
        else:
            elements.append(Paragraph("No health data available.", getSampleStyleSheet()['Normal']))

        doc.build(elements)

        buffer.seek(0)  # Reset buffer position

        # Create a new HttpResponse with the PDF content
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_animals_report.pdf"'

        buffer.close()  # Close the buffer to release resources

        return response
    
class PdfMonthlyCostsReportAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        user_animals = Animal.objects.filter(owner=pk)
        serializer = AnimalSerializer(user_animals, many=True)
        #time manipulation
        today = datetime.now()
        end_date = today 
        start_date = end_date - timedelta(days=30)
        #
        animal_ids = [animal['id'] for animal in serializer.data]
        costs = []
        queryset = Costs.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                queryset = Costs.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date + timedelta(days=1),
                    animal=int(id))
                serializer = CostsSerializer(queryset, many=True)
                costs.extend(serializer.data)
        costs = sorted(costs, key=itemgetter('created_at'), reverse=True)
         # Create a PDF document in memory using BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add content to the PDF
        elements.append(Paragraph("Raport kosztow z ostatnich 30 dni", getSampleStyleSheet()['Title']))
        elements.append(Paragraph(f"Od: {remove_diacritics(changeDateFormat(str(start_date)))} Do: {remove_diacritics(changeDateFormat(str(end_date)))}", getSampleStyleSheet()['Normal']))

        # Add the costs data to the PDF as a table
        elements.append(Paragraph("Koszty", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if costs:
            cost_data = [["Zwierze", "Nazwa", "Data", "Kategoria", "Kwota"]]
            for cost in costs:
                cost_data.append([remove_diacritics(getAnimalName(cost["animal"])), remove_diacritics(cost["name"]), remove_diacritics(changeDateFormat(cost["created_at"])),remove_diacritics(getCostCategoryName(cost["category"])), cost["amount"]])
            costs_table = create_table(cost_data, [100, 100, 150, 150, 100])
            elements.append(costs_table)
        else:
            elements.append(Paragraph("No costs data available.", getSampleStyleSheet()['Normal']))

        doc.build(elements)

        buffer.seek(0)  # Reset buffer position

        # Create a new HttpResponse with the PDF content
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_animals_report.pdf"'

        buffer.close()  # Close the buffer to release resources

        return response

class PdfMonthlyHealthReportAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        #time manipulation
        today = datetime.now()
        end_date = today 
        start_date = end_date - timedelta(days=30)
        user_animals = Animal.objects.filter(owner=pk)
        serializer = AnimalSerializer(user_animals, many=True)
        animal_ids = [animal['id'] for animal in serializer.data]

        # vaccination
        vaccinations = []
        querysetVaccinations = Vaccination.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                querysetVaccinations = Vaccination.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date + timedelta(days=1),
                    animal=int(id))
                serializerVaccination = VaccinationSerializer(querysetVaccinations, many=True)
                vaccinations.extend(serializerVaccination.data)
        #health
        health = []
        querysetHealth = Health.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                querysetHealth = Health.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date + timedelta(days=1),
                    animal=int(id))
                serializerHealth = HealthSerializer(querysetHealth, many=True)
                health.extend(serializerHealth.data)

       # Create a PDF document in memory using BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add content to the PDF
        elements.append(Paragraph("Raport zdrowia z ostatnich 30 dni", getSampleStyleSheet()['Title']))
        elements.append(Paragraph(f"Od: {remove_diacritics(changeDateFormat(str(start_date)))} Do: {remove_diacritics(changeDateFormat(str(end_date)))}", getSampleStyleSheet()['Normal']))

        # Add the vaccination data to the PDF as a table
        elements.append(Paragraph("Szczepionki", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if vaccinations:
            vaccination_data = [["Zwierze", "Szczepionka", "Podana", "Wazna do"]]
            for vaccination in vaccinations:
                vaccination_data.append([remove_diacritics(getAnimalName(vaccination["animal"])), remove_diacritics(vaccination["name"]), remove_diacritics(changeDateFormat(vaccination["created_at"])),remove_diacritics(changeDateFormat(vaccination["expiration_date"]))])
            vaccination_table = create_table(vaccination_data, [100, 100, 200, 200])
            elements.append(vaccination_table)
        else:
            elements.append(Paragraph("No vaccination data available.", getSampleStyleSheet()['Normal']))

        #elements.append(PageBreak())

        # Add the health data to the PDF as a table
        elements.append(Paragraph("Historia zdrowia", getSampleStyleSheet()['Heading2']))
        elements.append(Spacer(1, 12))
        if health:
            health_data = [["Zwierze", "Choroba", "Data"]]
            for animalHealth in health:
                health_data.append([remove_diacritics(getAnimalName(animalHealth["animal"])), remove_diacritics(animalHealth["name"]),remove_diacritics(changeDateFormat(animalHealth["created_at"]))])


            health_table = create_table(health_data, [200, 200, 200])
            elements.append(health_table)
        else:
            elements.append(Paragraph("No health data available.", getSampleStyleSheet()['Normal']))

        doc.build(elements)

        buffer.seek(0)  # Reset buffer position

        # Create a new HttpResponse with the PDF content
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_animals_report.pdf"'

        buffer.close()  # Close the buffer to release resources
        return response
    

