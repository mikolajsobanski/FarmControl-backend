from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions

from ..models import Note, Task, TaskComment
from apiauth.models import Farmer
from apiauth.serializers import FarmerSerializer
from ..serializers import NoteSerializer, TaskSerializer, TaskCommentSerializer

from django.db.models import Q


class NoteAPIView(APIView):
    def post(self, request):
        pk = request.data['pk']
        title = request.data['title']
        content = request.data['content']
        
        farmer = Farmer.objects.filter(id=pk).first()
        if farmer is None:
            raise exceptions.AuthenticationFailed('User not found!')
        
        Note.objects.create(
            owner = pk,
            title = title,
            content = content
        )

        return Response({
            'message': 'success'
        })
    
    def get(self, request):
        pk = request.query_params.get('pk')
        
        farmer = Farmer.objects.filter(id=pk).first()
        if farmer is None:
            raise exceptions.AuthenticationFailed('User not found!')
        
        notes = Note.objects.filter(owner=pk).order_by('-updated_at')
        serializer = NoteSerializer(notes, many=True)
        return Response({'notes': serializer.data})
    
    def put(self, request):
        pk_note = request.data['pk_note']
        note = Note.objects.filter(id=pk_note).first()
        serializer = NoteSerializer(note, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'success'
        })
    
    def delete(self, request):
        pk_note = request.query_params.get('pk_note')
        note = Note.objects.filter(id=pk_note).first()
        note.delete()
        return Response({
            'message': 'success'
        })


class TaskAPIView(APIView):
    def post(self,request):
        pk_owner = request.data['pk_owner']
        pk_worker = request.data['pk_worker']
        title = request.data['title']
        content = request.data['content']
        description = request.data['description']

        farmer = Farmer.objects.filter(id=pk_owner).first()
        if farmer is None:
            raise exceptions.AuthenticationFailed('User not found!')
        
        worker = Farmer.objects.filter(id=pk_worker).first()
        if worker is None:
            raise exceptions.AuthenticationFailed('User not found!')
        
        Task.objects.create(
            owner = pk_owner,
            worker = pk_worker,
            title = title,
            description = description,
            content = content,
        )

        return Response({
            'message': 'success'
        })  
    def put(self, request):
        pk = request.data['pk']
        tasks = Task.objects.filter(id=pk).first()
        serializer = TaskSerializer(tasks, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'success'
        })
    def delete(self, request):
        pk = request.query_params.get('pk')
        task = Task.objects.filter(id=pk).first()
        task.delete()
        return Response({
            'message': 'success'
        })

class MakeCompleteTaskAPIView(APIView):
    def post(self, request):
        pk = request.data['pk']
        task = Task.objects.get(id=pk)
        task.status = True
        task.save()
        return Response({
            'message': 'success'
        })
    
class MakeInProgressTaskAPIView(APIView):
     def post(self, request):
        pk = request.data['pk']
        task = Task.objects.get(id=pk)
        task.status = False
        task.save()
        return Response({
            'message': 'success'
        })

class GetInProgressTaskAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        condition1 = Q(owner=pk)
        condition2 = Q(worker=pk)
        condition3 = Q(status=False)
        combined_conditions = (condition1 | condition2) & condition3
        tasks = Task.objects.filter(combined_conditions).distinct()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
class GetCompleteTaskAPIView(APIView):
    def get(self, request):
        pk = request.query_params.get('pk')
        condition1 = Q(owner=pk)
        condition2 = Q(worker=pk)
        condition3 = Q(status=True)
        combined_conditions = (condition1 | condition2) & condition3
        tasks = Task.objects.filter(combined_conditions).distinct()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
class TaskCommentsAPIView(APIView):
    def post(self, request):
        owner_id = request.data['owner']
        task_id = request.data['task']
        text = request.data['text']

        farmer = Farmer.objects.filter(id=owner_id).first()
        if farmer is None:
            raise exceptions.AuthenticationFailed('User not found!')
        
        task = Task.objects.get(id=task_id)
        if task is None:
            raise exceptions.AuthenticationFailed('Task not found!')
        
        comment = TaskComment.objects.create(owner=owner_id, task=task, text=text)
        task.comments.add(comment)
        task.save()
        task_comments = task.comments.all()
        return Response({
            'message': 'success'
        })
    def get(self, request):
        task_id = request.query_params.get('pk')
        task = Task.objects.get(id=task_id)
        if task is None:
            raise exceptions.AuthenticationFailed('Task not found!')
        comments = task.comments.all()
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)
    def put(self,request):
        pk = request.data['pk']
        text = request.data['text']
        comment = TaskComment.objects.get(id=pk)
        
        comment.text = text
        comment.save()
        serializer = TaskCommentSerializer(comment, many=False)
        return Response({
            'message': 'success'
        })
    def delete(self, request):
        pk = request.query_params.get('pk')
        comment = TaskComment.objects.filter(id=pk).first()
        comment.delete()
        return Response({
            'message': 'success'
        })


