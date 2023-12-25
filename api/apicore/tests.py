from django.urls import reverse
from django.test import TestCase
from datetime import datetime
from .models import Animal, Species, Health, Costs, Vaccination, Note, Task, TaskComment
from rest_framework.test import APIClient
from rest_framework import status
from .serializers import AnimalSerializer

class AnimalModelTest(TestCase):
    def setUp(self):
        self.species = Species.objects.create(name='Test Species', description='Test Description', lifetime='Test Lifetime',
                                             avg_age=5, nutrition='Test Nutrition', weight=10.5, avg_weight='Test Avg Weight', type='Test Type')

        self.animal_data = {
            'name': 'Test Animal',
            'photo': 'path/to/photo.jpg',
            'species': self.species,
            'owner': 1,
            'dob': datetime.now(),
            'sex': 'male',
            'status': True
        }

    def test_create_animal(self):
        animal = Animal.objects.create(**self.animal_data)
        self.assertEqual(animal.name, self.animal_data['name'])
        self.assertEqual(animal.photo, self.animal_data['photo'])
        self.assertEqual(animal.species, self.animal_data['species'])
        self.assertEqual(animal.owner, self.animal_data['owner'])
        self.assertEqual(animal.dob, self.animal_data['dob'])
        self.assertEqual(animal.sex, self.animal_data['sex'])
        self.assertEqual(animal.status, self.animal_data['status'])

    def test_animal_str_method(self):
        animal = Animal.objects.create(**self.animal_data)
        self.assertEqual(str(animal.name), 'Test Animal')

class SpeciesModelTest(TestCase):
    def setUp(self):
        self.species_data = {
            'name': 'Test Species',
            'description': 'Test Description',
            'lifetime': 'Test Lifetime',
            'avg_age': 5,
            'nutrition': 'Test Nutrition',
            'weight': 10.5,
            'avg_weight': 'Test Avg Weight',
            'type': 'Test Type'
        }

    def test_create_species(self):
        species = Species.objects.create(**self.species_data)
        self.assertEqual(species.name, self.species_data['name'])
        self.assertEqual(species.description, self.species_data['description'])
        self.assertEqual(species.lifetime, self.species_data['lifetime'])
        self.assertEqual(species.avg_age, self.species_data['avg_age'])
        self.assertEqual(species.nutrition, self.species_data['nutrition'])
        self.assertEqual(species.weight, self.species_data['weight'])
        self.assertEqual(species.avg_weight, self.species_data['avg_weight'])
        self.assertEqual(species.type, self.species_data['type'])

    def test_species_str_method(self):
        species = Species.objects.create(**self.species_data)
        self.assertEqual(str(species.name), 'Test Species')

class NoteModelTest(TestCase):
    def setUp(self):
        self.note_data = {
            'owner': 1,
            'title': 'Test Title',
            'content': 'Test Content'
        }

    def test_create_note(self):
        note = Note.objects.create(**self.note_data)
        self.assertEqual(note.owner, self.note_data['owner'])
        self.assertEqual(note.title, self.note_data['title'])
        self.assertEqual(note.content, self.note_data['content'])

    def test_note_str_method(self):
        note = Note.objects.create(**self.note_data)
        self.assertEqual(str(note.title), 'Test Title')

class TaskModelTest(TestCase):
    def setUp(self):
        self.task_data = {
            'owner': 1,
            'worker': 2,
            'title': 'Test Task',
            'description': 'Test Description',
            'content': 'Test Content',
            'status': False,
        }

    def test_create_task(self):
        task = Task.objects.create(**self.task_data)
        self.assertEqual(task.owner, self.task_data['owner'])
        self.assertEqual(task.worker, self.task_data['worker'])
        self.assertEqual(task.title, self.task_data['title'])
        self.assertEqual(task.description, self.task_data['description'])
        self.assertEqual(task.content, self.task_data['content'])
        self.assertEqual(task.status, self.task_data['status'])

    def test_task_str_method(self):
        task = Task.objects.create(**self.task_data)
        self.assertEqual(str(task.title), 'Test Task')

#    def test_add_task_comment(self):
#        task = Task.objects.create(**self.task_data)
#        comment = TaskComment.objects.create(owner=1, task=task, text='Test Comment')
#        self.assertEqual(str(task.comments.first()), str(comment))


class IntegrationTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_species_api_view(self):
        url = reverse('SpeciesAPIView')
        data = {
            'name': 'Example Name',
            'description': 'Example Description',
            'avg_age': 5,
            'lifetime': 10,
            'nutrition': 'Herbivore',
            'weight': 50,
            'avg_weight': 100,
            'type': 'Mammal',
            'photo': 'example.jpg',
        }

        # Wysłanie żądania POST
        response = self.client.post(url, data, format='json')

        # Sprawdzenie, czy odpowiedź ma kod 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Sprawdzenie, czy widok GET zwraca kod 200 (OK)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AnimalIntegrationTest(TestCase):

    def setUp(self):
        self.client = APIClient()


class TaskModelIntegrationTest(TestCase):

    def setUp(self):
        # Przygotowanie danych testowych
        self.task_data = {
            'owner': 1,
            'worker': 2,
            'title': 'Test Task',
            'description': 'Test description',
            'content': 'Test content',
            'status': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        }

        self.task = Task.objects.create(**self.task_data)

        self.comment_data = {
            'owner': 1,
            'task': self.task,
            'text': 'Test comment',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        }

        self.comment = TaskComment.objects.create(**self.comment_data)
        self.task.comments.add(self.comment)

    def test_task_creation(self):
        # Sprawdzenie, czy zadanie zostało poprawnie utworzone
        self.assertEqual(self.task.owner, self.task_data['owner'])
        self.assertEqual(self.task.worker, self.task_data['worker'])
        self.assertEqual(self.task.title, self.task_data['title'])
        self.assertEqual(self.task.description, self.task_data['description'])
        self.assertEqual(self.task.content, self.task_data['content'])
        self.assertEqual(self.task.status, self.task_data['status'])
        self.assertTrue(isinstance(self.task.created_at, datetime))
        self.assertTrue(isinstance(self.task.updated_at, datetime))

    def test_task_status_change(self):
        # Sprawdzenie, czy zmiana statusu zadania działa poprawnie
        self.task.status = True
        self.task.save()
        updated_task = Task.objects.get(id=self.task.id)
        self.assertTrue(updated_task.status)

    def test_task_comments_relation(self):
        # Sprawdzenie, czy relacja z komentarzami działa poprawnie
        self.assertEqual(self.task.comments.count(), 1)
        self.assertEqual(self.task.comments.first().text, self.comment_data['text'])