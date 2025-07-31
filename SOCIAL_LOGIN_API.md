# Social Login API Documentation

This document describes how to implement Google, Facebook, and Apple ID authentication for your mobile app using our Django REST API.

## Overview

The API provides three social login endpoints that accept tokens from mobile apps and return JWT tokens for authentication.

## Base URL

```
https://your-api-domain.com/api/accounts/
```

## Authentication Endpoints

### 1. Google Login

**Endpoint:** `POST /google/login/`

**Request Body:**
```json
{
    "access_token": "google_access_token_from_mobile_app"
}
```

**Response:**
```json
{
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "avatar": null,
        "weekly_login_stats": {...},
        "check_in": [...]
    }
}
```

**Error Response:**
```json
{
    "error": "Invalid access token"
}
```

### 2. Facebook Login

**Endpoint:** `POST /facebook/login/`

**Request Body:**
```json
{
    "access_token": "facebook_access_token_from_mobile_app"
}
```

**Response:**
```json
{
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "avatar": null,
        "weekly_login_stats": {...},
        "check_in": [...]
    }
}
```

**Error Response:**
```json
{
    "error": "Invalid access token"
}
```

### 3. Apple ID Login

**Endpoint:** `POST /apple/login/`

**Request Body:**
```json
{
    "id_token": "apple_id_token_from_mobile_app",
    "user": {
        "name": {
            "firstName": "John",
            "lastName": "Doe"
        }
    }
}
```

**Response:**
```json
{
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "avatar": null,
        "weekly_login_stats": {...},
        "check_in": [...]
    }
}
```

**Error Response:**
```json
{
    "error": "Invalid token"
}
```

## Mobile App Implementation

### iOS (Swift)

#### Google Sign-In

```swift
import GoogleSignIn

class GoogleSignInManager {
    func signIn() {
        guard let presentingViewController = UIApplication.shared.windows.first?.rootViewController else { return }
        
        GIDSignIn.sharedInstance.signIn(withPresenting: presentingViewController) { [weak self] result, error in
            guard let self = self else { return }
            
            if let error = error {
                print("Google Sign-In error: \(error)")
                return
            }
            
            guard let user = result?.user,
                  let accessToken = user.accessToken.tokenString else {
                print("Failed to get access token")
                return
            }
            
            // Send token to your backend
            self.sendTokenToBackend(accessToken: accessToken, provider: "google")
        }
    }
    
    private func sendTokenToBackend(accessToken: String, provider: String) {
        let url = URL(string: "https://your-api-domain.com/api/accounts/\(provider)/login/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["access_token": accessToken]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            // Handle response
            if let data = data {
                let response = try? JSONSerialization.jsonObject(with: data)
                print("Response: \(response)")
            }
        }.resume()
    }
}
```

#### Facebook Sign-In

```swift
import FBSDKLoginKit

class FacebookSignInManager {
    func signIn() {
        let loginManager = LoginManager()
        loginManager.logIn(permissions: ["email", "public_profile"], from: nil) { [weak self] result, error in
            guard let self = self else { return }
            
            if let error = error {
                print("Facebook Sign-In error: \(error)")
                return
            }
            
            guard let accessToken = AccessToken.current?.tokenString else {
                print("Failed to get access token")
                return
            }
            
            // Send token to your backend
            self.sendTokenToBackend(accessToken: accessToken, provider: "facebook")
        }
    }
    
    private func sendTokenToBackend(accessToken: String, provider: String) {
        let url = URL(string: "https://your-api-domain.com/api/accounts/\(provider)/login/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["access_token": accessToken]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            // Handle response
            if let data = data {
                let response = try? JSONSerialization.jsonObject(with: data)
                print("Response: \(response)")
            }
        }.resume()
    }
}
```

#### Apple Sign-In

```swift
import AuthenticationServices

class AppleSignInManager: NSObject, ASAuthorizationControllerDelegate {
    func signIn() {
        let request = ASAuthorizationAppleIDProvider().createRequest()
        request.requestedScopes = [.fullName, .email]
        
        let controller = ASAuthorizationController(authorizationRequests: [request])
        controller.delegate = self
        controller.performRequests()
    }
    
    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
            let idToken = appleIDCredential.identityToken
            let idTokenString = String(data: idToken!, encoding: .utf8)!
            
            let userInfo: [String: Any] = [
                "name": [
                    "firstName": appleIDCredential.fullName?.givenName ?? "",
                    "lastName": appleIDCredential.fullName?.familyName ?? ""
                ]
            ]
            
            // Send token to your backend
            sendTokenToBackend(idToken: idTokenString, userInfo: userInfo)
        }
    }
    
    private func sendTokenToBackend(idToken: String, userInfo: [String: Any]) {
        let url = URL(string: "https://your-api-domain.com/api/accounts/apple/login/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "id_token": idToken,
            "user": userInfo
        ]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            // Handle response
            if let data = data {
                let response = try? JSONSerialization.jsonObject(with: data)
                print("Response: \(response)")
            }
        }.resume()
    }
}
```

