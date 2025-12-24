const mongoose = require("mongoose");
const Patient = require("../models/Patient");

// Create a new patient
const createPatient = async (req, res) => {
  try {
    const patient = new Patient({ ...req.body, createdBy: "testUser" });
    await patient.save();
    res.status(201).json({ message: "Patient created successfully", patient });
  } catch (err) {
    console.error("Error in createPatient:", err);
    res.status(500).json({ message: "Server error creating patient" });
  }
};

// Get all patients
const getPatients = async (req, res) => {
  try {
    const patients = await Patient.find({});
    res.json(patients || []);
  } catch (err) {
    console.error("Error in getPatients:", err);
    res.status(500).json({ message: "Server error fetching patients" });
  }
};

// ✅ Get predictions (moved router logic into function)
const getPredictions = async (req, res) => {
  try {
    const predictedCollection = mongoose.connection.collection("predicted");
    const data = await predictedCollection.find({}).toArray();
    res.status(200).json(data);
  } catch (err) {
    console.error("Error fetching predictions:", err);
    res.status(500).json({ message: "Error fetching predictions" });
  }
};

// Get disease stats
const getDiseaseStats = async (req, res) => {
  try {
    const stats = await Patient.aggregate([
      {
        $group: {
          _id: "$condition",
          count: { $sum: 1 },
          avgAge: { $avg: "$age" },
        },
      },
      { $sort: { count: -1 } },
      { $limit: 10 },
    ]);

    res.json(stats);
  } catch (err) {
    console.error("Error fetching disease stats:", err);
    res.status(500).json({ message: "Error fetching disease stats" });
  }
};

module.exports = {
  createPatient,
  getPatients,
  getPredictions,
  getDiseaseStats,
};
