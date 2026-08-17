# ASIAN Footwears — Backend Developer Interview Question Bank
**Role:** Backend Developer (India) · **Tech Stack:** Python + SQL
**Total:** 60 questions (20 Beginner · 20 Intermediate · 20 Advanced)
**Prepared:** 2026-06-26 · For: Ujjawal Shrivastav

> Use: pehle khud answer socho, phir Jarvis se mock karwao ya answer-key maango.

---

## 🟢 BEGINNER (20) — basics pakke hone chahiye

### Python (1–12)
1. Python ek interpreted language hai ya compiled? Iska matlab kya hai?
2. `list`, `tuple`, aur `set` mein kya farak hai? Ek-ek example do.
3. `==` aur `=` mein kya farak hai?
4. Mutable aur immutable data types kya hote hain? Do-do example.
5. Ye code kya print karega: `x = [1,2,3]; print(x[-1])` — aur `-1` ka matlab kya hai?
6. `for` loop aur `while` loop mein kab kaun sa use karte ho?
7. `if / elif / else` ka kaam kya hai? Ek chhota example likho.
8. Function kya hota hai? `def` keyword ka use kya hai?
9. `def greet(name="Guest")` — yahan `name="Guest"` kya hai (default argument)?
10. String ko upper-case karne ka method kya hai? (`"asian".upper()` kya dega?)
11. `len()`, `type()`, `range()` — teeno kya karte hain?
12. Dictionary se value kaise nikaalte ho? `d = {"size": 9}` — size kaise access karein?

### SQL (13–20)
13. SQL ka full form kya hai aur ye kis kaam aati hai?
14. `SELECT * FROM products;` ka matlab kya hai? `*` kya karta hai?
15. `WHERE` clause ka kaam kya hai? Ek example do.
16. Primary key kya hoti hai? Ek footwear `products` table mein kya ho sakti hai?
17. `INSERT`, `UPDATE`, `DELETE` — teeno kya karte hain?
18. `ORDER BY price DESC` ka matlab kya hai?
19. `COUNT(*)` kya batata hai? Ek example.
20. Database ek table aur ek spreadsheet (Excel) mein kya similarity hai — rows aur columns kya hote hain?

---

## 🟡 INTERMEDIATE (20) — yahan se interview serious hota hai

### Python (1–10)
1. `*args` aur `**kwargs` ka kya use hai? Kab lagते hain?
2. List comprehension kya hai? `[x*2 for x in range(5)]` ka output kya hoga?
3. `try / except / finally` — teeno block kab chalte hain?
4. Class aur object mein farak? `__init__` method kya karta hai?
5. Inheritance kya hai? Ek footwear example do (jaise `Product` → `Shoe`).
6. `is` aur `==` mein kya farak hai?
7. Shallow copy aur deep copy mein kya antar hai?
8. Python mein module aur package mein kya farak hai? `import` kaise kaam karta hai?
9. Virtual environment (`venv`) kya hota hai aur kyun use karte hain?
10. JSON ko Python dictionary mein kaise badlte ho aur ulta? (`json.loads` / `json.dumps`)

### SQL (11–20)
11. `JOIN` kya hota hai? `INNER JOIN` aur `LEFT JOIN` mein farak?
12. `GROUP BY` ka use kya hai? Ek example: har category mein kitne products?
13. `HAVING` aur `WHERE` mein kya farak hai?
14. Foreign key kya hoti hai? `orders` aur `customers` table ko kaise jodegi?
15. Index kya hota hai aur query fast kaise karta hai?
16. `DISTINCT` keyword kya karta hai?
17. Aggregate functions kya hote hain? (`SUM`, `AVG`, `MIN`, `MAX`) — ek example.
18. `NULL` value kya hoti hai? `WHERE price = NULL` kyun kaam nahi karta?
19. Subquery kya hoti hai? Ek example (sabse mehngi shoe dhoondho).
20. Ek query likho: `orders` table se woh customers dikhao jinhone 5 se zyada orders kiye hain.

---

## 🔴 ADVANCED (20) — senior backend thinking

### Python (1–10)
1. Decorator kya hota hai? Ek example jahan tum function ka time measure karo.
2. Generator kya hai? `yield` aur `return` mein farak? Memory ke liye kaise behtar hai?
3. Python ka GIL (Global Interpreter Lock) kya hai? Multithreading pe iska kya asar?
4. `multiprocessing` vs `threading` vs `asyncio` — backend mein kab kaun sa?
5. Context manager kya hai? `with open(...)` andar se kaise kaam karta hai?
6. `@staticmethod`, `@classmethod`, instance method — teeno mein farak?
7. Python mein memory management kaise hota hai? Garbage collection kya hai?
8. REST API mein idempotency kya hoti hai? Kaun se HTTP methods idempotent hote hain?
9. Ek API ko fast banane ke liye caching kaise use karoge? (Redis ka role)
10. Database password jaise secrets ko code mein kaise handle karoge production mein? (env vars, secret manager)

### SQL (11–20)
11. Database normalization kya hai? 1NF, 2NF, 3NF ka chhota matlab.
12. Transaction kya hota hai? ACID properties kya hain?
13. `INNER JOIN` waali ek slow query ko fast kaise banaoge? (EXPLAIN, indexes)
14. Deadlock kya hota hai database mein? Kaise avoid karte hain?
15. Index ke fayde aur nuksaan — index har column pe kyun nahi lagate?
16. Window functions kya hain? `ROW_NUMBER()` ya `RANK()` ka ek use case.
17. SQL Injection kya hota hai aur Python (parameterized queries) se kaise rokte ho?
18. Connection pooling kya hai aur backend mein kyun zaroori hai?
19. `DELETE`, `TRUNCATE`, `DROP` — teeno mein kya farak? Kab kya use karein?
20. Ek footwear company ke liye scenario: roz lakhon orders aa rahe hain, reporting query slow ho gayi — aap kya-kya optimize karoge? (indexing, partitioning, read-replica, denormalization)

---

## 🎯 Interview Tips (ASIAN Footwears specific)
- Tech stack Python + SQL hai — to **inventory, orders, products, customers** waale examples sochke rakho. Footwear domain mein answer doge to interviewer ko lagega tum role samajhte ho.
- Har answer mein **"kyun"** add karo, sirf "kya" nahi.
- Code/query likhne ko bole to **bolke + likhke** dono karo (sochne ka process dikhao).
- Na aaye to imaandari se bolo "ye main confident nahi hoon, par main aise approach karta" — bluff se accha hai.
