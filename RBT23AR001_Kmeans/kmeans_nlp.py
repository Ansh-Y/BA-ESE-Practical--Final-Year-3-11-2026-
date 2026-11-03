# K-Means for NLP: clustering text documents (Colab ready, no extra installs)
# Pipeline: raw text -> TF-IDF -> SVD (dense, normalized) -> K-Means (from scratch)

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score

# ---------- 1. Data ----------
cats = ["sci.space", "rec.sport.hockey", "comp.graphics", "talk.politics.guns"]
data = fetch_20newsgroups(subset="train", categories=cats,
                          remove=("headers", "footers", "quotes"))
texts, y_true = data.data, data.target
K = len(cats)
print(f"{len(texts)} documents, {K} true classes")

# ---------- 2. Features ----------
tfidf = TfidfVectorizer(stop_words="english", max_df=0.5, min_df=5, sublinear_tf=True)
X_tfidf = tfidf.fit_transform(texts)
terms = np.array(tfidf.get_feature_names_out())

# SVD (LSA) makes vectors dense and compact; Normalizer makes Euclidean ~ cosine
reducer = make_pipeline(TruncatedSVD(100, random_state=0), Normalizer(copy=False))
X = reducer.fit_transform(X_tfidf)


# ---------- 3. K-Means from scratch ----------
def sq_dist(X, C):
    return (X ** 2).sum(1)[:, None] - 2 * X @ C.T + (C ** 2).sum(1)[None]


class KMeansScratch:
    def __init__(self, k, n_init=5, max_iter=100, tol=1e-4, seed=0):
        self.k, self.n_init, self.max_iter, self.tol, self.seed = k, n_init, max_iter, tol, seed

    def _init_pp(self, X, rng):  # k-means++ seeding
        C = [X[rng.integers(len(X))]]
        for _ in range(self.k - 1):
            d = sq_dist(X, np.array(C)).min(1).clip(0)
            C.append(X[rng.choice(len(X), p=d / d.sum())])
        return np.array(C)

    def fit(self, X):
        rng = np.random.default_rng(self.seed)
        best = None
        for _ in range(self.n_init):
            C = self._init_pp(X, rng)
            for _ in range(self.max_iter):
                lab = sq_dist(X, C).argmin(1)                      # assign step
                newC = np.array([X[lab == j].mean(0) if (lab == j).any()
                                 else X[rng.integers(len(X))]       # re-seed empty cluster
                                 for j in range(self.k)])           # update step
                shift = np.linalg.norm(newC - C)
                C = newC
                if shift < self.tol:
                    break
            inertia = sq_dist(X, C).min(1).sum()
            if best is None or inertia < best[0]:
                best = (inertia, C)
        self.inertia_, self.centers_ = best
        self.labels_ = sq_dist(X, self.centers_).argmin(1)
        return self

    def predict(self, X):
        return sq_dist(X, self.centers_).argmin(1)


# ---------- 4. Choose k (elbow + silhouette) ----------
ks = range(2, 9)
inertias, sils = [], []
for k in ks:
    m = KMeansScratch(k).fit(X)
    inertias.append(m.inertia_)
    sils.append(silhouette_score(X, m.labels_))

fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
ax[0].plot(ks, inertias, "o-"); ax[0].set(title="Elbow (inertia)", xlabel="k")
ax[1].plot(ks, sils, "o-");     ax[1].set(title="Silhouette", xlabel="k")
plt.tight_layout(); plt.show()

# ---------- 5. Final model + evaluation ----------
km = KMeansScratch(K).fit(X)
sk = KMeans(K, n_init=5, random_state=0).fit(X)
for name, lab in [("scratch", km.labels_), ("sklearn", sk.labels_)]:
    print(f"{name:8s} silhouette={silhouette_score(X, lab):.3f}  "
          f"ARI={adjusted_rand_score(y_true, lab):.3f}  "
          f"NMI={normalized_mutual_info_score(y_true, lab):.3f}")

# ---------- 6. Interpret clusters: top TF-IDF terms ----------
for j in range(K):
    mean_vec = np.asarray(X_tfidf[km.labels_ == j].mean(0)).ravel()
    top = terms[mean_vec.argsort()[-8:][::-1]]
    print(f"Cluster {j} ({(km.labels_ == j).sum()} docs): {', '.join(top)}")

# ---------- 7. 2D visualization ----------
X2 = PCA(2, random_state=0).fit_transform(X)
plt.figure(figsize=(6, 5))
plt.scatter(X2[:, 0], X2[:, 1], c=km.labels_, cmap="tab10", s=8)
plt.title("K-Means clusters (PCA view)"); plt.show()

# ---------- 8. Cluster new text ----------
new = ["The shuttle launch was delayed due to engine trouble",
       "The goalie made 40 saves in overtime"]
print(km.predict(reducer.transform(tfidf.transform(new))))
