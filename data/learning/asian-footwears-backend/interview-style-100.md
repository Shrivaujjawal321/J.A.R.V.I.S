# ASIAN Footwears — 100 Questions, *Interview ki Tarah*
**Role:** Python + SQL Backend Developer (fresher) · **For:** Ujjawal Shrivastav · **Prepared:** 2026-06-27

> Ye list kal wali (`python-100-questions.md`) se alag hai. Wo **syllabus/revision** style thi — topic-by-topic, flat facts.
> Ye list **interview ki tarah** likhi hai — jaise interviewer saamne baith ke poochta hai: conversational phrasing, "kyun" + follow-ups, code dikha ke "ye kya print karega", "is code mein bug dhoondho", footwear-company scenarios, aur asli round-flow (intro → tech → scenario → HR).
>
> **Kaise use karein:** Jarvis se bolo *"interview-style mock le lo"* — main ek-ek karke poochunga, tumhara jawab sunke follow-up dunga, aur end mein scorecard. Ya khud padho, har question pe bolke jawab dene ki practice karo (likhke nahi — interview mein bolna padta hai).

---

## 🤝 ROUND 1 — Warm-up & Apne Baare Mein (1–10)
*(Yahin interviewer pehla impression banata hai. Confident, short, role-relevant raho.)*

1. "Apne baare mein thoda batao — background, aur Python/backend mein kaise aaye?"
2. "Aapne resume mein Python likha hai — koi ek project batao jisme aapne Python use kiya, aur usme aapka exact role kya tha?"
3. "Aapko backend development hi kyun pasand hai, frontend ya kuch aur kyun nahi?"
4. "ASIAN Footwears ke baare mein aapne kya socha — humein ek backend developer ki zaroorat kyun ho sakti hai?"
5. "Aapne ab tak ka sabse tough coding problem kaun sa solve kiya? Kaise approach kiya?"
6. "Agar kisi cheez ka jawab aapko nahi aata, to aap kaise seekhte ho? Koi recent example?"
7. "Python aapne self-learn kiya ya course se? Roz kitna practice karte ho?"
8. "Aapko comfortable kaunse area mein lagta hai — Python, SQL, ya APIs? Aur kahan improve karna hai?"
9. "Team mein kaam karna pasand hai ya akele? Kyun?"
10. "Is role se 6 mahine baad aap khud ko kahan dekhte ho?"

---

## 🐍 ROUND 2 — Python, Jaise Interviewer Kuredta Hai (11–35)
*(Sirf "kya hai" nahi — "kyun", "kab use karoge", "tradeoff kya hai". Har answer ke baad follow-up aata hai.)*

