import json
import logging
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chatbot.serializers import ChatRequestSerializer
from chatbot.agents.supervisor import SupervisorAgent
from chatbot.services.mcp_client import ProjectMCPClient

logger = logging.getLogger(__name__)


class ChatAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        try:
            supervisor = SupervisorAgent()
            result = async_to_sync(supervisor.process)(
                payload.get("message", ""),
                payload.get("parameters", {}),
                payload.get("agent"),
            )
        except ValueError as exc:
            return Response(
                {"status": "validation_error", "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (RuntimeError, OSError, TimeoutError, ConnectionError, json.JSONDecodeError):
            logger.exception("MCP workflow failed")
            return Response(
                {"status": "error", "message": "MCP workflow unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(result)


class MCPCapabilitiesAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            client = ProjectMCPClient()
            result = async_to_sync(client.get_server_capabilities)()
        except (RuntimeError, OSError, TimeoutError, ConnectionError, json.JSONDecodeError):
            logger.exception("MCP capability discovery failed")
            return Response(
                {"status": "error", "message": "MCP server unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(result)

