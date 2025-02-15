# books/urls.py
from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # 도서 관련
    path('', views.book_list, name='book-list'),
    path('<int:pk>/', views.book_detail, name='book-detail'),
    path('create/', views.book_create, name='book-create'),
    path('<int:pk>/update/', views.book_update, name='book-update'),
    path('<int:pk>/delete/', views.book_delete, name='book-delete'),

    # 대출 관련
    path('loans/', views.loan_list, name='loan-list'),
    # path('loans/user/', views.user_loan_list, name='user-loan-list'),
    path('loans/create/<int:book_id>/', views.loan_create, name='loan-create'),
    path('loans/return/<int:loan_id>/', views.loan_return, name='loan-return'),
    path('loans/overdue/', views.loan_overdue_list, name='loan-overdue'),

    # 예약 관련
    path('reservations/', views.reservation_list, name='reservation-list'),
    # path('reservations/user/', views.user_reservation_list, name='user-reservation-list'),
    path('reservations/create/<int:book_id>/',
         views.reservation_create, name='reservation-create'),
    path('reservations/cancel/<int:reservation_id>/',
         views.reservation_cancel, name='reservation-cancel'),

    # API 엔드포인트 (선택 사항)
    #     path('search/', views.book_search, name='book-search'),
    #     path('status/<int:book_id>/', views.book_status, name='book-status'),
    #     path('loans/status/<int:loan_id>/', views.loan_status, name='loan-status'),
    #
]
