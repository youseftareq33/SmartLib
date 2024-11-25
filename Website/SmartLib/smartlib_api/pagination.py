from rest_framework.pagination import PageNumberPagination

class BookPagination(PageNumberPagination):
    page_size = 5  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size

class WishListPagination(PageNumberPagination):
    page_size = 12  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size

class NotificationPagination(PageNumberPagination):
    page_size = 12  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size

class UploadedBookPagination(PageNumberPagination):
    page_size = 12  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size