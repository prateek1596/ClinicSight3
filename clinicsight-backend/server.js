const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const mongoose = require('mongoose');
const connectDB = require('./config/db');

// Load environment variables
dotenv.config();

// Connect to MongoDB
connectDB();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Attach MongoDB connection (optional, for direct collection access)
app.locals.db = mongoose.connection;

// Routes
app.use('/api/patients', require('./routes/patientRoutes'));
app.use('/api/auth', require('./routes/authRoutes'));
app.use("/api/recentpatients", require("./routes/recentPatientRoutes"));


// Default route
app.get('/', (req, res) => {
  res.send('ClinicSight API is running...');
});

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
