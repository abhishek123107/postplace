# Instagram Business Setup Guide

## Overview
This guide explains how to set up Instagram Business integration for Postify, which is required for advanced Instagram posting features.

## Prerequisites

1. **Facebook Business Account**
   - Create a Facebook Business Manager account
   - Verify your business identity
   - Have a business email and phone number

2. **Instagram Business Account**
   - Convert your personal Instagram account to a business account
   - Or create a new Instagram Business account
   - Connect to your Facebook Business Page

3. **Facebook Business Page**
   - Create a Facebook Business Page
   - Link it to your Instagram Business account
   - Ensure proper permissions are granted

## Step-by-Step Setup

### 1. Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app: "My Apps" → "Create App"
3. Choose "Business" app type
4. Add "Instagram Basic Display" platform
5. Configure app settings:
   - App Name: "Postify Instagram Integration"
   - App Contact Email: your email
   - Privacy Policy URL: your privacy policy
   - Terms of Service URL: your terms

### 2. Configure Instagram Permissions

Add these permissions to your Facebook App:

**Required Permissions:**
- `instagram_basic`
- `instagram_content_publish`
- `instagram_manage_comments`
- `instagram_manage_insights`
- `pages_show_list`
- `pages_read_engagement`
- `business_management`

**Optional Permissions:**
- `instagram_manage_events`
- `instagram_manage_topics`
- `instagram_manage_custom_audiences`

### 3. Get Instagram User ID

1. Go to Instagram Business Settings
2. Navigate to "Accounts" → "Linked Accounts"
3. Find your Instagram Business Account ID
4. Note this ID for environment configuration

### 4. Configure Environment Variables

Add these to your `.env` file:

```bash
# Instagram Business API
INSTAGRAM_APP_ID=your_instagram_app_id
INSTAGRAM_APP_SECRET=your_instagram_app_secret

# Instagram User ID (from Business Settings)
IG_USER_ID=your_instagram_user_id

# Facebook Business (required for Instagram)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
META_REDIRECT_URI=http://localhost:8000/auth/callback?platform=instagram
```

## Environment Variable Details

### INSTAGRAM_APP_ID
- **Source**: Facebook Developers → Your App → Settings → Basic
- **Format**: Numeric string
- **Example**: "123456789012345"

### INSTAGRAM_APP_SECRET
- **Source**: Facebook Developers → Your App → Settings → Advanced
- **Format**: Alphanumeric string
- **Security**: Keep this secret and never expose it

### IG_USER_ID
- **Source**: Instagram Business Settings → Accounts
- **Format**: Numeric string
- **Purpose**: Identifies your Instagram Business account
- **Example**: "17841401234567890"

### FACEBOOK_APP_ID/SECRET
- **Source**: Same as Instagram app (they're linked)
- **Purpose**: Required for Instagram Business API access
- **Note**: Instagram Business uses Facebook's Graph API

## Testing Your Setup

### 1. Test OAuth Flow
```bash
# Start the backend
python -m uvicorn app.main:app --reload --port 8000

# Test Instagram connect
curl "http://localhost:8000/auth/connect?platform=instagram&user_id=test-user"
```

### 2. Verify Business Account
```python
# Test user info endpoint
curl "http://localhost:8000/instagram/user-info?user_id=test-user"
```

### 3. Test Media Upload
```python
# Test with a small image
curl -X POST \
  -F "user_id=test-user" \
  -F "media=@test-image.jpg" \
  -F "media_type=IMAGE" \
  "http://localhost:8000/instagram/upload-media"
```

## Common Setup Issues

### Issue: "Instagram account is not a business account"
**Solution:**
1. Open Instagram app
2. Go to Settings → Account → Switch to Professional Account
3. Choose "Business"
4. Follow the setup wizard
5. Re-authenticate in Postify

### Issue: "Missing IG_USER_ID"
**Solution:**
1. Go to [Facebook Business Settings](https://business.facebook.com/settings)
2. Navigate to "Instagram" → "Instagram Accounts"
3. Find your business account
4. Copy the "Instagram Account ID"
5. Add to environment variables

### Issue: "Not enough permissions"
**Solution:**
1. Go to Facebook Developers → Your App
2. Review "App Review" status
3. Request additional permissions if needed
4. Re-authenticate to grant new permissions

### Issue: "Page posting for today is limited"
**Solution:**
- Wait until the next day (resets at midnight PST)
- Check your posting frequency
- Consider using Facebook Business Manager to request higher limits

## Business Account Benefits

Setting up Instagram Business provides:

### Advanced Features
- **Direct Media Upload**: No more external URLs
- **Carousel Support**: Multiple images in one post
- **Video/Reels**: Native video posting
- **Stories**: Instagram Story integration
- **Insights**: Detailed analytics data

### Higher Limits
- **Posts**: 25 posts per day (vs. personal limits)
- **API Calls**: Higher rate limits
- **Media Upload**: Larger file sizes supported
- **Analytics**: More detailed metrics

### Professional Tools
- **Business Inbox**: Unified message management
- **Ad Creation**: Direct Instagram ads integration
- **Shopping Tags**: Product tagging support
- **Branded Content**: Branded content tools

## Security Best Practices

### Protect Your Credentials
1. **Environment Variables**: Never commit `.env` to version control
2. **App Secrets**: Use Facebook's secret management
3. **Access Control**: Limit app permissions to minimum required
4. **Monitoring**: Monitor API usage for anomalies

### Token Security
1. **Short-lived Tokens**: Use short expiration times
2. **Token Refresh**: Implement proper refresh logic
3. **Secure Storage**: Encrypt tokens in database
4. **Revocation**: Allow users to revoke access

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
3. Test Instagram endpoints
4. Verify permissions and responses

### Common Error Codes

| Error Code | Description | Solution |
|-------------|-------------|----------|
| 190 | Invalid access token | Re-authenticate user |
| 200 | Permissions error | Check app permissions |
| 2 | API Rate Limit | Implement backoff |
| 10 | User not found | Verify user ID |

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

## Support Resources

### Documentation
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/)
- [Facebook Business Help](https://www.facebook.com/business/help)
- [Meta for Developers](https://developers.facebook.com/)

### Community
- [Meta Developers Group](https://www.facebook.com/groups/developers/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/instagram-api)
- [GitHub Discussions](https://github.com/facebook/instagram-api/discussions)

## Migration from Personal Account

If you're migrating from a personal Instagram account:

1. **Backup Data**: Download your Instagram data
2. **Convert Account**: Use Instagram's built-in conversion
3. **Update Apps**: Reconfigure all connected apps
4. **Test Integration**: Verify all features work
5. **Notify Users**: Inform users about the migration

## Next Steps

After setting up Instagram Business:

1. **Test Basic Posting**: Verify simple image posts work
2. **Test Advanced Features**: Try carousels and videos
3. **Monitor Analytics**: Set up insights tracking
4. **Scale Usage**: Gradually increase posting frequency
5. **Optimize Content**: Use analytics to improve engagement

This setup enables all advanced Instagram features in Postify, providing professional-grade social media management capabilities.
