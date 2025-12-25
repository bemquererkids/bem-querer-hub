import sys
import os

# Adiciona a pasta root e a pasta backend ao path para encontrar os módulos
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
sys.path.append(os.path.join(base_path, 'backend'))

from app.main import app

# Export app directly for Vercel
# Vercel's Python runtime will handle it correctly