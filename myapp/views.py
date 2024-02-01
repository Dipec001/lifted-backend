from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from jose import jwt  # Install jose library: pip install python-jose
from .models import CustomUser, Feed, Like, Comment
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .serializers import CustomUserSerializer, FeedSerializer, CommentSerializer
from rest_framework import status, permissions
import uuid
from rest_framework_simplejwt.tokens import RefreshToken

load_dotenv()

# Create your views here.
def index(request):
    return HttpResponse({'detail'})


def trigger_error(request):
    division_by_zero = 1 / 0


# class AppleLogin(APIView):
#     def post(self, request):
#         # Handle Sign in with Apple token
#         apple_token = request.data.get('apple_token')

#         if not apple_token:
#             return Response({'error': 'Apple token is required'}, status=status.HTTP_400_BAD_REQUEST)


#         # Verify and decode Apple ID token
        
#         decoded_token = self.verify_apple_token(apple_token)
#         print(f"decoded_token= {decoded_token}")
#         if not decoded_token:
#             return Response({'error': 'Invalid Apple ID token'}, status=status.HTTP_400_BAD_REQUEST)

#         # Get user's Apple ID
#         try:
#             apple_id = decoded_token.get('sub')
#         except AttributeError:
#             return Response({'error':'Signature expired'})

#         # Check if the user already exists
#         try:
#             social_account = SocialAccount.objects.get(uid=apple_id, provider='apple')
#             user = social_account.user
#         except SocialAccount.DoesNotExist:
#             # If it doesn't exist, get profile details from frontend, create a new user and associated social account

#             # Extract profile user information
#             user_info = {
#                 'first_name': request.data.get('first_name'),
#                 'last_name': request.data.get('last_name'),
#                 'email': request.data.get('email'),
#                 # 'profile_picture': decoded_token.get('picture'),
#                 # Add any other fields you want to extract
#             }

#             # if not user_info['email']:
#             #     return Response({'detail': 'New User: Yes'}, status=status.HTTP_400_BAD_REQUEST)

#             # Check if the email already exists
#             existing_user = CustomUser.objects.filter(email=user_info['email']).first()
#             if existing_user:
#                 return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 # User does not exist, create a new user
#                 user = CustomUser.objects.create_user(
#                 email=user_info['email'],
#                 username=generate_unique_username(user_info['email']),
#                 first_name=user_info.get('first_name', ''),
#                 last_name=user_info.get('last_name', '')
#                 )
#                 user.save()


#                 # Create a SocialAccount entry for the user
#                 SocialAccount.objects.create(user=user, uid=apple_id, provider='apple')

#                 # Prompt the user for profile details
#                 user_serializer = CustomUserSerializer(instance=user, data=request.data)
#                 if user_serializer.is_valid():
#                     user_serializer.save()
#                 else:
#                     return Response({'error': user_serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({'error':f'{str(e)}'})


#         # Exchange Apple token for access token and refresh token
#         # token_response = self.exchange_apple_token(apple_token)
#         # if 'error' in token_response:
#         #     return Response({'error': 'Failed to exchange Apple token'}, status=status.HTTP_400_BAD_REQUEST)

#         # Your authentication logic (e.g., creating JWT token)
#         # jwt_token = self.create_jwt_token(user.id)

#         # return Response({'token': jwt_token}, status=status.HTTP_200_OK)
            
#          # Use Simple JWT to generate access and refresh tokens
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)

#         return Response({'access_token': access_token, 'refresh_token': str(refresh)}, status=status.HTTP_200_OK)

#     def verify_apple_token(self, apple_token):
#         # Your implementation to verify and decode the Apple token
#         try:
#             # Use your public key or the Apple public key to verify the signature
#             # Your implementation here
#             secret_key = os.getenv('client_secret')
#             decoded_token = jwt.decode(
#                 apple_token,
#                 algorithms='RS256',
#                 key=secret_key,
#                 audience=os.getenv('client_id'),
#                 options={"verify_signature": False},
#                 issuer='https://appleid.apple.com',)
#             return decoded_token
#         except Exception as e:
#             return str(e)

#     def exchange_apple_token(self, apple_token):
#         # Your implementation to exchange Apple token for access token and refresh token
#         token_endpoint = 'https://appleid.apple.com/auth/token'
#         client_id = os.getenv('client_id')
#         client_secret = os.getenv('client_secret')
#         redirect_uri = os.getenv('redirect_uri')

#         data = {
#             'client_id': client_id,
#             'client_secret': client_secret,
#             'code': apple_token,
#             'grant_type': 'authorization_code',
#             'redirect_uri': redirect_uri,
#         }

#         response = requests.post(token_endpoint, data=data)
#         return response.json()
    
#     def create_jwt_token(self, user_id):
#         # Your implementation to create a JWT token
#         # Include necessary claims such as 'exp', 'iat', etc.
#         secret_key = os.getenv('client_secret')  # Replace 'your-secret-key' with the actual secret key
#         token_payload = {
#             'user_id': user_id,
#             'exp': datetime.utcnow() + timedelta(days=1),  # Token expiration time (adjust as needed)
#             'iat': datetime.utcnow(),  # Issued at time
#             # Add any other claims we want in the token
#         }

#         token = jwt.encode(token_payload, secret_key, algorithm='HS256')
#         # Return the generated JWT token
#         return token

# def generate_unique_username(email):
#     # Combine email and name (or any other information) to create a base username
#     base_username = f"{email}"

#     # Generate a unique identifier using uuid4()
#     unique_id = str(uuid.uuid4())[:8]  # Take the first 8 characters for simplicity

#     # Combine the base username and unique identifier
#     unique_username = f"{base_username}_{unique_id}"

#     return unique_username


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

        # Validate and create the user
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

            # Validate and create the user
            if not all([first_name, last_name, email]):
                return Response({'error': 'Incomplete user details'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the email already exists
            existing_user = CustomUser.objects.filter(email=email).first()
            if existing_user:
                return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            


            # Create a new user without saving to the database yet
            user = CustomUser(
                email=email,
                username=self.generate_unique_username(email),
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

    # The rest of the code (generate_unique_username, etc.) remains unchanged
    def generate_unique_username(self, email):
        # Combine email and name (or any other information) to create a base username
        base_username = f"{email}"

        # Generate a unique identifier using uuid4()
        unique_id = str(uuid.uuid4())[:8]  # Take the first 8 characters for simplicity

        # Combine the base username and unique identifier
        unique_username = f"{base_username}_{unique_id}"

        return unique_username


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
            serializer.save(user=request.user, feed=feed)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_serializer_context(self):
        # Override this method to include the request in the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
