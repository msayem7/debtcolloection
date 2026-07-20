from django.http import JsonResponse
from .models import Branch, SystemConfig


class BranchCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method == 'POST' and request.path.endswith('/v1/chq/branches/'):
            max_branches = SystemConfig.get_int('MAX_BRANCH_COUNT', 0)
            if max_branches > 0:
                current_count = Branch.objects.count()
                if current_count >= max_branches:
                    return JsonResponse(
                        {'error': {
                            'code': 400,
                            'message': 'System has reached its maximum branch opening capacity. Please contact the administrator.'
                        }},
                        status=400
                    )
        return None