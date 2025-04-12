# Document Analyzer Backend

This is the backend server for the Document Analyzer application. It provides user authentication and data storage using MongoDB.

## Prerequisites

- Node.js (v14 or higher)
- MongoDB (local installation or MongoDB Atlas account)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the root directory with the following variables:
```
MONGODB_URI=mongodb://localhost:27017/document_analyzer
JWT_SECRET=your_jwt_secret_key_here
PORT=5000
```

3. Start the development server:
```bash
npm run dev
```

The server will start on port 5000 (or the port specified in your .env file).

## API Endpoints

### Authentication

- POST `/api/register` - Register a new user
- POST `/api/login` - Login user
- GET `/api/profile` - Get user profile (requires authentication)
- PUT `/api/settings` - Update user settings (requires authentication)

## Security

- Passwords are hashed using bcrypt
- JWT tokens are used for authentication
- CORS is enabled for frontend communication
