from django.shortcuts import render

# pip install djangorestframework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import *
from .serializers import *

# pip install djangorestframework-jwt
import jwt
import datetime

# pip install django-bcrypt
import bcrypt

#-------
# pip install urlsafe-base64-py
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
#---------
from .pagination import *
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Avg
from django.db.models import Count
from django.db.models import Case, When, Value

# notes:- guest page_contactUs, regiseration process, book_favourite_counter manual !!!, insert book


#-- login
class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user_password = request.data.get('user_password')

        try:
            user = User.objects.get(email=email, user_password=user_password)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found or incorrect password!", status=status.HTTP_401_UNAUTHORIZED)

       
        payload = {
            'id': user.user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        return Response({
            'jwt': token
        }, status=status.HTTP_200_OK)




#-- register
class RegisterAPIView(APIView):
    def post(self, request):
        user_name = request.data.get('user_name')
        email = request.data.get('email')
        user_password = request.data.get('user_password')
        
        # Hash the password using bcrypt and verify hashing
        hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

        # Save the user with the hashed password
        user = User(user_name=user_name, email=email, user_password=hashed_password)
        user.save()

        reader=Reader(user=user)
        reader.save()

        return Response({'message': 'User registered successfully. Please check your email to verify your account.'}, status=status.HTTP_200_OK)
    


#-- list category
class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

#-- list book (pagination achived)
class BookListView(APIView):
    def get(self, request):
        books = Book.objects.all()  
        paginator = BookPagination()  
        result_page = paginator.paginate_queryset(books, request)  
        serializer = BookSerializer(result_page, many=True)  
        return paginator.get_paginated_response(serializer.data)
    

#-- list most readed book (pagination achived)
class MostReaded_BookListView(APIView):
    def get(self, request):
        books = Book.objects.order_by('-book_reading_counter')
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


#-- list last uploaded book (pagination achived)
class LastUploaded_BookListView(APIView):
    def get(self, request):
        books = Book.objects.order_by('-book_uploaded_date')
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

#-- add rating and review
class AddRatingAndReviewView(APIView):
    def post(self, request):
        # Extract data from request
        book_id = request.data.get("book_id")
        reader_id = request.data.get("reader_id")
        rating = request.data.get("rating")
        review = request.data.get("review")

        # Validate that required fields are present
        if not (book_id and reader_id and rating is not None and review):
            return Response({"error": "All fields (book_id, reader_id, rating, review) are required."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Fetch the book and reader objects
        try:
            book = Book.objects.get(pk=book_id)
            reader = Reader.objects.get(pk=reader_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found."}, status=status.HTTP_404_NOT_FOUND)

        # Create the Rating_And_Review entry
        Rating_And_Review.objects.create(
            book=book,
            reader=reader,
            rating=rating,
            review=review
        )

        # Recalculate the average rating for the book
        ratings = Rating_And_Review.objects.filter(book=book).values_list('rating', flat=True)
        total_ratings = sum(ratings)
        rating_count = len(ratings)
        average_rating = round(total_ratings / rating_count) if rating_count > 0 else 0

        # Update the book's average rating
        book.book_rating_avg = average_rating
        book.save()

        return Response({"message": "Rating and review added successfully."}, status=status.HTTP_201_CREATED)
    
#-- list Most Rating book (pagination achived)
class MostRating_BookListView(APIView):
    def get(self, request):
        books = Book.objects.order_by('-book_rating_avg')
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

#-- list searched book
class BookSearchView(APIView):
    def get(self, request):
        # Get parameters from the request
        search_query = request.query_params.get('search', '').strip()
        sort_by = request.query_params.get('sort_by', '')
        category_ids = request.query_params.get('category', None)
        min_rating = request.query_params.get('min_rating', None)

        # Base queryset, only filter if search query is provided
        books = Book.objects.all()
        if search_query:
            books = books.filter(book_name__icontains=search_query)

        # Filter by multiple categories if provided
        if category_ids:
            category_id_list = category_ids.split(',')
            books = books.filter(category__category_id__in=category_id_list)

        # Filter by minimum rating if provided
        if min_rating:
            books = books.filter(book_rating_avg__gte=min_rating)

        # Apply sorting
        if sort_by == 'reviewed':
            books = books.order_by('-book_reading_counter')
        elif sort_by == 'favourite':
            books = books.order_by('-book_favourite_counter')
        elif sort_by == 'newest':
            books = books.order_by('-book_uploaded_date')

        # Apply pagination
        paginator = BookPagination()
        paginated_books = paginator.paginate_queryset(books, request)

        # Serialize the paginated data
        serializer = BookSerializer(paginated_books, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)

    

#-----------------------------------Reader
#-- list most readed book based on reader preferences (pagination achived)
# class MostReadedPreferences_BookListView(APIView):
#     def get(self, request):
#         user = request.user
#         if not user.is_authenticated:
#             return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
#         # Get categories from user preferences
#         user_preferences = Preferences.objects.filter(reader__user=user).values_list('category', flat=True)
        
#         # Filter books based on the user's preferred categories
#         books = Book.objects.filter(category__in=user_preferences).order_by('-book_reading_counter')
        
#         # Apply pagination
#         paginator = BookPagination()
#         result_page = paginator.paginate_queryset(books, request)
#         serializer = BookSerializer(result_page, many=True)
        
#         return paginator.get_paginated_response(serializer.data)

class MostReadedPreferences_BookListView(APIView):
    def get(self, request):
        # Get the user_id directly from the query parameters
        user_id = request.query_params.get('user_id')
        
        # Get categories from user preferences based on user_id
        user_preferences = Preferences.objects.filter(reader__user__user_id=user_id).values_list('category', flat=True)
        
        # Filter books based on the user's preferred categories
        books = Book.objects.filter(category__in=user_preferences).order_by('-book_reading_counter')
        
        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    

class MostRatingPreferences_BookListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get categories from user preferences based on user_id
        user_preferences = Preferences.objects.filter(reader__user__user_id=user_id).values_list('category', flat=True)
        
        # Filter books based on the user's preferred categories and order by rating
        books = Book.objects.filter(category__in=user_preferences).order_by('-book_rating_avg')
        
        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

class LastUploadedPreferences_BookListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get categories from user preferences based on user_id
        user_preferences = Preferences.objects.filter(reader__user__user_id=user_id).values_list('category', flat=True)
        
        # Filter books based on the user's preferred categories and order by upload date
        books = Book.objects.filter(category__in=user_preferences).order_by('-book_uploaded_date')
        
        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

#-- list continue reading book (pagination achived)
class BookContinueReadingListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter books in the BookContinueReading table for the specified user and order in reverse
        continue_reading_books = Book.objects.filter(bookcontinuereading__reader__user__user_id=user_id).order_by('-bookcontinuereading__continue_reading_id')

        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(continue_reading_books, request)
        serializer = BookSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    

class LastThreeWishListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        reader_id = request.query_params.get('reader_id')
        if not reader_id:
            return Response({"error": "Reader ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the last three wishlist items for the given reader, ordered by `wish_list_id`
        last_three_items = WishList.objects.filter(reader_id=reader_id).order_by('-wish_list_id')[:3]
        
        # Extract the book_ids from the last three wishlist items, preserving the order
        book_ids = [item.book_id for item in last_three_items]
        
        # Fetch the corresponding Book objects using the extracted book_ids in the same order as book_ids
        books = Book.objects.filter(book_id__in=book_ids).order_by(
            Case(*[When(book_id=book_id, then=pos) for pos, book_id in enumerate(book_ids)], default=0)
        )
        
        # Serialize the Book objects
        serializer = BookSerializer(books, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

class LastThreeNotificationListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        reader_id = request.query_params.get('reader_id')
        if not reader_id:
            return Response({"error": "Reader ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the last three notifications for the given reader, ordered by `notification_id`
        last_three_items = Notification.objects.filter(reader_id=reader_id).order_by('-notification_id')[:3]
        
        # Extract only the notification_record from each item
        notification_records = [item.notification_record for item in last_three_items]
        
        # Return the list of notification records
        return Response(notification_records, status=status.HTTP_200_OK)

    
#-- list wishlist (pagination achived)
class WishListListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        reader_id = request.query_params.get('reader_id')
        if not reader_id:
            return Response({"error": "Reader ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the wishlist items for the given reader, ordered by `wish_list_id`
        items = WishList.objects.filter(reader_id=reader_id).order_by('-wish_list_id')

        # Paginate the results
        paginator = WishListPagination()
        result_page = paginator.paginate_queryset(items, request)

        # Extract the book_ids from the wishlist items
        book_ids = [item.book_id for item in result_page]

        # Fetch the corresponding Book objects in the same order as book_ids
        books = Book.objects.filter(book_id__in=book_ids).order_by(
            Case(*[When(book_id=book_id, then=pos) for pos, book_id in enumerate(book_ids)], default=0)
        )

        # Serialize the Book objects
        serializer = BookSerializer(books, many=True)

        # Return the paginated response with serialized data
        return paginator.get_paginated_response(serializer.data)


#-- list notification (pagination achived)
class NotificationListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        reader_id = request.query_params.get('reader_id')
        if not reader_id:
            return Response({"error": "Reader ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the notifications for the given reader
        notifications = Notification.objects.filter(reader_id=reader_id).order_by('-notification_id')

        # Apply pagination
        paginator = NotificationPagination()
        result_page = paginator.paginate_queryset(notifications, request)

        # Extract the notification_record from each item
        notification_records = [item.notification_record for item in result_page]

        # Return the paginated response with notification records
        return paginator.get_paginated_response(notification_records)


#-- insert feedback
class InsertFeedbackView(APIView):
    def post(self, request):
        # Get the reader_id and feedback description from the request data
        reader_id = request.data.get('reader_id')
        feedback_description = request.data.get('feedback_description')

        if not reader_id or not feedback_description:
            return Response({"error": "Reader ID and feedback description are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new FeedBack record
        feedback = FeedBack.objects.create(reader_id=reader_id, feedback_description=feedback_description)

        # Serialize the feedback object
        serializer = FeedBackSerializer(feedback)

        # Return the serialized data as response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#-- list uploaded_book (pagination achived)
class UploadedBookListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        reader_id = request.query_params.get('reader_id')
        if not reader_id:
            return Response({"error": "Reader ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the wishlist items for the given reader, ordered by `wish_list_id`
        items = UploadedBook.objects.filter(reader_id=reader_id).order_by('-uploaded_book_id')

        # Paginate the results
        paginator = UploadedBookPagination()
        result_page = paginator.paginate_queryset(items, request)

        # Extract the book_ids from the wishlist items
        book_ids = [item.book_id for item in result_page]

        # Fetch the corresponding Book objects in the same order as book_ids
        books = Book.objects.filter(book_id__in=book_ids).order_by(
            Case(*[When(book_id=book_id, then=pos) for pos, book_id in enumerate(book_ids)], default=0)
        )

        # Serialize the Book objects
        serializer = BookSerializer(books, many=True)

        # Return the paginated response with serialized data
        return paginator.get_paginated_response(serializer.data)
    

class CreateBookView(APIView):
    def post(self, request):
        # Extract the data from the request body
        data = request.data

        # Serialize the data using a serializer
        serializer = BookSerializer(data=data)

        if serializer.is_valid():
            # Save the new book to the database
            serializer.save()
            return Response({"message": "Book created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
