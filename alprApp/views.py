from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Import alpr integration
from .alpr_integration import alpr_service

class ALPRProcessView(APIView):
    """
    Endpoint POST /api/v1/alpr/
    Aceita upload multipart com multiplas imagens 'images'.
    Retorna JSON com os textos detectados e informações detalhadas.
    """
    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')

        if not images:
            return Response({"[ERROR]": "Not found image."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            alpr_results = alpr_service.process_images(images)
            return Response({"results": alpr_results}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"[ERROR]": f"Process failed: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
