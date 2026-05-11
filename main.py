import sys
import os

# Ensure the src directory is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app_config import APP_TITLE
from src.gui import AuraApp

if __name__ == "__main__":
    print(f"Starting {APP_TITLE}")
    app = AuraApp()
    app.mainloop()
