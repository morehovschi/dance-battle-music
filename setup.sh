#!/bin/bash

pip install playwright==1.50.0
playwright install chromium
pip install -U "yt-dlp[default]"
pip install jupyter
pip install numpy==2.1.3
pip install pandas==2.2.3
pip install librosa==0.11.0
pip install tensorflow
# Uncomment the below if installing with CUDA support
# python3 -m pip install tensorflow[and-cuda]
pip install librosa
pip install tqdm

# Clone the neural-audio-fp repository
git clone https://github.com/mimbres/neural-audio-fp.git lib/neural-audio-fp

# Create an __init__.py file in the repository to make it importable
touch lib/neural-audio-fp/__init__.py

# Install neural-audio-fp requirements
if [ -f neural-audio-fp/requirements.txt ]; then
    echo "Installing neural-audio-fp requirements..."
    pip install -r neural-audio-fp/requirements.txt
fi

# Create a simple PYTHONPATH helper script
cat > set_path.sh << 'EOF'
#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/lib
echo "PYTHONPATH set to include $(pwd)/lib"
EOF

chmod +x set_path.sh
echo "Setup complete! Before running your scripts, execute:"
echo "source ./set_path.sh"