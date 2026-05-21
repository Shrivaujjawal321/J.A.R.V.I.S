"""One-call global seed lock across random, numpy, torch (CPU+CUDA), and LightGBM."""

from __future__ import annotations

import os
import random


def set_seed(seed: int = 42) -> int:
    """Set seed for random, numpy, torch (CPU + all CUDA devices), and LightGBM determinism.

    Idempotent — safe to call multiple times with the same value.
    Returns the seed used.
    """
    random.seed(seed)

    import numpy as np
    np.random.seed(seed)

    # LightGBM determinism via env var (must be set before any lgb calls)
    os.environ["LIGHTGBM_SEED"] = str(seed)

    # Torch — optional import so harness works in torch-free envs
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

    return seed
