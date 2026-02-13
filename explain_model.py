import pandas as pd
import joblib
import shap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
import matplotlib.pyplot as plt
import numpy as np

# --- Suppress warnings ---
warnings.filterwarnings("ignore", category=UserWarning)
pd.options.mode.chained_assignment = None

print("Loading model, scaler, and feature list...")
model = joblib.load("ddos_model.pkl")
scaler = joblib.load("scaler.pkl")
feature_list = joblib.load("feature_list.pkl")

print("Loading and preparing datasets for explanation...")
sim_df = pd.read_csv("DDoS-Dataset-Simulation.csv")
real_df = pd.read_csv("DDoS-Dataset-Real-World.csv")

# --- Normalize label names ---
if 'label' in sim_df.columns:
    sim_df["label"] = sim_df["label"].replace({-1: 0, 1: 1})
else:
    sim_df["Label"] = 0 # Default if column missing

if 'Label' in real_df.columns:
    real_df["Label"] = real_df["Label"].replace({"Benign": 0, "Normal": 0})
    real_df["Label"] = real_df["Label"].apply(lambda x: 1 if x != 0 else 0)
else:
    real_df["Label"] = 0 # Default if column missing

# --- Rename & Align ---
sim_df = sim_df.rename(columns={"timestamp": "time", "src_ip": "ip.src", "dst_ip": "ip.dst", "protocol": "ip.proto", "packet_length": "frame.len", "tcp_flags": "tcp.flags", "label": "Label"})

# Drop columns not needed for the model
sim_df = sim_df.drop(columns=["time", "ip.src", "ip.dst"], errors='ignore')
real_df = real_df.drop(columns=["ip.src", "ip.dst", "frame.time"], errors='ignore')

# --- Final Column Alignment ---
all_required_columns = feature_list + ["Label"]

# Ensure every required column exists (fill with 0 if missing)
for col in all_required_columns:
    if col not in sim_df.columns:
        sim_df[col] = 0
    if col not in real_df.columns:
        real_df[col] = 0

# Now it is safe to select and concatenate
combined_df = pd.concat([sim_df[all_required_columns], real_df[all_required_columns]], ignore_index=True)

# --- Split and Scale ---
X = combined_df[feature_list]
y = combined_df["Label"]
X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

_, test_df, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_test_scaled_df = pd.DataFrame(scaler.transform(test_df), columns=feature_list)

print("\n--- Initializing SHAP Explainer ---")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test_scaled_df)

# Handle SHAP output format
if isinstance(shap_values, list):
    shap_values_ddos = shap_values[1]
else:
    shap_values_ddos = shap_values[:, :, 1] if len(shap_values.shape) == 3 else shap_values

# --- Save Plots ---
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values_ddos, X_test_scaled_df.values, feature_names=feature_list, plot_type="dot", show=False)
plt.savefig("shap_summary_plot.png", bbox_inches='tight')
plt.close()

# Local Explanation
attack_index = 0
y_pred_test = model.predict(scaler.transform(test_df))
for i, (pred, actual) in enumerate(zip(y_pred_test, y_test.reset_index(drop=True))):
    if pred == 1 and actual == 1:
        attack_index = i
        break

base_val = explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
force_plot = shap.force_plot(base_val, shap_values_ddos[attack_index, :], X_test_scaled_df.iloc[attack_index, :], matplotlib=False)
shap.save_html("shap_force_plot.html", force_plot)

print("\nExplanation complete. Plots saved.")