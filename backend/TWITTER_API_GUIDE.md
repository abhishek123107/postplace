# X (Twitter) API Integration Guide

## Overview
This document describes the enhanced X (Twitter) API integration in Postify, which now supports advanced posting features including media uploads, comprehensive error handling, and user analytics.

## Features Added

### 1. Advanced Media Upload
- **Images**: Automatic optimization and resizing for Twitter
- **Videos**: MP4 video upload with proper categorization
- **GIFs**: Animated GIF support with correct media category
- **Smart processing**: Automatic image conversion to JPEG for better compression

### 2. Enhanced Error Handling
- **Duplicate content**: Detects and prevents duplicate tweets
- **Rate limiting**: Handles Twitter's usage caps gracefully
- **URL validation**: Checks for disallowed URLs
- **Video duration**: Validates video length restrictions
- **Specific error messages**: User-friendly error descriptions

### 3. Advanced Posting Features
- **Media attachments**: Support for up to 4 images or 1 video
- **Reply functionality**: Thread and reply support
- **User information**: Get current user details and metrics
- **Tweet metrics**: Detailed analytics for individual tweets

## API Functions

### `twitter_upload_media()`
Uploads media files to Twitter/X and returns media ID.

**Parameters:**
- `access_token`: Twitter access token
- `access_token_secret`: Twitter access token secret
- `api_key`: Twitter API key
- `api_secret`: Twitter API secret
- `media_bytes`: File content as bytes
- `filename`: Original filename

**Returns:**
```python
{
    "media_id": "1234567890",
    "status": "uploaded"
}
```

**Features:**
- Automatic image resizing (max 1000px width)
- Format conversion to JPEG for better compression
- Support for videos, GIFs, and images
- Proper media categorization

### `twitter_post_with_media()`
Creates a tweet with media and advanced options.

**Parameters:**
- `access_token`: Twitter access token
- `access_token_secret`: Twitter access token secret
- `api_key`: Twitter API key
- `api_secret`: Twitter API secret
- `content`: Tweet text content
- `media_ids`: Optional list of media IDs
- `reply_to_tweet_id`: Optional tweet ID to reply to
- `who_can_reply`: Optional reply restrictions

**Returns:**
```python
{
    "id": "1234567890",
    "text": "Tweet content",
    "created_at": "2024-01-01T12:00:00Z",
    "user": {
        "screen_name": "username",
        "name": "Display Name"
    },
    "entities": {},
    "public_metrics": {}
}
```

### `twitter_get_user_info()`
Retrieves current user information from Twitter/X.

**Parameters:**
- `access_token`: Twitter access token
- `access_token_secret`: Twitter access token secret
- `api_key`: Twitter API key
- `api_secret`: Twitter API secret

**Returns:**
```python
{
    "id": "123456789",
    "username": "username",
    "name": "Display Name",
    "verified": True,
    "profile_image_url": "https://...",
    "protected": False,
    "followers_count": 1000,
    "following_count": 500,
    "tweet_count": 2500
}
```

### `twitter_get_tweet_metrics()`
Gets detailed metrics for a specific tweet.

**Parameters:**
- `access_token`: Twitter access token
- `access_token_secret`: Twitter access token secret
- `api_key`: Twitter API key
- `api_secret`: Twitter API secret
- `tweet_id`: Tweet ID to get metrics for

**Returns:**
```python
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

## Environment Variables

Required for X (Twitter) integration:

```bash
# Twitter API Credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_CONSUMER_KEY=your_consumer_key  # Alternative to API_KEY
TWITTER_CONSUMER_SECRET=your_consumer_secret  # Alternative to API_SECRET

# Twitter OAuth
TWITTER_REDIRECT_URI=http://localhost:8000/auth/callback?platform=twitter
```

## Usage Examples

### Basic Text Post
```python
tweet_result = twitter_post_with_media(
    access_token="your_token",
    access_token_secret="your_secret",
    api_key="your_api_key",
    api_secret="your_api_secret",
    content="Hello Twitter! #socialmedia"
)
```

### Post with Image
```python
# Upload image first
upload_result = twitter_upload_media(
    access_token="your_token",
    access_token_secret="your_secret",
    api_key="your_api_key",
    api_secret="your_api_secret",
    media_bytes=image_bytes,
    filename="post.jpg"
)

