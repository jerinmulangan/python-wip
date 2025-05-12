import re
import csv

log_file = "training_log.txt"
output_csv = "parsed_results.csv"

with open(log_file, "r") as f:
    lines = f.readlines()

# Regex patterns
config_line_pattern = re.compile(r"=== Config: (.*?)\}, Architecture: \[(.*?)\] ===")
epoch_pattern = re.compile(r"Epoch (\d+)/\d+ - Train Loss: ([\d.]+) - Val Acc: ([\d.]+)")
fold_pattern = re.compile(r"--- Fold (\d+)/\d+ ---")

data_rows = []

current_config = {}
current_fold = None

for line in lines:
    line = line.strip()

    # Match config and architecture
    config_match = config_line_pattern.match(line)
    if config_match:
        config_str, architecture = config_match.groups()
        config_dict = eval(config_str + "}")  # Add back closing brace for safe eval
        current_config = {
            "lr": config_dict["lr"],
            "batch_size": config_dict["batch_size"],
            "optimizer": config_dict["optimizer"],
            "dropout": config_dict["dropout"],
            "architecture": f"[{architecture}]"
        }
        continue

    # Match fold
    fold_match = fold_pattern.match(line)
    if fold_match:
        current_fold = int(fold_match.group(1))
        continue

    # Match epoch info
    epoch_match = epoch_pattern.match(line)
    if epoch_match and current_config and current_fold is not None:
        epoch_num = int(epoch_match.group(1))
        train_loss = float(epoch_match.group(2))
        val_acc = float(epoch_match.group(3))

        data_rows.append({
            **current_config,
            "fold": current_fold,
            "epoch": epoch_num,
            "train_loss": train_loss,
            "val_acc": val_acc
        })

# Write CSV
fieldnames = ["lr", "batch_size", "optimizer", "dropout", "architecture", "fold", "epoch", "train_loss", "val_acc"]
with open(output_csv, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data_rows)

print(f"✅ Parsed data saved to {output_csv}")
