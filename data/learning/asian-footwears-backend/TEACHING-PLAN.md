# Python + SQL Teaching Plan — ASIAN Footwears Backend Prep
**For:** Ujjawal · **Started:** 2026-06-26 · **Mode:** comprehension (read+understand, predict-output checks, Hinglish, one step at a time)
**Source:** python-100-questions.md + question-bank.md (SQL)

> Rule: PEHLE padhao, FIR test. Koi topic miss na ho. Known topics = fast recap; gaps = proper teach.

---

## 🐍 PYTHON TRACK (mostly known — gaps fill karne hain)

**Already strong (roadmap complete):** functions, data structures, comprehensions, f-strings, try/except, file handling, modules/pip, OOP basics, lambda/map/filter, generators/decorators, venv, numpy/pandas, APIs/JSON, async.

**Gap topics to TEACH (ye nahi padhe the):**
- [x] P1. Ternary operator (one-line if-else) ✅ (2026-07-02) — formula "haan-wala if shart else na-wala" + both predict-checks correct (Premium, Out of stock)
- [x] P2. `zip()` + `enumerate()` ✅ (2026-07-02) — zip=jacket-zipper jodi analogy, enumerate=item+number (start=1); checks correct (one zip pairing slip 9-5, self-evident typo)
- [x] P3. Shallow copy vs deep copy ✅ (2026-07-02) — first check missed (said deep affects original — inverted), re-taught "shallow=juda→change failta, deep=alag→change rukta"; then BOTH follow-up checks correct (deep→1, shallow→shipped). Locked both directions.
- [x] P4. `global` keyword + variable scope ✅ (2026-07-02) — common-fridge/kamre-ki-almari analogy; read-global-free vs modify-needs-global trap; all 3 checks correct (Hello ASIAN, error-predict, global-keyword fix). Interview one-liner given ("global avoid karo, pass+return better").
- [x] P5. `@staticmethod` vs `@classmethod` vs instance method ✅ (2026-07-02) — dukaan analogy (customer-bill/calculator/register) + pehchan shortcut (self/decorator/cls); all checks correct incl. spotting decorator as clue. Interview one-liner given.
- [x] P6. `__str__` vs `__repr__` ✅ (2026-07-02) — dibba-label vs warehouse-barcode analogy + chai→coffee→paani fallback chain. Missed fallback check first (said ugly), re-taught priority chain; also clarified repr="representation" not return-related (Boss asked). Final check correct (no-methods→ugly).
- [x] P7. `isinstance()` vs `type()` ✅ (2026-07-02) — "exact naam vs family se ho?" analogy; inheritance farak + tuple multi-check; both predict-checks correct first try (True/False on Dog/Animal).
- [x] P8. Iterator vs Iterable ✅ (2026-07-02) — playlist/play-head analogy + "for loop = iter()+next() internally" + generators=readymade iterators. First check order slip (said Puma,Nike,Bata — corrected: list order from first), StopIteration check correct.
- [x] P9. GIL + multiprocessing vs threading vs asyncio ✅ (2026-07-02) — "ek mic" analogy for GIL + I/O-vs-CPU decision table; scenario check correct (resize→multiprocessing, price-fetch→asyncio). Interview one-liner given.
- [x] P10. Polish: status codes + `*args`/`**kwargs` + sort vs sorted + slicing ✅ (2026-07-02) — (a) status codes: 2xx/4xx/5xx family rule, 404-vs-500 check correct (mock-miss fixed!); (b) args/kwargs: 2 misses first (counted total, then inverted) → "= dikha toh kwargs" rule → locked 3rd check; (c) sort/sorted: asked full re-explain → almari analogy → checks correct incl. None-return; (d) slicing: [2:6]→OTWE correct, [::-1] first miss (said R) → reverse-vs-[-1] farak taught → lock-check both correct (NAISA, N).

---

## 🗄️ SQL TRACK (mostly NEW — full teach from scratch)

- [ ] S1. SQL kya hai + database/table/row/column intuition
- [ ] S2. SELECT + WHERE (data padhna)
- [ ] S3. ORDER BY + LIMIT + DISTINCT
- [ ] S4. INSERT / UPDATE / DELETE (CRUD)
- [ ] S5. Aggregate functions (COUNT/SUM/AVG/MIN/MAX)
- [ ] S6. GROUP BY + HAVING
- [ ] S7. Primary key + Foreign key
- [ ] S8. JOINs (INNER / LEFT) — the big one
- [ ] S9. Subqueries
- [ ] S10. Indexes (query fast kaise)
- [ ] S11. Transactions + ACID
- [ ] S12. NULL handling + SQL injection (parameterized queries)

---

## Progress log
- 2026-07-02: **MEGA SESSION — ENTIRE PYTHON GAP TRACK (P1–P10) COMPLETE in one sitting.** Interview urgency mode (date near). Pattern held: logic mostly right, slips on detail (shallow-copy direction, repr-fallback, args/kwargs split, [::-1] vs [-1], iterator order) — each re-taught with analogy + lock-check until correct. Boss asked one full re-explain (sort) — given from scratch, then clean. Strongest first-try topics: ternary, scope/global, isinstance-vs-type, GIL scenario, 404-vs-500 (mock-miss now FIXED). NEXT SESSION: SQL track S1 se shuru (bilkul naya, role ka aadha weight) + quick re-drill of today's slip points (shallow/deep direction, kwargs `=` rule, [::-1]). Then interview-style mock #2 (target 8+, baseline 6.2).
- 2026-06-26: Plan created. Starting Python gaps first (quick wins on strong base), then full SQL.
