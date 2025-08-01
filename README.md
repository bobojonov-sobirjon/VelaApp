# Vela - FastAPI Meditation API

A FastAPI REST API for meditation and wellness services with external API integration.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Vela
   ```

2. **Create and activate virtual environment**
   ```bash
   # On Windows
   python -m venv env
   env\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server**
   ```bash
   # Using uvicorn with the correct module path
   python3 -m uvicorn apps.accounts.generate.main:vela --host 0.0.0.0 --port 8000 --reload
   
   # Alternative command (if the above doesn't work)
   uvicorn apps.accounts.generate.main:vela --host 0.0.0.0 --port 8000 --reload
   ```

The application will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive API Documentation
- **URL**: `http://localhost:8000/docs`
- **Description**: Swagger UI with interactive API documentation

### Alternative Documentation
- **URL**: `http://localhost:8000/redoc`
- **Description**: ReDoc documentation

## 🔧 Available Endpoints

### Meditation Generation APIs
- `POST /sleep` - Generate sleep manifestation audio
- `POST /spark` - Generate morning spark audio
- `POST /calm` - Generate calming reset audio
- `POST /dream` - Generate dream visualizer audio
- `POST /check-in` - Generate check-in audio

### Request Format
All endpoints accept the same request body format:

```json
{
  "name": "string",
  "goals": "string",
  "dreamlife": "string",
  "dream_activities": "string",
  "ritual_type": "Story" | "Guided",
  "tone": "Dreamy" | "ASMR",
  "voice": "female" | "male",
  "length": 2 | 5 | 10,
  "check_in": "string"
}
```

### Response Format
All endpoints return audio files in WAV format with appropriate filenames:
- Sleep manifestation: `sleep_manifestation.wav`
- Morning spark: `morning_spark.wav`
- Calming reset: `calming_reset.wav`
- Dream visualizer: `dream_visualizer.wav`

## 🧪 Testing

### Test the External Meditation API
```bash
python test_external_meditation_api.py
```

### Test Error Handling
```bash
python test_error_handling.py
```

### Test Meditation API
```bash
python test_meditation_api.py
```

## 🌟 Key Features

### Audio Generation
The FastAPI application generates meditation audio files using:
- **Script Generation**: Creates personalized meditation scripts
- **Audio Synthesis**: Converts text to speech using ElevenLabs API
- **Music Mixing**: Combines speech with background music
- **Multiple Formats**: Supports different meditation types and durations

### Example Usage

#### Generate Sleep Manifestation Audio
```bash
curl -X POST "http://localhost:8000/sleep" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "goals": "I want to achieve deep, restful sleep every night",
    "dreamlife": "I dream of a peaceful, stress-free life",
    "dream_activities": "Reading, meditation, and spending time in nature",
    "ritual_type": "Story",
    "tone": "Dreamy",
    "voice": "female",
    "length": 5,
    "check_in": "Feeling ready for a peaceful night"
  }' \
  --output sleep_manifestation.wav
```

#### Generate Morning Spark Audio
```bash
curl -X POST "http://localhost:8000/spark" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "goals": "I want to start each day with energy and motivation",
    "dreamlife": "I dream of a successful career and fulfilling relationships",
    "dream_activities": "Exercise, healthy eating, and personal growth",
    "ritual_type": "Guided",
    "tone": "ASMR",
    "voice": "male",
    "length": 2,
    "check_in": "Ready to seize the day"
  }' \
  --output morning_spark.wav
```

## 🛠️ Development

### Project Structure
```
Vela/
├── apps/
│   └── accounts/
│       └── generate/
│           ├── main.py          # FastAPI application entry point
│           ├── generation.py    # Script generation logic
│           ├── synthesis.py     # Audio synthesis
│           ├── music.py         # Music mixing
│           └── functions.py     # Utility functions
├── config/                     # Configuration files
├── staticfiles/               # Static files
├── requirements.txt           # Python dependencies
└── db.sqlite3                # SQLite database
```

### Environment Variables
The application uses default settings for development. For production, you should:

1. Set up proper environment variables for API keys
2. Configure proper `ALLOWED_HOSTS`
3. Set up a production database

### Database
The application uses SQLite by default. For production, consider using PostgreSQL or MySQL.

## 🚀 Deployment

### Using Uvicorn (Development)
```bash
uvicorn apps.accounts.generate.main:vela --host 0.0.0.0 --port 8000 --reload
```

### Using Uvicorn (Production)
```bash
uvicorn apps.accounts.generate.main:vela --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn apps.accounts.generate.main:vela -w 4 -k uvicorn.workers.UvicornWorker
```

### Using Docker (if Dockerfile exists)
```bash
docker build -t vela .
docker run -p 8000:8000 vela
```

## 📝 Logging

Logs are written to `django.log` in the project root. Check this file for debugging information.

## 🔧 Troubleshooting

### Common Issues

1. **Import Error**: Make sure you're in the virtual environment
   ```bash
   # Activate virtual environment
   source env/bin/activate  # Linux/Mac
   env\Scripts\activate     # Windows
   ```

2. **Module Not Found**: Make sure you're running from the project root
   ```bash
   # Make sure you're in the Vela directory
   pwd  # Should show the path to your Vela project
   ```

3. **Port Already in Use**: Change the port
   ```bash
   uvicorn apps.accounts.generate.main:vela --host 0.0.0.0 --port 8001 --reload
   ```

4. **Permission Error**: Make sure you have write permissions to the project directory

### Getting Help

- Check the application logs
- Use FastAPI's automatic documentation at `/docs`
- Check the ReDoc documentation at `/redoc`

## 📄 License

This project is licensed under the BSD License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support, please contact: contact@snippets.local 