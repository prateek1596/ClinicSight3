const express = require("express");
const RecentPatient = require("../models/recentPatientModel");
const router = express.Router();

// ✅ POST: Add recent patient
router.post("/add", async (req, res) => {
  try {
    const newRecent = new RecentPatient(req.body);
    await newRecent.save();
    res.status(201).json({
      message: "Recent patient added successfully",
      recentPatient: newRecent,
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// ✅ GET: Fetch all recent patients
router.get("/", async (req, res) => {
  try {
    const recents = await RecentPatient.find().sort({ createdAt: -1 });
    res.status(200).json(recents);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

module.exports = router;
