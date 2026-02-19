# Facebook API Integration Guide

## Overview
This document describes the enhanced Facebook API integration in Postify, which now supports advanced Facebook Business features including media uploads, comprehensive error handling, and analytics.

## Features Added

### 1. Advanced Media Upload
- **Images**: Direct image upload with optimization
- **Videos**: MP4 video upload with proper categorization
- **Multiple Media**: Support for multiple images in posts
- **Smart Processing**: Automatic media type detection and validation

### 2. Enhanced Error Handling
- **Token Validation**: Detects expired and invalid tokens
- **Media Errors**: Comprehensive media upload error handling
- **Content Policy**: Facebook Community Standards violations
- **Rate Limiting**: Posting frequency and API limits
- **Permission Errors**: Detailed permission issue detection

### 3. Advanced Posting Features
- **Media Attachments**: Support for images and videos
- **Link Sharing**: Direct URL posting capability
- **Page Management**: Multiple Facebook page support
- **Analytics**: Detailed post and page insights
- **User Information**: Page and user data retrieval

## API Functions

### `facebook_upload_media()`
Uploads media files to Facebook and return media ID.

**Parameters:**
- `page_id`: Facebook page ID
- `page_access_token`: Page access token
- `media_bytes`: File content as bytes
- `filename`: Original filename
- `published`: Whether to publish immediately (default: False)

**Returns:**
```python
{
    "id": "1234567890",
    "post_id": "post_123456",
    "created_time": "2024-01-01T12:00:00Z"
}
```

**Features:**
- Automatic media type detection (image/video)
- Proper file categorization
- Error handling for large files
- Support for unpublished media

### `facebook_post_with_media()`
Creates a Facebook post with media and advanced options.

**Parameters:**
- `page_id`: Facebook page ID
- `page_access_token`: Page access token
- `message`: Post content
- `media_ids`: Optional list of media IDs
- `link`: Optional URL to share
- `published`: Whether to publish immediately (default: True)

**Returns:**
```python
{
    "id": "1234567890",
    "permalink_url": "https://www.facebook.com/1234567890"
}
```

### `facebook_post_video()`
Posts a video to Facebook with advanced options.

**Parameters:**
- `page_id`: Facebook page ID
- `page_access_token`: Page access token
- `video_bytes`: Video content as bytes
- `filename`: Video filename
- `description`: Video description
- `published`: Whether to publish immediately (default: True)

**Returns:**
```python
{
    "id": "1234567890",
    "permalink_url": "https://www.facebook.com/reel/1234567890"
}
```

### `facebook_handle_errors()`
Converts Facebook API errors to user-friendly messages.

**Parameters:**
- `error_response`: Raw error response from Facebook API

**Returns:** User-friendly error message string

**Handled Errors:**
- Token expiration and validation
- Media upload failures
- Content policy violations
- Rate limiting
- Permission issues
- Service availability

### `facebook_get_page_info()`
Retrieves Facebook page information.

**Parameters:**
- `page_id`: Facebook page ID
- `page_access_token`: Page access token

**Returns:**
```python
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

### `facebook_get_page_insights()`
Gets detailed insights for a Facebook page.

**Parameters:**
- `page_id`: Facebook page ID
- `page_access_token`: Page access token
- `metrics`: Optional list of metrics to retrieve
- `period`: Time period (default: "day")
- `days`: Number of days to analyze (default: 7)

**Returns:**
```python
{
    "page_id": "1234567890",
    "insights": [
        {
            "name": "page_impressions_unique",
            "values": [{"value": 1000, "end_time": "..."}]
        }
    ]
}
```

### `facebook_get_post_insights()`
Gets insights for a specific Facebook post.

**Parameters:**
- `post_id`: Facebook post ID
- `page_access_token`: Page access token
- `metrics`: Optional list of metrics to retrieve

**Returns:**
```python
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

### `facebook_get_user_pages()`
Gets all Facebook pages for a user.

**Parameters:**
- `user_access_token`: User access token

**Returns:**
```python
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

## Environment Variables

Required for Facebook integration:

```bash
# Facebook App Configuration
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
META_REDIRECT_URI=http://localhost:8000/auth/callback?platform=facebook

