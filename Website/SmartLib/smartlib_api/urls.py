from django.urls import path
from .views import *


urlpatterns = [
    path('login',UserLoginView.as_view()),
    path('register',RegisterAPIView.as_view()),
    path('getAllCategories/', CategoryListView.as_view()),
    path('getAllBooks/', BookListView.as_view()),
    path('getMostReadedBook/', MostReaded_BookListView.as_view()),
    path('getMostRatingBook/', MostRating_BookListView.as_view()),
    path('getLastUploadedBook/', LastUploaded_BookListView.as_view()),
    path('insertRatingAndReview/', AddRatingAndReviewView.as_view()),
    path('search/', BookSearchView.as_view()),
    path('getMostReadedPreferencesBook/', MostReadedPreferences_BookListView.as_view()),
    path('getMostRatingPreferencesBook/', MostRatingPreferences_BookListView.as_view()),
    path('getLastPreferencesUploadedBook/', LastUploadedPreferences_BookListView.as_view()),
    path('getContinue-reading-books/', BookContinueReadingListView.as_view()),
    path('getLastThreeWishListView/', LastThreeWishListView.as_view()),
    path('getLastThreeNotificationListView/', LastThreeNotificationListView.as_view()),
    path('getWishList_ListView/', WishListListView.as_view()),
    path('getNotificationListView/', NotificationListView.as_view()),
    path('InsertFeedbackView/', InsertFeedbackView.as_view()),
    path('getUploadedBookListView/', UploadedBookListView.as_view()),
    path('insertBook/', CreateBookView.as_view()),
]
