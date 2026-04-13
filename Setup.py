"""
🚀 Quick setup for Taskify Desktop App
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all dependencies"""
    requirements = [
        "nltk==3.8.1",
        "textblob==0.17.1", 
        "customtkinter==5.2.2",
        "darkdetect==0.2.0"
    ]
    
    for req in requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])

def setup_nltk():
    """Setup NLTK data"""
    import nltk
    nltk.download('vader_lexicon', quiet=True)

if __name__ == "__main__":
    print("🤖 Taskify App Setup")
    print("=" * 40)
    
    choice = input("1. Install requirements\n2. Setup NLTK only\n3. Full setup\nChoose (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        install_requirements()
    
    if choice in ['2', '3']:
        setup_nltk()
    
    print("\n🚀 Ready! Run: python Taskify.py")