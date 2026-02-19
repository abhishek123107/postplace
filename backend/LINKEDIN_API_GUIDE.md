# LinkedIn API Integration Guide

## Overview
This document describes the enhanced LinkedIn API integration in Postify, which now supports modern LinkedIn posting features including media uploads, proper text formatting, and improved error handling.

## Features Added

### 1. Media Upload Support
- **Images**: Upload single or multiple images
- **Videos**: Upload MP4 videos with chunked upload
- **Documents**: Upload PDF documents
- **Automatic detection**: File type detection based on extension

### 2. Enhanced Text Formatting
- **Markdown escaping**: Proper escaping of special characters for LinkedIn
- **Mention preservation**: Company mentions are preserved while escaping other content
- **Special character handling**: Handles `#`, `@`, `_`, `*`, `|`, `[]`, `()`, `{}` properly

### 3. Modern API Endpoints
- **Posts API**: Uses `/rest/posts` instead of legacy `/v2/ugcPosts`
- **Media API**: Uses `/rest/{images|videos|documents}` for uploads
- **Version headers**: Includes `LinkedIn-Version: 202601` header

## API Functions

### `linkedin_upload_media()`
Uploads media files to LinkedIn and returns media URN.

**Parameters:**
- `access_token`: LinkedIn access token
- `author_urn`: Author URN (e.g., `urn:li:person:123`)
- `media_bytes`: File content as bytes
- `filename`: Original filename

**Returns:**
```python
{
    "media_urn": "urn:li:image:123",
    "status": "uploaded"
}
```

### `linkedin_fix_text()`
Escapes special characters for LinkedIn markdown while preserving mentions.

**Parameters:**
- `text`: Original text content

**Returns:** Escaped text safe for LinkedIn API

### `linkedin_share_post()`
Creates a LinkedIn post with optional media and article links.

**Parameters:**
- `author_urn`: Author URN
- `access_token`: LinkedIn access token
- `text`: Post content
- `article_url`: Optional article URL to share
- `media_urns`: Optional list of media URNs

**Returns:**
```python
{
    "restli_id": "123456789",
    "status_code": 201,
    "post_url": "https://www.linkedin.com/feed/update/123456789"
}
```

## Environment Variables

Required for LinkedIn integration:

```bash
# LinkedIn OAuth
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/auth/callback?platform=linkedin

# LinkedIn Posting
LINKEDIN_AUTHOR_URN=urn:li:person:YOUR_PERSON_ID
```

## Usage Examples

### Basic Text Post
```python
result = linkedin_share_post(
    author_urn="urn:li:person:123",
    access_token="your_token",
    text="Hello LinkedIn! #professional"
)
```

### Post with Image
```python
# Upload image first
upload_result = linkedin_upload_media(
    access_token="your_token",
    author_urn="urn:li:person:123",
    media_bytes=image_bytes,
    filename="post.jpg"
)

# Create post with image
result = linkedin_share_post(
    author_urn="urn:li:person:123",
    access_token="your_token",
    text="Check out this image! 📸",
    media_urns=[upload_result["media_urn"]]
)
```

### Post with Article Link
```python
result = linkedin_share_post(
    author_urn="urn:li:person:123",
    access_token="your_token",
    text="Great article about tech trends",
    article_url="https://example.com/article"
)
```

### Post with Company Mention
```python
text = "Excited to work with @[Microsoft](urn:li:organization:1035) on this project!"
escaped_text = linkedin_fix_text(text)

result = linkedin_share_post(
    author_urn="urn:li:person:123",
    access_token="your_token",
    text=escaped_text
)
```

## Error Handling

The integration includes comprehensive error handling:

- **Upload failures**: Clear error messages for media upload issues
- **API errors**: Detailed error responses from LinkedIn API
- **Validation**: Proper validation of required parameters
- **Chunked uploads**: Handles large file uploads in chunks

## Integration Points

### Manual Posting (`/post/send`)
- Supports image uploads with automatic media upload
- Returns post URL for easy sharing
- Proper error handling and user feedback

### Scheduled Posts (`publish_due_scheduled_posts`)
- Automatically uploads media for scheduled posts
- Maintains blog post URL sharing functionality
- Error logging for failed scheduled posts

### OAuth Flow
- Enhanced scopes for better API access
- Proper state management for security
- Token storage and refresh capabilities

## Best Practices

1. **Media Preparation**
   - Resize images to optimal dimensions (recommended: 1200x627)
   - Use JPEG format for better compression
   - Keep videos under LinkedIn's size limits

2. **Text Formatting**
   - Use `linkedin_fix_text()` for all post content
   - Preserve mentions using the format `@[Name](urn:li:organization:id)`
   - Keep posts under 3000 characters

3. **Error Handling**
   - Always check API response status codes
   - Handle media upload failures gracefully
   - Log errors for debugging

4. **Rate Limiting**
   - LinkedIn has posting limits (2 concurrent jobs)
   - Implement backoff for failed requests
   - Monitor API usage

## Troubleshooting

### Common Issues

1. **"Missing LINKEDIN_AUTHOR_URN"**
   - Set the environment variable with your LinkedIn person URN
   - Format: `urn:li:person:YOUR_PERSON_ID`

2. **Media Upload Failures**
   - Check file size limits
   - Verify file format support
   - Ensure proper authentication

3. **Text Formatting Issues**
   - Use `linkedin_fix_text()` to escape special characters
   - Preserve mention format in company tags

4. **API Version Errors**
   - Ensure `LinkedIn-Version: 202601` header is set
   - Update API endpoints if deprecated

## Migration Notes

This enhanced integration replaces the legacy LinkedIn posting functionality:

- **Old**: Used `/v2/ugcPosts` endpoint
- **New**: Uses `/rest/posts` endpoint
- **Old**: Basic text posting only
- **New**: Full media support with proper formatting
- **Old**: Limited error handling
- **New**: Comprehensive error handling and validation

The migration is backward compatible - existing posts will continue to work, but new posts will use the enhanced functionality.
