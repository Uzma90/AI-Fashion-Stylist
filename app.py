from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_wardrobe():
    """Load wardrobe data from JSON file"""
    try:
        with open('wardrobe.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"items": []}

def save_wardrobe(wardrobe):
    """Save wardrobe data to JSON file"""
    with open('wardrobe.json', 'w') as f:
        json.dump(wardrobe, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get additional data from form
        item_type = request.form.get('item_type', 'unknown')
        color = request.form.get('color', 'unknown')
        style = request.form.get('style', 'unknown')
        
        # Add to wardrobe
        wardrobe = load_wardrobe()
        item = {
            'id': len(wardrobe['items']) + 1,
            'filename': filename,
            'filepath': filepath,
            'item_type': item_type,
            'color': color,
            'style': style,
            'uploaded_at': datetime.now().isoformat()
        }
        wardrobe['items'].append(item)
        save_wardrobe(wardrobe)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'item': item
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/wardrobe')
def get_wardrobe():
    wardrobe = load_wardrobe()
    return jsonify(wardrobe)

@app.route('/generate-outfit', methods=['POST'])
def generate_outfit():
    data = request.get_json()
    mood = data.get('mood', 'casual')
    occasion = data.get('occasion', 'daily')
    
    wardrobe = load_wardrobe()
    
    if not wardrobe['items']:
        return jsonify({'error': 'No items in wardrobe'}), 400
    
    # Generate outfit using AI
    outfit = generate_outfit_with_ai(wardrobe['items'], mood, occasion)
    
    return jsonify({
        'outfit': outfit,
        'mood': mood,
        'occasion': occasion
    })

def generate_outfit_with_ai(items, mood, occasion):
    """Generate outfit using AI based on mood and occasion"""
    
    # Create a prompt for the AI
    items_description = []
    for item in items:
        items_description.append(f"- {item['item_type']} ({item['color']}, {item['style']} style)")
    
    items_text = "\n".join(items_description)
    
    prompt = f"""
    You are a fashion stylist. Based on the user's wardrobe and their desired mood/occasion, suggest a complete outfit.
    
    User's Wardrobe:
    {items_text}
    
    Desired Mood: {mood}
    Occasion: {occasion}
    
    Please suggest a complete outfit by selecting items from the wardrobe. Consider:
    1. Color coordination
    2. Style matching
    3. Occasion appropriateness
    4. Mood expression
    
    Return your response in JSON format with this structure:
    {{
        "outfit": {{
            "top": "item description",
            "bottom": "item description", 
            "shoes": "item description",
            "accessories": "item description"
        }},
        "styling_tips": "Brief styling advice",
        "reasoning": "Why this outfit works for the mood/occasion"
    }}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional fashion stylist with expertise in creating outfits for different moods and occasions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Try to parse JSON response
        try:
            outfit_data = json.loads(ai_response)
            return outfit_data
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            return {
                "outfit": {
                    "top": "Select a top that matches your mood",
                    "bottom": "Choose appropriate bottoms",
                    "shoes": "Pick comfortable shoes",
                    "accessories": "Add accessories to complete the look"
                },
                "styling_tips": ai_response,
                "reasoning": "AI-generated styling advice"
            }
    
    except Exception as e:
        # Fallback outfit generation without AI
        return generate_fallback_outfit(items, mood, occasion)

def generate_fallback_outfit(items, mood, occasion):
    """Fallback outfit generation when AI is not available"""
    
    # Simple rule-based outfit generation
    outfit = {
        "top": "Choose a comfortable top",
        "bottom": "Select appropriate bottoms",
        "shoes": "Pick suitable shoes",
        "accessories": "Add finishing touches"
    }
    
    if mood == "formal":
        outfit["styling_tips"] = "Opt for classic pieces in neutral colors. Ensure everything is well-fitted and polished."
    elif mood == "casual":
        outfit["styling_tips"] = "Keep it relaxed and comfortable. Mix textures and add personal touches."
    elif mood == "party":
        outfit["styling_tips"] = "Go bold with colors and statement pieces. Don't forget to accessorize!"
    else:
        outfit["styling_tips"] = "Choose pieces that make you feel confident and comfortable."
    
    outfit["reasoning"] = f"This outfit is designed for a {mood} mood and {occasion} occasion."
    
    return outfit

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
