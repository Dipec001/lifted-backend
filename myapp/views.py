from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from jose import jwt  # Install jose library: pip install python-jose
from .models import CustomUser, Feed, Like, Comment, WorkoutType, Exercise, UserWorkout, SelectedExercise, Set
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .serializers import CustomUserSerializer, FeedSerializer, CommentSerializer, WorkoutTypeSerializer,ExerciseSerializer, UserWorkoutSerializer
from django.db.models import Prefetch
from rest_framework import status, permissions
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist


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

        # Check if the user already exists
        try:
            social_account = SocialAccount.objects.get(uid=apple_id, provider='apple')
            user = social_account.user
            new_user = False
        except SocialAccount.DoesNotExist:
            # If it doesn't exist, it's a new user
            new_user = True

        # If it's a new user, return a flag indicating so
        if new_user:
            return Response({'new_user': True}, status=status.HTTP_200_OK)

        # If it's an existing user, generate access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({'access_token': access_token, 'refresh_token': str(refresh)}, status=status.HTTP_200_OK)

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

    def exchange_apple_token(self, apple_token):
        # Your implementation to exchange Apple token for access token and refresh token
        token_endpoint = 'https://appleid.apple.com/auth/token'
        client_id = os.getenv('client_id')
        client_secret = os.getenv('client_secret')
        redirect_uri = os.getenv('redirect_uri')

        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': apple_token,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }

        response = requests.post(token_endpoint, data=data)
        return response.json()

    def create_jwt_token(self, user_id):
        # Your implementation to create a JWT token
        # Include necessary claims such as 'exp', 'iat', etc.
        secret_key = os.getenv('client_secret')  # Replace 'your-secret-key' with the actual secret key
        token_payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1),  # Token expiration time (adjust as needed)
            'iat': datetime.utcnow(),  # Issued at time
            # Add any other claims we want in the token
        }

        token = jwt.encode(token_payload, secret_key, algorithm='HS256')
        # Return the generated JWT token
        return token

    def generate_unique_username(self, email):
        # Combine email and name (or any other information) to create a base username
        base_username = f"{email}"

        # Generate a unique identifier using uuid4()
        unique_id = str(uuid.uuid4())[:8]  # Take the first 8 characters for simplicity

        # Combine the base username and unique identifier
        unique_username = f"{base_username}_{unique_id}"

        return unique_username


class UserRegistration(APIView):
    def post(self, request):
        # Extract the Apple token from the request
        apple_token = request.data.get('apple_token')

        if not apple_token:
            return Response({'error': 'Apple token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Decode Apple ID token if provided
        decoded_token = self.verify_apple_token(apple_token)
        print(decoded_token)
        if not decoded_token:
            return Response({'error': 'Invalid Apple ID token'}, status=status.HTTP_400_BAD_REQUEST)
        apple_id = decoded_token.get('sub')

        # and create the user
        if not apple_id:
            return Response({'error': 'Invalid Apple ID or missing user identifier'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already exists
        try:
            social_account = SocialAccount.objects.get(uid=apple_id, provider='apple')
            user = social_account.user
            return self.generate_tokens_response(user)
        except SocialAccount.DoesNotExist:
            # If it doesn't exist, it's a new user

            # Example: Extracting additional details from the request
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            username = request.data.get('username')

            # Validate and create the user
            if not all([first_name, last_name, email, username]):
                return Response({'error': 'Incomplete user details'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the email already exists
            existing_user = CustomUser.objects.filter(email=email).first()
            if existing_user:
                return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            


            # Create a new user without saving to the database yet
            user = CustomUser(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name
            )


            # Validate the user without saving
            user_serializer = CustomUserSerializer(instance=user, data=request.data)
            if user_serializer.is_valid():

                # Save the user to the database
                user_serializer.save()

                # Create a SocialAccount entry for the user
                SocialAccount.objects.create(user=user, uid=apple_id, provider='apple')

                # Generate access and refresh tokens for the new user
                return self.generate_tokens_response(user)
            else:
                return Response({'error': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'access_token': access_token, 'refresh_token': str(refresh)}, status=status.HTTP_200_OK)

    # # The rest of the code (generate_unique_username, etc.) remains unchanged
    # def generate_unique_username(self, email):
    #     # Combine email and name (or any other information) to create a base username
    #     base_username = f"{email}"

    #     # Generate a unique identifier using uuid4()
    #     unique_id = str(uuid.uuid4())[:8]  # Take the first 8 characters for simplicity

    #     # Combine the base username and unique identifier
    #     unique_username = f"{base_username}_{unique_id}"

    #     return unique_username


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

class FollowAPIView(APIView):
    """
    View to follow and unfollow
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        """Follow User"""
        user = request.user
        following_to_user = get_object_or_404(CustomUser, pk=pk)

        if user == following_to_user:
            return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        if user in following_to_user.followers.all():
            return Response({'error': 'You are already following this user'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Create a new instance of UserFollowing to represent the follow action
        follow_instance = UserFollowing.objects.create(user_id=user, following_user_id=following_to_user)

        # Serialize the follow action
        serializer = FollowingSerializer(follow_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)
