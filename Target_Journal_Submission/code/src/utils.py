import logging, os, random
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.environ.get("RESULTS_DIR", os.path.join(ROOT, "results"))
LOGS = os.path.join(RESULTS, "experiment_logs")


def set_seed(seed):
    random.seed(seed); np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass


def device():
    """CPU / CUDA / Apple-MPS detection (only the optional CNN uses it)."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"


def get_logger(name):
    os.makedirs(LOGS, exist_ok=True)
    lg = logging.getLogger(name)
    lg.setLevel(logging.INFO)
    if not lg.handlers:
        fmt = logging.Formatter("%(asctime)s %(message)s")
        for h in (logging.FileHandler(os.path.join(LOGS, f"{name}.log")), logging.StreamHandler()):
            h.setFormatter(fmt); lg.addHandler(h)
    return lg
