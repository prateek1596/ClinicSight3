from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import RandomForestClassifier, RandomForestClassificationModel
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pymongo import MongoClient
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

# === Start Spark Session ===
spark = SparkSession.builder.appName("ClinicSightRandomForest").getOrCreate()

# === Load CSV (LOCAL or HDFS) ===
df = spark.read.csv("hdfs://localhost:9000/clinicsight/dirty_v3_path.csv", header=True, inferSchema=True)

# === Select relevant columns ===
ml_df = df.select(
    "Age", "Gender", "Glucose", "Blood Pressure", "BMI",
    "Oxygen Saturation", "LengthOfStay", "Cholesterol", "Triglycerides",
    "HbA1c", "Smoking", "Alcohol", "Physical Activity", "Diet Score",
    "Family History", "Stress Level", "Sleep Hours", "Medical Condition"
).dropna()

# === Index categorical columns ===
indexers = [
    StringIndexer(inputCol="Gender", outputCol="GenderIndex"),
    StringIndexer(inputCol="Smoking", outputCol="SmokingIndex"),
    StringIndexer(inputCol="Alcohol", outputCol="AlcoholIndex"),
    StringIndexer(inputCol="Physical Activity", outputCol="ActivityIndex"),
    StringIndexer(inputCol="Family History", outputCol="HistoryIndex"),
    StringIndexer(inputCol="Medical Condition", outputCol="ConditionIndex")
]

for indexer in indexers:
    ml_df = indexer.fit(ml_df).transform(ml_df)

# === Extract condition mapping ===
condition_map = ml_df.select("Medical Condition", "ConditionIndex").distinct().toPandas()
condition_dict = dict(zip(condition_map["ConditionIndex"], condition_map["Medical Condition"]))

# === Assemble features ===
assembler = VectorAssembler(
    inputCols=[
        "Age", "GenderIndex", "Glucose", "Blood Pressure", "BMI",
        "Oxygen Saturation", "LengthOfStay", "Cholesterol", "Triglycerides",
        "HbA1c", "SmokingIndex", "AlcoholIndex", "ActivityIndex",
        "Diet Score", "HistoryIndex", "Stress Level", "Sleep Hours"
    ],
    outputCol="features"
)
ml_data = assembler.transform(ml_df).select("features", "ConditionIndex")

# === Split data into train & test sets ===
train_data, test_data = ml_data.randomSplit([0.8, 0.2], seed=42)
print(f"📊 Training samples: {train_data.count()} | Testing samples: {test_data.count()}")

# === Train Random Forest model ===
rf = RandomForestClassifier(
    labelCol="ConditionIndex",
    featuresCol="features",
    numTrees=50,
    maxBins=1100,
    seed=42
)
model = rf.fit(train_data)

# === Evaluate on test data ===
predictions = model.transform(test_data)
evaluator = MulticlassClassificationEvaluator(labelCol="ConditionIndex", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print(f"✅ Random Forest Test Accuracy: {accuracy:.4f}")
for metric in ["accuracy", "weightedPrecision", "weightedRecall", "f1"]:
    evaluator.setMetricName(metric)
    value = evaluator.evaluate(predictions)
    print(f"{metric.capitalize()}: {value:.4f}")

# === Save model locally ===
model_path = os.path.join(os.path.dirname(__file__), "clinicsight-backend", "ml_model", "rf_model_local")
if os.path.exists(model_path):
    import shutil
    shutil.rmtree(model_path)
model.save(model_path)
print("💾 Random Forest model saved locally as 'rf_model_local'")

# === Convert to Pandas for visualization ===
export_data = predictions.select("features", "ConditionIndex", "prediction").limit(500).toPandas()
export_data["Actual Condition"] = export_data["ConditionIndex"].map(condition_dict)
export_data["Predicted Condition"] = export_data["prediction"].map(condition_dict)

# === Visualization: Prediction distribution ===
plt.figure(figsize=(8, 5))
export_data["Predicted Condition"].value_counts().plot(kind="bar", color="skyblue")
plt.title("Predicted Medical Condition Distribution")
plt.xlabel("Condition")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# === Confusion Matrix ===
conf_matrix = pd.crosstab(export_data["Actual Condition"], export_data["Predicted Condition"])
plt.figure(figsize=(10, 8))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()

# === Accuracy by condition ===
correct_preds = export_data[export_data["Actual Condition"] == export_data["Predicted Condition"]]
accuracy_by_condition = correct_preds["Actual Condition"].value_counts() / export_data["Actual Condition"].value_counts()
accuracy_by_condition = accuracy_by_condition.fillna(0).sort_values(ascending=False)

plt.figure(figsize=(8, 5))
accuracy_by_condition.plot(kind="bar", color="green")
plt.title("Accuracy by Medical Condition")
plt.xlabel("Condition")
plt.ylabel("Accuracy")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# === Optional: Export predictions to MongoDB ===
try:
    client = MongoClient("mongodb://localhost:27017/?directConnection=true")
    mongo_db = client["clinicsight"]
    collection = mongo_db["predicted_conditions"]

    export_data["features"] = export_data["features"].apply(lambda v: v.toArray().tolist())
    records = export_data[["features", "Actual Condition", "Predicted Condition"]].to_dict(orient="records")

    collection.delete_many({})
    collection.insert_many(records)

    print("✅ Predictions successfully exported to MongoDB!")
except Exception as e:
    print(f"⚠️ MongoDB export failed: {e}")

# === Example: Reload model later for diagnosis ===
print("\n🔁 Testing model reload...")
loaded_model = RandomForestClassificationModel.load("rf_model_local")
print("✅ Model reloaded successfully!")

