# ==========================================
# 1. IMPORT REQUIRED LIBRARIES
# ==========================================
import numpy as np
import pandas as pd
import matplotlib
# Force a non-interactive backend to safely generate files without window system crashes
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler

# Set aesthetic configurations for plots
sns.set_theme(style="whitegrid")

# ==========================================
# 2. GENERATE AND PREPARE REALISTIC DATA
# ==========================================
X_raw, _ = make_blobs(
    n_samples=300, 
    centers=4, 
    cluster_std=0.60, 
    random_state=42
)

df = pd.DataFrame(X_raw, columns=['Annual_Income_k$', 'Spending_Score'])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

print("Dataset sample (First 5 scaled rows):")
print(pd.DataFrame(X_scaled, columns=df.columns).head())
print("\nProcessing visualizations...")

# ==========================================
# 3. THE ELBOW METHOD (FINDING OPTIMAL K)
# ==========================================
wcss = []
k_range = range(1, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=10, random_state=42)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(k_range, wcss, marker='o', linestyle='--', color='b')
plt.title('The Elbow Method for Optimal K')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('WCSS (Inertia)')
plt.xticks(k_range)

# SAVE THE ELBOW PLOT AS AN IMAGE
plt.savefig('elbow_method.png', dpi=300, bbox_inches='tight')
plt.close()
print(" -> Saved: elbow_method.png")

# ==========================================
# 4. TRAINING THE K-MEANS MODEL
# ==========================================
optimal_k = 4
kmeans_final = KMeans(n_clusters=optimal_k, init='k-means++', max_iter=300, n_init=10, random_state=42)
df['Cluster_Labels'] = kmeans_final.fit_predict(X_scaled)

# ==========================================
# 5. VISUALIZING THE RESULTS
# ==========================================
plt.figure(figsize=(10, 6))

sns.scatterplot(
    x='Annual_Income_k$', 
    y='Spending_Score', 
    hue='Cluster_Labels', 
    data=df, 
    palette='viridis', 
    s=70, 
    alpha=0.8
)

cluster_centers = scaler.inverse_transform(kmeans_final.cluster_centers_)

plt.scatter(
    cluster_centers[:, 0], 
    cluster_centers[:, 1], 
    s=250, 
    c='red', 
    marker='X', 
    label='Centroids'
)

plt.title('Customer Segments Derived via K-Means Clustering')
plt.xlabel('Annual Income (k$)')
plt.ylabel('Spending Score (1-100)')
plt.legend(title='Clusters & Metrics')

# SAVE THE FINAL CLUSTERS PLOT AS AN IMAGE
plt.savefig('customer_clusters.png', dpi=300, bbox_inches='tight')
plt.close()
print(" -> Saved: customer_clusters.png")
print("\nExecution complete! Check your project folder for the image files.")