# Facebook Page Configuration
FB_PAGE_ID=your_facebook_page_id

# Meta Graph API
META_GRAPH_BASE=https://graph.facebook.com/v20.0
```

## Usage Examples

### Basic Text Post
```python
fb_res = facebook_post_text(
    page_id="1234567890",
    page_access_token="your_token",
    message="Hello Facebook! #socialmedia"
)
```

### Post with Image
```python
# Upload image first
media_result = facebook_upload_media(
    page_id="1234567890",
    page_access_token="your_token",
    media_bytes=image_bytes,
    filename="photo.jpg",
    published=False
)

# Create post with media
fb_res = facebook_post_with_media(
    page_id="1234567890",
    page_access_token="your_token",
    message="Check out this image! 📸",
    media_ids=[media_result["id"]],
    published=True
)
```

### Post with Video
```python
fb_res = facebook_post_video(
    page_id="1234567890",
    page_access_token="your_token",
    video_bytes=video_bytes,
    filename="video.mp4",
    description="Amazing video content! 🎥",
    published=True
)
```

### Post with Link
```python
fb_res = facebook_post_with_media(
    page_id="1234567890",
    page_access_token="your_token",
    message="Check out this amazing article!",
    link="https://example.com/article",
    published=True
)
```

### Get Page Information
```python
page_info = facebook_get_page_info(
    page_id="1234567890",
    page_access_token="your_token"
)
print(f"Page: {page_info['name']}")
print(f"Followers: {page_info['fan_count']}")
```

### Get Page Insights
```python
insights = facebook_get_page_insights(
    page_id="1234567890",
    page_access_token="your_token",
    metrics=["page_impressions_unique", "page_post_engagements"],
    period="day",
    days=7
)

for metric in insights["insights"]:
    print(f"{metric['name']}: {metric['values'][0]['value']}")
```

### Get User Pages
```python
pages = facebook_get_user_pages(user_access_token="your_token")
for page in pages:
    print(f"Page: {page['name']} ({page['id']})")
```

## Error Handling

The integration includes comprehensive error handling:

### Token Errors
- **"Please re-authenticate your Facebook account"**: Token validation failed
- **"Access token expired, please re-authenticate"**: Token expired (error 490)
- **"Access token has been revoked, please re-authenticate"**: Token revoked

### Media Errors
- **"Photos should be smaller than 4 MB and saved as JPG, PNG"**: File too large (error 1366046)
- **"You are posting too fast, please slow down"**: Rate limiting (error 1390008)

### Content Policy Errors
- **"Content flagged as abusive by Facebook"**: Content violation (error 1346003)
- **"Content violates Facebook Community Standards"**: Policy violation (error 1404102)
- **"Security check required by Facebook"**: Security review needed (error 1404006)

### Permission Errors
- **"Page publishing authorization required, please re-authenticate"**: Insufficient permissions (error 1404078)
- **"Cannot post Facebook.com links"**: Link restriction (error 1609008)

### Service Errors
- **"Facebook service temporarily unavailable"**: Service outage (error 1363047, 1609010)
- **"Account temporarily limited for security reasons"**: Account restricted (error 1404112)

## Media Guidelines

### Image Specifications
- **Formats**: JPEG, PNG, GIF, BMP
- **Size**: Maximum 4MB
- **Resolution**: Recommended 1200x630px for feed posts
- **Aspect Ratio**: Any, but 1.91:1 is recommended

### Video Specifications
- **Formats**: MP4, MOV
- **Size**: Maximum 4GB
- **Duration**: Maximum 240 minutes
- **Resolution**: Recommended 1080x1920px for vertical

### Content Guidelines
- **Text Length**: Maximum 63,206 characters
- **Links**: Facebook.com links may be restricted
- **Hashtags**: Up to 30 hashtags per post
- **Mentions**: Up to 50 tags per post

## Integration Points

### Manual Posting (`/post/send`)
- Supports image and video uploads
- Automatic media optimization
- Enhanced error messages
- Returns post URL and permalink

### Scheduled Posts (`publish_due_scheduled_posts`)
- Media upload for scheduled content
- Error logging for failed posts
- Maintains page posting functionality

### OAuth Flow
- Enhanced authentication with page selection
- Token storage and management
- Page access token generation

## Best Practices

1. **Media Preparation**
   - Use high-quality images for better engagement
   - Optimize videos for web (H.264 codec)
   - Compress images without losing quality
   - Test media uploads before production

2. **Content Guidelines**
   - Stay within Facebook's character limits
   - Use relevant hashtags for discoverability
   - Follow Facebook's community standards
   - Avoid spammy content patterns

3. **Error Handling**
   - Implement retry logic for rate limits
   - Provide clear error messages to users
   - Log errors for debugging
   - Monitor API usage

4. **Rate Limiting**
   - Facebook allows reasonable posting limits
   - Implement backoff strategies
   - Monitor page-level limits
   - Respect content policy restrictions

## Advanced Features

### Multi-Page Support
```python
# Get all user pages
pages = facebook_get_user_pages(user_access_token="user_token")

