import re
import csv

input_file = "training_log1.txt"   # your full raw input file
output_file = "val_accuracy_strip.csv"

results = []
current_fold = None
current_model = None
current_config = None

# Regex patterns
fold_model_config_re = re.compile(
    r"Fold (\d+) - Model: (\S+) - Config: ({.*})"
)
epoch_re = re.compile(
    r"Epoch\s+(\d+): Train Loss = [\d.]+ \| Val Acc = ([\d.]+)"
)

with open(input_file, "r") as infile:
    for line in infile:
        fold_match = fold_model_config_re.search(line)
        epoch_match = epoch_re.search(line)

        if fold_match:
            current_fold = int(fold_match.group(1))
            current_model = fold_match.group(2)
            current_config = eval(fold_match.group(3))  # assumes safe, controlled input
        elif epoch_match and current_fold is not None:
            epoch = int(epoch_match.group(1))
            val_acc = float(epoch_match.group(2))
            results.append({
                "Fold": current_fold,
                "Model": current_model,
                "Epoch": epoch,
                "Val_Acc": val_acc,
                **current_config  # flatten config dict
            })

# Get all unique config keys for CSV header
all_keys = sorted({key for r in results for key in r if key not in ("Fold", "Model", "Epoch", "Val_Acc")})

fieldnames = ["Fold", "Model", "Epoch", "Val_Acc"] + all_keys

# Write to CSV
with open(output_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print(f"Validation accuracy strip saved to {output_file}")
