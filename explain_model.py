import pandas as pd
import joblib
import shap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
import matplotlib.pyplot as plt

# --- Suppress warnings ---
warnings.filterwarnings("ignore", category=UserWarning)
pd.options.mode.chained_assignment = None

print("Loading model, scaler, and feature list...")
# 1. Load your saved model and utilities
model = joblib.load("ddos_model.pkl")
scaler = joblib.load("scaler.pkl")
feature_list = joblib.load("feature_list.pkl")

print("Loading and preparing datasets for explanation...")

# 2. Re-load and prep data to get a test set
# (SHAP needs the test data to generate explanations)
sim_df = pd.read_csv("DDoS-Dataset-Simulation.csv")
real_df = pd.read_csv("DDoS-Dataset-Real-World.csv")

# --- Normalize label names (same as model.py) ---
if 'label' in sim_df.columns:
    sim_df["label"] = sim_df["label"].replace({-1: 0, 1: 1})
else:
    raise ValueError("'label' column not found in simulated dataset.")

if 'Label' in real_df.columns:
    real_df["Label"] = real_df["Label"].replace({"Benign": 0, "Normal": 0})
    real_df["Label"] = real_df["Label"].apply(lambda x: 1 if x != 0 else 0)
else:
    raise ValueError("'Label' column not found in real-world dataset.")


# --- Rename (same as model.py) ---
sim_df = sim_df.rename(columns={
    "timestamp": "time", "src_ip": "ip.src", "dst_ip": "ip.dst",
    "protocol": "ip.proto", "packet_length": "frame.len",
    "tcp_flags": "tcp.flags", "label": "Label"
})

# --- Drop & Encode (same as model.py) ---
sim_df = sim_df.drop(columns=["time", "ip.src", "ip.dst"], errors='ignore')
real_df = real_df.drop(columns=["ip.src", "ip.dst", "frame.time"], errors='ignore')
proto_encoder = LabelEncoder()
if "ip.proto" in sim_df.columns and sim_df["ip.proto"].dtype == object:
    sim_df["ip.proto"] = proto_encoder.fit_transform(sim_df["ip.proto"])
if "ip.proto" in real_df.columns and real_df["ip.proto"].dtype == object:
    real_df["ip.proto"] = proto_encoder.fit_transform(real_df["ip.proto"])

# --- Align columns (same as model.py) ---
all_features = set(feature_list) | {"Label"}
sim_df = sim_df[[c for c in sim_df.columns if c in all_features]]
real_df = real_df[[c for c in real_df.columns if c in all_features]]
sim_df = sim_df.fillna(0)
real_df = real_df.fillna(0)
for col in set(real_df.columns) - set(sim_df.columns):
    if col != "Label":
        sim_df[col] = 0
for col in set(sim_df.columns) - set(real_df.columns):
    if col != "Label":
        real_df[col] = 0

# Ensure 'Label' column exists before trying to drop it from features
if "Label" in sim_df.columns and "Label" in real_df.columns:
    common_columns = sorted(list(set(sim_df.columns) & set(real_df.columns)))
    combined_df = pd.concat([sim_df[common_columns], real_df[common_columns]], ignore_index=True)
else:
    raise ValueError("Label column missing after preprocessing.")

# --- Split data (same as model.py) ---
X = combined_df[feature_list]
y = combined_df["Label"]
X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

# We only need the test set, but we must use the same split
train_df, test_df, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --- Scale data (same as model.py) ---
X_test_scaled = scaler.transform(test_df)
# Convert to DataFrame with columns - THIS IS THE KEY
X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=feature_list)


print("\n--- Initializing SHAP Explainer ---")
# 3. Create a SHAP explainer for your model
explainer = shap.TreeExplainer(model)

# 4. Calculate SHAP values for the test set
print("Calculating SHAP values (this may take a moment)...")
# Pass the SCALED DATAFRAME to the explainer
shap_values = explainer.shap_values(X_test_scaled_df) 

# We are interested in explanations for the "DDoS" class (class 1)
shap_values_ddos = shap_values[1]


print("\n--- Generating Global Explanation Plot (Beeswarm) ---")
# 5. Create a "Beeswarm" plot for global importance
plt.figure() # Create a new figure to avoid overlap
shap.summary_plot(
    shap_values_ddos,
    X_test_scaled_df,  # <--- THIS IS THE CORRECTED LINE
    plot_type="dot",
    show=False
)
print("Saving beeswarm plot to 'shap_summary_plot.png'")
plt.savefig("shap_summary_plot.png", bbox_inches='tight')
plt.clf() # Clear the figure after saving


print("\n--- Generating Local Explanation for one Attack ---")
# 6. Explain a SINGLE packet (Local Importance)
attack_index = 0
try:
    y_pred_test = model.predict(X_test_scaled)
    y_test_reset = y_test.reset_index(drop=True) # Reset index for proper comparison
    
    for i in range(len(y_pred_test)):
        if y_pred_test[i] == 1 and y_test_reset[i] == 1:
            attack_index = i
            break
except Exception as e:
    print(f"Could not find attack index, defaulting to 0. Error: {e}")


print(f"Explaining prediction for packet index: {attack_index} (an actual attack)")

# Create a force plot for this single prediction
force_plot = shap.force_plot(
    explainer.expected_value[1],
    shap_values_ddos[attack_index, :],
    X_test_scaled_df.iloc[attack_index, :], # Use scaled data for display
    matplotlib=False
)

# Save the interactive plot to an HTML file
shap.save_html("shap_force_plot.html", force_plot)
print("Saved local force plot to 'shap_force_plot.html'")

print("\nExplanation complete. Check the .png and .html files.")
