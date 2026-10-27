from django.urls import path
from chatbot.views import ChatAPIView, MCPCapabilitiesAPIView

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat-api'),
    path('mcp/capabilities/', MCPCapabilitiesAPIView.as_view(), name='mcp-capabilities'),
]