11. "List aur tuple dono cheezein store karte hain — to aap production code mein kaunsa kab choose karoge, aur kyun?"
12. "Maan lo ek `products` list hai shoes ki. Aapko duplicates hatane hain — kaunsa data structure use karoge aur kyun?"
13. "Dictionary aur list mein, lookup speed ka kya farak hai? Agar 10 lakh products mein se ek SKU dhoondhna ho to kaunsa fast?"
14. "`is` aur `==` — dono `True` de sakte hain, par ek case batao jahan `==` `True` de aur `is` `False`."
15. "Mutable aur immutable — chalo ek follow-up: ek function ko list paas ki aur usne usme change kar diya. Bahar wali list change hui ya nahi? Kyun?"
16. "Default argument mein list dena (`def f(x=[])`) — ye galat kyun maana jaata hai? Kya hota hai?"  *(classic trap)*
17. "`*args` aur `**kwargs` — aapne kabhi use kiya? Ek real situation batao jahan ye zaroori the."
18. "List comprehension achhi hai, par kab aapko normal `for` loop use karna chahiye, comprehension nahi?"
19. "Shallow copy aur deep copy — agar `orders` list ke andar dictionaries hain, to shallow copy se kya problem aa sakti hai?"
20. "`try/except` — aap har cheez ko ek bade `try` mein daal dete ho. Iska nuksaan kya hai?"
21. "Aap `except:` likhte ho ya `except Exception as e:` — farak kya hai, aur production mein kaunsa sahi?"
22. "Function ko `return` nahi diya to kya return hota hai? Aapne dekha hai aisa kabhi?"
23. "Class aur object ka farak ek footwear example se samjhao — `Shoe` class kaisi dikhegi?"
24. "Inheritance ka ek real use batao — `Product` se `Shoe` aur `Sandal` banane mein kya faayda?"
25. "`__init__` ke alawa koi dunder method use kiya hai? `__str__` kab kaam aata hai?"
26. "`@staticmethod` aur `@classmethod` — inme se ek choose karne ki situation batao."
27. "Generator kya hai — aur agar 1 crore orders process karne hain to list ki jagah generator kyun behtar?"
28. "Decorator — aapne kabhi banaya? Ek API endpoint ka response-time measure karna ho to decorator se kaise karoge?"
29. "GIL ke baare mein suna hai? Iska matlab kya hai ki Python 'multithreading mein slow' hota hai?"
30. "Ek kaam I/O-heavy hai (1000 API calls), doosra CPU-heavy hai (image resize). Dono ke liye aap threading, multiprocessing, ya asyncio — kya choose karoge?"
31. "`with open(...) as f:` — `with` ka faayda kya hai? File close khud kaise ho jaati hai?"
32. "Aap ek dictionary se key access kar rahe ho jo exist nahi karti — kya hota hai? Isse safely kaise handle karoge? (`.get()` vs `[]`)"
33. "`sort()` aur `sorted()` mein farak? Ek list of shoe-dicts ko price ke hisaab se sort karna ho to?"
34. "Python mein ek number ko string banaya, fir wapas number — `int("5")` theek hai, par `int("5.5")` kya karega?"
35. "Aapke code mein performance issue hai — aap kaise pata lagaoge ki kaunsa hissa slow hai? (profiling soch)"

---

## 💻 ROUND 3 — "Ye Code Kya Print Karega / Bug Dhoondho" (36–52)
*(Interview ka sabse common round. Bolo: pehle dimaag mein run karo, fir output bolo. Galti ho to wapas dekh ke khud pakdo.)*

36. "Ye kya print karega?  `x = [1, 2, 3]; print(x[-1])`"
37. "Ye?  `print('asian'[1:4])`"
38. "Ye?  `print(2 ** 3 ** 2)`  — order ka dhyaan rakhna."
39. "Ye?  `a = '5'; b = 5; print(a + str(b))`  — aur agar `str` hata dein to?"
40. "Ye?  `print(bool(0), bool(''), bool([]), bool('0'))`"
41. "Ye?  `print(10 / 3, 10 // 3, 10 % 3)`"
42. "Ye loop kya print karega?  `for i in range(1, 6, 2): print(i)`"
43. "Ye?  `d = {'a': 1}; print(d.get('b', 'N/A'))`"
44. "Ye list comprehension kya banayegi?  `[x*2 for x in range(5) if x % 2 == 0]`"
45. "Ye kya print karega?  `s = 'asian'; print(s[::-1])`"
46. "Is code mein bug kya hai?  `def total(items): for i in items: sum += i; return sum`"
47. "Ye chalega?  `nums = (1, 2, 3); nums[0] = 99` — nahi to error kaunsa aayega?"
48. "Bug batao:  `if x = 5:` — ye kya galat hai?"
49. "Ye kya return karega?  `print(len('asian') == 5 and 'yes' or 'no')`"
50. "Ye output?  `lst = [1, 2, 3]; lst2 = lst; lst2.append(4); print(lst)` — `lst` mein 4 aaya ya nahi? Kyun?"
51. "Is function mein silent bug hai — pakdo:  `def discount(price, pct=10): return price - price * pct`  (hint: percentage)"
52. "Ye kya print karega aur kyun?  `print(0.1 + 0.2 == 0.3)`"  *(float precision trap)*

---

