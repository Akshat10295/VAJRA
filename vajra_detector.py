import argparse
import joblib
import pandas as pd
from scapy.all import sniff, rdpcap, IP, TCP
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# ------------------ Load model and utilities ------------------
print("Initializing Vajra DDoS Detector...")

model = joblib.load("ddos_model.pkl")
scaler = joblib.load("scaler.pkl")
feature_list = joblib.load("feature_list.pkl")

print(f"Loaded model and feature list: {feature_list}")


# ------------------ Feature Extraction ------------------
def extract_features(pkt):
    """Extracts relevant numerical features from each packet."""
    try:
        if IP in pkt:
            ip_layer = pkt[IP]
            proto = ip_layer.proto
            frame_len = len(pkt)
        else:
            return None

        tcp_srcport = tcp_dstport = tcp_flags = tcp_ack = tcp_syn = tcp_push = 0

        if TCP in pkt:
            tcp_layer = pkt[TCP]
            tcp_srcport = tcp_layer.sport
            tcp_dstport = tcp_layer.dport
            tcp_flags = int(tcp_layer.flags)
            tcp_ack = 1 if tcp_layer.flags & 0x10 else 0
            tcp_syn = 1 if tcp_layer.flags & 0x02 else 0
            tcp_push = 1 if tcp_layer.flags & 0x08 else 0

        return {
            "frame.len": frame_len,
            "ip.proto": proto,
            "tcp.srcport": tcp_srcport,
            "tcp.dstport": tcp_dstport,
            "tcp.flags": tcp_flags,
            "tcp.flags.ack": tcp_ack,
            "tcp.flags.push": tcp_push,
            "tcp.flags.syn": tcp_syn,
        }

    except Exception:
        return None


# ------------------ Prediction Logic ------------------
def predict_packet(features):
    """Scales and predicts label for a single feature set."""
    df = pd.DataFrame([features])[feature_list]
    X_scaled = scaler.transform(df)
    pred = model.predict(X_scaled)[0]
    return pred

# ------------------ LIVE MODE ------------------
def live_mode():
    """Continuously monitors live packets."""
    print("\nStarting real-time detection (Press Ctrl+C to stop)...\n")

    def process_packet(pkt):
        features = extract_features(pkt)
        if not features:
            return
        pred = predict_packet(features)
        label = "DDoS Attack" if pred == 1 else "Normal"
        src = pkt[IP].src if IP in pkt else "N/A"
        dst = pkt[IP].dst if IP in pkt else "N/A"
        print(f"[LIVE] {src} → {dst} | {label}")

    sniff(prn=process_packet, store=False)


# ------------------ OFFLINE MODE ------------------
def offline_mode(pcap_file, output_file, max_packets):
    """Processes packets from a PCAP file and logs predictions."""
    print(f"\n[OFFLINE] Reading packets from: {pcap_file}")
    packets = rdpcap(pcap_file)
    print(f"[OFFLINE] Total packets loaded: {len(packets)}")

    results = []
    for i, pkt in enumerate(packets[:max_packets]):
        features = extract_features(pkt)
        if not features:
            continue
        pred = predict_packet(features)
        src = pkt[IP].src if IP in pkt else None
        dst = pkt[IP].dst if IP in pkt else None
        results.append({
            "index": i,
            "src": src,
            "dst": dst,
            "prediction": "DDoS" if pred == 1 else "Normal"
        })

    out_df = pd.DataFrame(results)
    out_df.to_csv(output_file, index=False)
    print(f"[OFFLINE] Saved predictions to {output_file}")
    print(f"[OFFLINE] Total analyzed packets: {len(out_df)}")


# ------------------ Main CLI Entry ------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vajra DDoS Detection Tool")
    parser.add_argument("--mode", choices=["live", "offline"], required=True, help="Detection mode")
    parser.add_argument("--pcap", type=str, help="Path to .pcap file for offline mode")
    parser.add_argument("--out", type=str, default="predictions.csv", help="Output CSV file for offline mode")
    parser.add_argument("--max", type=int, default=500, help="Maximum packets to analyze (offline mode)")
    args = parser.parse_args()
    # python vajra_detector.py --mode offline --pcap test_traffic.pcap --out my_results.csv --max 500
    # python vajra_detector.py --mode live
    if args.mode == "live":
        live_mode()
    elif args.mode == "offline":
        if not args.pcap:
            print("Please provide a .pcap file using --pcap <filename>")
        else:
            offline_mode(args.pcap, args.out, args.max)
