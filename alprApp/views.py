from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from .alpr_integration import alpr_service

@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                # use a key única 'images' e permita múltiplos arquivos repetindo a mesma key
                'images': {
                    'type': 'array',
                    'items': {'type': 'string', 'format': 'binary'},
                    'description': "Send one or more files using the same key 'images'."
                }
            },
            'required': ['images']
        }
    },
    responses={200: {'type': 'object'}},
    description="POST multipart/form-data with key 'images' and one or more files",
)

class ALPRProcessView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': "Send archive with key 'images'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            results = alpr_service.process_images(images)
            return Response({'results': results}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'No results': ""}, status=status.HTTP_200_OK)
        