# Create tweet with image
tweet_result = twitter_post_with_media(
    access_token="your_token",
    access_token_secret="your_secret",
    api_key="your_api_key",
    api_secret="your_api_secret",
    text="Check out this image! 📸",
    media_ids=[upload_result["media_id"]]
)
```

### Reply to Tweet
```python
tweet_result = twitter_post_with_media(
    access_token="your_token",
    access_token_secret="your_secret",
    api_key="your_api_key",
    api_secret="your_api_secret",
    text="Great point! I agree.",
    reply_to_tweet_id="1234567890"
)
```

### Get User Information
```python
user_info = twitter_get_user_info(
    access_token="your_token",
    access_token_secret="your_secret",
    api_key="your_api_key",
    api_secret="your_api_secret"
)
```

### Get Tweet Metrics
```python
metrics = twitter_get_tweet_metrics(
    access_token="your_token",
    access_token_secret="your_secret",
    api_key="your_api_key",
    api_secret="your_api_secret",
    tweet_id="1234567890"
)
```

## Error Handling

The integration includes comprehensive error handling:

### Specific Error Types

1. **Duplicate Content**
   ```python
   HTTPException: "You have already posted this content. Please wait before posting again."
   ```

2. **Rate Limiting**
   ```python
   HTTPException: "Twitter posting limit reached. Please try again later."
   ```

3. **Invalid URL**
   ```python
   HTTPException: "The tweet contains a URL that is not allowed on X."
   ```

4. **Video Duration**
   ```python
   HTTPException: "The video is longer than the allowed duration for this account."
   ```

5. **Media Upload Failures**
   ```python
   HTTPException: "Failed to upload media to Twitter: [specific error]"
   ```

## Media Guidelines

### Image Specifications
- **Formats**: JPEG, PNG, GIF, WebP
- **Size**: Up to 5MB
- **Dimensions**: Automatic optimization to max 1000px width
- **Aspect Ratio**: Maintained during resizing
- **Quality**: JPEG compression at 85% for optimal size

### Video Specifications
- **Format**: MP4 only
- **Size**: Up to 512MB
- **Duration**: Account-dependent (usually 2:20 for most accounts)
- **Resolution**: Recommended 1280x720 (720p)

### GIF Specifications
- **Format**: Animated GIF
- **Size**: Up to 15MB
- **Duration**: Up to 60 seconds

## Integration Points

### Manual Posting (`/post/send`)
- Supports image, video, and GIF uploads
- Automatic media optimization
- Enhanced error messages
- Returns tweet URL for easy sharing

### Scheduled Posts (`publish_due_scheduled_posts`)
- Media upload for scheduled content
- Error logging for failed posts
- Maintains thread functionality

### OAuth Flow
- Enhanced authentication with user details
- Token storage and management
- Account verification

## Best Practices

1. **Media Preparation**
   - Use high-quality images for better engagement
   - Keep videos short and engaging
   - Optimize file sizes before upload

2. **Content Guidelines**
   - Stay within Twitter's character limits
   - Use relevant hashtags for discoverability
   - Avoid duplicate content within 24 hours

3. **Error Handling**
   - Implement retry logic for rate limits
   - Provide clear error messages to users
   - Log errors for debugging

4. **Rate Limiting**
   - Twitter allows 300 posts per 3 hours
   - Implement backoff strategies
   - Monitor API usage

## Advanced Features

### Thread Support
While the basic implementation supports replies, full thread functionality can be extended:

```python
# Post first tweet
first_tweet = twitter_post_with_media(...)

# Reply to create thread
second_tweet = twitter_post_with_media(
    reply_to_tweet_id=first_tweet["id"],
    ...
)
```

### Analytics Integration
Use the metrics functions for comprehensive analytics:

```python
# Get tweet performance
metrics = twitter_get_tweet_metrics(...)

# Track engagement
engagement_rate = (
    metrics["public_metrics"]["like_count"] + 
    metrics["public_metrics"]["retweet_count"]
) / user_info["followers_count"]
```

### Auto-Reposting
Implement automated reposting based on engagement:

```python
# Check if tweet meets criteria
if metrics["public_metrics"]["like_count"] >= threshold:
    # Repost with comment
    twitter_post_with_media(
        content="Great discussion! 🔄",
        reply_to_tweet_id=tweet_id
    )
```

## Troubleshooting

### Common Issues

1. **"Twitter credentials missing"**
   - Verify all environment variables are set
   - Check API key and secret format

2. **"Failed to upload media"**
   - Check file size limits
   - Verify supported formats
   - Ensure proper authentication

3. **"Twitter posting limit reached"**
   - Wait for rate limit to reset
   - Implement backoff strategy
   - Check API usage dashboard

4. **"You have already posted this content"**
   - Modify content slightly
   - Wait before reposting
   - Check for accidental duplicates

### Debug Mode
Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration Notes

This enhanced integration replaces the legacy Twitter functionality:

- **Old**: Basic text posting only
- **New**: Full media support with optimization
- **Old**: Limited error handling
- **New**: Comprehensive error detection and user-friendly messages
- **Old**: Simple response format
- **New**: Rich response with user data and metrics

The migration is backward compatible - existing posts will continue to work, but new posts will use the enhanced functionality with media support and better error handling.