### Android (Kotlin)

#### Google Sign-In

```kotlin
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions

class GoogleSignInManager {
    private lateinit var googleSignInClient: GoogleSignInClient
    
    fun signIn() {
        val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestEmail()
            .requestIdToken("your-web-client-id")
            .build()
        
        googleSignInClient = GoogleSignIn.getClient(context, gso)
        
        val signInIntent = googleSignInClient.signInIntent
        startActivityForResult(signInIntent, RC_SIGN_IN)
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        if (requestCode == RC_SIGN_IN) {
            val task = GoogleSignIn.getSignedInAccountFromIntent(data)
            try {
                val account = task.getResult(ApiException::class.java)
                val accessToken = account.idToken
                
                // Send token to your backend
                sendTokenToBackend(accessToken, "google")
            } catch (e: ApiException) {
                Log.w("GoogleSignIn", "signInResult:failed code=${e.statusCode}")
            }
        }
    }
    
    private fun sendTokenToBackend(accessToken: String, provider: String) {
        val url = "https://your-api-domain.com/api/accounts/$provider/login/"
        val jsonObject = JSONObject()
        jsonObject.put("access_token", accessToken)
        
        val request = Request.Builder()
            .url(url)
            .post(jsonObject.toString().toRequestBody("application/json".toMediaType()))
            .build()
        
        OkHttpClient().newCall(request).enqueue(object : Callback {
            override fun onResponse(call: Call, response: Response) {
                val responseBody = response.body?.string()
                Log.d("API", "Response: $responseBody")
            }
            
            override fun onFailure(call: Call, e: IOException) {
                Log.e("API", "Error: ${e.message}")
            }
        })
    }
}
```

#### Facebook Sign-In

```kotlin
import com.facebook.CallbackManager
import com.facebook.FacebookCallback
import com.facebook.FacebookException
import com.facebook.login.LoginManager
import com.facebook.login.LoginResult

class FacebookSignInManager {
    private lateinit var callbackManager: CallbackManager
    
    fun signIn() {
        callbackManager = CallbackManager.Factory.create()
        
        LoginManager.getInstance().logInWithReadPermissions(
            this,
            listOf("email", "public_profile")
        )
        
        LoginManager.getInstance().registerCallback(callbackManager,
            object : FacebookCallback<LoginResult> {
                override fun onSuccess(result: LoginResult) {
                    val accessToken = result.accessToken.token
                    sendTokenToBackend(accessToken, "facebook")
                }
                
                override fun onCancel() {
                    Log.d("Facebook", "Login cancelled")
                }
                
                override fun onError(error: FacebookException) {
                    Log.e("Facebook", "Login error: ${error.message}")
                }
            })
    }
    
    private fun sendTokenToBackend(accessToken: String, provider: String) {
        val url = "https://your-api-domain.com/api/accounts/$provider/login/"
        val jsonObject = JSONObject()
        jsonObject.put("access_token", accessToken)
        
        val request = Request.Builder()
            .url(url)
            .post(jsonObject.toString().toRequestBody("application/json".toMediaType()))
            .build()
        
        OkHttpClient().newCall(request).enqueue(object : Callback {
            override fun onResponse(call: Call, response: Response) {
                val responseBody = response.body?.string()
                Log.d("API", "Response: $responseBody")
            }
            
            override fun onFailure(call: Call, e: IOException) {
                Log.e("API", "Error: ${e.message}")
            }
        })
    }
}
```

## Environment Variables

Make sure to set these environment variables in your Django settings:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=your_redirect_uri

# Facebook OAuth
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_REDIRECT_URI=your_redirect_uri

# Apple ID
APPLE_CLIENT_ID=your_apple_client_id
APPLE_TEAM_ID=your_apple_team_id
APPLE_KEY_ID=your_apple_key_id
APPLE_PRIVATE_KEY=your_apple_private_key
```

## Error Handling

Common error responses:

- `400 Bad Request`: Invalid token or authentication failed
- `401 Unauthorized`: Token expired or invalid
- `500 Internal Server Error`: Server error

## Security Notes

1. Always use HTTPS in production
2. Validate tokens on the server side
3. Store JWT tokens securely in the mobile app
4. Implement token refresh logic
5. Handle token expiration gracefully

## Testing

You can test the endpoints using tools like Postman or curl:

```bash
# Google Login
curl -X POST https://your-api-domain.com/api/accounts/google/login/ \
  -H "Content-Type: application/json" \
  -d '{"access_token": "your_google_access_token"}'

# Facebook Login
curl -X POST https://your-api-domain.com/api/accounts/facebook/login/ \
  -H "Content-Type: application/json" \
  -d '{"access_token": "your_facebook_access_token"}'

# Apple Login
curl -X POST https://your-api-domain.com/api/accounts/apple/login/ \
  -H "Content-Type: application/json" \
  -d '{"id_token": "your_apple_id_token", "user": {"name": {"firstName": "John", "lastName": "Doe"}}}'
``` 