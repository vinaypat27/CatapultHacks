require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const User = require('./models/User');
const Document = require('./models/Document');
const path = require('path');

const app = express();
const { spawn } = require('child_process');


// Middleware
app.use(cors());
app.use(express.json({ limit: '1000mb' }));
app.use(express.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI)
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('MongoDB connection error:', err));

// Middleware to verify JWT token
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ message: 'No token provided' });
    }

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ message: 'Invalid token' });
        }
        req.user = user;
        next();
    });
};

// Register endpoint
app.post('/api/register', async (req, res) => {
    try {
        const { firstName, lastName, email, password } = req.body;

        if (!firstName || !lastName || !email || !password) {
            return res.status(400).json({ message: 'All fields are required' });
        }

        // Check if user already exists
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ message: 'Email already registered' });
        }

        // Create new user
        const user = new User({
            firstName,
            lastName,
            email,
            password
        });

        await user.save();
        console.log('User created successfully:', user._id);

        // Generate JWT token
        const token = jwt.sign(
            { userId: user._id, email: user.email },
            process.env.JWT_SECRET,
            { expiresIn: '24h' }
        );

        res.status(201).json({
            token,
            user: {
                id: user._id,
                firstName: user.firstName,
                lastName: user.lastName,
                email: user.email
            }
        });
    } catch (error) {
        console.error('Error creating user:', error);
        res.status(500).json({ message: 'Error creating user', error: error.message });
    }
});

// Login endpoint
app.post('/api/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ message: 'Email and password are required' });
        }

        // Find user
        const user = await User.findOne({ email });
        if (!user) {
            console.log('Login failed: User not found -', email);
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        // Check password
        const isMatch = await user.comparePassword(password);
        if (!isMatch) {
            console.log('Login failed: Invalid password -', email);
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        console.log('User logged in successfully:', user._id);

        // Generate JWT token
        const token = jwt.sign(
            { userId: user._id, email: user.email },
            process.env.JWT_SECRET,
            { expiresIn: '24h' }
        );

        res.json({
            token,
            user: {
                id: user._id,
                firstName: user.firstName,
                lastName: user.lastName,
                email: user.email
            }
        });
    } catch (error) {
        console.error('Error logging in:', error);
        res.status(500).json({ message: 'Error logging in', error: error.message });
    }
});

// Protected route to get user profile
app.get('/api/profile', authenticateToken, async (req, res) => {
    try {
        const user = await User.findById(req.user.userId).select('-password');
        if (!user) {
            return res.status(404).json({ message: 'User not found' });
        }
        res.json(user);
    } catch (error) {
        res.status(500).json({ message: 'Error fetching profile', error: error.message });
    }
});

// Upload document endpoint
app.post('/api/documents', authenticateToken, async (req, res) => {
    try {
        const { fileName, fileType, fileSize, content } = req.body;

        // Validate file type
        const allowedTypes = ['text/plain', 'application/pdf'];
        if (!allowedTypes.includes(fileType)) {
            return res.status(400).json({ message: 'Only PDF and text files are supported' });
        }

        // Create new document
        const document = new Document({
            userId: req.user.userId,
            fileName,
            fileType,
            fileSize,
            content
        });

        await document.save();
        res.json(document);
    } catch (error) {
        console.error('Error uploading document:', error);
        res.status(500).json({ message: 'Error uploading document', error: error.message });
    }
});

app.get('/api/documents', authenticateToken, async (req, res) => {
    try {
        const documents = await Document.find({ userId: req.user.userId });
        res.json(documents);
    } catch (error) {
        res.status(500).json({ message: 'Error fetching documents', error: error.message });
    }
});

// Get document by ID
app.get('/api/documents/:id', authenticateToken, async (req, res) => {
    try {
        const document = await Document.findOne({
            _id: req.params.id,
            userId: req.user.userId
        });

        if (!document) {
            return res.status(404).json({ message: 'Document not found' });
        }

        res.json(document);
    } catch (error) {
        console.error('Error retrieving document:', error);
        res.status(500).json({ message: 'Error retrieving document', error: error.message });
    }
});

app.delete('/api/documents/:id', authenticateToken, async (req, res) => {
    try {
        const document = await Document.findOneAndDelete({ _id: req.params.id, userId: req.user.userId });
        if (!document) {
            return res.status(404).json({ message: 'Document not found' });
        }
        res.json({ message: 'Document deleted successfully' });
    } catch (error) {
        res.status(500).json({ message: 'Error deleting document', error: error.message });
    }
});


// Document analysis endpoint
app.post('/api/analyze', authenticateToken, async (req, res) => {
    try {
        const { message, documentId } = req.body;

        if (!message || !documentId) {
            return res.status(400).json({ message: 'Message and document ID are required' });
        }

        // Get the document
        const document = await Document.findOne({ _id: documentId, userId: req.user.userId });
        if (!document) {
            return res.status(404).json({ message: 'Document not found' });
        }

        // For now, return a simple response
        // TODO: Integrate with actual AI service
        const response = `I understand you're asking about "${message}" in relation to the document "${document.fileName}". This is a placeholder response - we'll integrate with a real AI service soon.`;

        res.json({ response });
    } catch (error) {
        console.error('Error analyzing document:', error);
        res.status(500).json({ message: 'Error analyzing document' });
    }
});


// Compliance analysis endpoint
app.post('/api/analyze-compliance', authenticateToken, async (req, res) => {
    try {
      const { documentId } = req.body;
      
      // Fetch the document from your database
      const document = await Document.findById(documentId);
      if (!document) {
        return res.status(404).json({ error: 'Document not found' });
      }
      
      // Save PDF content to a temporary file
      const tempFilePath = `/tmp/${document._id}.pdf`;
      require('fs').writeFileSync(tempFilePath, Buffer.from(document.content, 'base64'));
      
      // Call the Python script
const pythonProcess = spawn('python3', ['compliance_checker.py', tempFilePath]);
      
      let result = '';
      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        // Clean up temp file
        require('fs').unlinkSync(tempFilePath);
        
        if (code !== 0) {
          return res.status(500).json({ error: 'Analysis failed' });
        }
        
        // Parse the result
        const analysisResult = JSON.parse(result);
        res.json(analysisResult);
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

// Serve static files
app.use(express.static(path.join(__dirname, '../frontend')));

// Handle all other routes by serving index.html
app.get('*', (req, res) => {
    if (!req.path.startsWith('/api')) {
        res.sendFile(path.join(__dirname, '../frontend/index.html'));
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});


app.post('/api/analyze-compliance', authenticateToken, async (req, res) => {
  try {
    const { documentId } = req.body;
    
    // Fetch the document from your database
    const document = await Document.findById(documentId);
    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }
    
    // Save PDF content to a temporary file
    const tempFilePath = `/tmp/${document._id}.pdf`;
    require('fs').writeFileSync(tempFilePath, Buffer.from(document.content, 'base64'));
    
    // Call the Python script
    const pythonProcess = spawn('python', ['compliance_checker.py', tempFilePath]);
    
    let result = '';
    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      // Clean up temp file
      require('fs').unlinkSync(tempFilePath);
      
      if (code !== 0) {
        return res.status(500).json({ error: 'Analysis failed' });
      }
      
      // Parse the result
      const analysisResult = JSON.parse(result);
      res.json(analysisResult);
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
