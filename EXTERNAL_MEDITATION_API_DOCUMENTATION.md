# External Meditation API with User Check

## Overview

The `ExternalMeditationAPIView` has been enhanced with a new serializer `ExternalMeditationWithUserCheckSerializer` that checks if the user exists in the `MeditationGenerate` model and adjusts the required fields accordingly.

## Functionality

### User Check Logic

The API now performs the following checks:

1. **User Authentication**: The user must be authenticated to access the endpoint
2. **MeditationGenerate Check**: Checks if the user has any records in the `MeditationGenerate` model
3. **CustomUserDetail Check**: If user exists in `MeditationGenerate`, retrieves user details from `CustomUserDetail`

### Request Body Requirements

#### When User Does NOT Exist in MeditationGenerate

If the user has no records in `MeditationGenerate`, all fields are required:

```json
{
    "plan_type": 1,
    "gender": "male",
    "dream": "User's dream description",
    "goals": "User's specific goals",
    "age_range": "25-35",
    "happiness": "What makes user happy",
    "ritual_type": "guided",
    "tone": "dreamy",
    "voice": "male",
    "duration": "5"
}
```

#### When User EXISTS in MeditationGenerate

If the user has records in `MeditationGenerate`, only the following fields are required:

```json
{
    "plan_type": 1,
    "ritual_type": "guided",
    "tone": "dreamy",
    "voice": "male",
    "duration": "5"
}
```

The missing fields (`gender`, `dream`, `goals`, `age_range`, `happiness`) will be automatically populated from the user's `CustomUserDetail` record.

### Response Format

The API response includes a new field `user_exists_in_meditation` to indicate whether the user was found in the `MeditationGenerate` model:

```json
{
    "success": true,
    "message": "Meditation generated successfully",
    "plan_type": "Test Ritual Type",
    "api_response": {...},
    "endpoint_used": "external_api_endpoint",
    "file_url": "http://example.com/meditation.mp3",
    "meditation_id": 123,
    "user_exists_in_meditation": true
}
```

### Error Handling

#### Authentication Error (401)
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### Validation Error (400)
```json
{
    "error": "Validation failed",
    "details": {
        "gender": "gender is required when user is not found in MeditationGenerate",
        "dream": "dream is required when user is not found in MeditationGenerate"
    },
    "user_exists_in_meditation": false
}
```

#### Missing User Detail Error (400)
```json
{
    "error": "Validation failed",
    "details": {
        "non_field_errors": ["User detail not found. Please provide all required fields."]
    },
    "user_exists_in_meditation": true
}
```

## API Endpoint

- **URL**: `/api/auth/meditation/external/`
- **Method**: `POST`
- **Authentication**: Required (JWT Token)
- **Content-Type**: `application/json`

## Usage Examples

### First-time User (No MeditationGenerate records)

```bash
curl -X POST /api/auth/meditation/external/ \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": 1,
    "gender": "male",
    "dream": "I want to achieve financial freedom",
    "goals": "Save $50,000 in 2 years",
    "age_range": "25-35",
    "happiness": "Spending time with family",
    "ritual_type": "guided",
    "tone": "dreamy",
    "voice": "male",
    "duration": "5"
  }'
```

### Returning User (Has MeditationGenerate records)

```bash
curl -X POST /api/auth/meditation/external/ \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": 1,
    "ritual_type": "guided",
    "tone": "dreamy",
    "voice": "male",
    "duration": "5"
  }'
```

## Testing

The functionality is thoroughly tested with the following test cases:

1. **Serializer Tests**:
   - User not in MeditationGenerate (all fields required)
   - User in MeditationGenerate (only basic fields required)
   - Missing required fields validation
   - Unauthenticated user validation
   - User exists but no CustomUserDetail

2. **API Tests**:
   - User not in MeditationGenerate
   - User in MeditationGenerate
   - Unauthenticated access
   - Missing required fields

Run tests with:
```bash
python manage.py test apps.accounts.tests
```

## Implementation Details

### New Serializer: `ExternalMeditationWithUserCheckSerializer`

- Extends the original `ExternalMeditationSerializer`
- Adds conditional field validation based on user existence in `MeditationGenerate`
- Automatically populates missing fields from `CustomUserDetail` when user exists
- Provides clear error messages for missing required fields

### Updated View: `ExternalMeditationAPIView`

- Changed permission from `AllowAny` to `IsAuthenticated`
- Uses the new serializer with user check functionality
- Returns `user_exists_in_meditation` flag in response
- Enhanced error handling with user existence information

## Database Models Used

- `MeditationGenerate`: To check if user has meditation records
- `CustomUserDetail`: To retrieve user details when user exists in MeditationGenerate
- `RitualType`: To validate plan_type field
- `CustomUser`: For authentication and user identification 