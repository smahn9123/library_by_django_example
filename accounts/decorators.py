from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps  # wraps 데코레이터를 사용하여 데코레이터를 작성


# 뷰 함수를 인자로 받는 데코레이터 이뜻은 뷰 함수를 인자로 받아서 뷰 함수를 반환한다는 뜻
def librarian_required(view_func):
    """사서 권한 필요한 뷰의 데코레이터"""
    @wraps(view_func)  # wraps 데코레이터를 사용하여 데코레이터를 작성 즉, view_func 함수를 래핑하여 사용 -> 결국 view_func 함수를 반환
    def _wrapped_view(request, *args, **kwargs):  # 뷰 함수의 인자를 받아서 처리
        if not request.user.is_authenticated:  # 로그인이 되어 있지 않은 경우
            messages.error(request, '로그인이 필요합니다.')  # 에러 메시지 출력
            return redirect('accounts:login')  # 로그인 페이지로 이동

        if not request.user.is_librarian():  # 사서 권한이 없는 경우
            messages.error(request, '사서 권한이 필요합니다.')  # 에러 메시지 출력
            return redirect('accounts:profile')  # 프로필 페이지로 이동

        return view_func(request, *args, **kwargs)  # 뷰 함수 실행
    return _wrapped_view  # 래핑된 뷰 함수 반환
