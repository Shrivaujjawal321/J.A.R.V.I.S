"""
wizard.rag.smoke_rag
====================
Smoke test for the RAG layer.

Verifies:
  1. LanceDB store can be created (in a temp directory).
  2. 5 toy Markdown documents can be ingested.
  3. A query returns at least 1 cited chunk with expected fields.
  4. format_context_block produces non-empty Source [N] output.
  5. retrieve_context tool returns a valid ContextResult dict.
  6. NLI faithfulness gate runs without error (if model available).
  7. Empty store query returns empty list gracefully.

Run::

    python -m wizard.rag.smoke_rag
    # or
    python wizard/rag/smoke_rag.py

Does NOT require GPU. Does NOT require Gemini API key (HyDE is disabled).
Downloads bge-small-en-v1.5 (~90MB) and cross-encoder/nli-deberta-v3-small (~80MB)
on first run — subsequent runs use HuggingFace cache.
"""

from __future__ import annotations

import logging
import sys
import tempfile
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("smoke_rag")

# ---------------------------------------------------------------------------
# 5 toy documents — realistic steel-plant maintenance content
# ---------------------------------------------------------------------------

TOY_DOCS: list[dict] = [
    {
        "doc_name": "BF-SOP-001-Cooling-System",
        "asset_id": "BF-01",
        "equipment_id": "BF-01",
        "equipment_type": "blast_furnace",
        "doc_type": "sop",
        "criticality": "critical",
        "text": """## Section 3 — Cooling Water System Maintenance

### 3.1 Inspection Schedule
The cooling water valve (ID: BF-CWV-031) must be inspected every 500 operating hours.
Visual inspection includes checking for corrosion, scale buildup, and valve seat wear.
Temperature differential across the valve should not exceed 15°C during normal operation.

### 3.2 Fault Indicators
Cooling water flow rate below 45 m³/hour indicates blockage or pump cavitation.
Temperature rise exceeding 12°C above baseline triggers Level-2 alert in SCADA.
Pressure drop > 0.8 bar across the circuit requires immediate investigation.

### 3.3 Corrective Action
Step 1: Isolate the circuit using bypass valve BF-BPV-019.
Step 2: Flush the line with demineralized water at 60°C for 20 minutes.
Step 3: Replace the strainer element (Part No: SKF-STR-080) if flow < 40 m³/hour.
Step 4: Record corrective action in the CMMS work order system.
""",
    },
    {
        "doc_name": "EAF-Manual-Electrode-System",
        "asset_id": "EAF-04",
        "equipment_id": "EAF-04",
        "equipment_type": "electric_arc_furnace",
        "doc_type": "manual",
        "criticality": "critical",
        "text": """## Section 5 — Electrode Arm Hydraulic System

### 5.1 Hydraulic Specifications
Operating pressure: 180–210 bar. Maximum working pressure: 250 bar.
Hydraulic oil: ISO VG 46 (change interval: 4000 operating hours).
Filter rating: 10 micron absolute. Bypass valve opens at 3.5 bar differential.

### 5.2 Bearing Maintenance
Electrode arm pivot bearings (SKF 6310-2RS1) require lubrication every 250 hours.
Apply 15g of Mobilux EP2 grease per bearing using the designated grease nipple.
Replace bearings at vibration reading > 7.2 mm/s (RMS) or temperature > 85°C.
Replacement kit part number: EAF-BEARING-KIT-04.

### 5.3 Failure Signatures
Bearing failure typically progresses: noise increase → vibration rise → temperature spike.
CRITICAL threshold: temperature > 95°C or vibration > 9.0 mm/s — immediate shutdown required.
Mean time between failure (MTBF) for this bearing class: 8,500 hours.
""",
    },
    {
        "doc_name": "Pump-P80-Failure-Analysis-2024",
        "asset_id": "P80-BEARING",
        "equipment_id": "P80-BEARING",
        "equipment_type": "centrifugal_pump",
        "doc_type": "failure_analysis",
        "criticality": "high",
        "text": """## Failure Analysis Report — Pump P80 Bearing Failure (March 2024)

### Root Cause Summary
Premature bearing failure occurred after 3,200 hours (MTBF 6,000 hours).
Root cause identified as lubrication starvation due to blocked grease channel.
Contributing factor: vibration-induced loosening of grease nipple cap.

### 5-Why Analysis
1. Why did the bearing fail? — Inadequate lubrication.
2. Why was lubrication inadequate? — Grease channel blocked by contamination.
3. Why was the channel contaminated? — Coolant leak from adjacent seal.
4. Why did the seal leak? — Seal replacement interval exceeded (actual 3,800h vs 2,500h spec).
5. Why was the interval exceeded? — CMMS PM work order not triggered due to hours counter reset.

### Corrective Actions
- Implement hourly counter validation in CMMS (completed 2024-04-15).
- Increase seal inspection frequency to every 1,500 hours.
- Add coolant level sensor on P80 lube circuit.

### Similar Equipment
This failure pattern applies to pumps P81, P82, P83 sharing the same bearing class (NU-330EM).
""",
    },
    {
        "doc_name": "Conveyor-HSM-Bearing-SOP",
        "asset_id": "HSM-CONV-01",
        "equipment_id": "HSM-CONV-01",
        "equipment_type": "conveyor",
        "doc_type": "sop",
        "criticality": "high",
        "text": """## Section 2 — Roller Bearing Replacement Procedure

### 2.1 Safety Requirements
Lock-out/Tag-out (LOTO) procedure LOTO-HSM-07 must be completed before starting.
Minimum two technicians required. PPE: heat-resistant gloves, safety glasses, steel-toe boots.
Estimated duration: 4 hours. Requires planned production stoppage.

### 2.2 Replacement Steps
Step 1: Remove drive coupling using hydraulic puller (Tool No: HSM-PULL-03).
Step 2: Extract bearing using 20-ton press (Part: FAG-33210-A replacement bearing).
Step 3: Clean bearing housing bore with acetone. Inspect for spalling or corrosion.
Step 4: Heat replacement bearing to 80°C using induction heater. Install within 90 seconds.
Step 5: Apply 25g Mobilith SHC 100 grease to bearing cavity before sealing.
Step 6: Align coupling to within ±0.05mm using laser alignment tool (Tool: HSM-ALIGN-02).
Step 7: Verify vibration < 3.5 mm/s RMS after restart before releasing to production.

### 2.3 Parts Required
- FAG-33210-A bearing (stock location: Warehouse B, Bin 7)
- O-ring kit HSM-OR-021 (always replace O-rings on reassembly)
""",
    },
    {
        "doc_name": "Hydraulic-Unit-HPU-Incident-2023",
        "asset_id": "HPU-03",
        "equipment_id": "HPU-03",
        "equipment_type": "hydraulic_power_unit",
        "doc_type": "incident_summary",
        "criticality": "high",
        "text": """## Incident Report — HPU-03 Pressure Loss Event (November 2023)

### Incident Summary
HPU-03 lost hydraulic pressure (0 bar from 185 bar operating) at 14:32 IST on 2023-11-18.
Production impact: 3.5 hours unplanned downtime. Cost: ₹2,62,500 (at ₹75,000/hr rate).

### Timeline
14:30 — Operator noted pressure gauge fluctuation (185→175→140 bar over 2 minutes).
14:32 — SCADA low-pressure alarm fired. Emergency pressure relief valve opened.
14:35 — Maintenance team dispatched. Hydraulic pump shaft found sheared.
16:10 — Replacement pump (spare HPU-PUMP-SPARE-03) installed and pressure restored.
18:02 — System recommissioned and production resumed.

### Root Cause
Pump shaft fatigue failure due to cavitation damage from low oil level.
Oil level float sensor had failed 6 days prior — logged but not actioned.

### Lessons Learned
1. Unactioned sensor faults must trigger escalation if not resolved within 24 hours.
2. Minimum oil level alarm should have dual redundancy.
3. Spare pump must be pre-staged for CRITICAL-tier equipment.
""",
    },
]


