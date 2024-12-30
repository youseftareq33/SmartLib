from django.shortcuts import redirect, render

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

#--------
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
from django.db.utils import IntegrityError

#----------
from django.contrib.auth.tokens import default_token_generator 
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.contrib import messages

# notes:- guest page_contactUs, regiseration process, book_favourite_counter manual !!!, insert book, copy url confirm register page

#-- redirect page --

def guestPage(request):
    return render(request, '1_1_guestHome_page.html')

def aboutUsPage(request):
    return render(request, '1_2_aboutUs_page.html')

def privacyPolicyPage(request):
    return render(request, '1_3_privacyPolicy_page.html')

def loginPage(request):
    return render(request, '2_login_page.html')

def registerPage(request):
    return render(request, '3_register_page.html')

def confirm_email_register(request):
    email = request.GET.get('email', '')  # Retrieve email from query parameters
    return render(request, '4_1_confirm_email_register_page.html', {'email': email})

def findAccountPage(request):
    return render(request, '5_1_find_account_forgetPass_page.html')

def confirm_email_change_password(request):
    email = request.GET.get('email', '')  # Retrieve email from query parameters
    return render(request, '5_2_confirm_email_forgetPass_page.html', {'email': email})

def resetPasswordPage(request, email):
    return render(request, '5_4_reset_password_page.html', {'email': email})

def homePage(request):
    return render(request, '6_home_page.html')

def RankPage(request):
    return render(request, '7_gamefication_page.html')

def WishListPage(request):
    return render(request, '8_wishlist_page.html')

def NotificationPage(request):
    return render(request, '9_notification_page.html')

def MyUploadedBookPage(request):
    return render(request, '10_myUploadedBook_page.html')
#--------------------------------------------------------------------------------------------


#-- login --


class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user_password = request.data.get('user_password')


        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)
            
            # Verify the password using bcrypt
            if not bcrypt.checkpw(user_password.encode('utf-8'), user.user_password.encode('utf-8')):
                raise AuthenticationFailed("Incorrect password!", status=status.HTTP_401_UNAUTHORIZED)
            else:
                if user.is_active:
                    payload = {
                        'id': user.user_id,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=180), # 3 hours
                        'iat': datetime.datetime.utcnow()
                    }

                    token = jwt.encode(payload, 'secret', algorithm='HS256')

                    return Response({'jwt': token}, status=status.HTTP_200_OK)
                else:
                    raise AuthenticationFailed("Your account has not activated yet.", status=status.HTTP_401_UNAUTHORIZED)
                    
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found or incorrect password!", status=status.HTTP_401_UNAUTHORIZED)
#--------------------------------------------------------------------------------------------


#-- register--


