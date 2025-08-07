from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.accounts.models import CustomUserDetail, MeditationGenerate, RitualType, Rituals
from apps.accounts.serializers import ExternalMeditationWithUserCheckSerializer
from apps.accounts.views import ExternalMeditationAPIView
from unittest.mock import patch, MagicMock, PropertyMock

User = get_user_model()

class ExternalMeditationWithUserCheckSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.ritual_type = RitualType.objects.create(
            name='Test Ritual Type',
            description='Test Description'
        )
        self.ritual = Rituals.objects.create(
            name='Test Ritual',
            description='Test Description',
            ritual_type='guided',
            tone='dreamy',
            voice='male',
            duration='5'
        )

    def test_serializer_with_user_not_in_meditation_generate(self):
        """Test serializer when user doesn't exist in MeditationGenerate"""
        data = {
            'plan_type': self.ritual_type.id,
            'gender': 'male',
            'dream': 'Test dream',
            'goals': 'Test goals',
            'age_range': '25-35',
            'happiness': 'Very happy',
            'ritual_type': 'guided',
            'tone': 'dreamy',
            'voice': 'male',
            'duration': '5'
        }
        
        # Mock request context
        mock_request = MagicMock()
        mock_request.user = self.user
        # Use PropertyMock for is_authenticated
        type(mock_request.user).is_authenticated = PropertyMock(return_value=True)
        
        serializer = ExternalMeditationWithUserCheckSerializer(
            data=data,
            context={'request': mock_request}
        )
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['gender'], 'male')
        self.assertEqual(serializer.validated_data['dream'], 'Test dream')

    def test_serializer_with_user_in_meditation_generate(self):
        """Test serializer when user exists in MeditationGenerate"""
        # Create user detail
        user_detail = CustomUserDetail.objects.create(
            user=self.user,
            gender='female',
            dream='Existing dream',
            goals='Existing goals',
            age_range='30-40',
            happiness='Happy'
        )
        
        # Create meditation record for user
        meditation = MeditationGenerate.objects.create(
            user=self.user,
            details=self.ritual,
            ritual_type=self.ritual_type
        )
        
        # Only provide required fields
        data = {
            'plan_type': self.ritual_type.id,
            'ritual_type': 'guided',
            'tone': 'dreamy',
            'voice': 'male',
            'duration': '5'
        }
        
        # Mock request context
        mock_request = MagicMock()
        mock_request.user = self.user
        # Use PropertyMock for is_authenticated
        type(mock_request.user).is_authenticated = PropertyMock(return_value=True)
        
        serializer = ExternalMeditationWithUserCheckSerializer(
            data=data,
            context={'request': mock_request}
        )
        
        self.assertTrue(serializer.is_valid())
        # Should populate missing fields from user detail
        self.assertEqual(serializer.validated_data['gender'], 'female')
        self.assertEqual(serializer.validated_data['dream'], 'Existing dream')

    def test_serializer_missing_required_fields_when_user_not_in_meditation(self):
        """Test serializer validation when user not in MeditationGenerate and missing required fields"""
        data = {
            'plan_type': self.ritual_type.id,
            'ritual_type': 'guided',
            'tone': 'dreamy',
            'voice': 'male',
            'duration': '5'
            # Missing: gender, dream, goals, age_range, happiness
        }
        
        # Mock request context
        mock_request = MagicMock()
        mock_request.user = self.user
        # Use PropertyMock for is_authenticated
        type(mock_request.user).is_authenticated = PropertyMock(return_value=True)
        
        serializer = ExternalMeditationWithUserCheckSerializer(
            data=data,
            context={'request': mock_request}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('gender', serializer.errors)
        self.assertIn('dream', serializer.errors)
        self.assertIn('goals', serializer.errors)
        self.assertIn('age_range', serializer.errors)
        self.assertIn('happiness', serializer.errors)

    def test_serializer_user_not_authenticated(self):
        """Test serializer validation when user is not authenticated"""
        data = {
            'plan_type': self.ritual_type.id,
            'gender': 'male',
            'dream': 'Test dream',
            'goals': 'Test goals',
            'age_range': '25-35',
            'happiness': 'Very happy',
            'ritual_type': 'guided',
            'tone': 'dreamy',
            'voice': 'male',
            'duration': '5'
        }
        
        # Mock request context with unauthenticated user
        mock_request = MagicMock()
        mock_request.user = self.user
        # Use PropertyMock for is_authenticated
        type(mock_request.user).is_authenticated = PropertyMock(return_value=False)
        
        serializer = ExternalMeditationWithUserCheckSerializer(
            data=data,
            context={'request': mock_request}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_serializer_user_exists_but_no_user_detail(self):
        """Test serializer when user exists in MeditationGenerate but no CustomUserDetail"""
        # Create meditation record for user (but no CustomUserDetail)
        meditation = MeditationGenerate.objects.create(
            user=self.user,
            details=self.ritual,
            ritual_type=self.ritual_type
        )
        
        data = {
            'plan_type': self.ritual_type.id,
            'ritual_type': 'guided',
            'tone': 'dreamy',
            'voice': 'male',
            'duration': '5'
        }
        
        # Mock request context
        mock_request = MagicMock()
        mock_request.user = self.user
        # Use PropertyMock for is_authenticated
        type(mock_request.user).is_authenticated = PropertyMock(return_value=True)
        
        serializer = ExternalMeditationWithUserCheckSerializer(
            data=data,
            context={'request': mock_request}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class ExternalMeditationAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.ritual_type = RitualType.objects.create(
            name='Test Ritual Type',
            description='Test Description'
        )
        self.ritual = Rituals.objects.create(
            name='Test Ritual',
            description='Test Description',
            ritual_type='guided',
            tone='dreamy',
            voice='male',
            duration='5'
        )

    @patch('apps.accounts.views.ExternalMeditationService')
    def test_external_meditation_api_user_not_in_meditation(self, mock_service):
        """Test API when user doesn't exist in MeditationGenerate"""
        # Mock the service response
        mock_service_instance = MagicMock()
        mock_service_instance.process_meditation_request.return_value = {
            'success': True,
            'meditation_id': 1,
            'file_url': 'http://example.com/file.mp3'
        }
        mock_service.return_value = mock_service_instance
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
        
        data = {
            'plan_type': self.ritual_type.id,
            'gender': 'male',
            'dream': 'Test dream',
            'goals': 'Test goals',
            'age_range': '25-35',
            'happiness': 'Very happy',
            'ritual_type': 'guided',
            'tone': 'dreamy',
            'voice': 'male',
            'duration': '5'
        }
        
        response = self.client.post('/api/auth/meditation/external/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['user_exists_in_meditation'])

    @patch('apps.accounts.views.ExternalMeditationService')
    def test_external_meditation_api_user_in_meditation(self, mock_service):
        """Test API when user exists in MeditationGenerate"""
        # Create user detail
        user_detail = CustomUserDetail.objects.create(
            user=self.user,
            gender='female',
            dream='Existing dream',
            goals='Existing goals',
            age_range='30-40',
            happiness='Happy'
        )
        
        # Create meditation record for user
        meditation = MeditationGenerate.objects.create(
            user=self.user,
            details=self.ritual,
            ritual_type=self.ritual_type
        )
        
        # Mock the service response
        mock_service_instance = MagicMock()
        mock_service_instance.process_meditation_request.return_value = {
            'success': True,
            'meditation_id': 1,
            'file_url': 'http://example.com/file.mp3'
        }
        mock_service.return_value = mock_service_instance
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
        
        # Only provide required fields
        data = {
            'plan_type': self.ritual_type.id,
            'ritual_type': 'guided',
            'tone': 'dreamy',
            'voice': 'male',
            'duration': '5'
        }
        
        response = self.client.post('/api/auth/meditation/external/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['user_exists_in_meditation'])

    def test_external_meditation_api_unauthenticated(self):
        """Test API when user is not authenticated"""
        data = {
            'plan_type': self.ritual_type.id,
            'gender': 'male',
            'dream': 'Test dream',
            'goals': 'Test goals',
            'age_range': '25-35',
            'happiness': 'Very happy',
            'ritual_type': 'guided',
            'tone': 'dreamy',
            'voice': 'male',
            'duration': '5'
        }
        
        response = self.client.post('/api/auth/meditation/external/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_external_meditation_api_missing_required_fields(self):
        """Test API when required fields are missing"""
        # Authenticate user
        self.client.force_authenticate(user=self.user)
        
        # Missing required fields
        data = {
            'plan_type': self.ritual_type.id,
            'ritual_type': 'guided',
            'tone': 'dreamy',
            'voice': 'male',
            'duration': '5'
            # Missing: gender, dream, goals, age_range, happiness
        }
        
        response = self.client.post('/api/auth/meditation/external/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('gender', response.data['details'])
        self.assertIn('dream', response.data['details'])
        self.assertIn('goals', response.data['details'])
        self.assertIn('age_range', response.data['details'])
        self.assertIn('happiness', response.data['details'])
        self.assertFalse(response.data['user_exists_in_meditation'])
