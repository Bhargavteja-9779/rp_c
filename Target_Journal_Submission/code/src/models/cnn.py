"""Compact 1D-CNN regressor for NIR spectra (architecture family used for mango DM in the
literature: one convolution layer followed by dense layers). Runs on CPU, CUDA or Apple MPS."""
from __future__ import annotations

import numpy as np


class CNN1D:
    def __init__(self, epochs=40, batch=256, lr=1e-3, weight_decay=1e-4, filters=8, kernel=9,
                 seed=0, device=None, val_frac=0.1, patience=8, threads=None):
        self.__dict__.update(dict(epochs=epochs, batch=batch, lr=lr, weight_decay=weight_decay, filters=filters,
                                  kernel=kernel, seed=seed, device=device, val_frac=val_frac, patience=patience,
                                  threads=threads))

    def _net(self, p):
        import torch.nn as nn
        return nn.Sequential(
            nn.Conv1d(1, self.filters, self.kernel, padding=self.kernel // 2), nn.ELU(),
            nn.Flatten(), nn.Linear(self.filters * p, 64), nn.ELU(), nn.Linear(64, 32), nn.ELU(), nn.Linear(32, 1))

    def fit(self, X, y, units=None):
        import torch
        from ..utils import device as _dev
        if self.threads:
            torch.set_num_threads(self.threads)
        torch.manual_seed(self.seed)
        rng = np.random.default_rng(self.seed)
        dev = self.device or _dev()
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-8
        self.ym, self.ys = y.mean(), y.std() + 1e-8
        Xs = ((X - self.mu) / self.sd).astype(np.float32)
        ys = ((y - self.ym) / self.ys).astype(np.float32)
        # unit-grouped internal validation split for early stopping
        if units is None:
            units = np.arange(len(y)).astype(str)
        uu = np.unique(units)
        vu = rng.choice(uu, size=max(1, int(self.val_frac * len(uu))), replace=False)
        va = np.isin(units, vu)
        net = self._net(X.shape[1]).to(dev)
        opt = torch.optim.Adam(net.parameters(), lr=self.lr, weight_decay=self.weight_decay)
        Xt = torch.from_numpy(Xs[~va]).unsqueeze(1).to(dev); yt = torch.from_numpy(ys[~va]).to(dev)
        Xv = torch.from_numpy(Xs[va]).unsqueeze(1).to(dev); yv = torch.from_numpy(ys[va]).to(dev)
        best, best_state, bad = np.inf, None, 0
        self.history = []
        for ep in range(self.epochs):
            net.train()
            perm = torch.from_numpy(rng.permutation(len(yt)))
            tl = 0.0
            for i in range(0, len(perm), self.batch):
                b = perm[i:i + self.batch]
                opt.zero_grad()
                loss = ((net(Xt[b]).squeeze(1) - yt[b]) ** 2).mean()
                loss.backward(); opt.step()
                tl += loss.item() * len(b)
            net.eval()
            with torch.no_grad():
                vl = ((net(Xv).squeeze(1) - yv) ** 2).mean().item()
            self.history.append((ep, tl / len(yt), vl))
            if vl < best - 1e-5:
                best, bad = vl, 0
                best_state = {k: v.detach().clone() for k, v in net.state_dict().items()}
            else:
                bad += 1
                if bad >= self.patience:
                    break
        net.load_state_dict(best_state)
        self.net, self.dev = net, dev
        return self

    def predict(self, X):
        import torch
        self.net.eval()
        out = []
        Xs = ((X - self.mu) / self.sd).astype(np.float32)
        with torch.no_grad():
            for i in range(0, len(Xs), 8192):
                xb = torch.from_numpy(Xs[i:i + 8192]).unsqueeze(1).to(self.dev)
                out.append(self.net(xb).squeeze(1).cpu().numpy())
        return np.concatenate(out) * self.ys + self.ym