class RegisterAPIView(APIView):
    def post(self, request):

        try:
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

            send_verification_email_register(user=user,request=request)

            return Response(
                {
                'message': 'User registered successfully. Please check your email to verify your account.',
                'email': email
                }, status=status.HTTP_200_OK)
        
        except IntegrityError as e:
            if 'unique constraint' in str(e):
                return Response({'error': 'This email address is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#--------------------------------------------------------------------------------------------


#-- register confirmation process --


class ExpiringTokenGenerator_register(PasswordResetTokenGenerator):
    def make_token(self, user):
        """
        Override the default method to include an expiration time (30 minute).
        """
        timestamp = str(int(timezone.now().timestamp()))  # Current timestamp
        expiration_time = (timezone.now() + datetime.timedelta(minutes=30)).timestamp()  # Token expires in 30 minute
        return f"{super().make_token(user)}-{int(expiration_time)}"  # Append expiration time to token

    def check_token(self, user, token):
        """
        Override the default method to check if the token has expired.
        """
        try:
            base_token, expiration_time = token.rsplit('-', 1)
            expiration_time = float(expiration_time)
            if timezone.now().timestamp() > expiration_time:
                return False  # Token is expired
            return super().check_token(user, base_token)
        except (ValueError, IndexError):
            return False  # Invalid token format

token_generator_register = ExpiringTokenGenerator_register()

# send email for register
def send_verification_email_register(user, request):
    
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator_register.make_token(user)  # Use the custom token generator

    mail_subject = 'Activate your account.'
    message = render_to_string('4_2_email_templet_register.html', {
        'user': user,
        'domain': request.get_host(),
        'uid': uid,
        'token': token,
        'user_name': user.user_name,
    })

    email_message = EmailMultiAlternatives(
        mail_subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email_message.attach_alternative(message, "text/html")
    email_message.send()


def send_another_email(request, email):
    try:
        user = User.objects.get(email=email)
        send_verification_email_register(user, request)
        return JsonResponse({'message': 'Verification email sent successfully.'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User with the provided email does not exist.'}, status=404)

    
class activate_register(APIView):
    def get(self, request, uidb64, token):
        try:
            # Decode user ID from the token
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid activation link.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid and not expired
        if token_generator_register.check_token(user, token) and not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been activated successfully.')
            return redirect('loginPage')  # This should return a redirect response
        elif user.is_active:
            messages.info(request, 'Your account is already activated.')
            return redirect('loginPage')  # This should return a redirect response
        else: ####################### change
            messages.error(request, 'Activation link is invalid or expired.')
            return redirect('loginPage')  # This should return a redirect response
#--------------------------------------------------------------------------------------------


#-- forget password process --


class EmailExistView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)
            return Response({"exists": True, "message": "Email is found."}, status=status.HTTP_200_OK)       
        except User.DoesNotExist:
            return Response({"exists": False, "message": "Email not found."}, status=status.HTTP_404_NOT_FOUND)


class ExpiringTokenGenerator_forget_pass(PasswordResetTokenGenerator):
    def make_token(self, user):
        """
        Override the default method to include an expiration time (30 minute).
        """
        timestamp = str(int(timezone.now().timestamp()))  # Current timestamp
        expiration_time = (timezone.now() + datetime.timedelta(minutes=30)).timestamp()  # Token expires in 30 minute
        return f"{super().make_token(user)}-{int(expiration_time)}"  # Append expiration time to token

    def check_token(self, user, token):
        """
        Override the default method to check if the token has expired.
        """
        try:
            base_token, expiration_time = token.rsplit('-', 1)
            expiration_time = float(expiration_time)
            if timezone.now().timestamp() > expiration_time:
                return False  # Token is expired
            return super().check_token(user, base_token)
        except (ValueError, IndexError):
            return False  # Invalid token format

token_generator_forget_pass = ExpiringTokenGenerator_forget_pass()

# send email for change password
def send_verification_email_forget_pass(user, request):
    
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator_forget_pass.make_token(user)  # Use the custom token generator

    mail_subject = 'Change Account Password.'
    message = render_to_string('5_3_email_templet_forgetPass.html', {
        'user': user,
        'domain': request.get_host(),
        'uid': uid,
        'token': token,
        'user_name': user.user_name,
    })

    email_message = EmailMultiAlternatives(
        mail_subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email_message.attach_alternative(message, "text/html")
    email_message.send()


def send_another_email_change_pass(request, email):
    try:
        user = User.objects.get(email=email)
        send_verification_email_forget_pass(user, request)
        return JsonResponse({'message': 'Verification email sent successfully.'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User with the provided email does not exist.'}, status=404)

class activate_change_password(APIView):
    def get(self, request, uidb64, token):
        try:
            # Decode user ID from the token
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            email = user.email
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid activation link.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid and not expired
        if token_generator_forget_pass.check_token(user, token):
            return redirect('resetPasswordPage',email)  # This should return a redirect response
        else: ####################### change
            messages.error(request, 'Activation link is invalid or expired.')
            return redirect('loginPage')  # This should return a redirect response  

class reset_password(APIView):
    def post(self, request):
        email = request.data.get('email')
        user_password=request.data.get('user_password')

        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)

            # Hash the password using bcrypt and verify hashing
            hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

            user.user_password = hashed_password
            user.save()
            messages.success(request, 'Your account has reset password successfully.')
            return redirect('loginPage')      
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
#--------------------------------------------------------------------------------------------


#-- list category
class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------------------------

#-- get name from id
class UserNameListView(APIView):
    def get(self, request, user_id):
        try:
            # Fetch the user by ID
            user = User.objects.get(user_id=user_id)
            # Return the user_name
            return Response({"user_name": user.user_name}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#--------------------------------------------------------------------------------------------

#-- get reader
class ReaderInfoListView(APIView):
    def get(self, request):

        user_id = request.query_params.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
            serializer = ReaderSerializer(reader)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)
        
#--------------------------------------------------------------------------------------------

#-- list book (pagination achived)
class BookListView(APIView):
    def get(self, request):
        books = Book.objects.all()  
        paginator = BookPagination()  
        result_page = paginator.paginate_queryset(books, request)  
        serializer = BookSerializer(result_page, many=True)  
        return paginator.get_paginated_response(serializer.data)
    
#--------------------------------------------------------------------------------------------

#-- list most readed book (pagination achived)
class MostReaded_BookListView(APIView):
    def get(self, request):
        books = Book.objects.filter(status=Book.Status.ACCEPTED).order_by('-book_reading_counter')
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

#-- list last uploaded book (pagination achived)
class LastUploaded_BookListView(APIView):
    def get(self, request):
        books = Book.objects.filter(status=Book.Status.ACCEPTED).order_by('-book_uploaded_date')
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
#--------------------------------------------------------------------------------------------

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
    
#--------------------------------------------------------------------------------------------

#-- list Most Rating book (pagination achived)
class MostRating_BookListView(APIView):
    def get(self, request):
        books = Book.objects.filter(status=Book.Status.ACCEPTED).order_by('-book_rating_avg')
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
#--------------------------------------------------------------------------------------------

#-- list searched book
class BookSearchView(APIView):
    def get(self, request):
        # Get parameters from the request
        search_query = request.query_params.get('search', '').strip()
        sort_by = request.query_params.get('sort_by', '')
        category_ids = request.query_params.get('category', None)
        min_rating = request.query_params.get('min_rating', None)

        # Base queryset, only filter if search query is provided
        books = Book.objects.filter(status=Book.Status.ACCEPTED)
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

class MostReadedPreferences_BookListView(APIView):
    def get(self, request):
        # Get the user_id directly from the query parameters
        user_id = request.query_params.get('user_id')
        
        # Get categories from user preferences based on user_id
        user_preferences = Preferences.objects.filter(reader__user__user_id=user_id).values_list('category', flat=True)
        
        # Filter books based on the user's preferred categories
        books = Book.objects.filter(category__in=user_preferences, status=Book.Status.ACCEPTED).order_by('-book_reading_counter')
        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
#--------------------------------------------------------------------------------------------

class MostRatingPreferences_BookListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get categories from user preferences based on user_id
        user_preferences = Preferences.objects.filter(reader__user__user_id=user_id).values_list('category', flat=True)
        
        # Filter books based on the user's preferred categories and order by rating
        books = Book.objects.filter(category__in=user_preferences, status=Book.Status.ACCEPTED).order_by('-book_rating_avg')
        
        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

class LastUploadedPreferences_BookListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get categories from user preferences based on user_id
        user_preferences = Preferences.objects.filter(reader__user__user_id=user_id).values_list('category', flat=True)
        
        # Filter books based on the user's preferred categories and order by upload date
        books = Book.objects.filter(category__in=user_preferences, status=Book.Status.ACCEPTED).order_by('-book_uploaded_date')
        
        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

#-- list continue reading book (pagination achived)
class BookContinueReadingListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter books in the BookContinueReading table for the specified user and order in reverse
        continue_reading_books = Book.objects.filter(bookcontinuereading__reader__user__user_id=user_id, status=Book.Status.ACCEPTED).order_by('-bookcontinuereading__continue_reading_id')

        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(continue_reading_books, request)
        serializer = BookSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    
#--------------------------------------------------------------------------------------------

class LastThreeWishListView(APIView):
    def get(self, request):

        user_id = request.query_params.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the last three wishlist items for the given reader, ordered by `wish_list_id`
        last_three_items = WishList.objects.filter(reader_id=reader.reader_id).order_by('-wish_list_id')[:3]
        
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
    
    
#--------------------------------------------------------------------------------------------

class LastThreeNotificationListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters

        user_id = request.query_params.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Get the last three notifications for the given reader, ordered by `notification_id`
        last_three_items = Notification.objects.filter(reader_id=reader.reader_id).order_by('-notification_id')[:3]
        
        # Serialize the Book objects
        serializer = NotificationListSerializer(last_three_items, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


#--------------------------------------------------------------------------------------------

#-- list wishlist (pagination achived)
class WishListListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        user_id = request.query_params.get('user_id')

        # Validate book_id and user_id
        if not user_id:
            return Response({"error": "User ID not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the wishlist items for the given reader, ordered by `wish_list_id`
        items = WishList.objects.filter(reader_id=reader.reader_id).order_by('-wish_list_id')

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
    
#--------------------------------------------------------------------------------------------

class AddBookToWishlist(APIView):
    def post(self, request):
        # Retrieve book_id and user_id from the request body
        book_id = request.data.get('book_id')
        user_id = request.data.get('user_id')

        # Validate book_id and user_id
        if not book_id or not user_id:
            return Response({"error": "Book ID and User ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate the book existence
        try:
            book = Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the book is already in the wishlist
        if WishList.objects.filter(book=book, reader=reader).exists():
            return Response({"error": "Book already in wishlist"}, status=status.HTTP_400_BAD_REQUEST)

        # Add the book to the wishlist
        WishList.objects.create(book=book, reader=reader)

        # Increment the book's favorite counter
        book.book_favourite_counter = (book.book_favourite_counter or 0) + 1
        book.save(update_fields=['book_favourite_counter'])

        return Response(
            {"message": "Book added to wishlist", "book_favourite_counter": book.book_favourite_counter},
            status=status.HTTP_201_CREATED
        )



#--------------------------------------------------------------------------------------------
   
class RemoveBookFromWishlist(APIView):
    def post(self, request):
        book_id = request.data.get('book_id')
        user_id = request.data.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the book from the wishlist
        try:
            wishlist_item = WishList.objects.get(book_id=book_id, reader_id=reader.reader_id)
            wishlist_item.delete()

            # Optionally, decrement the book's favourite counter here
            book = Book.objects.get(book_id=book_id)
            book.book_favourite_counter -= 1
            book.save()

            return Response({"message": "Book removed from wishlist"}, status=status.HTTP_200_OK)
        except WishList.DoesNotExist:
            return Response({"error": "Book not in wishlist"}, status=status.HTTP_400_BAD_REQUEST)
        
#--------------------------------------------------------------------------------------------
class CheckBookInWishlist(APIView):
    def get(self, request):
        book_id = request.query_params.get('book_id')
        user_id = request.query_params.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the book is in the wishlist
        if WishList.objects.filter(book_id=book_id, reader_id=reader.reader_id).exists():
            return Response({"in_wishlist": True}, status=status.HTTP_200_OK)
        else:
            return Response({"in_wishlist": False}, status=status.HTTP_200_OK)


#--------------------------------------------------------------------------------------------

#-- list notification (pagination achived)
class NotificationListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        user_id = request.query_params.get('user_id')

        # Validate book_id and user_id
        if not user_id:
            return Response({"error": "User ID not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the notifications for the given reader
        notifications = Notification.objects.filter(reader_id=reader.reader_id).order_by('-notification_id')

        # Apply pagination
        paginator = NotificationPagination()
        result_page = paginator.paginate_queryset(notifications, request)

        serializer = NotificationListSerializer(result_page, many=True)

        # Return the paginated response with serialized data
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

#-- insert feedback
class InsertFeedbackView(APIView):
    def post(self, request):
        # Get the reader_id and feedback description from the request data
        user_id = request.data.get('user_id')
        feedback_description = request.data.get('feedback_description')

        if not user_id or not feedback_description:
            return Response({"error": "User ID and feedback description are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new FeedBack record
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)
        
        feedback = FeedBack.objects.create(reader_id=reader.reader_id, feedback_description=feedback_description)

        # Serialize the feedback object
        serializer = FeedBackSerializer(feedback)

        # Return the serialized data as response
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#--------------------------------------------------------------------------------------------
  
#-- list uploaded_book (pagination achived)
class UploadedBookListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        user_id = request.query_params.get('user_id')

        # Validate book_id and user_id
        if not user_id:
            return Response({"error": "User ID not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the wishlist items for the given reader, ordered by `wish_list_id`
        items = UploadedBook.objects.filter(reader_id=reader.reader_id).order_by('-uploaded_book_id')

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
    
#--------------------------------------------------------------------------------------------
#-- remove uploaded_book (pagination achived)

class RemoveUploadedBookView(APIView):
    def delete(self, request):
        # Get the book_id and user_id from query parameters
        book_id = request.query_params.get('book_id')
        user_id = request.query_params.get('user_id')

        # Validate book_id and user_id
        if not book_id or not user_id:
            return Response({"error": "Both book_id and user_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Try to find the UploadedBook record
        try:
            uploaded_book = UploadedBook.objects.get(book_id=book_id, reader_id=reader.reader_id)
            book=Book.objects.get(book_id=book_id)

        except UploadedBook.DoesNotExist:
            return Response({"error": "UploadedBook record not found"}, status=status.HTTP_404_NOT_FOUND)

        # Delete the record
        uploaded_book.delete()
        book.delete()

        # Return a success response
        return Response({"message": "Book successfully removed from uploaded books"}, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------------------------
#-- list uploaded_book (pagination achived)
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
    

#--------------------------------------------------------------------------------------------

#-- gamefication record (pagination achived)
class GamificationRecordListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Filter records for the specified user and order by date_and_time (most recent first)
        gamification_records = Gamification_Record.objects.filter(reader_id=reader.reader_id).order_by('-date_and_time')

        # Apply pagination
        paginator = GameficationPagination()
        result_page = paginator.paginate_queryset(gamification_records, request)
        serializer = GameficationSerializer(result_page, many=True)  # Use the correct serializer here

        return paginator.get_paginated_response(serializer.data)
        

