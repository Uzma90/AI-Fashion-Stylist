# 🚀 Quick Installation Guide

## Option 1: Simple Version (No Dependencies Required)

This version works with just Python standard library - no need to install anything extra!

1. **Run the simple version**:
   ```bash
   python simple_app.py
   ```

2. **Open your browser** and go to: `http://localhost:8000`

3. **Start using it**:
   - Upload your clothing items
   - Select mood and occasion
   - Get outfit suggestions!

## Option 2: Full Version (With AI Features)

If you want the full AI-powered version with OpenAI integration:

### Step 1: Install Python Dependencies

**For Windows:**
```bash
# If you have pip installed:
pip install Flask Flask-CORS Pillow openai python-dotenv Werkzeug

# If pip is not installed, download and install it first:
# Go to https://pip.pypa.io/en/stable/installation/
```

**Alternative - Install pip first:**
1. Download `get-pip.py` from https://bootstrap.pypa.io/get-pip.py
2. Run: `python get-pip.py`
3. Then run: `pip install Flask Flask-CORS Pillow openai python-dotenv Werkzeug`

### Step 2: Set up OpenAI API (Optional)

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a `.env` file in the project folder:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. If you don't have an API key, the app will work with fallback mode

### Step 3: Run the Full Version

```bash
python app.py
```

Then open: `http://localhost:5000`

## 🎯 Which Version Should You Use?

- **Simple Version**: Perfect for getting started quickly, no installation needed
- **Full Version**: Better AI-powered suggestions, requires dependency installation

## 🛠️ Troubleshooting

### "pip is not recognized"
- Download and install pip from https://pip.pypa.io/en/stable/installation/
- Or use the simple version instead

### "No module named 'flask'"
- Run: `pip install Flask Flask-CORS Pillow openai python-dotenv Werkzeug`
- Or use the simple version instead

### Port already in use
- Change the port in the Python file
- Or stop other applications using the same port

## 🎉 You're Ready!

Once you have either version running:
1. Upload photos of your clothing items
2. Categorize them (type, color, style)
3. Select your mood and occasion
4. Get personalized outfit suggestions!

**Happy Styling! 👗✨**
