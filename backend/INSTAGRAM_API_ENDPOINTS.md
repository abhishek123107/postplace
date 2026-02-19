# Instagram API Endpoints

## New API Endpoints Added

### 1. Get User Information
```http
GET /instagram/user-info
```

**Query Parameters:**
- `user_id`: User ID for authentication

**Response:**
```json
{
  "id": "123456789",
  "username": "username",
  "account_type": "BUSINESS",
  "media_count": 150,
  "followers_count": 1000,
  "follows_count": 500
}
```

### 2. Get Media Insights
```http
GET /instagram/media-insights
```

**Query Parameters:**
- `user_id`: User ID for authentication
- `media_id`: Instagram media ID to get insights for
- `metrics`: Optional comma-separated list of metrics

**Response:**
```json
{
  "media_id": "1234567890",
  "insights": [
    {
      "name": "impressions",
      "values": [{"value": 1000}]
    },
    {
      "name": "likes",
      "values": [{"value": 50}]
    }
  ]
}
```

### 3. Create Media Carousel
```http
POST /instagram/create-carousel
```

**Form Data:**
- `user_id`: User ID
- `caption`: Carousel caption
- `media`: Multiple media files (2-10 images)

**Response:**
```json
{
  "id": "1234567890",
  "permalink": "https://www.instagram.com/p/ABC123/",
  "status": "published"
}
```

### 4. Upload Media
```http
POST /instagram/upload-media
```

**Form Data:**
- `user_id`: User ID
- `media`: Media file
- `media_type`: Type of media ('IMAGE', 'VIDEO', 'CAROUSEL')

**Response:**
```json
{
  "container_id": "1234567890",
  "status": "created"
}
```

## Enhanced Existing Endpoints

### /post/send (Instagram)
Now supports:
- Direct media uploads (no external URLs)
- Multiple media formats (images, videos, carousels)
- Automatic media optimization
- Enhanced error handling with user-friendly messages
- Rich response with permalinks

### /auth/connect (Instagram)
Enhanced with:
- Business account validation
- Better error messages for account type issues
- Enhanced scope validation

### /auth/callback (Instagram)
Enhanced with:
- Business account verification
- Token refresh capabilities
- User profile data retrieval

## Error Response Format

All endpoints return consistent error responses:

```json
{
  "detail": {
    "platform": "instagram",
    "error": "User-friendly error message"
  }
}
```

## Media Specifications

### Supported Formats
- **Images**: JPEG, PNG
- **Videos**: MP4 (H.264)
- **Carousels**: 2-10 images only

### Size Limits
- **Images**: Maximum 30MB
- **Videos**: Maximum 4GB
- **Carousels**: Each image max 30MB

### Resolution Guidelines
- **Images**: Maximum 1920x1080px
- **Videos**: Recommended 1080x1920px
- **Aspect Ratio**: Between 4:5 and 1.91:1

## Rate Limiting

- **Posts**: 25 posts per day for business accounts
- **Media Upload**: 100 uploads per hour
- **API Requests**: 200 requests per hour per user
- **Insights**: 100 requests per hour per user

## Authentication

All endpoints require Instagram Business OAuth tokens stored in the database. The system automatically handles token retrieval and validation.

## Business Account Requirements

Instagram integration requires:
- Instagram Business account
- Connected Facebook Business Page
- Proper API permissions
- Valid IG User ID

## Error Codes

### Common Error Types

1. **Account Issues (400)**
   - Non-business account
   - Missing permissions
   - Invalid tokens

2. **Media Errors (400)**
   - Invalid format
   - File too large
   - Unsupported aspect ratio

3. **Content Errors (400)**
   - Caption too long
   - Carousel validation failed
   - Spam detection

4. **Rate Limits (429)**
   - Daily post limit reached
   - API rate limit exceeded
   - Too many uploads

## Webhook Support

For real-time updates:
```http
POST /instagram/webhook
```

**Events Supported:**
- Media published
- Comment added
- User mentioned
- Account updated
