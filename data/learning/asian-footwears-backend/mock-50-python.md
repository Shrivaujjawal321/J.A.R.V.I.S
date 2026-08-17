# Python Mock Interview — 50 Questions
**For:** Ujjawal Shrivastav · **Role:** Python Backend Developer (ASIAN Footwears) · **Prepared:** 2026-07-02
**Use:** Jarvis ek-ek karke poochega (mock mode), end mein scorecard. Baseline mock: 6.2/10 → target 8+.

> Mix: basics (warm-up) → data structures → functions → OOP → errors/files → advanced (aaj ke P1–P10 included) → APIs/backend → code-reading (predict/spot-bug).

---

## A. Warm-up Basics (1–8)
1. Python interpreted language hai ya compiled? Iska matlab kya hai?
2. Mutable aur immutable types mein farak — 2-2 example do.
3. `==` aur `is` mein kya farak hai?
4. `None` kya hai? Function `return` na kare toh kya milta hai?
5. Indentation Python mein itni important kyun hai?
6. f-string kya hai? Ek example bolo.
7. Ternary operator kya hota hai? Ek line mein likha if-else kaise padhte ho?
8. `break`, `continue`, `pass` — teeno ka farak.

## B. Data Structures (9–18)
9. List aur tuple — production code mein kaunsa kab choose karoge?
10. Duplicates hatane ke liye kaunsa data structure? Kyun?
11. 10 lakh products mein SKU dhoondhna ho — list ya dictionary? Kyun?
12. Dictionary mein `[]` access aur `.get()` mein farak? `.get()` ka doosra argument kya karta hai?
13. `append()` vs `extend()` — farak batao.
14. List slicing: `nums[1:4]` kya deta hai? End index include hota hai?
15. String reverse kaise karoge? `[::-1]` aur `[-1]` mein farak?
16. Set ordered hota hai? Duplicate kyun nahi rakhta?
17. Shallow copy vs deep copy — nested dict waali list mein shallow copy se kya problem?
18. `zip()` aur `enumerate()` kab use karte ho?

## C. Functions (19–26)
19. `print()` aur `return` mein farak?
20. Default argument mein list dena (`def f(x=[])`) galat kyun maana jaata hai?
21. `*args` aur `**kwargs` kya hain? Kaise batwara hota hai?
22. Lambda function kya hai? Normal function se kab better?
23. `map()` aur `filter()` ka farak ek example se.
24. Variable scope — global variable ko function ke andar modify kaise karte ho?
25. `sorted()` aur `.sort()` mein farak? `.sort()` kya return karta hai?
26. List comprehension mein `if` filter kahan lagta hai — pehle filter ya pehle transform?

## D. OOP (27–33)
27. Class aur object ka farak — footwear example se samjhao.
28. `__init__` aur `self` kya karte hain?
29. Inheritance ka faayda ek real example se — `Product` → `Shoe`.
30. Instance method vs `@staticmethod` vs `@classmethod` — kaise decide karte ho?
31. `__str__` aur `__repr__` mein farak? Sirf `__repr__` ho toh `print()` kya karega?
32. `isinstance()` aur `type()` mein farak — inheritance mein kaunsa sahi?
33. `super()` kya karta hai?

## E. Errors & Files (34–38)
34. try/except ka structure — `except:` aur `except Exception as e:` mein production mein kaunsa sahi? Kyun?
35. Ek bade try block mein sab kuch daalna galat kyun?
36. `finally` block kab chalta hai?
37. `with open()` ka faayda kya hai plain `open()` se?
38. File modes — `w`, `r`, `a` mein farak?

## F. Advanced (39–44)
39. Generator kya hai? 1 crore records process karne mein list se better kyun?
40. Iterator aur iterable mein farak? `for` loop andar se kya karta hai?
41. Decorator kya hai? `@app.route` jaisa syntax kya kar raha hota hai?
42. GIL kya hai? "Python multithreading mein slow" kyun kehte hain?
43. I/O-bound vs CPU-bound kaam — threading/multiprocessing/asyncio kab kaunsa?
44. `async`/`await` kya hai? `asyncio.gather` kya karta hai?

## G. APIs & Backend (45–47)
45. GET aur POST mein farak? LLM ko prompt bhejne ke liye kaunsa?
46. Status codes: 200, 201, 400, 401, 404, 500 — kiski galti kaunse mein (client/server)?
47. `response.json()` kya deta hai? Uske baad data kaise access karte ho?

## H. Code Reading — Predict/Spot-bug (48–50)
48. [Predict] `nums = [1,2,3]; b = nums; b.append(4); print(nums)` → kya print hoga?
49. [Spot-bug] `def f(): return x; print("done")` — `print` kab chalega?
50. [Predict] `d = {"a": 1}; print(d.get("b", 0))` → kya print hoga?

---

## Mock log
- ✅ Mock #2 — 2026-07-03, all 50 questions. **Overall: 6.4/10** (baseline 6.2 → +0.2).
  - Section scores: A Warm-up 7.0 · B Data Structures 7.9 · C Functions 5.6 · D OOP 5.8 · E Errors/Files 7.0 · F Advanced 5.5 · G APIs 6.5 · H Code Reading 5.0
  - **Improved:** status codes (7.5, pehle sabse weak), try/except reasoning, data structures strong.
  - **Weak (revision list):**
    1. **Aliasing/mutability** — Q48 miss kiya (b=nums → same list). Q2/Q13/Q17/Q20/Q48 sab isi concept ke roop. #1 priority.
    2. **append vs extend** — ulta bataya (append=nested, extend=flatten).
    3. **pass vs return** — pass="function end" bola (galat; pass=no-op placeholder).
    4. **None-return pattern** — print-only function → None (Q19), .sort() → None (Q25).
    5. **map()** — aata hi nahi tha (map=transform all, filter=select some).
    6. **GIL full form** — "Global Interpreter Lock" (galat yaad tha); I/O-bound mein threading TRUE, CPU-bound mein FALSE.
    7. **async/await** — await = doosron ko time dena, not "wait karna padega"; gather = concurrent (not parallel).
    8. **__init__/self** — Q28 answer hi nahi diya; constructor + "khud wala object" pakka karo.
    9. **Nested JSON access** — data["products"][0]["price"] — list index bhool gaye.
    10. **d.get() print** — sirf value print hoti hai, poori dict nahi (Q50).
    11. **Thin answers** — Q18/Q26/Q33 mein 1-line jawab; har answer mein example + "kyun" bolna hai.
- Mock #3 (next): revision list ke 11 topics pehle drill karo, fir naya mock. Target: 7.5+.
- Drill session 2026-07-03: Topics 1-4 ✅ CLEAR (aliasing, append/extend, pass/return/break/continue, None-return). Topic 5 (map/filter) par pause — Boss ne AI/ML pivot kiya. Resume point: Topic 5 check question (4 products, map-ya-filter + count). Baaki pending: 5 map/filter · 6 GIL · 7 async/await · 8 __init__/self · 9 nested JSON · 10 d.get print · 11 thin answers.