## 🗄️ ROUND 4 — SQL, Footwear Data Ke Saath (53–74)
*(Interviewer aksar ek table dikha ke 'iske liye query likho' bolta hai. Tables maan lo: `products(id, name, category, price, stock)`, `orders(id, customer_id, product_id, qty, order_date)`, `customers(id, name, city)`.)*

53. "SQL kya hai, aur ek backend developer ko iski zaroorat roz kis cheez ke liye padti hai?"
54. "`products` table se sirf woh shoes dikhao jinka price 2000 se zyada hai — query bolo."
55. "Sabse mehngi 5 shoes nikalo — query?  (ORDER BY + LIMIT)"
56. "Har category mein kitne products hain — ye kaise nikaloge? (GROUP BY)"
57. "`WHERE` aur `HAVING` — dono filter karte hain, to farak kya hai? Ek example jahan dono ek hi query mein lagein."
58. "INNER JOIN aur LEFT JOIN ka farak ek scenario se samjhao — agar mujhe woh customers bhi chahiye jinhone abhi tak koi order nahi kiya, to kaunsa JOIN?"
59. "`orders` aur `customers` ko jod ke har order ke saath customer ka naam dikhao — query."
60. "Primary key aur foreign key — `orders` table mein dono kaunse columns honge?"
61. "Total revenue nikalo (qty × price ka sum) — kaunse functions/joins lagenge?"
62. "Woh customers dikhao jinhone 5 se zyada orders kiye hain — query? (GROUP BY + HAVING)"
63. "`COUNT(*)` aur `COUNT(column)` mein farak hai kya? NULL ke saath kya hota hai?"
64. "`DISTINCT` kab zaroori hota hai? Ek JOIN ke baad duplicate rows aa gayin — kaise hatoge?"
65. "`price = NULL` likhne se rows kyun nahi aatin? Sahi tarika kya hai?"
66. "Subquery: woh shoes dikhao jinka price average price se zyada hai — kaise likhoge?"
67. "Index kya hai — aur agar `WHERE name = 'Nike Air'` har baar slow hai, to aap kya karoge?"
68. "Index har column pe kyun nahi laga dete? Nuksaan kya hai?"
69. "`DELETE`, `TRUNCATE`, `DROP` — galti se kaunsa chala dein to sabse zyada nuksaan, aur kyun?"
70. "Transaction kya hai? Ek order place hone mein stock ghatana + order insert karna — dono saath kyun hone chahiye? (ACID soch)"
71. "Window function: har category mein top-selling shoe nikalni ho to `ROW_NUMBER()`/`RANK()` kaise help karega?"
72. "SQL Injection — `\"SELECT * FROM users WHERE name = '\" + input + \"'\"` — isme kya galat hai, aur Python se kaise rokoge?"
73. "Roz lakhon orders aa rahe hain, ek reporting query ab 40 second leti hai — aap kya-kya try karoge? (indexing, query rewrite, partitioning, read-replica)"
74. "Aapko ek slow query di gayi hai — debug kaise karoge? `EXPLAIN` ka kya role hai?"

---

## 🧩 ROUND 5 — Scenario & "Aap Kya Karoge" (75–87)
*(Real backend sochne ka test. Koi single answer nahi — approach aur tradeoffs maango, sochke bolo.)*

