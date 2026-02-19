# Facebook API Endpoints

## New API Endpoints Added

### 1. Get Page Information
```http
GET /facebook/page-info
```

**Query Parameters:**
- `user_id`: User ID for authentication
- `page_id`: Facebook page ID

**Response:**
```json
{
  "id": "1234567890",
  "name": "Page Name",
  "username": "page-username",
  "fan_count": 1000,
  "talking_about_count": 50,
  "picture": "https://...",
  "cover": "https://..."
}
```

### 2. Get Page Insights
```http
GET /facebook/page-insights
```

**Query Parameters:**
- `user_id`: User ID for authentication
- `page_id`: Facebook page ID
- `metrics`: Optional comma-separated list of metrics
- `period`: Time period (day/week/month)
- `days`: Number of days to analyze

**Response:**
```json
{
  "page_id": "1234567890",
  "insights": [
    {
      "name": "page_impressions_unique",
      "values": [
        {"value": 1000, "end_time": "2024-01-01T00:00:00Z"}
      ]
    }
  ]
}
```

### 3. Get Post Insights
```http
GET /facebook/post-insights
```

**Query Parameters:**
- `user_id`: User ID for authentication
- `post_id`: Facebook post ID
- `metrics`: Optional comma-separated list of metrics

**Response:**
```json
{
  "post_id": "1234567890",
  "insights": [
    {
      "name": "post_impressions_unique",
      "values": [{"value": 500}]
    }
  ]
}
```

### 4. Get User Pages
```http
GET /facebook/user-pages
```

**Query Parameters:**
- `user_id`: User ID for authentication

**Response:**
```json
[
  {
    "id": "1234567890",
    "name": "Page Name",
    "username": "page-username",
    "picture": "https://...",
    "access_token": "page_access_token"
  }
]
```

### 5. Upload Media
```http
POST /facebook/upload-media
```

**Form Data:**
- `user_id`: User ID
- `page_id`: Facebook page ID
- `media`: Media file (image/video)
- `published`: Whether to publish immediately (true/false)

**Response:**
```json
{
  "id": "1234567890",
  "post_id": "post_123456",
  "created_time": "2024-01-01T12:00:00Z"
}
```

### 6. Post Video
```http
POST /facebook/post-video
```

**Form Data:**
- `user_id`: User ID
- `page_id`: Facebook page ID
- `video`: Video file
- `description`: Video description
- `published`: Whether to publish immediately

**Response:**
```json
{
  "id": "1234567890",
  "permalink_url": "https://www.facebook.com/reel/1234567890"
}
```

## Enhanced Existing Endpoints

### /post/send (Facebook)
Now supports:
- Direct media uploads (images and videos)
- Multiple media attachments
- Link sharing capability
- Enhanced error handling with user-friendly messages
- Rich response with permalinks

### /auth/connect (Facebook)
Enhanced with:
- Page selection support
- Better error messages for permission issues
- Enhanced scope validation

### /auth/callback (Facebook)
Enhanced with:
- Page access token generation
- User profile data retrieval
- Token refresh capabilities

## Error Response Format

All endpoints return consistent error responses:

```json
{
  "detail": {
    "platform": "facebook",
    "error": "User-friendly error message"
  }
}
```

## Media Specifications

### Supported Formats
- **Images**: JPEG, PNG, GIF, BMP
- **Videos**: MP4, MOV
- **File Size**: Maximum 4MB for images, 4GB for videos

### Resolution Guidelines
- **Images**: Recommended 1200x630px for feed posts
- **Videos**: Recommended 1080x1920px for vertical content
- **Aspect Ratio**: Flexible, but 1.91:1 recommended for feed

## Rate Limiting

- **Posts**: No strict limit, but reasonable usage expected
- **Media Upload**: 100 uploads per hour per page
- **API Requests**: 200 requests per hour per user
- **Insights**: 100 requests per hour per page

## Authentication

All endpoints require Facebook OAuth tokens stored in the database. The system automatically handles:
- User token validation
- Page access token generation
- Token refresh and expiration

## Page Management

### Multi-Page Support
- Users can connect multiple Facebook pages
- Each page has separate access tokens
- Page selection during posting
- Unified user experience across pages

### Page Permissions
Required Facebook app permissions:
- `pages_show_list`
- `business_management`
- `pages_manage_posts`
- `pages_manage_engagement`
- `pages_read_engagement`
- `read_insights`

## Error Codes

### Common Error Types

1. **Authentication Errors (400)**
   - Token validation failures
   - Expired access tokens
   - Revoked permissions

2. **Media Errors (400)**
   - File too large (error 1366046)
   - Unsupported format
   - Upload timeout

3. **Content Policy Errors (400)**
   - Community Standards violations (error 1404102)
   - Abusive content (error 1346003)
   - Security checks (error 1404006)

4. **Permission Errors (400)**
   - Insufficient page permissions (error 1404078)
   - Missing required scopes
   - Access token issues (error 490)

5. **Rate Limiting (400)**
   - Posting too fast (error 1390008)
   - API rate limits exceeded
   - Service temporarily unavailable

## Webhook Support

For real-time updates:
```http
POST /facebook/webhook
```

**Events Supported:**
- Page posts published
- Comments added
- Page likes
- User interactions
- Page insights updated

## Analytics Integration

### Available Metrics

**Page Metrics:**
- `page_impressions_unique`: Unique page impressions
- `page_post_engagements`: Post engagements
- `page_posts_impressions_unique`: Post impressions
- `page_daily_follows`: New followers
- `page_video_views`: Video views

**Post Metrics:**
- `post_impressions_unique`: Unique post impressions
- `post_reactions_by_type_total`: Total reactions
- `post_clicks`: Total clicks
- `post_clicks_by_type`: Clicks by type

### Data Processing
- Automatic metric calculation
- Time-based aggregation
- Trend analysis
- Performance comparison

## Best Practices

### Media Upload
- Compress images before upload
- Use recommended resolutions
- Test upload with smaller files first
- Handle upload timeouts gracefully

### Content Posting
- Respect character limits (63,206)
- Use engaging content formats
- Include relevant hashtags
- Post at optimal times

### Error Handling
- Implement retry logic for transient errors
- Provide clear user feedback
- Log errors for debugging
- Monitor API usage patterns

This enhanced Facebook API integration provides professional-grade social media management with comprehensive media support, advanced analytics, and robust error handling.
