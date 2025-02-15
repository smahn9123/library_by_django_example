from django import forms 
from .models import Book, Loan, Reservation

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'publisher', 'total_quantity']
        
        # 각 필드별 위젯 설정
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '도서명을 입력하세요'
                }
            ),
            'author': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '저자명을 입력하세요'
                }
            ),
            'isbn': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ISBN을 입력하세요'
                }
            ),
            'publisher': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '출판사명을 입력하세요'
                }
            ),
            'total_quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',  # 최소값 설정
                }
            )
        }
        
        # 각 필드별 레이블 설정
        labels = {
            'title': '도서명',
            'author': '저자',
            'isbn': 'ISBN',
            'publisher': '출판사',
            'total_quantity': '총 수량'
        }
        
        # 각 필드별 도움말 설정
        help_texts = {
            'isbn': 'ISBN 13자리를 입력하세요',
            'total_quantity': '최소 1권 이상 입력하세요'
        }
    
    def clean_isbn(self):
        """ISBN 유효성 검사"""
        isbn = self.cleaned_data.get('isbn')
        if len(isbn) != 13:  # ISBN은 13자리여야 함
            raise forms.ValidationError('ISBN은 13자리여야 합니다.')
            
        # ISBN이 이미 존재하는지 확인 (수정 시에는 자기 자신은 제외)
        exists = Book.objects.filter(isbn=isbn)
        if self.instance:  # 수정 시
            exists = exists.exclude(pk=self.instance.pk)
        if exists.exists():
            raise forms.ValidationError('이미 등록된 ISBN입니다.')
            
        return isbn
    
    def clean_total_quantity(self):
        """수량 유효성 검사"""
        quantity = self.cleaned_data.get('total_quantity')
        if quantity < 1:  # 최소 1권
            raise forms.ValidationError('수량은 1권 이상이어야 합니다.')
        return quantity
    
    def save(self, commit=True):
        """저장 시 available_quantity도 함께 설정"""
        instance = super().save(commit=False)
        if not self.instance.pk:  # 새로운 도서 등록 시
            instance.available_quantity = instance.total_quantity
        elif instance.total_quantity < self.instance.available_quantity:  # 수정 시 총 수량을 줄이는 경우
            instance.available_quantity = instance.total_quantity
        if commit:
            instance.save()
        return instance
    
class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = []  # user와 book은 view에서 처리할 것이므로 비워둡니다.

    def clean(self):
        cleaned_data = super().clean() # 기존 clean 메서드를 실행합니다.
        user = self.user  # view에서 전달받은 user 
        book = self.book  # view에서 전달받은 book

        # 대출 가능 여부 검증
        if not user.can_borrow():
            raise forms.ValidationError('최대 대출 가능 권수(3권)를 초과했습니다.')
        
        if user.has_overdue_books():
            raise forms.ValidationError('연체된 도서가 있어 대출이 불가능합니다.')
            
        if not book.is_available():
            raise forms.ValidationError('현재 대출 가능한 도서가 없습니다.')
        
        return cleaned_data # cleaned_data를 반환합니다.

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) # user를 kwargs에서 추출합니다.
        self.book = kwargs.pop('book', None) # book을 kwargs에서 추출합니다.
        super().__init__(*args, **kwargs)   # 기존 __init__ 메서드를 실행합니다.

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = []  # user와 book은 view에서 처리

    def clean(self):
        cleaned_data = super().clean()
        user = self.user
        book = self.book

        # 이미 동일한 도서에 대한 예약이 있는지 확인
        existing_reservation = Reservation.objects.filter(
            user=user,
            book=book,
            status='WAITING'
        ).exists()
        
        if existing_reservation:
            raise forms.ValidationError('이미 예약한 도서입니다.')
        
        # 현재 대출 가능한 도서가 있는 경우 예약 불가
        if book.is_available():
            raise forms.ValidationError('현재 대출 가능한 도서가 있어 예약할 수 없습니다.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.book = kwargs.pop('book', None)
        super().__init__(*args, **kwargs)
