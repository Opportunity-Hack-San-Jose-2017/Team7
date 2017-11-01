"""
Main entry
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
from platobot.api.app import create_app
from platobot.config import DevConfig, ProdConfig

if __name__ == '__main__':
    if os.environ.get('WORK_ENV') == 'PROD':
        app = create_app(ProdConfig)
        app.run(port=5000, host="0.0.0.0", use_reloader=False)
    else:
        app = create_app(DevConfig)
        app.run(port=5000, host="0.0.0.0", use_reloader=True, debug=True)
