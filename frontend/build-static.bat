@echo off
REM Build command for frontend static site on Windows

REM Set environment variables
set REACT_APP_API_URL=https://your-api-domain.com

REM Install dependencies
echo Installing dependencies...
npm install

REM Build the React app as static files
echo Building React app...
npm run build

echo Build complete! Static files are in 'build/' directory
echo Ready for deployment to static hosting services

pause
