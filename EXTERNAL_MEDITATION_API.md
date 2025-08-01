# External Meditation API Documentation

## Overview

The External Meditation API allows you to generate meditation content by sending requests to external meditation services. The API maps plan types to specific external endpoints and transforms the request data to match the external API format.

## API Endpoint

```
POST /meditation/external/
```

## Request Format

### Headers
```
Content-Type: application/json
Authorization: Bearer <your_jwt_token>  # Optional for testing
```

### Request Body

```json
{
  "plan_type": 2,
  "gender": "male",
  "dream": "Wake up in a hammock enveloped within nature, with a waterfall in the background",
  "goals": "Enjoy life to the Fullest. Make vela an Editor's Choice Wellness app in the AppStore",
  "age_range": "25",
  "happiness": "Adventure, Beauty, Nature, Creation. I feel most me when I'm building something that matters.",
  "ritual_type": "story",
  "tone": "dreamy",
  "voice": "female",
  "duration": "2"
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plan_type` | integer | Yes | ID of the RitualType that determines which external API to use |
| `gender` | string | Yes | User's gender |
| `dream` | string | Yes | User's dream description |
| `goals` | string | Yes | User's goals |
| `age_range` | string | Yes | User's age range |
| `happiness` | string | Yes | What makes the user happy |
| `ritual_type` | string | Yes | Type of ritual ('story' or 'guided_meditations') |
| `tone` | string | Yes | Tone of the meditation ('dreamy' or 'asmr') |
| `voice` | string | Yes | Voice type ('male' or 'female') |
| `duration` | string | Yes | Duration in minutes ('2', '5', or '10') |

## External API Mapping

The service maps RitualType names to external API endpoints:

| RitualType Name | External API Endpoint |
|-----------------|----------------------|
| Sleep Manifestation | http://31.97.98.47:8000/sleep |
| Morning Spark | http://31.97.98.47:8000/spark |
| Calming Reset | http://31.97.98.47:8000/calm |
| Dream Visualizer | http://31.97.98.47:8000/dream |

## Data Transformation

The service transforms your request data to match the external API format:

| Your Field | External API Field | Transformation |
|------------|-------------------|---------------|
| `duration` | `length` | Converted to integer |
| `ritual_type` | `ritual_type` | Capitalized (e.g., 'story' → 'Story') |
| `voice` | `voice` | Capitalized (e.g., 'female' → 'Female') |
| `tone` | `tone` | Capitalized (e.g., 'dreamy' → 'Dreamy') |
| `goals` | `goals` | No change |
| `dream` | `dreamlife` | No change |
| `happiness` | `dream_activities` | No change |
| `age_range` | `name` | No change |
| `gender` | `check_in` | No change |

## Response Format

### Success Response (200)

```json
{
  "success": true,
  "message": "Meditation generated successfully",
  "plan_type": "Morning Spark",
  "endpoint_used": "http://31.97.98.47:8000/spark",
  "api_response": {
    "success": true,
    "file_data": "http://example.com/meditation.mp3",
    "file_name": "meditation_1234567890.mp3",
    "response_data": {...}
  },
  "file_url": "/media/meditations/meditation_1234567890.mp3",
  "meditation_id": 123
}
```

### Error Response (400)

```json
{
  "error": "Validation failed",
  "details": {
    "plan_type": ["Plan type with ID 999 does not exist."]
  }
}
```

### Error Response (500)

```json
{
  "success": false,
  "message": "External API request failed: HTTP 500: Internal Server Error",
  "plan_type": "Morning Spark",
  "endpoint_used": "http://31.97.98.47:8000/spark",
  "api_response": {
    "success": false,
    "error": "HTTP 500: Internal Server Error"
  }
}
```

## Setup Instructions

### 1. Create RitualType Records

First, create the necessary RitualType records in your database:

```bash
python setup_ritual_types.py
```

This will create the following RitualType records:
- Sleep Manifestation
- Morning Spark
- Calming Reset
- Dream Visualizer

### 2. Test the API

You can test the API using the provided test script:

```bash
python test_external_meditation_api.py
```

### 3. Example Usage

```python
import requests

# API endpoint
url = "http://localhost:8000/meditation/external/"

# Request data
data = {
    "plan_type": 2,  # ID of the RitualType
    "gender": "male",
    "dream": "Wake up in a hammock enveloped within nature, with a waterfall in the background",
    "goals": "Enjoy life to the Fullest. Make vela an Editor's Choice Wellness app in the AppStore",
    "age_range": "25",
    "happiness": "Adventure, Beauty, Nature, Creation. I feel most me when I'm building something that matters.",
    "ritual_type": "story",
    "tone": "dreamy",
    "voice": "female",
    "duration": "2"
}

# Make the request
response = requests.post(url, json=data)

# Check the response
if response.status_code == 200:
    result = response.json()
    print(f"Success! Meditation ID: {result['meditation_id']}")
    print(f"File URL: {result['file_url']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

## Notes

1. **Authentication**: The API currently allows anonymous access for testing. In production, you should require authentication.

2. **File Storage**: Generated meditation files are saved to the `MeditationGenerate` model and can be accessed via the returned `file_url`.

3. **Error Handling**: The service includes comprehensive error handling for network issues, timeouts, and external API failures.

4. **Logging**: All API requests and responses are logged for debugging purposes.

5. **Fallback**: If the external API is unavailable, the service will still create a meditation record but without the audio file. 