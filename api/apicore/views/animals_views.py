from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from ..serializers import SpeciesSerializer, AnimalSerializer, CostsCategorySerializer, VaccinationSerializer, HealthSerializer, CostsSerializer
from ..models import Species, Animal, CostsCategory, Vaccination, Health, Costs
from apiauth.models import Farmer
from operator import itemgetter

class SpeciesAPIView(APIView):
    def post(self, request):
        data = request.data
        species = Species.objects.create(
            name = data['name'],
            description = data['description'],
            avg_age = data['avg_age'],
            lifetime = data['lifetime'],
            nutrition = data['nutrition'],
            weight = data['avg_age'],
            avg_weight = data['avg_weight'],
            type = data['type'],
            photo = data['photo'],
        )
        serializer = SpeciesSerializer(species, many=False)
        
        print(serializer)
        return Response({
            'message': 'success',
            'data': serializer.data
        })
    def get(self, request):
        species = Species.objects.filter()
        serializer = SpeciesSerializer(species, many=True)
        return Response(serializer.data)
    
class SpeciesSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('query')
        results = Species.objects.annotate(
            similarity=TrigramSimilarity('name', query)
        ).filter(similarity__gt=0.1).order_by('-similarity')
        serializer = SpeciesSerializer(results, many=True)
        return Response(serializer.data)

class SpeciesShortDetailsApiView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        species = Species.objects.filter(id=pk).first()
        serializer = SpeciesSerializer(species, many=False)
        return Response(serializer.data)

    
class AnimalApiView(APIView):
    def post(self, request):
        data = request.data
        species = Species.objects.filter(id=data['species']).first()
        photo = request.FILES.get('photo')
        print(photo)
        animal = Animal.objects.create(
            name = data['name'],
            photo = photo,
            species = species,
            owner = data['owner'],
            dob = data['dob'],
            sex = data['sex']
        )
        serializer = AnimalSerializer(animal, many=False)
        return Response({
            'message': 'success',
            'animal': serializer.data
        })
    def get(self, request):
        pk = request.query_params.get('pk')
        animals = Animal.objects.filter(owner=pk)
        serializer = AnimalSerializer(animals, many=True)
        return Response(serializer.data)
    def delete(self, request):
        pk = request.query_params.get('pk')
        animal = Animal.objects.filter(id=pk).first()
        animal.delete()
        return Response({
            'message': 'success'
        })
    def put(self, request):
        pk_animal = request.data['pk_animal']
        animal = Animal.objects.filter(id=pk_animal).first()
        serializer = AnimalSerializer(animal, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'success'
        })

class CostCategoryAPIView(APIView):
    def get(self, request):
        categories = CostsCategory.objects.filter()
        serializer = CostsCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
class SingleCostCategoryAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        costCategory = CostsCategory.objects.filter(id=pk).first()
        return Response(costCategory.name)

class VaccinationAPIView(APIView):
    def post(self, request):
        pk_animal = request.data['pk_animal']
        animal = Animal.objects.filter(id=pk_animal).first()
        vaccination = Vaccination.objects.create(
           name = request.data['name'],
           animal = animal,
           date = request.data['date'],
           expiration_date = request.data['expiration_date']
        )
        serializer = VaccinationSerializer(vaccination, many=False)
        return Response({
            'message': 'success'
        })
    def get(self, request):
        pk_animal = request.query_params.get('pk_animal')
        animal = Animal.objects.filter(id=pk_animal).first()
        vaccination = Vaccination.objects.filter(animal=animal)
        serializer = VaccinationSerializer(vaccination, many=True)
        return Response(serializer.data)
    def put(self, request):
        pk_vaccination = request.data['pk_vaccination']
        vaccination = Vaccination.objects.filter(id=pk_vaccination).first()
        serializer = VaccinationSerializer(vaccination, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'success'
        })
    def delete(self, request):
        pk = request.query_params.get('pk')
        vaccination = Vaccination.objects.filter(id=pk).first()
        vaccination.delete()
        return Response({
            'message': 'success'
        })
    
class HelathAPIView(APIView):
    def post(self, request):
        pk_animal = request.data['pk_animal']
        animal = Animal.objects.filter(id=pk_animal).first()
        health = Health.objects.create(
            name = request.data['name'],
            description = request.data['description'],
            animal = animal
        )
        serializer = HealthSerializer(health, many=False)
        return Response({
            'message': 'success'
        })
    def get(self, request):
        pk_animal = request.query_params.get('pk_animal')
        animal = Animal.objects.filter(id=pk_animal).first()
        health = Health.objects.filter(animal=animal)
        serializer = HealthSerializer(health, many=True)
        return Response(serializer.data)
    def put(self, request):
        pk_health = request.data['pk_health']
        health = Health.objects.filter(id=pk_health).first()
        serializer = HealthSerializer(health, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'success'
        })
    def delete(self, request):
        pk = request.query_params.get('pk')
        health = Health.objects.filter(id=pk).first()
        health.delete()
        return Response({
            'message': 'success'
        })

class CostsAPIView(APIView):
    def post(self, request):
        pk_animal = request.data['pk_animal']
        animal = Animal.objects.filter(id=pk_animal).first()
        costCategory = request.data['category']
        category = CostsCategory.objects.filter(id=costCategory).first()
        cost = Costs.objects.create(
            name = request.data['name'],
            amount = request.data['amount'],
            category = category,
            animal = animal
        )
        serializer = CostsSerializer(cost, many=False)
        animal.animal_costs.add(cost)
        return Response({
            'message': 'success'
        })
    def get(self, request):
        pk_animal = request.query_params.get('pk_animal')
        animal = Animal.objects.filter(id=pk_animal).first()
        costs = Costs.objects.filter(animal=animal)
        serializer = CostsSerializer(costs, many=True)
        return Response(serializer.data)
    def put(self, request):
        pk_cost = request.data['pk_cost']
        cost = Costs.objects.filter(id=pk_cost).first()
        serializer = CostsSerializer(cost, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'success'
        })
    def delete(self, request):
        pk = request.query_params.get('pk')
        cost = Costs.objects.filter(id=pk).first()
        cost.delete()
        return Response({
            'message': 'success'
        })

class LatestCostsAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        ownerAnimals = Animal.objects.filter(owner=pk)
        serializer = AnimalSerializer(ownerAnimals, many=True)
        animal_ids = [animal['id'] for animal in serializer.data]
        costs = []
        queryset = Costs.objects.all()
        if not len(animal_ids) == 0:
            for id in animal_ids:
                queryset = Costs.objects.filter(animal=int(id))
                serializer = CostsSerializer(queryset, many=True)
                costs.extend(serializer.data)
        else:
            worker = Farmer.objects.get(id=pk)
            owner = worker.id_owner
            workerAnimals = Animal.objects.filter(owner=owner)
            serializerWorker = AnimalSerializer(workerAnimals, many=True)
            animalWorker_ids = [animal['id'] for animal in serializerWorker.data]
            if not len(animalWorker_ids) == 0:
                for id in animalWorker_ids:
                    queryset = Costs.objects.filter(animal=int(id))
                    serializer = CostsSerializer(queryset, many=True)
                    costs.extend(serializer.data)
            
        costs = sorted(costs, key=itemgetter('created_at'), reverse=True)
        return Response(costs)
            
        
