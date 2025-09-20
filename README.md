# 👗 AI Fashion Stylist

An intelligent web application that helps you create perfect outfits from your wardrobe based on your mood and occasion.

## ✨ Features

- **Wardrobe Management**: Upload and categorize your clothing items
- **AI-Powered Styling**: Get personalized outfit suggestions using AI
- **Mood-Based Selection**: Choose outfits based on your mood (casual, formal, party, etc.)
- **Occasion Matching**: Get appropriate outfits for different occasions
- **Beautiful Web Interface**: Modern, responsive design that works on all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- OpenAI API key (optional - has fallback mode)

### Installation

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API (Optional)**:
   - Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a `.env` file in the project root:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```
   - If you don't have an API key, the app will work with a fallback outfit generation system

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and go to: `http://localhost:5000`

## 🎯 How to Use

### 1. Upload Your Wardrobe
- Click "Add to Wardrobe" section
- Upload photos of your clothing items
- Categorize each item (type, color, style)

### 2. Generate Outfits
- Select your desired mood (casual, formal, party, etc.)
- Choose the occasion (daily, work, date, etc.)
- Click "Generate My Outfit" to get AI-powered suggestions

### 3. Get Styling Tips
- View complete outfit recommendations
- Read styling tips and reasoning
- See why each outfit works for your mood/occasion

## 🛠️ Technical Details

### Architecture
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenAI GPT-3.5-turbo (with fallback)
- **Storage**: JSON file-based wardrobe storage
- **Image Handling**: Local file storage with Pillow

### File Structure
```
AI Fashion Stylist/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── static/               # Static files (CSS, JS, images)
├── uploads/              # Uploaded clothing images
├── wardrobe.json         # Wardrobe data storage
└── README.md            # This file
```

## 🎨 Customization

### Adding New Clothing Types
Edit the `item_type` options in `templates/index.html`:
```html
<option value="new_type">New Clothing Type</option>
```

### Adding New Moods
Edit the `mood` options in `templates/index.html`:
```html
<option value="new_mood">New Mood</option>
```

### Modifying AI Prompts
Edit the `generate_outfit_with_ai()` function in `app.py` to customize how the AI generates outfits.

## 🔧 Troubleshooting

### Common Issues

1. **"No module named 'flask'"**
   - Run: `pip install -r requirements.txt`

2. **Upload fails**
   - Check file size (max 16MB)
   - Ensure file is an image (PNG, JPG, JPEG, GIF)

3. **AI not working**
   - Check your OpenAI API key in `.env` file
   - The app will work with fallback mode if no API key

4. **Port already in use**
   - Change the port in `app.py`: `app.run(port=5001)`

## 🌟 Future Enhancements

- [ ] User accounts and multiple wardrobes
- [ ] Weather-based outfit suggestions
- [ ] Outfit history and favorites
- [ ] Social sharing features
- [ ] Advanced AI image analysis
- [ ] Mobile app version
- [ ] Integration with fashion APIs

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this AI Fashion Stylist!

---

**Happy Styling! 👗✨**
