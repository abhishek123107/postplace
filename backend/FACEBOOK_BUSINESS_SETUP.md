# Facebook Business Setup Guide

## Overview
This guide explains how to set up Facebook Business integration for Postify, which is required for advanced Facebook posting features.

## Prerequisites

1. **Facebook Developer Account**
   - Create a Facebook Developer account
   - Verify your developer identity
   - Have a verified Facebook account

2. **Facebook Business Manager**
   - Create a Facebook Business Manager account
   - Link your developer account to Business Manager
   - Set up Business Settings

3. **Facebook Page**
   - Create or have an existing Facebook Page
   - Ensure page is properly configured
   - Have admin access to the page

## Step-by-Step Setup

### 1. Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app: "My Apps" → "Create App"
3. Choose "Business" app type
4. Configure app settings:
   - App Name: "Postify Facebook Integration"
   - App Contact Email: your email
   - Privacy Policy URL: your privacy policy
   - Terms of Service URL: your terms

### 2. Configure App Permissions

Add these permissions to your Facebook App:

**Required Permissions:**
- `pages_show_list` - Access Facebook Pages
- `business_management` - Manage business assets
- `pages_manage_posts` - Create and manage posts
- `pages_manage_engagement` - Manage engagement
- `pages_read_engagement` - Read engagement data
- `read_insights` - Access page insights

**Optional Permissions:**
- `instagram_basic` - Instagram basic access
- `instagram_content_publish` - Instagram content publishing
- `instagram_manage_comments` - Instagram comment management

### 3. Get Facebook Page ID

1. Go to your Facebook Page
2. Click "About" tab on the left
3. Scroll down to find "Page ID"
4. Note this ID for environment configuration

### 4. Configure Environment Variables

Add these to your `.env` file:

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

## Environment Variable Details

### FACEBOOK_APP_ID
- **Source**: Facebook Developers → Your App → Settings → Basic
- **Format**: Numeric string
- **Example**: "123456789012345"
- **Purpose**: Identifies your Facebook app

### FACEBOOK_APP_SECRET
- **Source**: Facebook Developers → Your App → Settings → Advanced
- **Format**: Alphanumeric string
- **Security**: Keep this secret and never expose it

### FB_PAGE_ID
- **Source**: Facebook Page → About → Page ID
- **Format**: Numeric string
- **Purpose**: Identifies your Facebook Page
- **Example**: "123456789012345"

### META_REDIRECT_URI
- **Source**: Your application's callback URL
- **Format**: Full URL with platform parameter
- **Purpose**: OAuth callback destination
- **Example**: "http://localhost:8000/auth/callback?platform=facebook"

## Testing Your Setup

### 1. Test OAuth Flow
```bash
# Start the backend
python -m uvicorn app.main:app --reload --port 8000

# Test Facebook connect
curl "http://localhost:8000/auth/connect?platform=facebook&user_id=test-user"
```

### 2. Verify Page Access
```python
# Test page info endpoint
curl "http://localhost:8000/facebook/page-info?user_id=test-user&page_id=YOUR_PAGE_ID"
```

### 3. Test Media Upload
```python
# Test with a small image
curl -X POST \
  -F "user_id=test-user" \
  -F "page_id=YOUR_PAGE_ID" \
  -F "media=@test-image.jpg" \
  -F "published=false" \
  "http://localhost:8000/facebook/upload-media"
```

## Common Setup Issues

### Issue: "Missing FB_PAGE_ID in environment"
**Solution:**
1. Go to your Facebook Page
2. Click "About" in the left menu
3. Scroll to the bottom to find "Page ID"
4. Copy the numeric ID
5. Add to environment variables

### Issue: "Please re-authenticate your Facebook account"
**Solution:**
1. Check app permissions are granted
2. Verify app is in development mode
3. Ensure redirect URI matches exactly
4. Re-authenticate the user

### Issue: "Page publishing authorization required"
**Solution:**
1. Verify `pages_manage_posts` permission
2. Check user is page admin
3. Ensure page access token is generated
4. Re-authenticate with proper scopes

### Issue: "Content violates Facebook Community Standards"
**Solution:**
1. Review Facebook Community Standards
2. Check content for policy violations
3. Remove prohibited content
4. Consider appealing if content is compliant