# Post to specific page
for page in pages:
    if page["id"] == target_page_id:
        fb_res = facebook_post_text(
            page_id=page["id"],
            page_access_token=page["access_token"],
            message="Targeted post content"
        )
        break
```

### Analytics Integration
```python
# Get comprehensive page insights
insights = facebook_get_page_insights(
    page_id="1234567890",
    page_access_token="your_token",
    metrics=[
        "page_impressions_unique",
        "page_post_engagements",
        "page_daily_follows",
        "page_video_views"
    ],
    period="week",
    days=30
)

# Process insights data
for metric in insights["insights"]:
    metric_name = metric["name"]
    for value_data in metric["values"]:
        date = value_data["end_time"]
        value = value_data["value"]
        print(f"{metric_name} on {date}: {value}")
```

### Content Scheduling
```python
# Create unpublished media first
media_result = facebook_upload_media(
    page_id="1234567890",
    page_access_token="your_token",
    media_bytes=image_bytes,
    filename="scheduled_image.jpg",
    published=False  # Keep unpublished
)

# Schedule post for later
scheduled_time = "2024-01-01T18:00:00Z"
fb_res = facebook_post_with_media(
    page_id="1234567890",
    page_access_token="your_token",
    message="Scheduled post content",
    media_ids=[media_result["id"]],
    published=True  # This would be scheduled via API
)
```

## Troubleshooting

### Common Issues

1. **"Missing FB_PAGE_ID in environment"**
   - Set the Facebook Page ID environment variable
   - Get page ID from Facebook Page settings
   - Ensure page is properly configured

2. **"Please re-authenticate your Facebook account"**
   - User needs to reconnect their Facebook account
   - Check token expiration times
   - Implement automatic token refresh

3. **"Photos should be smaller than 4 MB"**
   - Compress images before upload
   - Use JPEG format for better compression
   - Check file size before uploading

4. **"Content violates Facebook Community Standards"**
   - Review content against Facebook policies
   - Remove prohibited content
   - Appeal content restrictions if necessary

### Debug Mode
Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test API Calls
Use Facebook's Graph API Explorer:
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Test page endpoints
4. Verify permissions and responses

## Migration Notes

This enhanced integration replaces legacy Facebook functionality:

- **Old**: Basic text posting only
- **New**: Direct media upload with optimization
- **Old**: Limited error handling
- **New**: Comprehensive error detection and user-friendly messages
- **Old**: Simple response format
- **New**: Rich response with permalinks and media IDs

The migration is backward compatible - existing posts will continue to work, but new posts will use the enhanced functionality with direct media uploads and better error handling.

## Security Considerations

1. **Token Security**
   - Store access tokens securely
   - Implement token expiration handling
   - Use HTTPS for all API calls
   - Validate token permissions

2. **Content Security**
   - Validate user input
   - Sanitize post content
   - Check for malicious URLs
   - Implement content filtering

3. **API Security**
   - Use official Facebook SDK when possible
   - Validate API responses
   - Implement request signing
   - Monitor for suspicious activity

This enhanced Facebook integration provides professional-grade social media management capabilities with comprehensive media support, advanced error handling, and detailed analytics.