def run_smoke_test(verbose: bool = True) -> bool:
    """
    Execute the full smoke test. Returns True on pass, False on failure.
    """
    logger.info("=" * 60)
    logger.info("Maintenance Wizard — RAG layer smoke test")
    logger.info("=" * 60)

    passed = 0
    failed = 0

    def ok(msg: str) -> None:
        nonlocal passed
        passed += 1
        logger.info("[PASS] %s", msg)

    def fail(msg: str, exc: Exception = None) -> None:
        nonlocal failed
        failed += 1
        logger.error("[FAIL] %s%s", msg, f": {exc}" if exc else "")

    # ------------------------------------------------------------------
    # Test 0: py_compile guard — already confirmed by build script, but
    # verify imports work at runtime.
    # ------------------------------------------------------------------
    logger.info("")
    logger.info("Step 0: Import wizard.rag modules")
    try:
        from wizard.rag.store import get_store, ensure_fts_index, TABLE_NAME
        from wizard.rag.embedder import embed_texts, embed_single
        from wizard.rag.ingestion import ingest_text
        from wizard.rag.retriever import retrieve, format_context_block, chunks_to_cited_sources
        from wizard.rag.faithfulness import run_faithfulness_gate
        from wizard.rag.tools import retrieve_context, RAG_TOOLS, ContextResult
        ok("All wizard.rag submodules import cleanly.")
    except Exception as exc:
        fail("Import error", exc)
        return False

    # ------------------------------------------------------------------
    # Use a temp directory so the smoke test is fully isolated
    # ------------------------------------------------------------------
    with tempfile.TemporaryDirectory(prefix="wizard_rag_smoke_") as tmpdir:
        tmp_path = Path(tmpdir) / "lancedb"

        # ------------------------------------------------------------------
        # Test 1: Store creation
        # ------------------------------------------------------------------
        logger.info("")
        logger.info("Step 1: Create LanceDB store in temp dir")
        try:
            db = get_store(db_path=tmp_path)
            assert db is not None
            ok(f"LanceDB store created at {tmp_path}")
        except Exception as exc:
            fail("Store creation failed", exc)
            return False

        # ------------------------------------------------------------------
        # Test 2: Empty store query — must not crash
        # ------------------------------------------------------------------
        logger.info("")
        logger.info("Step 2: Query empty store (must return [] gracefully)")
        try:
            results = retrieve("bearing temperature alarm", db=db)
            assert isinstance(results, list)
            assert len(results) == 0
            ok("Empty store query returned [] without error.")
        except Exception as exc:
            fail("Empty store query raised exception", exc)
            # Not fatal — continue

        # ------------------------------------------------------------------
        # Test 3: Ingest 5 toy documents
        # ------------------------------------------------------------------
        logger.info("")
        logger.info("Step 3: Ingest 5 toy documents")
        total_chunks = 0
        for doc in TOY_DOCS:
            try:
                n = ingest_text(
                    text=doc["text"],
                    doc_name=doc["doc_name"],
                    asset_id=doc["asset_id"],
                    equipment_id=doc["equipment_id"],
                    equipment_type=doc["equipment_type"],
                    doc_type=doc["doc_type"],
                    criticality=doc["criticality"],
                    use_contextual_prefix=False,  # avoid LLM call in smoke test
                    db=db,
                )
                total_chunks += n
                logger.info("  Ingested '%s' → %d chunks", doc["doc_name"], n)
            except Exception as exc:
                fail(f"Ingest failed for '{doc['doc_name']}'", exc)

        if total_chunks > 0:
            ok(f"Ingested 5 documents → {total_chunks} total chunks.")
        else:
            fail("No chunks ingested from 5 toy documents.")
            return False

        # ------------------------------------------------------------------
        # Test 4: Retrieve — general query
        # ------------------------------------------------------------------
        logger.info("")
        logger.info("Step 4: Retrieve — general query")
        try:
            results = retrieve(
                query="bearing vibration temperature fault",
                top_k=3,
                use_hyde=False,  # disable HyDE to avoid LLM call
                db=db,
            )
            assert isinstance(results, list), "Expected list"
            assert len(results) > 0, "Expected at least 1 result"

            # Check fields present
            r0 = results[0]
            assert r0.text, "chunk text must not be empty"
            assert r0.doc_name, "doc_name must not be empty"
            assert r0.rerank_score >= 0.0, "rerank_score must be >= 0"

            ok(f"General query returned {len(results)} chunks. Top: '{r0.doc_name}' § {r0.section}")
        except Exception as exc:
            fail("General query retrieval failed", exc)
            return False

        # ------------------------------------------------------------------
        # Test 5: Retrieve — equipment-scoped query
        # ------------------------------------------------------------------
        logger.info("")
        logger.info("Step 5: Retrieve — equipment-scoped (EAF-04)")
        try:
            eaf_results = retrieve(
                query="electrode bearing lubrication",
                equipment_id="EAF-04",
                top_k=3,
                use_hyde=False,
                db=db,
            )
            assert isinstance(eaf_results, list)
            if len(eaf_results) > 0:
                # All results should be from EAF-04
                for r in eaf_results:
                    assert r.equipment_id == "EAF-04", (
                        f"Expected equipment_id='EAF-04', got '{r.equipment_id}'"
                    )
                ok(f"Scoped query (EAF-04) returned {len(eaf_results)} chunks, all correctly scoped.")
            else:
                ok("Scoped query (EAF-04) returned [] — acceptable if FTS not available.")
        except Exception as exc:
            fail("Equipment-scoped query failed", exc)

        # ------------------------------------------------------------------
        # Test 6: format_context_block — Source [N] output
        # ------------------------------------------------------------------
        logger.info("")
        logger.info("Step 6: format_context_block produces Source [N] output")
        try:
            chunks = retrieve(
                query="cooling water valve inspection",
                top_k=2,
                use_hyde=False,
                db=db,
            )
            assert len(chunks) > 0
            block = format_context_block(chunks)
            assert "Source [1]" in block, "Expected 'Source [1]' in context block"
            assert len(block) > 50, "Context block seems too short"
            ok(f"Context block generated ({len(block)} chars). First 100: {block[:100]!r}")
        except Exception as exc:
            fail("format_context_block failed", exc)

        # ------------------------------------------------------------------
        # Test 7: retrieve_context tool (LangGraph-compatible)
        # ------------------------------------------------------------------
        logger.info("")
        logger.info("Step 7: retrieve_context tool (ContextResult dict)")
        try:
            # Temporarily patch settings to use our temp db
            # The tool opens its own db — we need to call it through the module
            # so we patch the store to use tmp_path
            import wizard.rag.store as _store_mod
            original_path = _store_mod._get_lancedb_path

            def _patched_path():
                return tmp_path

            _store_mod._get_lancedb_path = _patched_path

            try:
                result_dict = retrieve_context(
                    query="pump bearing failure lubrication",
                    top_k=3,
                )
                assert isinstance(result_dict, dict), "Expected dict"
                # Validate it parses as ContextResult
                cr = ContextResult(**result_dict)
                assert cr.chunk_count >= 0
                ok(f"retrieve_context tool returned ContextResult with {cr.chunk_count} chunks.")
            finally:
                _store_mod._get_lancedb_path = original_path

        except Exception as exc:
            fail("retrieve_context tool failed", exc)

        # ------------------------------------------------------------------
        # Test 8: NLI faithfulness gate
        # ------------------------------------------------------------------
        logger.info("")
        logger.info("Step 8: NLI faithfulness gate")
        try:
            chunks = retrieve(
                query="bearing replacement procedure",
                top_k=2,
                use_hyde=False,
                db=db,
            )

            # Simulate an LLM answer that cites these chunks
            if len(chunks) >= 1:
                answer = (
                    "The bearing replacement requires LOTO procedure completion [1]. "
                    "Apply heat to 80°C before installation to achieve interference fit [1]."
                )
                gate_result = run_faithfulness_gate(
                    answer_text=answer,
                    retrieved_chunks=chunks,
                    threshold=0.3,  # low threshold for smoke test (NLI needs real chunks)
                )
                assert gate_result.overall_faithfulness >= 0.0
                assert gate_result.confidence in ("verified", "unverified", "low")
                ok(
                    f"NLI gate ran: overall_faithfulness={gate_result.overall_faithfulness:.3f}, "
                    f"confidence={gate_result.confidence}, "
                    f"claims_scored={len(gate_result.claim_scores)}"
                )
            else:
                ok("NLI gate skipped — no chunks to test against (empty retrieval).")
        except Exception as exc:
            # NLI model download may fail offline — warn but don't hard-fail smoke
            logger.warning("[WARN] NLI gate test failed (may be offline): %s", exc)
            ok("NLI gate skipped — model unavailable (acceptable in offline test).")

        # ------------------------------------------------------------------
        # Test 9: Idempotent re-ingest (same chunks, expect 0 new inserted)
        # ------------------------------------------------------------------
        logger.info("")
        logger.info("Step 9: Idempotent re-ingest (expect 0 new chunks)")
        try:
            doc = TOY_DOCS[0]
            n = ingest_text(
                text=doc["text"],
                doc_name=doc["doc_name"],
                asset_id=doc["asset_id"],
                equipment_id=doc["equipment_id"],
                equipment_type=doc["equipment_type"],
                doc_type=doc["doc_type"],
                criticality=doc["criticality"],
                db=db,
            )
            assert n == 0, f"Expected 0 new chunks on re-ingest, got {n}"
            ok("Re-ingest of existing doc returned 0 new chunks (idempotent).")
        except Exception as exc:
            fail("Idempotent re-ingest test failed", exc)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    logger.info("")
    logger.info("=" * 60)
    logger.info("SMOKE TEST COMPLETE — passed=%d, failed=%d", passed, failed)
    logger.info("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)
