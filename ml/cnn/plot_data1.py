import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the stripped CSV
df = pd.read_csv('val_accuracy_strip.csv')

# Optional: Convert optimizer, batch size, and dropout to string for labeling
df['optimizer'] = df['optimizer'].astype(str)
df['batch_size'] = df['batch_size'].astype(str)
df['dropout'] = df['dropout'].astype(str)

# Plot configuration
sns.set(style="whitegrid")
plt.figure(figsize=(12, 8))

# Create a FacetGrid to show multiple lines by optimizer and fold
g = sns.relplot(
    data=df,
    x='Epoch',
    y='Val_Acc',
    hue='optimizer',
    col='Fold',
    kind='line',
    style='optimizer',
    markers=True,
    facet_kws={'sharey': True, 'sharex': True}
)

# Titles and layout
g.set_titles("Fold {col_name}")
g.set_axis_labels("Epoch", "Validation Accuracy")
g.add_legend()

plt.suptitle("Validation Accuracy by Epoch, Fold, and Optimizer", y=1.03, fontsize=16)
plt.tight_layout()
plt.show()
