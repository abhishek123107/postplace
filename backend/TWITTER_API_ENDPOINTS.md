# X (Twitter) API Endpoints

## New API Endpoints Added

### 1. Get User Information
```http
GET /twitter/user-info
```

**Query Parameters:**
- `user_id`: User ID for authentication

**Response:**
```json
{
  "id": "123456789",
  "username": "username",
  "name": "Display Name",
  "verified": true,
  "profile_image_url": "https://...",
  "protected": false,
  "followers_count": 1000,
  "following_count": 500,
  "tweet_count": 2500
}
```

### 2. Get Tweet Metrics
```http
GET /twitter/tweet-metrics
```

**Query Parameters:**
- `user_id`: User ID for authentication
- `tweet_id`: Tweet ID to get metrics for

**Response:**
```json
{
  "id": "1234567890",
  "text": "Full tweet text",
  "created_at": "2024-01-01T12:00:00Z",
  "public_metrics": {
    "retweet_count": 10,
    "like_count": 50,
    "reply_count": 5,
    "quote_count": 2
  },
  "entities": {}
}
```

### 3. Post Tweet with Advanced Options
```http
POST /twitter/post-advanced
```

**Form Data:**
- `user_id`: User ID
- `content`: Tweet text
- `media`: Optional media files
- `reply_to_tweet_id`: Optional tweet ID to reply to
- `who_can_reply`: Optional reply restrictions

**Response:**
```json
{
  "id": "1234567890",
  "text": "Tweet content",
  "created_at": "2024-01-01T12:00:00Z",
  "user": {
    "screen_name": "username",
    "name": "Display Name"
  },
  "url": "https://twitter.com/username/status/1234567890"
}
```

## Enhanced Existing Endpoints

### /post/send (Twitter)
Now supports:
- Multiple media uploads (up to 4 images or 1 video)
- Automatic image optimization
- Enhanced error handling
- Rich response with tweet URL

### /auth/connect (Twitter)
Enhanced with:
- Better error messages
- Improved token handling
- User information retrieval

### /auth/callback (Twitter)
Enhanced with:
- Comprehensive token storage
- User profile data
- Verification status

## Error Response Format

All endpoints return consistent error responses:

```json
{
  "detail": {
    "platform": "twitter",
    "error": "Specific error message"
  }
}
```

## Rate Limiting

- **Posts**: 300 tweets per 3 hours
- **Media Upload**: 300 uploads per 3 hours
- **User Info**: 75 requests per 15 minutes
- **Tweet Metrics**: 75 requests per 15 minutes

## Authentication

All endpoints require Twitter OAuth tokens stored in the database. The system automatically handles token retrieval and validation.
