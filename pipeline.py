import pandas as pd
from pymongo import MongoClient

# === CONFIGURATION ===
CSV_PATH = r"C:\Users\prate\OneDrive\Desktop\ClinicSight\data\healthcare_dataset.csv"
EXPORT_PATH = r"C:\Users\prate\OneDrive\Desktop\ClinicSight\data\exported_healthcare.csv"
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "clinicsight"
COLLECTION_NAME = "patients"


# === STEP 1: Load CSV into MongoDB ===
def load_csv_to_mongodb():
    print("📥 Loading CSV into MongoDB...")
    df = pd.read_csv(CSV_PATH)
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    collection.drop()  # Clear old data
    collection.insert_many(df.to_dict(orient='records'))
    print(f"✅ Inserted {len(df)} records into MongoDB collection '{COLLECTION_NAME}'.")


# === STEP 2: Export MongoDB Data to CSV ===
def export_mongodb_to_csv():
    print("📤 Exporting MongoDB data to CSV...")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    records = list(collection.find())

    # Remove MongoDB's internal _id field
    for record in records:
        record.pop('_id', None)

    df = pd.DataFrame(records)
    df.to_csv(EXPORT_PATH, index=False)
    print(f"✅ Exported data to CSV file: {EXPORT_PATH}")


# === RUN PIPELINE ===
if __name__ == "__main__":
    load_csv_to_mongodb()
    export_mongodb_to_csv()
