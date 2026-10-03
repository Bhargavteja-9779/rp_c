"""PLS1 regression (NIPALS) with the chemometric diagnostics used in this work.

Notation (training data X ∈ R^{n×p}, mean-centred):
  T = X_c R          scores, R = W (PᵀW)^{-1}
  ŷ_a(x) = ȳ + (x − x̄)ᵀ R_{:,1:a} q_{1:a}
  Hotelling T²(x) = Σ_j t_j² / s_j²        (s_j² = sample variance of training score j)
  leverage h(x)  = 1/n + Σ_j t_j² / (t_jᵀ t_j)
  Q(x)           = ‖(x − x̄) − P_{:,1:a} t‖²   (squared reconstruction residual)
"""
import numpy as np


class PLS1:
    def __init__(self, n_components=20):
        self.A = int(n_components)

    def fit(self, X, y):
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        n, p = X.shape
        A = min(self.A, n - 1, p)
        self.x_mean = X.mean(0)
        self.y_mean = y.mean()
        Xa = X - self.x_mean
        yc = y - self.y_mean
        W = np.zeros((p, A)); P = np.zeros((p, A)); q = np.zeros(A); T = np.zeros((n, A))
        for a in range(A):
            w = Xa.T @ yc
            nw = np.linalg.norm(w)
            if nw < 1e-12:
                A = a
                break
            w /= nw
            t = Xa @ w
            tt = t @ t
            pa = Xa.T @ t / tt
            q[a] = yc @ t / tt
            Xa -= np.outer(t, pa)
            W[:, a], P[:, a], T[:, a] = w, pa, t
        self.A = A
        self.W, self.P, self.q, self.T = W[:, :A], P[:, :A], q[:A], T[:, :A]
        self.R = self.W @ np.linalg.pinv(self.P.T @ self.W)
        self.t_var = self.T.var(0, ddof=1) + 1e-300
        self.t_ss = (self.T ** 2).sum(0) + 1e-300
        self.n = n
        self.n_lv = A
        return self

    def set_n_lv(self, a):
        self.n_lv = int(min(a, self.A))
        return self

    def scores(self, X, a=None):
        a = self.n_lv if a is None else a
        return (np.asarray(X, float) - self.x_mean) @ self.R[:, :a]

    def predict(self, X, a=None):
        a = self.n_lv if a is None else a
        return self.scores(X, a) @ self.q[:a] + self.y_mean

    def predict_all(self, X):
        """Predictions for 1..A latent variables, shape (n, A)."""
        S = self.scores(X, self.A) * self.q
        return np.cumsum(S, axis=1) + self.y_mean

    def diagnostics(self, X, a=None):
        """Returns dict with T2, leverage h and Q residual for the model with ``a`` LVs."""
        a = self.n_lv if a is None else a
        Xc = np.asarray(X, float) - self.x_mean
        t = Xc @ self.R[:, :a]
        T2 = (t ** 2 / self.t_var[:a]).sum(1)
        h = 1.0 / self.n + (t ** 2 / self.t_ss[:a]).sum(1)
        E = Xc - t @ self.P[:, :a].T
        Q = (E ** 2).sum(1)
        return {"T2": T2, "h": h, "Q": Q, "scores": t}
