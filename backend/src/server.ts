import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { rateLimit } from 'express-rate-limit';
import morgan from 'morgan';
import commitRoutes from './routes/commitRoutes';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Security and utility middleware
app.use(helmet());
app.use(cors({ origin: process.env.FRONTEND_URL || 'http://localhost:5173', credentials: true }));
app.use(express.json());
app.use(morgan('dev'));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again later.'
});
app.use('/api', limiter);

// Dummy Database Connection (to be replaced with actual MongoDB URI)
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/commitiq')
    .then(() => console.log('✅ Connected to MongoDB'))
    .catch((err) => console.error('❌ MongoDB connection error:', err));

// Routes
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'CommitIQ Backend API' });
});

// Commit Analyzer Routes
app.use('/api/commits', commitRoutes);

// Auth Routes placeholder
app.use('/api/auth', (req, res) => {
    res.json({ message: 'Auth endpoint hit' });
});

app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
});
