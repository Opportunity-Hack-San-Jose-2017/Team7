# Setup virtual environment
rm -rf .tox
tox --recreate

echo "Created python env at CURRENT_DIR/.tox/py36"
echo "Do a 'source activate' in current directory to activate the venv"
