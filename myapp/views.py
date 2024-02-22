from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from jose import jwt  # Install jose library: pip install python-jose
from .models import CustomUser, Feed, Like, Comment, WorkoutType, Exercise, UserWorkout, SelectedExercise, Set, WorkoutGroup, CustomWorkout
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .serializers import (CustomUserSerializer, FeedSerializer, CommentSerializer, WorkoutTypeSerializer,ExerciseSerializer
                          , OnboardSerializer, WorkoutGroupSerializer, CustomWorkoutSerializer, WorkoutSessionSerializer, ZoneSerializer, WorkoutSetSerializer)
from django.db.models import Prefetch
from rest_framework import status, permissions
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .permissions import IsOwnerOrReadOnly


load_dotenv()

# Create your views here.
def index(request):
    return HttpResponse({'detail'})

@csrf_exempt
def trigger_error(request):

    division_by_zero = 1 / 0


class AppleLogin(APIView):
    def post(self, request):
        # Handle Sign in with Apple token
        apple_token = request.data.get('apple_token')

        if not apple_token:
            return Response({'error': 'Apple token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify and decode Apple ID token
        decoded_token = self.verify_apple_token(apple_token)
        print(decoded_token)

        if not decoded_token:
            return Response({'error': 'Invalid Apple ID token'}, status=status.HTTP_400_BAD_REQUEST)

        # Get user's Apple ID
        try:
            apple_id = decoded_token.get('sub')
        except AttributeError:
            return Response({'error': 'Signature expired'})
        
        try:
            # Attempt to retrieve the email from the decoded token
            email = decoded_token.get('email')
            print(email)

            if not email:
                # If the email field is missing from the token
                return Response({'error': 'Email not found in token'}, status=status.HTTP_400_BAD_REQUEST)

        except AttributeError:
            # If the decoded token doesn't have a get method or is not a dictionary-like object
            return Response({'error': 'Invalid token format'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already exists
        try:
            social_account = SocialAccount.objects.get(uid=apple_id, provider='apple')
            user = social_account.user
            new_user = False

            # Authenticate the existing user and return their data
            serializer = CustomUserSerializer(user)

            # Generate access and refresh tokens for the new user
            tokens_data = self.generate_tokens_response(user)

            user_data = serializer.data

            if user_data['username'] == user_data['email']:
                user_data['is_new_user'] = True
                user_data['username'] = None
            else:
                #new user attr when username is not set as False
                user_data.update({'is_new_user': False})

            # Include the access and refresh tokens in the response
            user_data.update(tokens_data)

            return Response(user_data, status=status.HTTP_200_OK)
        except SocialAccount.DoesNotExist:
            # If it doesn't exist, it's a new user
            is_new_user = True
        
            # Check if the email already exists
            existing_user = CustomUser.objects.filter(email=email).first()
            if existing_user:
                return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            

            # Create a new user without saving to the database yet
            user = CustomUser(
                email=email,
                username=email,  # Use the same value as the email by default
            )
            user.save()

            # Create a SocialAccount entry for the user
            SocialAccount.objects.create(user=user, uid=apple_id, provider='apple')

            # Authenticate the existing user and return their data
            serializer = CustomUserSerializer(user)

            # Generate access and refresh tokens for the new user
            tokens_data = self.generate_tokens_response(user)

            user_data = serializer.data

            # Include the access and refresh tokens in the response
            user_data.update(tokens_data)
            user_data.update({'is_new_user': True})

            if user_data['username'] == user_data['email']:
                user_data['username'] = None


            return Response(user_data, status=status.HTTP_200_OK)

    def verify_apple_token(self, apple_token):
        # Your implementation to verify and decode the Apple token
        try:
            # Use your public key or the Apple public key to verify the signature
            secret_key = os.getenv('client_secret')
            decoded_token = jwt.decode(
                apple_token,
                algorithms='RS256',
                key=secret_key,
                audience=os.getenv('client_id'),
                options={"verify_signature": False},
                issuer='https://appleid.apple.com',)
            return decoded_token
        except Exception as e:
            return None  # Return None instead of str(e) to distinguish from valid decoding
        
    def generate_tokens_response(self, user):
        # Generate access and refresh tokens for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return {'access_token': access_token, 'refresh_token': str(refresh)}

    # def exchange_apple_token(self, apple_token):
    #     # Your implementation to exchange Apple token for access token and refresh token
    #     token_endpoint = 'https://appleid.apple.com/auth/token'
    #     client_id = os.getenv('client_id')
    #     client_secret = os.getenv('client_secret')
    #     redirect_uri = os.getenv('redirect_uri')

    #     data = {
    #         'client_id': client_id,
    #         'client_secret': client_secret,
    #         'code': apple_token,
    #         'grant_type': 'authorization_code',
    #         'redirect_uri': redirect_uri,
    #     }

    #     response = requests.post(token_endpoint, data=data)
    #     return response.json()

class OnBoardingView(APIView):
    """
    This view is used to onboard/register a user
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(pk=request.user.pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid User"}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        # Convert username to lowercase if provided
        if 'username' in data:
            data['username'] = data['username'].lower()
        
        if user.username == user.email and 'username' not in data:
            return Response({"error": "Username is required"})
        
        
        serializer = OnboardSerializer(user, data=data, partial=True)  # Using partial=True to allow partial updates
        if serializer.is_valid():
            with transaction.atomic():

                print(data)

                serializer.save()

                # Generate access and refresh tokens for the new user
                tokens_data = self.generate_tokens_response(user)

                # Add is_new_user = False to the serialized data
                user_data = serializer.data

                user_data.update(tokens_data)
                user_data['is_new_user'] = False
                # serialized_data.update({'is_new_user': False})
                if 'username' not in data and  user.username.lower() == user.email.lower():
                    user_data['username'] = None

                

            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def generate_tokens_response(self, user):
        # Generate access and refresh tokens for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return {'access_token': access_token, 'refresh_token': str(refresh)}

# views.py

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserCreationSerializer
from rest_framework.permissions import AllowAny

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserCreationSerializer
    permission_classes = [AllowAny]


class FeedListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can access this view

    def get(self, request, *args, **kwargs):
        # Retrieve all feeds from the database
        feeds = Feed.objects.all()
        serializer = FeedSerializer(feeds, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = FeedSerializer(data=request.data)
        if serializer.is_valid():
            # Set the user field to the currently authenticated user
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FeedRetrieveUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can access this view

    def get(self, request, pk, *args, **kwargs):
        # Retrieve a specific feed by its primary key (pk)
        feed = get_object_or_404(Feed, pk=pk)
        serializer = FeedSerializer(feed)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        # Update a specific feed by its primary key (pk) and ensure the user making the request is the owner of the feed
        feed = get_object_or_404(Feed, pk=pk, user=request.user)
        serializer = FeedSerializer(feed, data=request.data, partial=True)
        if serializer.is_valid():
            # Save the updated feed
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        feed = get_object_or_404(Feed, pk=pk, user=request.user)
        feed.delete()
        return Response({'detail':'Feed deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class LikeActionView(APIView):
    """
    This endpoint is used to like or unlike a feed
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk, format=None):
        feed = get_object_or_404(Feed, pk=pk)
        user = request.user

        # Check if the user has already liked the post
        has_liked = Like.objects.filter(feed=feed, user=user).exists()

        if has_liked:
            # If the user has liked, it means they want to unlike
            Like.objects.filter(feed=feed, user=user).delete()
            feed.likes_count -= 1
            detail_msg = 'Feed unliked successfully.'
        else:
            # If the user hasn't liked, it means they want to like
            Like.objects.create(feed=feed, user=user)
            feed.likes_count += 1
            detail_msg = 'Feed liked successfully.'

        feed.save()  # Save the updated likes_count
        return Response({'detail': detail_msg}, status=status.HTTP_200_OK)
    

class CommentListCreateView(APIView):
    """
    This is the endpoint to  list all comments for a specific feed and create new comment on that feed
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        feed = get_object_or_404(Feed, pk=pk)
        comments = Comment.objects.filter(feed=feed)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        feed = get_object_or_404(Feed, pk=pk)
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            feed.comments_count += 1
            feed.save()  # Save the updated feed instance
            serializer.save(user=request.user, feed=feed)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_serializer_context(self):
        # Override this method to include the request in the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class WorkoutListView(APIView):
    """
    This endpoint is used to list the workout types
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        workouts = WorkoutType.objects.all()
        serializer = WorkoutTypeSerializer(workouts, many=True)
        return Response(serializer.data)
    
class ExercisesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, workout=None):
        if workout:
            # Retrieve exercises for a specific workout type
            exercises = Exercise.objects.filter(workout_type__name=workout)
        else:
            # Retrieve all exercises
            exercises = Exercise.objects.all()

        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data)


class UserWorkoutListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Retrieve all user workouts of the authenticated user.

        Returns:
            JsonResponse: JsonResponse containing serialized data of all user workouts.
        """
        print(f"Request headers: {request.headers}")
        user_workouts = UserWorkout.objects.filter(user=request.user).prefetch_related('selectedexercise_set__set_set')
        user_workouts_data = []

        for user_workout in user_workouts:
            selected_exercises_data = []

            for selected_exercise in user_workout.selectedexercise_set.all():
                sets_data = []
                for set_instance in selected_exercise.set_set.all():
                    set_data = {
                        'reps': set_instance.reps,
                        'weight': set_instance.weight
                    }
                    sets_data.append(set_data)

                exercise_data = {
                    'exercise_id': selected_exercise.exercise.id,
                    'exercise_name': selected_exercise.exercise.name,
                    'sets': sets_data
                }
                selected_exercises_data.append(exercise_data)

            user_workout_data = {
                'id': user_workout.id,
                'user': user_workout.user.id,
                'title': user_workout.title,
                'selected_exercises': selected_exercises_data,
                # Add other fields as needed
            }
            user_workouts_data.append(user_workout_data)

        return JsonResponse({'results': user_workouts_data})


    
    def post(self, request):
        """
        Create a new user workout entry.
        """
        request.data['user'] = request.user.id
        data = request.data
        exercise_data = data.get('selected_exercises')

        if not exercise_data:
            return JsonResponse({'detail': 'Exercises are required'}, status=400)

        with transaction.atomic():
            try:
                user_workout = UserWorkout.objects.create(user=request.user, title=data['title'])
                added_exercise_ids = []  # Track added exercise IDs

                for ex_data in exercise_data:
                    exercise_id = ex_data.get('exercise')
                    sets_data = ex_data.get('sets', [])
                    if not sets_data:
                        return JsonResponse({"detail": "Sets data is required for each selected exercise"})
                    if Exercise.objects.filter(id=exercise_id).exists():
                        # Check if the exercise ID is already added
                        if exercise_id in added_exercise_ids:
                            return JsonResponse({"detail": f"Exercise with ID {exercise_id} is already added to this user workout"}, status=400)
                        
                        exercise_instance = Exercise.objects.get(id=exercise_id)
                        selected_exercise = SelectedExercise.objects.create(user_workout=user_workout, exercise=exercise_instance)
                        added_exercise_ids.append(exercise_id)  # Add exercise ID to the list

                        for set_data in sets_data:
                            Set.objects.create(reps=set_data['reps'], weight=set_data['weight'], selected_exercise=selected_exercise)
                    else:
                        raise JsonResponse({"detail": "Invalid exercise ID"})

            except Exception as e:
                # Rollback if anything fails
                transaction.set_rollback(True)
                return JsonResponse({"detail": str(e)}, status=400)

        return JsonResponse({"detail": "User workout created successfully"}, status=201)


class UserWorkoutRetrieveUpdateView(APIView):
    """
    Retrieve, update or delete a user workout instance.
    """
    permission_classes=[permissions.IsAuthenticated]
    
    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve one User workout
        """
        print(f"Request headers: {request.headers}")
        try:
            # Retrieve a specific user workout by its primary key (pk)
            user_workout = get_object_or_404(UserWorkout, pk=pk, user=request.user)

            selected_exercises_data = []

            for selected_exercise in user_workout.selectedexercise_set.all():
                sets_data = []

                # Retrieve all sets for the selected exercise
                for set_instance in selected_exercise.set_set.all():
                    set_data = {
                        'reps': set_instance.reps,
                        'weight': set_instance.weight
                    }
                    sets_data.append(set_data)

                exercise_data = {
                    'exercise_id': selected_exercise.exercise.id,
                    'exercise_name': selected_exercise.exercise.name,
                    'sets': sets_data
                }
                selected_exercises_data.append(exercise_data)

            user_workout_data = {
                'id': user_workout.id,
                'user': user_workout.user.id,
                'title': user_workout.title,
                'selected_exercises': selected_exercises_data,
                # Add other fields as needed
            }

            return Response({'detail': user_workout_data})

        except Http404:
            return Response({'detail': 'User workout not found'}, status=status.HTTP_404_NOT_FOUND)


    def put(self, request, pk, *args, **kwargs):
        """
        Updates the user workout such as title, adds or removes exercises from it, and so on.
        """
        try:
            user_workout = UserWorkout.objects.get(pk=pk)
            if request.user != user_workout.user:
                return Response({'detail': 'You do not have permission to edit this user workout.'}, status=status.HTTP_403_FORBIDDEN)
            
            data = request.data
            if 'title' in data:
                user_workout.title = data['title']

            add_or_remove_exercises = data.get('add_remove_exercises', [])
            for action_dict in add_or_remove_exercises:
                action = action_dict.get("action")
                exercise_id = action_dict.get("exercise_id")
                if action and exercise_id:
                    try:
                        exercise = Exercise.objects.get(pk=int(exercise_id))
                        if action == 'ADD':
                            # Check if the exercise already exists in the user workout
                            if SelectedExercise.objects.filter(user_workout=user_workout, exercise=exercise).exists():
                                return Response({'detail': f'Exercise with ID {exercise_id} is already added to this user workout.'}, status=status.HTTP_400_BAD_REQUEST)
                        
                            selected_exercise = SelectedExercise.objects.create(user_workout=user_workout, exercise=exercise)
                            user_workout.selectedexercise_set.add(selected_exercise)
                        elif action == 'REMOVE':
                            selected_exercise = SelectedExercise.objects.filter(user_workout=user_workout, exercise=exercise).first()
                            if selected_exercise:
                                selected_exercise.delete()
                            else:
                                return Response({'detail': f'Exercise with ID {exercise_id} is not associated with this user workout.'}, status=status.HTTP_400_BAD_REQUEST)
                    except Exercise.DoesNotExist:
                        return Response({'detail': f'Exercise with ID {exercise_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                
            user_workout.save()

            # Get all SelectedExercise instances associated with the UserWorkout
            selected_exercises = SelectedExercise.objects.filter(user_workout=user_workout)

            # Get the IDs of the exercises associated with the SelectedExercise instances
            exercise_ids = [selected_exercise.exercise.id for selected_exercise in selected_exercises]

            user_workout_data = {
                'id': user_workout.id,
                'user': user_workout.user.id,
                'title': user_workout.title,
                'exercises': exercise_ids,
                # Add other fields as needed
            }
            return Response(user_workout_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'User workout does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        

    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a User workout
        """
        try: 
            user_workout = UserWorkout.objects.select_related('user').get(pk=pk)
            
            if user_workout.user != request.user:
                return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

            user_workout.delete()
            return Response({'detail': 'User workout deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except UserWorkout.DoesNotExist:
            return Response({'error': 'The specified user workout could not be found'}, status=status.HTTP_404_NOT_FOUND)


class EditSetAPIView(APIView):
    def put(self, request, set_id):
        try:
            set_instance = Set.objects.get(id=set_id)
            selected_exercise = set_instance.selected_exercise
            user_workout = selected_exercise.user_workout

            # Check if the user has permission to edit the set
            if request.user != user_workout.user:
                return Response({"detail": "You do not have permission to edit this set"}, status=status.HTTP_403_FORBIDDEN)

            reps = request.data.get('reps')
            weight = request.data.get('weight')
            if reps is not None:
                set_instance.reps = reps
            if weight is not None:
                set_instance.weight = weight
            set_instance.save()
            return Response({"detail": "Set updated successfully"}, status=status.HTTP_200_OK)
        except Set.DoesNotExist:
            return Response({"detail": "Set not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteSetAPIView(APIView):
    def delete(self, request, set_id):
        try:
            set_instance = Set.objects.get(id=set_id)
            selected_exercise = set_instance.selected_exercise
            user_workout = selected_exercise.user_workout

            # Check if the user has permission to delete the set
            if request.user != user_workout.user:
                return Response({"detail": "You do not have permission to delete this set"}, status=status.HTTP_403_FORBIDDEN)

            set_instance.delete()
            return Response({"detail": "Set deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Set.DoesNotExist:
            return Response({"detail": "Set not found"}, status=status.HTTP_404_NOT_FOUND)

class AddSetAPIView(APIView):
    def post(self, request, selected_exercise_id):
        try:
            selected_exercise = SelectedExercise.objects.get(id=selected_exercise_id)
            user_workout = selected_exercise.user_workout

            # Check if the user has permission to add a set to the selected exercise
            if request.user != user_workout.user:
                return Response({"detail": "You do not have permission to add a set to this selected exercise"}, status=status.HTTP_403_FORBIDDEN)

            reps = request.data.get('reps')
            weight = request.data.get('weight')
            if reps is None or weight is None:
                return Response({"detail": "Both reps and weight are required"}, status=status.HTTP_400_BAD_REQUEST)
            Set.objects.create(reps=reps, weight=weight, selected_exercise=selected_exercise)
            return Response({"detail": "Set added successfully"}, status=status.HTTP_201_CREATED)
        except SelectedExercise.DoesNotExist:
            return Response({"detail": "Selected exercise not found"}, status=status.HTTP_404_NOT_FOUND)
        
from .serializers import FollowingSerializer
from .models import UserFollowing
from django.db import IntegrityError

class FollowAPIView(APIView):
    """
    View to follow
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        """Follow User"""
        user = request.user
        following_to_user = get_object_or_404(CustomUser, pk=pk)

        if user == following_to_user:
            return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Attempt to create a new instance of UserFollowing to represent the follow action
            follow_instance = UserFollowing.objects.create(user_id=user, following_user_id=following_to_user)
        except IntegrityError:
            # If the follow relationship already exists, return an error response
            return Response({'error': 'You are already following this user'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        

        # Serialize the follow action
        serializer = FollowingSerializer(follow_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UnFollowAPIView(APIView):
    """
    View to undo follow (unfollow).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk, *args, **kwargs):
        """Unfollow User."""
        user = request.user
        
        # Retrieve the specific follow record for this user/followee
        following_in_question = get_object_or_404(UserFollowing, user_id=user, following_user_id=pk)

        # Delete the follow record
        following_in_question.delete()
        
        return Response({'success': 'Unfollowed successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class ProfileRetrieveUpdateAPIView(APIView):
    """
    Update Profile Details
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get(self, request, pk, *args, **kwargs):
        """
        Get Profile Details
        """
        # Retrieve the profile of the specified user
        user = get_object_or_404(CustomUser, pk=pk)
        
        # Serialize the profile data
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        """
        Update Profile Details
        """
        # Retrieve the profile of the specified user
        user = get_object_or_404(CustomUser, pk=pk)

        # Check if the requesting user is the owner of the profile
        self.check_object_permissions(request, user)

        # Check if the request data is valid
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """
        Delete  User Account. ONly permitted by the user
        """

        # Retrieve the profile of the specified user
        user = get_object_or_404(CustomUser, pk=pk)

        # Check if the requesting user is the owner of the profile
        self.check_object_permissions(request, user)

        # Delete the user account
        user.delete()

        return Response({"detail": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    
# class WorkoutGroupAPIView(APIView):
#     """
#     API endpoint for creating and retrieving workout groups.
#     """
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         serializer = WorkoutGroupSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request):
#         workout_groups = WorkoutGroup.objects.all()
#         serializer = WorkoutGroupSerializer(workout_groups, many=True)
#         return Response(serializer.data)
import json
from .models import WorkoutSession, Zone, WorkoutSet
class WorkoutGroupAPIView(APIView):
    """View to create a workout Group
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            workout_groups = WorkoutGroup.objects.filter(workoutsession__group__user=user).distinct()
            response_data = []

            for group in workout_groups:
                workout_sessions = []
                sessions = group.workoutsession_set.all()

                for session in sessions:
                    zones = []
                    session_zones = session.zones.all()

                    for zone in session_zones:
                        zones.append({
                            "zone_number": zone.zone_number,
                            "duration": str(zone.duration),
                            "hr_points": zone.hr_points
                        })

                    sets = []
                    session_sets = session.sets.all()

                    for workout_set in session_sets:
                        sets.append({
                            "reps": workout_set.reps,
                            "weight": workout_set.weight,
                            "avg_heart_rate": workout_set.avg_heart_rate
                        })

                    workout_sessions.append({
                        "start_time": session.start_time.isoformat(),
                        "end_time": session.end_time.isoformat() if session.end_time else None,
                        "total_hr_points": session.total_hr_points,
                        "avg_heart_rate_per_min": session.avg_heart_rate_per_min,
                        "zones": zones,
                        "sets": sets
                    })

                response_data.append({"workout_sessions": workout_sessions})

            return JsonResponse(response_data, status=200)

        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=400)
        
    def post(self, request):
        try:
            data = request.data.get('workout_session')  # Access 'workout_session' key

            if not data:
                return JsonResponse({"detail": "Workout session data is required."}, status=400)

            with transaction.atomic():
                workout_group = WorkoutGroup.objects.create()

                for session_data in data:  # Iterate over each workout session
                    start_time = session_data.get('start_time')
                    end_time = session_data.get('end_time')
                    total_hr_points = session_data.get('total_hr_points', 0)
                    avg_heart_rate_per_min = session_data.get('avg_heart_rate_per_min')
                    zones = session_data.get('zones', [])
                    sets = session_data.get('sets', [])

                    if not start_time:
                        return JsonResponse({"detail": "Start time is required."}, status=400)

                    num_zones = len(zones)
                    if num_zones != 5:
                        raise ValueError("This session does not have 5 zones.")

                    workout_session = WorkoutSession.objects.create(
                        start_time=start_time,
                        end_time=end_time,
                        total_hr_points=total_hr_points,
                        avg_heart_rate_per_min=avg_heart_rate_per_min,
                        group=workout_group
                    )

                    # Create zones
                    for zone_data in zones:
                        zone = Zone.objects.create(
                            workout_session=workout_session,
                            zone_number=zone_data.get('zone_number'),
                            duration=zone_data.get('duration'),
                            hr_points=zone_data.get('hr_points')
                        )

                    # Create workout sets
                    for set_data in sets:
                        workout_set = WorkoutSet.objects.create(
                            workout_session=workout_session,
                            reps=set_data.get('reps'),
                            weight=set_data.get('weight'),
                            avg_heart_rate=set_data.get('avg_heart_rate')
                        )

            return JsonResponse({"detail": "Workout group created successfully."}, status=201)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=400)



class CustomWorkoutAPIView(APIView):
    """
    API endpoint for creating and retrieving custom workouts.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CustomWorkoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        custom_workouts = CustomWorkout.objects.all()
        serializer = CustomWorkoutSerializer(custom_workouts, many=True)
        return Response(serializer.data)