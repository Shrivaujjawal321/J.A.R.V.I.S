"""
wizard.data
===========
Dataset layer for the Maintenance Wizard system.

Provides loaders for:
  - NASA C-MAPSS FD001 + FD003 (RUL regression + anomaly windows)
  - AI4I 2020 (UCI CC-BY-4.0, fault classification)

Public API::

    from wizard.data import (
        load_cmapss,           # -> CmapssDataset namedtuple
        load_ai4i,             # -> pd.DataFrame (Celsius, mapped fault names)
        ingest_sensor_rows,    # -> int  (rows written to wizard.db)
        get_framed_df,         # -> pd.DataFrame  (steel-plant column names)
        CMAPSS_STEEL_MAP,      # column alias dict
        AI4I_FAULT_MAP,        # fault -> steel fault name
    )

All heavy work is in sub-modules; this namespace re-exports the stable
integration contract that the agentic-core wave imports.
"""

from wizard.data.cmapss_loader import (
    CmapssDataset,
    load_cmapss,
    CMAPSS_STEEL_MAP,
    RUL_CAP,
)
from wizard.data.ai4i_loader import (
    load_ai4i,
    AI4I_FAULT_MAP,
    AI4I_STEEL_FAULT_CODES,
)
from wizard.data.dataset_framing import get_framed_df, frame_ai4i
from wizard.data.db_ingest import ingest_sensor_rows

__all__ = [
    # C-MAPSS
    "CmapssDataset",
    "load_cmapss",
    "CMAPSS_STEEL_MAP",
    "RUL_CAP",
    # AI4I
    "load_ai4i",
    "AI4I_FAULT_MAP",
    "AI4I_STEEL_FAULT_CODES",
    # Framing
    "get_framed_df",
    "frame_ai4i",
    # DB ingest
    "ingest_sensor_rows",
]
