"""
wizard.core.config
==================
Pydantic-settings configuration loaded from .env / environment variables.

Usage::

    from wizard.core.config import settings

    # Then use:
    settings.db_path
    settings.llm_provider
    settings.lancedb_path
    ...

All paths are relative to the repo root by default, but can be overridden.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class WizardSettings(BaseSettings):
    """
    Central configuration for the Maintenance Wizard system.
    Override any value via .env file or environment variable.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # REPO / DATA PATHS
    # ------------------------------------------------------------------
    repo_root: Path = Field(
        default=Path(__file__).resolve().parents[2],
        description="Absolute path to the maintenance-wizard repo root",
    )
    data_dir: Path = Field(
        default=Path("data"),
        description="Relative to repo_root: data/",
    )
    db_path: Path = Field(
        default=Path("data/wizard.db"),
        description="SQLite database file (WAL mode, zero-install)",
    )
    sessions_db_path: Path = Field(
        default=Path("data/sessions.db"),
        description="LangGraph SqliteSaver conversation checkpoint DB",
    )
    lancedb_path: Path = Field(
        default=Path("data/lancedb"),
        description="LanceDB vector store directory",
    )
    chromadb_path: Path = Field(
        default=Path("data/chromadb"),
        description="ChromaDB / Mem0 persistence directory",
    )
    models_dir: Path = Field(
        default=Path("data/models"),
        description="Trained model artifacts (joblib, ONNX, etc.)",
    )
    kg_dir: Path = Field(
        default=Path("data/kg"),
        description="Knowledge graph exports (JSON, GraphML)",
    )
    synthetic_dir: Path = Field(
        default=Path("data/synthetic"),
        description="Synthetic dataset outputs",
    )
    quarantine_path: Path = Field(
        default=Path("data/quarantine/invalid_entities.jsonl"),
        description="Invalid entity quarantine log",
    )
    demo_cache_path: Path = Field(
        default=Path("data/demo_cache.json"),
        description="Golden cached responses for demo crash-safety",
    )

    # ------------------------------------------------------------------
    # LLM CONFIG
    # ------------------------------------------------------------------
    llm_provider: Literal["gemini", "ollama", "claude", "openai"] = Field(
        default="gemini",
        description="Primary LLM provider: 'gemini' | 'ollama' | 'claude' | 'openai'",
    )
    llm_model_primary: str = Field(
        default="gemini/gemini-2.0-flash",
        description="LiteLLM model string for primary LLM (Gemini 2.0 Flash — free tier, GA)",
    )
    llm_model_fallback: str = Field(
        default="ollama/qwen2.5:3b",
        description="LiteLLM model string for offline fallback (Qwen2.5-3B via Ollama)",
    )
    llm_model_heavy: str = Field(
        default="gemini/gemini-2.0-flash",
        description="Sonnet-class model for RCA + Maintenance Plan agents",
    )
    llm_model_light: str = Field(
        default="gemini/gemini-2.0-flash",
        description="Haiku-class model for RUL + Prioritization agents",
    )
    llm_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=4096)
    llm_timeout_seconds: float = Field(default=30.0)

    # ------------------------------------------------------------------
    # API KEYS (redacted from logs — never print these)
    # ------------------------------------------------------------------
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key (free tier). Set via GEMINI_API_KEY env var.",
    )
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic Claude API key (optional — for Claude primary mode).",
    )
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key (optional).",
    )

    # ------------------------------------------------------------------
    # EMBEDDINGS
    # ------------------------------------------------------------------
    embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="SentenceTransformers model for RAG embeddings (ONNX backend)",
    )
    embedding_dim: int = Field(default=384, description="Embedding vector dimension")
    reranker_model: str = Field(
        default="ms-marco-MiniLM-L-12-v2",
        description="FlashRank reranker model (ONNX, no torch required)",
    )

    # ------------------------------------------------------------------
    # RAG CONFIG
    # ------------------------------------------------------------------
    rag_chunk_size: int = Field(default=512, description="Token target per chunk")
    rag_chunk_overlap: int = Field(default=64)
    rag_top_k_retrieve: int = Field(default=20, description="Candidates before rerank")
    rag_top_k_final: int = Field(default=5, description="Final cited sources")
    rag_hyde_enabled: bool = Field(
        default=True,
        description="Enable HyDE (hypothetical document embedding) for query expansion",
    )
    rag_nli_gate_enabled: bool = Field(
        default=True,
        description="Enable NLI entailment gate to validate RAG-grounded claims",
    )
    nli_model: str = Field(
        default="cross-encoder/nli-deberta-v3-small",
        description="NLI model for citation entailment check",
    )

    # ------------------------------------------------------------------
    # ML MODEL THRESHOLDS
    # ------------------------------------------------------------------
    anomaly_score_threshold: float = Field(
        default=0.65,
        description="IsolationForest/LSTM-AE score above which anomaly is flagged",
    )
    rul_critical_days: float = Field(
        default=14.0,
        description="RUL p50 <= this → CRITICAL alert",
    )
    rul_warning_days: float = Field(
        default=30.0,
        description="RUL p50 <= this → HIGH warning",
    )
    failure_prob_threshold: float = Field(
        default=0.70,
        description="LightGBM failure probability >= this → flag for prioritization",
    )
    wrps_critical: float = Field(
        default=75.0,
        description="WRPS >= this → CRITICAL risk tier",
    )
    wrps_high: float = Field(
        default=50.0,
        description="WRPS >= this → HIGH risk tier",
    )

    # ------------------------------------------------------------------
    # ALERTING ENGINE
    # ------------------------------------------------------------------
    alert_poll_interval_seconds: int = Field(
        default=5,
        description="APScheduler tick interval for proactive alert evaluator",
    )
    alert_cooldown_seconds: int = Field(
        default=300,
        description="Minimum seconds between repeated alerts for same asset+type",
    )
    demo_eaf04_trigger_seconds: int = Field(
        default=90,
        description=(
            "Seconds after demo start that EAF-04 CRITICAL alert auto-fires "
            "(the judges' wow moment)"
        ),
    )
    cost_avoidance_rate_inr_per_hour: float = Field(
        default=75_000.0,
        description="Assumed downtime cost rate for cost-avoidance ticker (₹75,000/hr)",
    )

    # ------------------------------------------------------------------
    # BACKEND
    # ------------------------------------------------------------------
    backend_host: str = Field(default="127.0.0.1")
    backend_port: int = Field(default=8000)
    backend_reload: bool = Field(default=False)
    backend_workers: int = Field(default=1)

    # ------------------------------------------------------------------
    # FRONTEND
    # ------------------------------------------------------------------
    streamlit_port: int = Field(default=8501)
    streamlit_page_title: str = Field(default="Maintenance Wizard — Tata Steel AI")

    # ------------------------------------------------------------------
    # OBSERVABILITY
    # ------------------------------------------------------------------
    phoenix_enabled: bool = Field(
        default=True,
        description="Launch Arize Phoenix local trace UI (port 6006)",
    )
    phoenix_port: int = Field(default=6006)
    langfuse_enabled: bool = Field(
        default=False,
        description="Enable Langfuse tracing (requires LANGFUSE_PUBLIC_KEY + SECRET_KEY)",
    )
    langfuse_public_key: str = Field(default="")
    langfuse_secret_key: str = Field(default="")

    # ------------------------------------------------------------------
    # EVAL
    # ------------------------------------------------------------------
    deepeval_enabled: bool = Field(default=False)
    ragas_enabled: bool = Field(default=False)
    golden_set_path: Path = Field(
        default=Path("data/golden.jsonl"),
        description="DeepEval golden test set (min 10 Q&A pairs)",
    )

    # ------------------------------------------------------------------
    # SYNTHETIC DATA
    # ------------------------------------------------------------------
    synthetic_doc_count: int = Field(
        default=500,
        description="Target synthetic knowledge document count",
    )
    synthetic_noise_fraction: float = Field(
        default=0.15,
        description="Fraction of synthetic docs with injected noise (15-20%)",
    )
    synthetic_dedup_threshold: float = Field(
        default=0.85,
        description="Cosine similarity threshold above which a doc is deduplicated",
    )
    synthetic_random_seed: int = Field(default=42)

    # ------------------------------------------------------------------
    # CIRCUIT BREAKER
    # ------------------------------------------------------------------
    circuit_breaker_fail_max: int = Field(default=5)
    circuit_breaker_reset_timeout: float = Field(default=60.0)

    # ------------------------------------------------------------------
    # VALIDATORS
    # ------------------------------------------------------------------
    @field_validator("db_path", "sessions_db_path", "lancedb_path", "chromadb_path",
                     "models_dir", "kg_dir", "synthetic_dir", mode="before")
    @classmethod
    def _make_absolute(cls, v: object) -> Path:
        """Keep relative paths as-is; callers resolve against repo_root."""
        return Path(str(v))  # type: ignore[return-value]

    def resolved_db_path(self) -> Path:
        """Return absolute path to wizard.db (relative to cwd if not absolute)."""
        p = Path(self.db_path)
        return p if p.is_absolute() else Path.cwd() / p

    def resolved_lancedb_path(self) -> Path:
        p = Path(self.lancedb_path)
        return p if p.is_absolute() else Path.cwd() / p


# Singleton instance — import and use directly
settings = WizardSettings()
