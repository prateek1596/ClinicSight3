const express = require('express');
const axios = require('axios');
const router = express.Router();

router.post('/', async (req, res) => {
  try {
    const response = await axios.post('http://localhost:7000/predict', req.body);
    res.json(response.data);
  } catch (error) {
    console.error('Prediction failed:', error.message);
    res.status(500).json({ error: 'Model unavailable, please consult a doctor' });
  }
});

router.post("/symptoms", async (req, res) => {
  try {
    const { symptoms } = req.body;
    const response = await axios.post("http://127.0.0.1:7000/predict", { symptoms }); // Flask server
    res.json({ prediction: response.data.prediction });
  } catch (err) {
    console.error("Prediction error:", err.message);
    res.status(500).json({ error: "Failed to get prediction" });
  }
});

module.exports = router;
