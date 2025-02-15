from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
 
class Book(models.Model):
   """
   도서 정보를 저장하는 모델
   """
   title = models.CharField(
       max_length=200, 
       verbose_name='도서명'
   )
   author = models.CharField(
       max_length=100, 
       verbose_name='저자'
   )
   isbn = models.CharField(
       max_length=13,
       unique=True,
       verbose_name='ISBN'
   )
   publisher = models.CharField(
       max_length=100, 
       verbose_name='출판사'
   )
   total_quantity = models.PositiveIntegerField( # PositiveIntegerField: 양수만 저장
       default=1,
       verbose_name='전체 수량'
   )
   available_quantity = models.PositiveIntegerField(
       default=1,
       verbose_name='대출 가능 수량'
   )
   created_at = models.DateTimeField(
       auto_now_add=True, # 생성 시간 자동 기록
       verbose_name='등록일'
   )
   updated_at = models.DateTimeField(
       auto_now=True, # 수정 시간 자동 기록
       verbose_name='수정일'
   )
 
   class Meta:
       verbose_name = '도서'
       verbose_name_plural = '도서 목록'
       ordering = ['-created_at'] # 기본 정렬 순서
 
   def __str__(self): # 객체를 문자열로 표현하는 메서드
       return self.title # 도서명으로 표현
 
   def is_available(self):
       """대출 가능 여부 확인"""
       return self.available_quantity > 0 # 대출 가능 수량이 0보다 크면 True 반환
   
   def decrease_quantity(self):
       """대출 시 수량 감소"""
       if self.is_available():
           self.available_quantity -= 1
           self.save()
           return True
       return False
 
   def increase_quantity(self):
       """반납 시 수량 증가"""
       if self.available_quantity < self.total_quantity:
           self.available_quantity += 1
           self.save()
           return True
       return False   
   
 
# ... 위 코드 계속
 
class Loan(models.Model):
   """
   도서 대출 정보를 저장하는 모델
   """
   STATUS_CHOICES = [
       ('ACTIVE', '대출중'),
       ('OVERDUE', '연체'),
       ('RETURNED', '반납완료'),
   ]
 
   user = models.ForeignKey( # ForeignKey: 다른 모델과의 관계 설정
       settings.AUTH_USER_MODEL, # settings.py에 지정한 사용자 모델
       on_delete=models.CASCADE, # 연결된 사용자가 삭제되면 대출 정보도 삭제
       verbose_name='사용자' 
   )
   book = models.ForeignKey(
       Book,
       on_delete=models.CASCADE,
       verbose_name='도서'
   )
   status = models.CharField(
       max_length=10,
       choices=STATUS_CHOICES,
       default='ACTIVE',
       verbose_name='상태'
   )
   loan_date = models.DateTimeField(
       auto_now_add=True,
       verbose_name='대출일'
   )
   due_date = models.DateTimeField(
       verbose_name='반납예정일'
   )
   returned_date = models.DateTimeField(
       null=True,
       blank=True,
       verbose_name='반납일'
   )
 
   class Meta:
       verbose_name = '대출'
       verbose_name_plural = '대출 목록'
       ordering = ['-loan_date'] # 최신 대출 순으로 정렬
 
   def __str__(self):
       return f"{self.user.username} - {self.book.title}"
 
   def is_overdue(self):
       """연체 여부 확인"""
       from django.utils import timezone
       return self.status == 'ACTIVE' and timezone.now() > self.due_date # 대출중이고 반납예정일이 지났으면 True 반환
   
class Reservation(models.Model):
   """
   도서 예약 정보를 저장하는 모델
   """
   STATUS_CHOICES = [
       ('WAITING', '대기중'),
       ('AVAILABLE', '대출가능'),
       ('CANCELLED', '취소됨'),
   ]
 
   user = models.ForeignKey(
       settings.AUTH_USER_MODEL,
       on_delete=models.CASCADE,
       verbose_name='사용자'
   )
   book = models.ForeignKey(
       Book,
       on_delete=models.CASCADE,
       verbose_name='도서'
   )
   status = models.CharField(
       max_length=10,
       choices=STATUS_CHOICES,
       default='WAITING',
       verbose_name='상태'
   )
   reserved_date = models.DateTimeField(
       auto_now_add=True,
       verbose_name='예약일'
   )
   expiry_date = models.DateTimeField(
       verbose_name='예약만료일'
   )
 
   class Meta:
       verbose_name = '예약'
       verbose_name_plural = '예약 목록'
       ordering = ['reserved_date'] # 예약일 순으로 정렬
       # 한 사용자가 같은 도서를 중복 예약할 수 없도록 제약
       unique_together = ['user', 'book', 'status'] # 사용자, 도서, 상태가 같은 경우 중복 예약 방지
 
   def __str__(self):
       return f"{self.user.username} - {self.book.title}"
 
   def is_expired(self):
       """예약 만료 여부 확인"""
       from django.utils import timezone
       return timezone.now() > self.expiry_date # 예약 만료일이 지났으면 True 반환