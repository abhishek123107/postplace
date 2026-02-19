# Instagram API Integration Guide

## Overview
This document describes the enhanced Instagram API integration in Postify, which now supports advanced Instagram Business features including media uploads, comprehensive error handling, and user analytics.

## Features Added

### 1. Advanced Media Upload
- **Images**: Automatic optimization and validation for Instagram
- **Videos**: MP4 video upload with proper categorization
- **Carousels**: Multi-image carousel support
- **Reels**: Video reel posting with thumbnail support
- **Smart processing**: Automatic media type detection and validation

### 2. Enhanced Error Handling
- **Business account validation**: Detects non-business accounts
- **Token management**: Handles expired and invalid tokens
- **Media errors**: Comprehensive media upload error handling
- **Content validation**: Caption length and format validation
- **Rate limiting**: Daily post limit awareness

### 3. Advanced Posting Features
- **Media attachments**: Support for images, videos, and carousels
- **Story support**: Instagram Story posting capability
- **User information**: Get current user details and metrics
- **Media insights**: Detailed analytics for media items

## API Functions

### `instagram_upload_media()`
Uploads media files to Instagram and returns container ID.

**Parameters:**
- `access_token`: Instagram access token
- `media_bytes`: File content as bytes
- `filename`: Original filename
- `media_type`: Type of media ('IMAGE', 'VIDEO', 'CAROUSEL')

**Returns:**
```python
{
    "container_id": "1234567890",
    "status": "created"
}
```

**Features:**
- Automatic media type detection
- Video support for Reels
- Carousel child item creation
- Resumable upload support

### `instagram_publish_media()`
Publishes a media container to Instagram feed.

**Parameters:**
- `access_token`: Instagram access token
- `container_id`: Media container ID from upload
- `caption`: Optional caption text

**Returns:**
```python
{
    "id": "1234567890",
    "permalink": "https://www.instagram.com/p/ABC123/",
    "status": "published"
}
```

### `instagram_create_media_carousel()`
Creates and publishes a carousel of multiple media items.

**Parameters:**
- `access_token`: Instagram access token
- `media_items`: List of media items with bytes and filenames
- `caption`: Optional caption text

**Returns:**
```python
{
    "id": "1234567890",
    "permalink": "https://www.instagram.com/p/ABC123/",
    "status": "published"
}
```

### `instagram_handle_errors()`
Converts Instagram API errors to user-friendly messages.

**Parameters:**
- `error_response`: Raw error response from Instagram API

**Returns:** User-friendly error message string

**Handled Errors:**
- Business account requirements
- Token expiration/invalidation
- Media upload failures
- Content validation errors
- Rate limiting
- Permission issues

### `instagram_get_user_info()`
Retrieves current Instagram user information.

**Parameters:**
- `access_token`: Instagram access token

**Returns:**
```python
{
    "id": "123456789",
    "username": "username",
    "account_type": "BUSINESS",
    "media_count": 150,
    "followers_count": 1000,
    "follows_count": 500
}
```

### `instagram_get_media_insights()`
Gets detailed insights for a specific media item.

**Parameters:**
- `access_token`: Instagram access token
- `media_id`: Instagram media ID
- `metrics`: List of metrics to retrieve

**Returns:**
```python
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

### `save_upload_to_disk()`
Saves uploaded media to disk with unique filenames.

**Parameters:**
- `media_bytes`: File content as bytes
- `filename`: Original filename

**Returns:** Unique filename string

## Environment Variables

Required for Instagram integration:

```bash
# Instagram Business API
INSTAGRAM_APP_ID=your_instagram_app_id
INSTAGRAM_APP_SECRET=your_instagram_app_secret

# Instagram User ID (from Facebook Business Page)
IG_USER_ID=your_instagram_user_id

# Facebook Business (required for Instagram Business)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
META_REDIRECT_URI=http://localhost:8000/auth/callback?platform=instagram
```

## Usage Examples

### Basic Image Post
```python
# Upload image
upload_result = instagram_upload_media(
    access_token="your_token",
    media_bytes=image_bytes,
    filename="photo.jpg",
    media_type='IMAGE'
)

# Publish to feed
publish_result = instagram_publish_media(
    access_token="your_token",
    container_id=upload_result["container_id"],
    caption="Beautiful sunset! 🌅 #nature"
)
```

### Video Reel Post
```python
# Upload video
upload_result = instagram_upload_media(
    access_token="your_token",
    media_bytes=video_bytes,
    filename="reel.mp4",
    media_type='VIDEO'  # Automatically sets to REELS
)

# Publish as Reel
publish_result = instagram_publish_media(
    access_token="your_token",
    container_id=upload_result["container_id"],
    caption="Amazing video content! #reels"
)
```

### Carousel Post
```python
# Prepare media items
media_items = [
    {"bytes": image1_bytes, "filename": "photo1.jpg"},
    {"bytes": image2_bytes, "filename": "photo2.jpg"},
    {"bytes": image3_bytes, "filename": "photo3.jpg"}
]