75. "Ek customer order place karta hai par stock sirf 1 bacha hai aur do log ek saath order kar dein — aap double-booking kaise rokoge?"
76. "Ek REST API banao soch ke: 'get all shoes of a category'. Endpoint kaisa hoga, response mein kya bhejoge, error kaise handle karoge?"
77. "Aapki API achanak slow ho gayi production mein — pehle 5 minute mein aap kya-kya check karoge?"
78. "Caching kaha use karoge is footwear site pe — kaunsa data cache karna safe hai, kaunsa nahi?"
79. "Ek file mein 10 lakh product rows hain, sabko database mein daalna hai — aap memory kaise bachayenge?"
80. "Database password aur API keys — aap inhe code mein kaise rakhte ho? GitHub pe galti se push ho jaye to?"
81. "Ek API har request pe poora product table laata hai aur slow hai — aap kya badloge? (pagination)"
82. "Order place hote waqt payment ho gaya par order insert fail ho gaya — ye situation kaise handle karoge?"
83. "Logs mein ek error baar-baar aa raha hai par app crash nahi ho rahi — aap isse kaise investigate karoge?"
84. "Ek naye intern ne `DELETE FROM orders` bina `WHERE` chala diya — abhi kya karoge, aur aage kaise rokoge?"
85. "Aapko ek bug report mila: 'discount galat lag raha hai'. Aap step-by-step kaise root cause dhoondhoge?"
86. "Inventory aur orders dono ko ek hi time pe update karna hai — agar beech mein server crash ho jaye to data kaise consistent rakhoge?"
87. "Ek API endpoint public hai aur log usse spam kar rahe hain — aap kaise protect karoge? (rate limiting soch)"

---

## 🐞 ROUND 6 — Debugging & Error Handling (88–93)
*(Interviewer error message dikha ke poochta hai 'iska matlab kya, ab kya karoge'.)*

88. "Code chalaya aur aaya `IndexError: list index out of range` — iska seedha matlab kya hai? Pehle kya check karoge?"
89. "`KeyError: 'size'` — ye kab aata hai? Isse safely kaise bachoge?"
90. "`TypeError: can only concatenate str (not \"int\") to str` — code mein kya galti hui hogi?"
91. "API call pe `500 Internal Server Error` aur `404 Not Found` — dono mein kya farak hai? Kiski galti kiski taraf?"
92. "Code local pe chal raha hai par server pe nahi — aap kaunse 3 cheezein sabse pehle check karoge?"
93. "Ek error 'kabhi-kabhi' aata hai, har baar nahi — aisa intermittent bug kaise pakadte ho?"

---

## 🎯 ROUND 7 — Role-fit, Judgement & HR Close (94–100)
*(Interview ke aakhir mein. Honest, mature, aur thoda role ke liye bhookha dikho.)*

94. "Aapko ek feature 2 din mein chahiye par aap jaante ho usme 4 din lagenge — interviewer/manager ko kya bologe?"
95. "Code review mein senior ne aapka kaam reject kar diya — aap kaise react karoge?"
96. "Aapko ek aisi technology pe kaam karna pade jo aapne kabhi nahi dekhi — pehla hafta kaise plan karoge?"
97. "Production mein aapki galti se bug gaya aur orders ruk gaye — aap kya karoge, aur team ko kaise batayenge?"
98. "Aapko hamare paas kyun rakhein, jab itne aur candidates hain — ek line mein?"
99. "Salary expectation kya hai? (range soch ke rakho, justify kar sako)"
100. "Aapke paas hamare liye koi sawaal hai?"  *(YES bolna — ye filter question hai. 2 acche sawaal taiyaar rakho.)*

---

## 📌 Yaad Rakhne Layak (interview ke din)
- **Bolke socho.** Chup ho ke sochne se accha hai "main aise soch raha hoon..." — interviewer ko approach dikhe.
- **Footwear domain ghuso.** `products / orders / customers / stock / SKU / size` — examples isi se do, lagega role samajhte ho.
- **"Kyun" hamesha add karo.** Sirf "list use karunga" nahi — "list use karunga *kyunki* order matter karta hai".
- **Na aaye to imaandari.** "Ye main confident nahi hoon, par main aise approach karta..." — bluff se 10x behtar.
- **Round 3 (code output) sabse zyada poocha jaata hai** — wahan galti mat karna, dimaag mein dheere run karo.
- **Q100 ka jawab hamesha 'haan'** — 2 thoughtful sawaal pehle se taiyaar (team kaisa kaam karti hai / pehle 3 mahine kya expect karein).

---

*Mock karwana ho to bolo: "Jarvis, interview-style mock le lo" — main Round 1 se shuru karunga, ek question, tumhara jawab, fir follow-up + feedback.*
