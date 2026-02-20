# Frontend Static Site Deployment Guide

## Overview
This guide covers deploying the Postify frontend as a static site to various platforms.

## Build Process

### 1. Build the Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# The build output will be in 'build/' directory
```

### 2. Environment Variables
Set these environment variables before building:
```bash
# For production API URL
export REACT_APP_API_URL=https://your-backend-domain.com

# For development (localhost)
export REACT_APP_API_URL=http://localhost:8000
```

## Deployment Platforms

### 1. Render (Static Site)

#### Option A: Using render.yaml (Recommended)
```yaml
# render.yaml
services:
  - type: web
    name: postify-frontend
    runtime: static
    buildCommand: "npm install && npm run build"
    publishPath: build
    envVars:
      - key: NODE_VERSION
        value: 22
```

#### Option B: Manual Setup
1. **Create Static Site Service** on Render
2. **Set Build Command**: `npm install && npm run build`
3. **Set Publish Directory**: `build`
4. **Set Node Version**: 22
5. **Add Environment Variables**:
   - `REACT_APP_API_URL=https://your-backend-domain.com`

### 2. Netlify

#### Using netlify.toml
```toml
[build]
  publish = "build"
  
[build.environment]
  NODE_VERSION = "22"

[build.commands]
  "npm install && npm run build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### Manual Setup
1. **Connect GitHub Repository** to Netlify
2. **Set Build Command**: `npm install && npm run build`
3. **Set Publish Directory**: `build`
4. **Add Environment Variables**:
   - `REACT_APP_API_URL=https://your-backend-domain.com`

### 3. Vercel

#### Using vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

#### Manual Setup
1. **Import Project** to Vercel
2. **Set Build Command**: `npm install && npm run build`
3. **Set Output Directory**: `build`
4. **Add Environment Variables**:
   - `REACT_APP_API_URL=https://your-backend-domain.com`

### 4. GitHub Pages

#### Setup
1. **Install gh-pages**:
   ```bash
   npm install --save-dev gh-pages
   ```

2. **Update package.json**:
   ```json
   {
     "homepage": "https://your-username.github.io/postify",
     "scripts": {
       "predeploy": "npm run build",
       "deploy": "gh-pages -d build"
     }
   }
   ```

3. **Deploy**:
   ```bash
   npm run deploy
   ```

### 5. Firebase Hosting

#### Setup
1. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase init hosting
   ```

2. **Configure firebase.json**:
   ```json
   {
     "hosting": {
       "public": "build",
       "rewrites": [
         {
           "source": "**",
           "destination": "/index.html"
         }
       ]
     }
   }
   ```

3. **Deploy**:
   ```bash
   firebase deploy
   ```

## Configuration Files Created

### 1. `render.yaml` - Full stack deployment
- Backend service configuration
- Frontend static site configuration
- Environment variables

### 2. `frontend/netlify.toml` - Netlify deployment
- Build configuration
- Redirect rules for React Router

### 3. `frontend/vercel.json` - Vercel deployment
- Build configuration
- Route handling

### 4. `frontend/render-static.toml` - Render static site
- Build configuration
- Redirect rules

## Important Notes

### React Router
All deployment configurations include proper redirects for React Router to handle client-side routing.

### Environment Variables
Make sure to set `REACT_APP_API_URL` to your backend URL:
- **Development**: `http://localhost:8000`
- **Production**: `https://your-backend-domain.com`

### Build Directory
React creates a `build/` directory (not `dist/`), so all configurations use `build` as the publish directory.

### HTTPS
For production, always use HTTPS URLs for API endpoints to avoid mixed content issues.

## Troubleshooting

### "Publish directory dist does not exist!"
**Solution**: Ensure your deployment platform is configured to use `build` directory, not `dist`.

### "404 errors on page refresh"
**Solution**: Ensure proper redirect rules are configured for React Router.

### "API requests failing"
**Solution**: Check that `REACT_APP_API_URL` is correctly set and accessible.

### "Build fails"
**Solution**: Check Node.js version compatibility and ensure all dependencies are installed.

## Quick Deployment Commands

### Render
```bash
# Push to GitHub and Render will auto-deploy
git add .
git commit -m "Deploy frontend"
git push origin main
```

### Netlify
```bash
# Connect repo to Netlify and auto-deploy
# Or manual drag-and-drop build folder
```

### Vercel
```bash
# Install Vercel CLI
npm i -g vercel
vercel --prod
```

### GitHub Pages
```bash
npm run deploy
```

Your frontend is now ready for static site deployment! 🚀