# Create carousel
carousel_result = instagram_create_media_carousel(
    access_token="your_token",
    media_items=media_items,
    caption="Multiple photos in one post! 📸 #carousel"
)
```

### Get User Information
```python
user_info = instagram_get_user_info(access_token="your_token")
print(f"Followers: {user_info['followers_count']}")
print(f"Account type: {user_info['account_type']}")
```

### Get Media Insights
```python
insights = instagram_get_media_insights(
    access_token="your_token",
    media_id="1234567890",
    metrics=["impressions", "likes", "comments", "shares"]
)

for metric in insights["insights"]:
    print(f"{metric['name']}: {metric['values'][0]['value']}")
```

## Error Handling

The integration includes comprehensive error handling:

### Business Account Errors
- **Non-business account**: "Your Instagram account is not a business account. Please convert it to a business account."

### Token Errors
- **Expired token**: "Your Instagram access has expired. Please re-authenticate your account."
- **Invalid session**: "Please re-authenticate your Instagram account."

### Media Errors
- **Upload timeout**: "Timeout downloading media. Please try again."
- **Media expired**: "Media expired. Please upload again."
- **Create failed**: "Failed to create media. Please try again."
- **Invalid format**: "Unsupported image/video format."
- **Too large**: "Image is too large. Maximum size is 30MB."
- **Aspect ratio**: "Aspect ratio not supported. Must be between 4:5 to 1.91:1."

### Content Validation
- **Caption too long**: "Caption is too long. Maximum is 2200 characters."
- **Carousel validation**: "Carousel validation failed. Please check your media items."

### Rate Limiting
- **Daily limit**: "You have reached the maximum of 25 posts per day for your account."
- **Page limit**: "Page posting for today is limited. Please try again tomorrow."

## Media Guidelines

### Image Specifications
- **Formats**: JPEG, PNG
- **Size**: Maximum 30MB
- **Resolution**: Maximum 1920x1080px
- **Aspect Ratio**: Between 4:5 and 1.91:1

### Video Specifications
- **Format**: MP4 only
- **Size**: Maximum 4GB
- **Duration**: Maximum 60 seconds for Reels
- **Resolution**: Recommended 1080x1920px

### Carousel Specifications
- **Media Count**: 2-10 items
- **Media Types**: Images only (no videos in carousels)
- **Consistency**: All items should have similar aspect ratios

## Integration Points

### Manual Posting (`/post/send`)
- Supports image, video, and carousel uploads
- Automatic media optimization
- Enhanced error messages
- Returns post URL and permalink

### Scheduled Posts (`publish_due_scheduled_posts`)
- Media upload for scheduled content
- Error logging for failed posts
- Maintains media processing

### OAuth Flow
- Enhanced authentication with business account detection
- Token storage and management
- Account verification

## Best Practices

1. **Media Preparation**
   - Use high-quality images for better engagement
   - Optimize video files for web (H.264 codec)
   - Maintain consistent aspect ratios in carousels
   - Compress images without losing quality

2. **Content Guidelines**
   - Stay within Instagram's character limits (2200 for captions)
   - Use relevant hashtags for discoverability
   - Follow Instagram's community guidelines

3. **Error Handling**
   - Implement retry logic for rate limits
   - Provide clear error messages to users
   - Log errors for debugging

4. **Rate Limiting**
   - Instagram allows 25 posts per day for business accounts
   - Implement backoff strategies
   - Monitor API usage

## Advanced Features

### Story Support
While basic implementation focuses on feed posts, the framework supports stories:

```python
# Upload story media
upload_result = instagram_upload_media(
    access_token="your_token",
    media_bytes=story_bytes,
    filename="story.jpg",
    media_type='IMAGE'  # Use appropriate story media type
)

# Publish as story (requires additional API endpoints)
# This would need additional implementation for story-specific endpoints
```

### Analytics Integration
Use insights functions for comprehensive analytics:

```python
# Get media performance
insights = instagram_get_media_insights(
    access_token="your_token",
    media_id="1234567890",
    metrics=["impressions", "reach", "likes", "comments", "shares", "saves"]
)

# Calculate engagement rate
likes = next((m for m in insights["insights"] if m["name"] == "likes"), None)
impressions = next((m for m in insights["insights"] if m["name"] == "impressions"), None)

if likes and impressions:
    engagement_rate = (likes["values"][0]["value"] / impressions["values"][0]["value"]) * 100
    print(f"Engagement rate: {engagement_rate:.2f}%")
```

## Troubleshooting

### Common Issues

1. **"Instagram account is not a business account"**
   - Convert personal account to business account
   - Connect to Facebook Business Page
   - Ensure proper permissions are granted

2. **"Missing IG_USER_ID in environment"**
   - Set the Instagram User ID environment variable
   - Get ID from Facebook Business Page settings
   - Verify page is properly connected

3. **"Failed to create Instagram media container"**
   - Check file format and size
   - Verify access token is valid
   - Ensure proper permissions

4. **"Media expired. Please upload again"**
   - Upload media within 24 hours of creation
   - Check upload timing
   - Implement retry logic

### Debug Mode
Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration Notes

This enhanced integration replaces legacy Instagram functionality:

- **Old**: Basic image posting via URL
- **New**: Direct media upload with optimization
- **Old**: Limited error handling
- **New**: Comprehensive error detection and user-friendly messages
- **Old**: Simple response format
- **New**: Rich response with permalinks and media IDs

The migration is backward compatible - existing posts will continue to work, but new posts will use the enhanced functionality with direct media uploads and better error handling.
