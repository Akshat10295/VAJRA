import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

print("Loading and preparing datasets...\n")

# --- Load datasets ---
sim_df = pd.read_csv("DDoS-Dataset-Simulation.csv")
real_df = pd.read_csv("DDoS-Dataset-Real-World.csv")

print(f"Simulation dataset: {sim_df.shape[0]} rows, {sim_df.shape[1]} columns")
print(f"Real-world dataset: {real_df.shape[0]} rows, {real_df.shape[1]} columns")

# --- Normalize label names ---
if 'label' in sim_df.columns:
    sim_df["label"] = sim_df["label"].replace({-1: 0, 1: 1})
else:
    raise ValueError("'label' column not found in simulated dataset.")

if 'Label' in real_df.columns:
    real_df["Label"] = real_df["Label"].replace({"Benign": 0, "Normal": 0})
    real_df["Label"] = real_df["Label"].apply(lambda x: 1 if x != 0 else 0)
else:
    raise ValueError("'Label' column not found in real-world dataset.")

# --- Rename simulated columns for consistency ---
sim_df = sim_df.rename(columns={
    "timestamp": "time",
    "src_ip": "ip.src",
    "dst_ip": "ip.dst",
    "protocol": "ip.proto",
    "packet_length": "frame.len",
    "tcp_flags": "tcp.flags",
    "label": "Label"
})

# --- Drop unnecessary string columns ---
sim_df = sim_df.drop(columns=["time", "ip.src", "ip.dst"], errors='ignore')
real_df = real_df.drop(columns=["ip.src", "ip.dst", "frame.time"], errors='ignore')

# --- Encode protocol values (like TCP/UDP) ---
proto_encoder = LabelEncoder()
if sim_df["ip.proto"].dtype == object:
    sim_df["ip.proto"] = proto_encoder.fit_transform(sim_df["ip.proto"])
if real_df["ip.proto"].dtype == object:
    real_df["ip.proto"] = proto_encoder.fit_transform(real_df["ip.proto"])

# --- Select relevant numeric features ---
sim_features = ["frame.len", "ip.proto", "tcp.flags", "Label"]
real_features = [
    "frame.len", "ip.proto", "tcp.srcport", "tcp.dstport",
    "tcp.flags.syn", "tcp.flags.push", "tcp.flags.ack", "Label"
]

sim_df = sim_df[[c for c in sim_features if c in sim_df.columns]]
real_df = real_df[[c for c in real_features if c in real_df.columns]]

# --- Fill NaN values ---
sim_df = sim_df.fillna(0)
real_df = real_df.fillna(0)

# --- Align columns ---
for col in set(real_df.columns) - set(sim_df.columns):
    sim_df[col] = 0
for col in set(sim_df.columns) - set(real_df.columns):
    real_df[col] = 0

common_columns = sorted(list(set(sim_df.columns) & set(real_df.columns)))
combined_df = pd.concat([sim_df[common_columns], real_df[common_columns]], ignore_index=True)

print(f"Combined dataset shape: {combined_df.shape}")
print("Columns used for training:", list(combined_df.columns))

# --- Split into features and labels ---
X = combined_df.drop(columns=["Label"])
y = combined_df["Label"]

# --- Ensure all columns are numeric ---
X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

# --- Train-test split ---
train_df, test_df, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --- Feature Scaling ---
print("\nScaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(train_df)
X_test_scaled = scaler.transform(test_df)

# --- Train Model ---
print("\nTraining Random Forest Model...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
rf_model.fit(X_train_scaled, y_train)

# --- Evaluate Model ---
print("\n--- Model Evaluation ---")
y_pred = rf_model.predict(X_test_scaled)

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
cm = confusion_matrix(y_test, y_pred)

print(f"Accuracy:  {acc*100:.2f}%")
print(f"Precision: {prec:.2f}")
print(f"Recall:    {rec:.2f}  (Attack detection rate)")
print(f"F1-Score:  {f1:.2f}\n")

print("Confusion Matrix:")
print(cm)

# --- Feature Importance ---
importances = pd.Series(rf_model.feature_importances_, index=X.columns)
importances = importances.sort_values(ascending=False)
print("\n--- Feature Importance ---")
print(importances)

# --- Save Model and Scaler ---
joblib.dump(rf_model, "ddos_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(list(X.columns), "feature_list.pkl")

print("\nModel, scaler, and feature list saved successfully:")
print(" - ddos_model.pkl")
print(" - scaler.pkl")
print(" - feature_list.pkl")

print("\nTraining complete! Vajra model is ready for deployment.")
