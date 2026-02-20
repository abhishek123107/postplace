# Render deployment fix for frontend static site

## Problem
Render is looking for `dist` directory but React creates `build` directory.

## Solution 1: Use Node runtime with serve (Recommended)
Update `render.yaml` to use Node runtime and serve the build directory:

```yaml
services:
  - type: web
    name: postify-frontend
    runtime: node
    buildCommand: "npm install && npm run build"
    startCommand: "serve -s build -l 3000"
    envVars:
      - key: NODE_VERSION
        value: 22
      - key: REACT_APP_API_URL
        value: https://postify-backend.onrender.com
    healthCheck:
      path: /
      port: 3000
```

## Solution 2: Create dist directory (Alternative)
Add a post-build script to copy build to dist:

```json
{
  "scripts": {
    "build": "react-scripts build && cp -r build dist"
  }
}
```

## Solution 3: Use Static Service with correct config
```yaml
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

## Current Fix Applied
I've updated `render.yaml` to use Node runtime with `serve` package, which will:
1. Build the React app to `build/` directory
2. Use `serve` to serve static files from `build/`
3. Handle React Router properly
4. Work with Render's deployment system

## Next Steps
1. Push the updated `render.yaml` and `package.json` to GitHub
2. Render will automatically redeploy with the new configuration
3. Frontend should now deploy successfully
