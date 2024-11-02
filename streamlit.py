# Import required packages
!pip install streamlit pyngrok -q
from pyngrok import ngrok
import time

# First, kill all existing tunnels
ngrok.kill()

# Kill any existing Streamlit processes
!kill -9 $(ps -ef | grep streamlit | grep -v grep | awk '{print $2}') 2>/dev/null

# Set your authtoken (only need to do this once)
# !ngrok authtoken 2oHY6OLpYCTVoyHZ18ThmbaHq9q_6M1bt4AyRfRohecVrUZHg
!ngrok authtoken 2oIBBvjscDOs6ZPInY3yxYzhlcV_6iyb26a2wsXhVCqPKrA4U

# Start Streamlit
!nohup streamlit run app.py --server.port 8501 &

# Wait for Streamlit to start
time.sleep(3)

# Create a new tunnel
try:
    tunnel = ngrok.connect(8501)
    print(f"Your Streamlit app is available at: {tunnel.public_url}")
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying alternative approach...")
    !pkill -f streamlit
    !pkill -f ngrok
    time.sleep(2)
    !streamlit run app.py & ngrok http 8501
