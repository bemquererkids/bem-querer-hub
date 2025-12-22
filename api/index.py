import sys
import os

# Adiciona a pasta atual e a pasta backend ao path para encontrar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.main import app