const express = require("express");
const mongoose = require("mongoose");
const {
  getPredictions,
  getDiseaseStats,
} = require("../controllers/patientController");

const router = express.Router();

/* ------------------------------------------------------------------
   ⚙️ TEMPORARY MODEL DEFINITION (Ideally move to /models/Patient.js)
-------------------------------------------------------------------*/
const patientSchema = new mongoose.Schema({
  name: { type: String, required: true },
  age: { type: Number, required: true },
  gender: { type: String, required: true },
  condition: { type: String, required: true },
  contact: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
});

// Prevent model overwrite error in development
const Patient =
  mongoose.models.Patient || mongoose.model("Patient", patientSchema);

/* ------------------------------------------------------------------
   🩺 PATIENT ROUTES
-------------------------------------------------------------------*/

// ✅ Add new patient
// POST /api/patients/add
router.post("/add", async (req, res) => {
  try {
    const newPatient = new Patient(req.body);
    await newPatient.save();
    res.status(201).json({
      message: "✅ Patient added successfully",
      patient: newPatient,
    });
  } catch (error) {
    console.error("❌ Error adding patient:", error);
    res.status(500).json({ message: error.message });
  }
});

// ✅ Get all patients
// GET /api/patients
router.get("/", async (req, res) => {
  try {
    const patients = await Patient.find().sort({ createdAt: -1 });
    res.status(200).json(patients);
  } catch (error) {
    console.error("❌ Error fetching patients:", error);
    res.status(500).json({ message: error.message });
  }
});

/* ------------------------------------------------------------------
   📊 STATS & PREDICTIONS ROUTES
   ⚠️ Must come BEFORE /:id to avoid route conflicts
-------------------------------------------------------------------*/

// ✅ Disease statistics
// GET /api/patients/stats
router.get("/stats", getDiseaseStats);

// ✅ Predictions
// GET /api/patients/predictions
router.get("/predictions", getPredictions);

/* ------------------------------------------------------------------
   🔍 INDIVIDUAL PATIENT ROUTE
-------------------------------------------------------------------*/

// ✅ Get patient by ID
// GET /api/patients/:id
router.get("/:id", async (req, res) => {
  try {
    const patient = await Patient.findById(req.params.id);
    if (!patient)
      return res.status(404).json({ message: "Patient not found" });
    res.status(200).json(patient);
  } catch (error) {
    console.error("❌ Error fetching single patient:", error);
    res.status(500).json({ message: error.message });
  }
});

module.exports = router;
