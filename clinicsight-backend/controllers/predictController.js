const { spawn } = require("child_process");

const diagnoseSymptoms = async (req, res) => {
  try {
    const { features } = req.body; // array of numeric features

    if (!features || features.length !== 17) {
      return res.status(400).json({ message: "Invalid or incomplete features" });
    }

    // Spawn Python process
    const pythonProcess = spawn("python", ["ml_model/predict.py", JSON.stringify(features)]);
    
    let output = "";
    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      console.error("Python Error:", data.toString());
    });

    pythonProcess.on("close", () => {
      const disease = output.trim() || "Consult a doctor";
      res.json({ disease });
    });
  } catch (error) {
    console.error("Prediction error:", error);
    res.status(500).json({ message: "Prediction failed" });
  }
};

module.exports = { diagnoseSymptoms };
