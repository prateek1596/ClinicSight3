from flask import Flask, request, jsonify
from pyspark.sql import SparkSession
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.feature import VectorAssembler
import pandas as pd
import traceback

app = Flask(__name__)

# Load Spark session and model
spark = SparkSession.builder.appName("ClinicSightPredictAPI").getOrCreate()
model = RandomForestClassificationModel.load("rf_model_local")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Expect data like: { "Age": 45, "Glucose": 150, "Blood Pressure": 80, ... }
        df = pd.DataFrame([data])
        spark_df = spark.createDataFrame(df)

        # Assemble features (must match training)
        assembler = VectorAssembler(
            inputCols=[
                "Age", "GenderIndex", "Glucose", "Blood Pressure", "BMI",
                "Oxygen Saturation", "LengthOfStay", "Cholesterol", "Triglycerides",
                "HbA1c", "SmokingIndex", "AlcoholIndex", "ActivityIndex",
                "Diet Score", "HistoryIndex", "Stress Level", "Sleep Hours"
            ],
            outputCol="features"
        )
        assembled = assembler.transform(spark_df)
        preds = model.transform(assembled).select("prediction").collect()

        if not preds:
            return jsonify({"prediction": "Unknown", "message": "Consult a doctor"}), 200

        prediction = preds[0]["prediction"]
        # Optionally map numeric label back to condition
        condition_map = {0: "Diabetes", 1: "Hypertension", 2: "Healthy"}  # example
        predicted_condition = condition_map.get(prediction, "Consult a doctor")

        return jsonify({"prediction": predicted_condition}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0' ,port=7000, debug=True)
