# alpr_api/views.py
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
                    'description': "Envie um ou mais arquivos usando a mesma chave 'images'."
                }
            },
            'required': ['images']
        }
    },
    responses={200: {'type': 'object'}},
    description="POST multipart/form-data com a chave 'images' (pode repetir para enviar várias)."
)
class ALPRProcessView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': "Envie arquivos na chave 'images'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            results = alpr_service.process_images(images)
            return Response({'results': results}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'No results': ""}, status=status.HTTP_200_OK)