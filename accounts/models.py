from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# Create your models here.


class User(AbstractUser):
    """
    사용자 모델: AbstractUser를 상속받아 기본 인증 시스템 활용
    기본 필드: username, password, email, first_name, last_name, is_staff, is_active, date_joined
    """
    ROLE_CHOICES = [
        ('LIBRARIAN', '사서'),
        ('USER', '일반 사용자'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='USER',
        verbose_name='역할'
    )
    phone = models.CharField(
        max_length=11,
        blank=True,
        verbose_name='전화번호'
    )

    def is_librarian(self):
        """사서 여부 확인"""
        return self.role == 'LIBRARIAN'

    def can_borrow(self):
        """대출 가능 여부 확인"""
        from books.models import Loan  # 순환 참조 방지를 위해 지역 import
        active_loans = Loan.objects.filter(
            user=self,
            status='ACTIVE'
        ).count()
        return active_loans < 3

    def has_overdue_books(self):
        """연체 도서 여부 확인"""
        from books.models import Loan
        return Loan.objects.filter(
            user=self,
            status='ACTIVE',
            due_date__lt=timezone.now()
        ).exists()

    def get_active_loans(self):
        """현재 대출 중인 도서 목록"""
        return self.loan_set.filter(status='ACTIVE')

    def get_active_reservations(self):
        """현재 예약 중인 도서 목록"""
        return self.reservation_set.filter(status='WAITING')

    class Meta:  # Meta 클래스를 통해 모델의 메타데이터(옵션) 설정
        verbose_name = '사용자'  # verbose_name 필드는 단수형 이름
        verbose_name_plural = '사용자 목록'  # verbose_name_plural 필드는 복수형 이름
