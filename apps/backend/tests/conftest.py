import sys
from unittest.mock import MagicMock

# Mock WeasyPrint before any FastAPI routers try to import it
sys.modules['weasyprint'] = MagicMock()

# If any specific components from weasyprint are imported directly, mock them too
mock_html = MagicMock()
sys.modules['weasyprint.HTML'] = mock_html
sys.modules['weasyprint.css'] = MagicMock()