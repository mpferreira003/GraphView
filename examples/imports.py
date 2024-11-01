import sys
import os

# Adiciona o diretório pai ao sys.path
def imports():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))