## Business Account Benefits

Setting up Facebook Business provides:

### Advanced Features
- **Direct Media Upload**: No more external URLs required
- **Multiple Media**: Support for multiple images/videos
- **Video Posting**: Native video and reel support
- **Page Analytics**: Detailed page insights
- **Post Analytics**: Individual post performance data

### Higher Limits
- **API Calls**: Higher rate limits for business apps
- **Media Upload**: Larger file sizes supported
- **Posting Frequency**: More generous posting limits
- **Insights**: Access to detailed analytics

### Professional Tools
- **Business Manager**: Centralized page management
- **Ad Creation**: Direct Facebook ads integration
- **Content Management**: Advanced content scheduling
- **Team Collaboration**: Multiple user access

## Security Best Practices

### Protect Your Credentials
1. **Environment Variables**: Never commit `.env` to version control
2. **App Secrets**: Use Facebook's secret management
3. **Access Control**: Limit app permissions to minimum required
4. **Monitoring**: Monitor API usage for anomalies

### Token Security
1. **Short-lived Tokens**: Use appropriate expiration times
2. **Token Refresh**: Implement proper refresh logic
3. **Secure Storage**: Encrypt tokens in database
4. **Revocation**: Allow users to revoke access

### Content Security
1. **Input Validation**: Sanitize all user inputs
2. **Content Filtering**: Implement content policy checks
3. **URL Validation**: Check for malicious URLs
4. **Rate Limiting**: Prevent abuse

## Troubleshooting

### Debug Mode
Enable detailed logging:
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

### Common Error Codes

| Error Code | Description | Solution |
|-------------|-------------|----------|
| 190 | Invalid access token | Re-authenticate user |
| 200 | Permissions error | Check app permissions |
| 490 | Access token expired | Refresh token |
| 1366046 | Photo too large | Compress image |
| 1404102 | Content violation | Review content |
| 1404078 | Insufficient permissions | Check page access |

## Production Deployment

### Required Settings
1. **HTTPS URLs**: All redirect URIs must use HTTPS
2. **Domain Verification**: Add your domain to Facebook Business
3. **App Review**: Submit app for review if needed
4. **Webhooks**: Configure webhook endpoints for real-time updates

### Monitoring
Monitor these metrics:
- API success/error rates
- Token refresh frequency
- Media upload success rates
- User engagement with posted content
- Page performance metrics

## Support Resources

### Documentation
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api/)
- [Facebook Business Help](https://www.facebook.com/business/help)
- [Meta for Developers](https://developers.facebook.com/)

### Community
- [Facebook Developers Group](https://www.facebook.com/groups/developers/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/facebook-graph-api)
- [GitHub Discussions](https://github.com/facebook/graph-api/discussions)

## Migration from Personal Account

If you're migrating from basic Facebook integration:

1. **Backup Data**: Download your Facebook data
2. **Create Business Account**: Set up Facebook Business Manager
3. **Create App**: Use Business app instead of personal
4. **Update Permissions**: Request business-level permissions
5. **Test Integration**: Verify all features work
6. **Notify Users**: Inform users about enhanced features

## Next Steps

After setting up Facebook Business:

1. **Test Basic Posting**: Verify simple text posts work
2. **Test Media Upload**: Try image and video posts
3. **Test Analytics**: Verify insights are accessible
4. **Test Multi-Page**: Try posting to different pages
5. **Scale Usage**: Gradually increase posting frequency
6. **Optimize Content**: Use analytics to improve engagement

## Advanced Configuration

### Custom Webhooks
Set up webhooks for real-time updates:
```python
# Webhook endpoint configuration
@app.post("/facebook/webhook")
def facebook_webhook():
    # Handle Facebook webhook events
    pass
```

### Custom Analytics
Implement custom analytics tracking:
```python
# Custom metrics collection
def track_facebook_metrics(post_id, metrics):
    # Store custom metrics
    pass
```

### Content Scheduling
Implement advanced scheduling:
```python
# Schedule posts for optimal times
def schedule_facebook_post(content, scheduled_time):
    # Schedule post for specific time
    pass
```

This setup enables all advanced Facebook features in Postify, providing professional-grade social media management capabilities with comprehensive media support, analytics, and multi-page management.
