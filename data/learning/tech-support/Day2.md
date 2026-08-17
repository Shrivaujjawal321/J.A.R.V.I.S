# Day 2 — Software Troubleshooting (Framework + Errors/Logs/HTTP + Networking + Tools)

## Day 2.1 — Troubleshooting Framework & Worked Scenarios

Boss, ye module aapko interview ke liye sabse zyada marks dilane wala hai. Software support role mein interviewer 80% questions isi skill par poochta hai — "ek user aaya, problem ye hai, aap kya karenge?" Yaad rakhiye: woh aapse answer nahi, **soch ka tarika (thought process)** sun-na chahta hai. Isiliye is module ko maine seekhne + bol kar dohraane dono ke liye banaya hai.

---

### 1. The Troubleshooting Framework — "IRIFVD"

**Kya hai (simple):**
Troubleshooting ka matlab hai — kisi problem ko randomly try-try karke nahi, balki ek **fixed structured method** se solve karna. Maine aapke liye ek easy naam diya hai jise interview mein bol sakte hain: **IRIFVD** —

| Step | English | Hinglish meaning |
|------|---------|------------------|
| **I** | Identify | Problem exactly kya hai, samajhna |
| **R** | Reproduce | Khud apne saamne wahi problem dobara laana |
| **I** | Isolate | Cause dhoondhna — ek baar mein ek cheez badal kar |
| **F** | Fix | Actual solution apply karna |
| **V** | Verify | Confirm karna ki problem sach mein gayi |
| **D** | Document | Likh dena — kya hua, kaise theek hua |

**Support role mein kyun important:**
Interviewer dekhna chahta hai ki aap **panic nahi karte, system follow karte ho**. Jo banda kehta hai "main pehle reproduce karunga, fir ek-ek cheez isolate karunga" — woh instantly senior lagta hai. Jo banda kehta hai "main restart maar dunga" — woh junior lagta hai.

**Kaise (mechanism):**
Ye 6 steps hamesha isi order mein chalte hain. Sabse important hidden rule: **"Change one thing at a time"** — Isolate step mein agar aap ek saath 3 cheezein badal denge, toh pata hi nahi chalega kis cheez ne fix kiya. Ye line interview mein zaroor bolni hai.

**Real example:**
User: "Mera report download nahi ho raha."
- **Identify:** Konsa report? Konsa button? Error aata hai ya kuch nahi hota?
- **Reproduce:** Aap apne system par wahi report download karke dekhte ho.
- **Isolate:** User ke browser mein? Sirf is user ke account mein? Sirf bade reports mein?
- **Fix:** Pata chala browser cache corrupt tha — cache clear.
- **Verify:** User se bolwaake confirm karaya download ab chal raha.
- **Document:** Ticket mein note — "Cache issue, cleared, resolved."

**Interview Q&A:**

> **Q: "Walk me through your troubleshooting process."**
> **A:** "Sir, main ek structured approach follow karta hoon. Pehle main problem ko **identify** karta hoon — exactly kya ho raha hai aur error message kya hai. Fir use **reproduce** karta hoon taaki main khud dekh sakoon. Fir **isolate** karta hoon — ek baar mein ek hi variable badalta hoon, taaki pata chale root cause kahaan hai. Fir **fix** apply karta hoon, **verify** karta hoon ki sach mein resolve hua user ke end par, aur last mein **document** kar deta hoon future reference ke liye."

> **Q: "Why is 'change one thing at a time' important?"**
> **A:** "Kyunki agar main ek saath kai cheezein badal doon aur problem theek ho jaaye, toh mujhe kabhi nahi pata chalega ki actually kis cheez ne fix kiya. Isolation tabhi possible hai jab ek waqt par ek hi variable change ho."

---

### 2. First Questions to Ask the User (Information Gathering)

**Kya hai:**
Problem solve karne se pehle, sahi sawaal poochna. 50% problem toh sahi questions se hi solve ho jaati hai.

**Support role mein kyun important:**
Naye support engineers seedha solution dhoondhne lag jaate hain bina poori picture liye. Interviewer test karta hai ki aap **pehle samajhte ho, fir act karte ho**. Ye empathy + method dono dikhaata hai.

**Kaise — the golden questions:**

| Question | Kya pata chalta hai |
|----------|--------------------|
| **"Kya change hua / kab se shuru hua?"** | Recent update, password change, naya device |
| **"Sabke saath ho raha hai ya sirf aapke saath?"** | Global outage vs single-user issue |
| **"Exact error message kya aa raha hai?"** | Direct clue / Google-able |
| **"Steps batao — aap kya karte ho jab ye hota hai?"** | Reproduce karne ke liye |
| **"Pehli baar kab dekha?"** | Timeline → kis change se match karta hai |
| **"Kya aapne pehle kuch try kiya?"** | Repeat kaam se bachna |

Ek pro tip yaad rakhiye: **"What changed?"** sabse powerful sawaal hai. Kal tak chal raha tha, aaj nahi — toh beech mein kuch toh badla.

**Real example:**
User: "Email send nahi ho raha." Aap poochte ho "Kab se?" → "Subah se." → "Kuch change kiya?" → "Haan, naya password set kiya tha." → Turant clue: email app mein purana password saved hai. Bina diagnostics ke solve.

**Interview Q&A:**

> **Q: "A user says 'the app is not working.' What's the first thing you do?"**
> **A:** "Sir, 'not working' bahut vague hai, isliye main pehle clarify karunga. Main poochunga — exactly kya ho raha hai, koi error message aa raha hai kya, kab se shuru hua, aur kya recently kuch change hua. Main ye bhi confirm karunga ki ye sirf unke saath ho raha hai ya doosre users ko bhi. Tab tak main solution nahi sochunga jab tak problem clearly define na ho jaaye."

> **Q: "Which single question gives you the most information?"**
> **A:** "'Kya recently kuch change hua?' — kyunki agar kal tak sab theek tha aur aaj problem hai, toh kuch na kuch badla hai: koi update, password change, naya device, ya network change. Wahi usually root cause hota hai."

---

### 3. Isolation Thinking — "User, Device, Network, ya Software?"

**Kya hai:**
Problem 4 mein se kisi ek layer mein hoti hai. Aapko **divide and conquer** karke pata lagana hai konsi layer.

| Layer | Sawaal | Quick test |
|-------|--------|-----------|
| **User** | Sahi steps follow kar raha hai? Sahi credentials? | Aap khud unke account se try karo / screen share |
| **Device** | Unke laptop/phone ki problem? | Doosre device par try karwao |
| **Network** | Internet slow/down? | Doosri website chal rahi hai? Wifi vs mobile data |
| **Software** | App/server mein bug ya outage? | Doosre users ko bhi ho raha? Status page |

**Support role mein kyun important:**
Ye soch dikhaati hai ki aap **blindly software ko blame nahi karte**. Bahut saari "software problems" actually user-error ya network ki hoti hain. Interviewer ye maturity dekhna chahta hai.

**Kaise — the isolation logic:**
- Sirf **ek user** ko? → User ya uska device/network.
- **Sabko**? → Software/server side (outage).
- Ek user, **doosre device par bhi**? → User-account ya server.
- Ek user, **doosra device theek**? → Pehle device/browser ki problem.

**Real example:**
User: "Website nahi khul rahi." Aap soch te ho — doosre users ko khul rahi (Software ✅). User ka internet? Doosri site chal rahi (Network ✅). Doosre browser mein try → khul gayi. Matlab pehle browser ka cache/extension issue. **Isolated: Device/Browser layer.**

**Interview Q&A:**

> **Q: "How do you know if a problem is on the user's side or the system's side?"**
> **A:** "Main check karta hoon ki ye sirf ek user ko ho raha hai ya sabko. Agar sabko ho raha hai toh ye server ya software side ka issue hai — possibly outage. Agar sirf ek user ko ho raha hai, toh main uske device, browser, ya network ko isolate karta hoon — jaise doosre device ya browser par try karwa kar."

> **Q: "A user can't access the app but everyone else can. Where do you focus?"**
> **A:** "Jab sirf ek user affected hai toh problem unke side par hai — software global nahi tута. Main unka network check karunga (doosri site chal rahi?), browser/cache, aur unka account/permissions. Sabse pehle doosre device ya browser par try karwaunga taaki device-specific issue isolate ho."

---

### 4. Root Cause vs Symptom + 5 Whys

**Kya hai:**
- **Symptom** = jo dikh raha hai (spinner ghoom raha hai).
- **Root cause** = asli wajah (server ne API call timeout kar di).
Symptom theek karna temporary; root cause theek karna permanent.

**5 Whys** = baar-baar "kyun?" poochna jab tak asli wajah na mile (usually ~5 baar).

**Support role mein kyun important:**
Agar aap sirf symptom theek karenge (restart maar diya), problem dobara aayegi → repeat tickets → unhappy customer. Interviewer dekhna chahta hai aap **permanent fix** ki soch rakhte ho.

**Kaise — 5 Whys example:**
```
Problem: User report download nahi kar pa raha.
Why? → Download button click pe error aata hai.
Why? → Server 500 error de raha hai.
Why? → Report query timeout ho rahi hai.
Why? → Report bahut bada hai, 1 lakh rows.
Why? → Date-range filter default "All time" pe set hai.
ROOT CAUSE → Default filter galat. Fix: default ko "last 30 days" karo.
```
Symptom fix hota "button dobara click karo." Root cause fix permanent hai.

**Real example:**
User baar-baar "logged out ho jaata hoon." Symptom: dobara login karwa do. 5 Whys → pata chala session timeout 5 min pe set hai (config galat). Root cause fix → ek baar mein sabki problem solve.

**Interview Q&A:**

> **Q: "What's the difference between fixing a symptom and fixing the root cause?"**
> **A:** "Symptom woh hai jo user ko dikh raha hai, jaise app crash. Root cause woh actual reason hai jiski wajah se crash ho raha hai, jaise memory leak. Agar main sirf symptom theek karunga — app restart karwa kar — toh problem wapas aayegi. Root cause fix karne se permanently solve hoti hai aur repeat tickets nahi aate."

> **Q: "Explain the 5 Whys technique."**
> **A:** "5 Whys ek simple root-cause technique hai jisme main baar-baar 'kyun' poochta hoon — usually paanch baar — jab tak surface symptom se neeche asli wajah tak na pahunch jaaun. Har 'kyun' ka jawaab agle 'kyun' ko deeper le jaata hai, jab tak woh real fixable cause na mil jaaye."

---

### 5. When to Solve Yourself vs Escalate

**Kya hai:**
Har problem aap khud solve nahi kar sakte. Kab khud karna hai, kab senior/dev team ko dena hai — ye judgement.

**Support role mein kyun important:**
Do galtiyan possible hain: (1) chhoti cheez bhi escalate kar dena → lazy lagta hai, (2) badi cheez ghante tak khud try karte rehna → SLA miss, customer frustrate. Interviewer **balance** dekhna chahta hai.

**Kaise — escalation decision table:**

| Khud solve karo | Escalate karo |
|----------------|---------------|
| Password reset, cache clear, settings | Code bug / actual software defect |
| Known issue jiska documented fix hai | Server down / outage (sabko ho raha) |
| User ko feature samjhana | Data corruption / data loss |
| Basic config change | Security issue (hacking, breach) |
| Steps jo aapko aate hain | Aapke access/permission se bahar |

**Golden rules:**
- Pehle khud **basic troubleshooting** zaroor karo, fir escalate (warna dev wapas bhej dega).
- Escalate karte waqt **poori jaankari do**: steps to reproduce, error, kya try kiya. Ye sabse important hai.
- Customer ko kabhi adhar mein mat chhodo — "Main isko senior team ko bhej raha hoon, aapko X time mein update milega."

**Real example:**
User ka data galat dikh raha hai — numbers match nahi kar rahe. Ye data integrity issue hai, aap config se theek nahi kar sakte. Aap reproduce karke, screenshots aur exact steps ke saath dev team ko escalate karte ho — aur user ko timeline dete ho.

**Interview Q&A:**

> **Q: "When would you escalate an issue instead of solving it yourself?"**
> **A:** "Main tab escalate karta hoon jab problem mere access ya knowledge se bahar ho — jaise actual code bug, server outage, data corruption, ya security issue. Lekin escalate karne se pehle main basic troubleshooting zaroor karta hoon aur poori detail collect karta hoon — steps to reproduce, error message, aur maine kya try kiya — taaki dev team ka time bache."

> **Q: "How do you escalate properly?"**
> **A:** "Main ek clear summary banata hoon: problem kya hai, kis user ko, kab se, exact error, steps to reproduce, aur maine kya-kya try kiya. Ye sab proper detail ke saath sahi team ko deta hoon. Saath hi customer ko inform karta hoon ki issue escalate ho gaya hai aur unhe kab tak update milega — taaki woh dark mein na rahein."

---

### 6. Six Full Worked Scenarios (Interview ka dil)

Boss, **ye section sabse important hai.** Interview mein scenario poochenge, aur aapko **out loud, step by step** bolna hai. Har scenario mein same framework dikhaiye: pehle questions, fir isolate, fir likely causes, fir fix. Niche har ek ka model walkthrough hai — inhe practice karke bolna.

---

#### Scenario 1 — "App crashes on launch" (kholte hi band ho jaata hai)

**Thought process (bol kar):**
"Pehle main poochunga — kab se ho raha hai, koi error message flash hota hai kya, aur kya recently app update hua ya device update hua. Fir confirm karunga ye sirf unke device par hai ya sabke."

**Isolate:** Sirf ek user? → Device/install. Sabko? → Bad app update (software).

**Likely causes & fixes:**

| Cause | Fix |
|-------|-----|
| Corrupt install / update | App uninstall–reinstall |
| Cache/data corrupt | App cache clear (settings → app → clear cache) |
| Device OS purana / incompatible | OS update ya supported version batao |
| Recent buggy app version | Pichla stable version / dev ko escalate |
| Device kam memory/storage | Storage free karwao, restart |

**One-line answer:** "Main reproduce karunga, dekhunga sabko ho raha ya ek ko. Ek ko → reinstall + cache clear + OS check. Sabko → buggy release hai, escalate to dev."

---

#### Scenario 2 — "User can't log in"

**Thought process:**
"Main poochunga — exact error kya aa raha hai? 'Wrong password' ya 'server error' ya page hi load nahi ho raha? Kab se? Recently password change kiya?"

**Isolate:** Galat password error = credentials. Server error = backend. Page load nahi ho raha = network.

**Likely causes & fixes:**

| Cause | Fix |
|-------|-----|
| Galat password / Caps Lock on | Password reset karwao, Caps check |
| Account locked (zyada attempts) | Unlock / thodi der wait |
| Account expired/deactivated | Account status check karo |
| CapsLock / autofill purana password | Manually type karwao |
| Server/auth service down | Sabko ho raha? → Outage, escalate |
| Browser cache/cookies | Cache clear / incognito try |

**One-line answer:** "Sabse pehle exact error dekhunga. 'Wrong password' → reset. 'Server error' aur sabko → outage escalate. Sirf ek user, page load issue → network/browser cache."

---

#### Scenario 3 — "Data not loading / spinner forever" (loading ghoomta rehta hai)

**Thought process:**
"Spinner ghoom raha matlab app data fetch kar raha hai par response nahi aa raha. Main poochunga — internet theek hai? Sirf ek screen par ya har jagah? Doosre users ko bhi?"

**Isolate:** User ka net slow? Server slow/down? Specific data bada?

**Likely causes & fixes:**

| Cause | Fix |
|-------|-----|
| User ka internet slow/down | Network check, reconnect, refresh |
| Server API down/slow | Sabko? → backend escalate |
| Bahut bada data set | Filter lagao / pagination |
| Browser cache / stuck session | Refresh, cache clear, re-login |
| Firewall/VPN block | VPN off karke try |

**One-line answer:** "Pehle internet confirm, fir doosri site/screen chal rahi check karunga. Sirf ek ko aur baaki sab theek → uska network/browser. Sabko → server side, escalate. Bada data → filter."

---

#### Scenario 4 — "A feature / button not working" (button click pe kuch nahi hota)

**Thought process:**
"Main poochunga — click karne par kuch nahi hota, ya error aata hai? Kab se? Sirf is button par ya poora page weird hai? Konsa browser/device?"

**Isolate:** Sirf ek button = feature bug ya page partially loaded. Poora page = network/load issue.

**Likely causes & fixes:**

| Cause | Fix |
|-------|-----|
| Page poora load nahi hua | Refresh / hard reload (Ctrl+Shift+R) |
| Browser cache purana version | Cache clear |
| Browser incompatible / extension block | Doosra browser / incognito |
| Permission nahi hai us feature ki | User role/permission check |
| Actual code bug | Sabko ho raha? → escalate to dev |

**One-line answer:** "Hard refresh + cache clear pehle. Doosre browser mein try. Agar permission ka issue → role check. Sabko ho raha → genuine bug, screenshots ke saath escalate."

---

#### Scenario 5 — "Software running very slow"

**Thought process:**
"Main poochunga — poora system slow ya sirf ye app? Kab se? Kis time par zyada? Kitne data/users ke saath?"

**Isolate:** Sirf ye app slow vs poora device slow. Sirf ek user vs sab. Peak time?

**Likely causes & fixes:**

| Cause | Fix |
|-------|-----|
| User ka device kam RAM / bahut tabs | Tabs/apps band, restart |
| Internet slow | Speed check, network change |
| Bahut bada data load ho raha | Filter / pagination / archive |
| Browser cache bloated | Cache clear |
| Server overload (peak time, sabko) | Backend escalate / monitor |

**One-line answer:** "Pehle dekhunga sirf ye app slow ya poora device. Ek user → device/network/cache. Sabko slow, khaaskar peak time → server load, escalate to backend team."

---

#### Scenario 6 — "An error popup appears"

**Thought process:**
"Sabse pehle **exact error text** padhunga / screenshot maangunga — wahi sabse bada clue hai. Fir poochunga kab aata hai — kis action par? Hamesha ya kabhi-kabhi?"

**Isolate:** Error kis step par trigger hota hai → wahi feature/cause. Sirf ek user ya sab.

**Likely causes & fixes:**

| Cause | Fix |
|-------|-----|
| Validation error (galat input) | Sahi format/required field batao |
| Session expired | Re-login |
| Permission denied | Access/role check |
| Network/timeout error | Connection check, retry |
| Server 500 / unknown bug | Sabko? exact error note karke escalate |

**One-line answer:** "Exact error message hamesha pehle padhunga — woh seedha cause batata hai. Validation → input theek karwao. Session expired → re-login. '500/server error' aur sabko → bug, error text ke saath escalate."

---

**Boss, ek line jo har scenario mein impress karegi:**
> "Main hamesha pehle confirm karta hoon ki ye **sirf ek user** ko ho raha hai ya **sabko** — kyunki ye ek sawaal hi decide kar deta hai ki problem device/user side par hai ya server/software side par."

Ye ek line bol denge toh interviewer samajh jaayega aap structured thinker ho.

---

### Quick self-check

1. IRIFVD framework ke 6 steps order mein bataiye, aur "change one thing at a time" kahaan aur kyun lagta hai?
2. Ek user kehta hai "app not working" — aapke pehle 4 sawaal kya honge?
3. Problem sirf ek user ko ho rahi hai vs sabko — har case mein cause kis layer (user/device/network/software) mein hoga?
4. "Spinner forever" scenario — apne thought process ko 4 steps mein bol kar dikhaiye.
5. Aap kab khud solve karenge aur kab escalate karenge — 3-3 examples do, aur escalate karte waqt kya-kya jaankari saath bhejenge?

---

## Day 2.2 — Reading Errors, Logs & HTTP Status Codes

Boss, ye module aapka **daily bread** hai support role mein. 80% interview questions isi area se nikalte hain — kyunki yahi kaam aap din-bhar karenge. Aaram se padhiye, har sub-topic ko samajhiye, ratne ki zarurat nahi hai.

---

### 1. Error Message Kaise Padhein (Don't Panic)

**Kya hai:**
Error message wo text hai jo software tab dikhata hai jab kuch galat hota hai. Dekhne mein darawna lagta hai — lambi-lambi lines, technical jargon — par **usme sirf 1-2 lines hi asli matlab ki hoti hain.** Baaki sab "noise" hai.

**Support role mein kyun important:**
Customer aapko ek screenshot bhejega: "ye error aa raha hai, kuch nahi chal raha." Aapka kaam hai us darawni screen mein se **key line nikalna** aur turant samajhna ki problem kya hai. Jo support engineer panic nahi karta aur seedha key line padhta hai — wo 10x fast hai. Interviewer yahi dekhta hai: kya aap chaos mein calm reh sakte ho.

**Kaise (extract the key line):**
1. **Sabse pehle aakhri/pehli "Error:" ya "Exception:" line dhundhiye.** Asli wajah usually wahi hoti hai.
2. **Error code note kariye** (jaise `ERR_CONNECTION_REFUSED`, `0x80070005`, `E1234`) — ye Google karne ke liye gold hai.
3. **Jo plain English mein likha hai use padhiye** — "Permission denied", "File not found", "Connection timed out" — ye seedha bata deta hai problem.
4. **Noise ignore kariye** — memory addresses, lambi file paths, internal function names — ye usually relevant nahi for first diagnosis.

**Real example:**
Customer screenshot bhejta hai:
```
Traceback (most recent call last):
  File "/app/server/payments.py", line 88, in process
    charge = gateway.submit(order)
  File "/app/lib/gateway.py", line 142, in submit
    raise ConnectionError("Payment gateway timed out after 30s")
ConnectionError: Payment gateway timed out after 30s
```
Sab kuch ignore — **aakhri line** padho: *"Payment gateway timed out after 30s"*. Matlab: payment provider (third-party) respond nahi kar raha. Ye user ki galti nahi, na hi config — ye **upstream service slow/down** hai. Aap escalate karoge ya status check karoge.

**Googling an error correctly:**
- Error ka **exact text ya error code** copy karo, quotes mein daalo: `"ConnectionError: Payment gateway timed out"`.
- Apna **product/software ka naam** add karo: `Salesforce ERR_xyz login`.
- **Personal data hata do** (email, user ID, order number) before searching — privacy.
- Prefer official docs, vendor status page, ya recent forum posts.

**Interview Q&A:**

**Q: "A customer sends you a huge error log. How do you approach it?"**
> A: "Main panic nahi karunga. Sabse pehle main 'Error' ya 'Exception' wali key line dhundhunga, kyunki wahi actual cause hota hai — baaki stack trace mostly context hai. Phir agar koi error code hai use note karunga. Us key line se main decide karunga ki ye user-side issue hai, config hai, ya server-side. Agar samajh na aaye to exact error text Google karunga product name ke saath."

**Q: "How do you Google an error message effectively?"**
> A: "Exact error text ya code ko quotes mein search karta hoon, product ka naam add karta hoon, aur koi personal/sensitive data pehle hata deta hoon. Official docs aur vendor status pages ko prefer karta hoon over random forums."

---

### 2. Application Logs & Log Levels

**Kya hai:**
Logs ek **diary** hai jo software apne baare mein likhta rehta hai — "ye hua, fir ye hua, yahan error aaya." Har line mein usually **timestamp + level + message** hota hai. Jab user ko problem hoti hai aur aapke samne reproduce nahi hota, logs hi sach batate hain ki andar kya hua.

**Support role mein kyun important:**
User ka description hamesha aadha-adhura hota hai ("kaam nahi kar raha"). Logs **objective truth** hain. Support engineer ka core skill hai: log mein jaake **us user ke time-stamp ke aas-paas ki ERROR line dhundhna.** Interviewer specifically poochta hai log levels kyunki ye basic literacy hai.

**Log levels (yaad rakhiye ye table):**

| Level | Matlab | Support ko kya karna |
|-------|--------|---------------------|
| **DEBUG** | Bahut detailed, developer ke liye, "step by step kya ho raha" | Normally ignore; sirf deep debugging mein dekho |
| **INFO** | Normal events — "user logged in", "order created" | Background context; problem nahi |
| **WARN** | Kuch theek nahi par abhi chal raha hai — "disk 85% full", "retry attempt 2" | Dhyaan do — ye aane wali problem ka signal ho sakta hai |
| **ERROR** | Kuch fail hua — operation complete nahi hua | **Yahi dhundho.** Asli problem usually yahin |
| **FATAL/CRITICAL** | Itna bura ki app crash/ruk gaya | Highest priority, turant escalate |

Severity order: `DEBUG < INFO < WARN < ERROR < FATAL`.

**Kaise (relevant line dhundhna):**
1. User se **exact time + timezone** poochho jab error aaya.
2. Log mein us timestamp ke aas-paas jao.
3. `ERROR` ya `FATAL` keyword search karo (`Ctrl+F`, ya command line pe `grep`).
4. Us error line ke **theek upar** ki lines bhi padho — context milta hai (kya request thi, kaunsa user).

```bash
# Sirf error lines dekhna
grep "ERROR" application.log

# Ek khaas user ke around dekhna
grep "user_id=4821" application.log

# Live log dekhte rehna jaise aata hai
tail -f application.log
```

**Stack trace kya hai (basic):**
Jab code crash hota hai, wo batata hai **kaun-si line pe, kis function mein, kis function ne use call kiya** — ek seedhi rasta (trace) jo crash tak pahuncha. Aap support mein **stack trace ki sirf last line / "Caused by" line** padho — wahi root cause hota hai. Poora trace developer ke liye hai.

**Real example:**
User: "3:42 PM pe maine report download kiya, blank file aayi."
Aap log mein jaate ho:
```
2026-06-21 15:42:07 INFO  ReportService  user_id=4821 requested report=sales_q2
2026-06-21 15:42:09 WARN  ReportService  query returned 0 rows for date range
2026-06-21 15:42:09 ERROR ReportService  Empty dataset — generated blank PDF
```
Aha! WARN bata raha hai **0 rows aaye** — matlab user ne shayad galat date range chuna, ya us range mein data hi nahi. Ye **user error / data issue** hai, software bug nahi. Aap user ko guide karoge: "sahi date range select kijiye."

**Interview Q&A:**

**Q: "What are log levels and which one matters most for support?"**
> A: "Log levels severity batate hain — DEBUG (developer detail), INFO (normal events), WARN (warning, abhi chal raha), ERROR (kuch fail hua), aur FATAL (app crash). Support ke liye sabse pehle ERROR aur FATAL dekhne hote hain, kyunki actual failure wahin hota hai. Par WARN bhi ignore nahi karta — wo aksar aane wali problem ka early signal deta hai."

**Q: "A user reports an issue but you can't reproduce it. What do you do?"**
> A: "Main user se exact time aur timezone poochunga, fir logs mein us timestamp ke around jaake ERROR line dhundhunga. Error line ke upar ki context lines se pata chalega ki kaunsi request thi aur kaun-sa user. Logs objective truth dete hain jab reproduce nahi ho pa raha."

**Q: "What is a stack trace?"**
> A: "Stack trace wo rasta dikhata hai jo crash tak pahuncha — kaun-si line, kaun-sa function, aur usko kisne call kiya. Support mein main usually last line ya 'Caused by' line padhta hoon — wahi root cause hota hai. Poora trace developer ko deta hoon."

---

### 3. HTTP Status Codes (Most Important — Master This)

**Kya hai:**
Jab aapka browser/app server se kuch maangta hai (page, data), server ek **3-digit number** wapas bhejta hai jo batata hai request ka kya hua. Ye support ka **universal language** hai. First digit se category samajh aati hai:

| Range | Matlab | Kiski galti |
|-------|--------|------------|
| **2xx** | Success | Sab theek |
| **3xx** | Redirect | URL kahin aur chala gaya |
| **4xx** | Client error | **Request mein problem (user/aapki side)** |
| **5xx** | Server error | **Server ki side mein problem** |

Yaad rakhne ka golden rule: **4xx = "tumne galat maanga" (client), 5xx = "humse nahi ho paya" (server).**

**Support role mein kyun important:**
HTTP code se aap **5 second mein** decide kar sakte ho ki galti user-side hai ya server-side — bina kuch poochhe. 401 dekha? Login problem. 500 dekha? Backend dev ka kaam. Ye sabse common interview question area hai support mein. **Iska table interview se pehle ek baar zaroor dohra lena.**

**Kaise (kahan dekhein):**
- Browser mein `F12` → **Network tab** → kisi bhi request pe click → "Status" column.
- Logs mein bhi status code aata hai (`status=404`).
- Customer ko bolo screenshot of Network tab, ya error page pe number likha hota hai.

**The full table (yaad rakhiye — interview gold):**

| Code | Naam | Client/Server | Matlab | Support kya kare |
|------|------|---------------|--------|------------------|
| **200** | OK | Success | Request safal, sab theek | Kuch nahi — agar phir bhi user ko issue hai to problem display/data mein hai, network mein nahi |
| **301** | Moved Permanently | Redirect | URL hamesha ke liye nayi jagah | Purana bookmark/link update karo |
| **302** | Found (temp redirect) | Redirect | Abhi ke liye kahin aur bheja (login page, maintenance) | Normal; agar loop ban jaaye to dekho |
| **400** | Bad Request | **Client** | Request hi galat/malformed (missing field, galat format) | User input/form check karo — kuch missing ya invalid hai |
| **401** | Unauthorized | **Client** | **Login nahi / token expire** (not authenticated) | User ko re-login bolo, session/token expire ho gaya |
| **403** | Forbidden | **Client** | Login to hai par **permission nahi** (not allowed) | User ke role/access rights check karo — unhe ye cheez dekhne ki permission nahi |
| **404** | Not Found | **Client** | Jo maanga wo exist nahi karta (galat URL, deleted item) | Galat link, typo, ya item delete ho gaya — sahi URL/record verify karo |
| **408** | Request Timeout | **Client** | User ki request bheejne mein bahut der lag gayi | Slow/unstable internet check karo user-side; retry bolo |
| **429** | Too Many Requests | **Client** | Bahut zyada requests bhej di — **rate limit** | User/app thodi der ruke; agar API hai to throttle/slow down |
| **500** | Internal Server Error | **Server** | Server crash/bug — generic "humse galti" | **Server-side bug.** Logs dekho, dev team ko escalate karo |
| **502** | Bad Gateway | **Server** | Ek server doosre se baat kar raha tha, ulta-pulta jawab mila | Upstream/backend service down — infra/dev escalate |
| **503** | Service Unavailable | **Server** | Server abhi handle nahi kar sakta — **overload ya maintenance** | Thodi der baad try; check maintenance/outage status |

**Yaad rakhne ke shortcuts:**
- **401 vs 403** (interview favorite!): **401 = "tum kaun ho? login karo"** (identity nahi). **403 = "pehchaan liya, par tumhe entry nahi"** (permission nahi). Bouncer analogy: 401 = ID nahi dikhayi; 403 = ID dikhayi par tum VIP list mein nahi.
- **404 vs 400**: 404 = "cheez exist nahi karti"; 400 = "tumne request hi galat banayi."
- **500 vs 502 vs 503**: 500 = server ka apna code phata; 502 = beech wala server ulta jawab; 503 = server zinda hai par busy/maintenance.

**Real example:**
- User: "Login ke baad dashboard nahi khul raha, blank." Aap Network tab mein dekhte ho ek request **403** de rahi hai ek "admin-reports" endpoint pe. Matlab: user logged in hai (401 nahi), par uske paas **admin permission nahi** — system blank dikha raha. Fix: user ka role check karo, ya unhe batao ye section unke access mein nahi.
- User: "Pura site down hai, error 503." Ye **server-side** hai (5xx) — shayad maintenance ya overload. Aap user ki galti nahi dhundhoge — status page check karoge aur batayenge "we're aware, working on it."

**Interview Q&A:**

**Q: "What's the difference between 401 and 403?"**
> A: "Dono client-side hain par alag. **401 Unauthorized** matlab user authenticated hi nahi — login nahi hai ya token expire ho gaya, to main re-login suggest karunga. **403 Forbidden** matlab user logged in to hai, par us resource ki permission nahi — main uske role aur access rights check karunga. Simple line: 401 = 'kaun ho tum?', 403 = 'tumhe andar nahi aane denge.'"

**Q: "User says the page won't load and you see a 500. What do you do, and whose problem is it?"**
> A: "500 Internal Server Error server-side hota hai — user ki galti nahi. Ye server pe koi unhandled bug ya crash hai. Main user ko batauunga ki ye humari taraf ka issue hai, server logs check karunga us timestamp pe, aur agar bug confirm hota hai to backend/dev team ko escalate karunga with the error details. Main user ko unnecessarily input change karne ko nahi bolunga, kyunki problem unke side nahi hai."

**Q: "Difference between 502 and 503?"**
> A: "Dono server-side. 502 Bad Gateway matlab ek server doosre upstream server se baat kar raha tha aur invalid response mila — usually backend service down ya misconfigured. 503 Service Unavailable matlab server abhi available nahi — overload ya maintenance ki wajah se — thodi der baad chalega. 502 ke liye main upstream service check/escalate karunga, 503 ke liye maintenance ya outage status confirm karunga."

**Q: "You get a 404. Is the website down?"**
> A: "Nahi, 404 ka matlab site down nahi — site chal rahi hai, par jo specific page/resource maanga gaya wo exist nahi karta. Usually galat URL, typo, ya item delete ho gaya. Main sahi URL ya record verify karunga. Agar site hi down hoti to 5xx aata, jaise 503."

---

### 4. User Error vs Config Issue vs Known Bug vs Server-Side Outage

**Kya hai:**
Har support ticket in chaar buckets mein se ek mein girta hai. **Sahi bucket pehchanna = aadha kaam done**, kyunki har bucket ka response alag hai.

**Support role mein kyun important:**
Galat bucket choose kiya to time waste — jaise server outage ko "user ko re-login karwao" bolna bekaar hai. Interviewer dekhta hai kya aap **triage** kar sakte ho: kaun fix karega, kitni jaldi.

**Comparison table:**

| Bucket | Kya hai | Kaise pehchanein | Kaun fix karta | Aapka response |
|--------|---------|------------------|----------------|----------------|
| **User error** | User ne galat step / galat data daala | Sirf 1 user ko, specific action pe; logs mein "invalid input"/0 rows; sab theek baaki sab ke liye | User (aap guide karo) | Sahi steps samjhao, screen-share, docs bhejo |
| **Config issue** | Setting/permission/account galat set hai | Ek user ya group ko consistently; 403, ya feature missing; install/account-level | Aap ya admin team setting badle | Settings/role verify aur fix karo |
| **Known bug** | Software mein confirmed defect | Multiple users same pattern; already bug tracker mein; specific error/500 | Dev team (patch) | Ticket se link karo, workaround do, status batao |
| **Server-side outage** | Server/service down ya degraded | **Bahut saare** users ek saath; 5xx codes; status page red; sab cheez slow/down | Infra/dev (restore) | Acknowledge, status page point, ETA, mat bolo "aap kuch karo" |

**Distinguishing trick — pucho ye 3 sawaal:**
1. **Kitne log affected?** Ek = user/config. Bahut saare ek saath = outage/bug.
2. **Kya code aa raha?** 4xx = client/user/config side. 5xx = server side.
3. **Kya ye pehle kaam karta tha?** Achanak sabke liye toota = outage/deploy. Hamesha is user ko = user/config.

**Real example:**
- Ek user "report blank": logs mein 0 rows → **user error** (galat date range).
- Ek team ko "Export button gayab": baaki sab ke paas hai → **config issue** (us team ka feature-flag off).
- 8 users same "save fail, error 500": pehle se ticket exists → **known bug**, workaround do.
- 50 tickets achaanak "site down 503": → **server outage**, escalate + status page.

**Interview Q&A:**

**Q: "How do you decide if an issue is a user error or an actual bug?"**
> A: "Main teen cheezein dekhta hoon: kitne users affected hain, kya HTTP code aa raha hai, aur kya ye pehle kaam karta tha. Agar sirf ek user ko, 4xx code, aur baakiyon ke liye theek hai — to user error ya config. Agar multiple users ko same pattern, ya 5xx code, ya achaanak sabke liye toota — to bug ya server-side. Main assume nahi karta, logs aur scope se confirm karta hoon."

**Q: "Many users report the same problem at the same time. What's your first thought?"**
> A: "Achaanak bahut saare users = likely server-side outage ya bad deployment, individual user error nahi. Main HTTP codes check karunga — 5xx confirm karega server-side — aur status page/monitoring dekhunga. Phir main jaldi escalate karunga aur baaki affected users ko ek consistent acknowledgement bhejunga, har ek ko alag-alag troubleshoot karne ke bajaye."

---

### 5. Basic SQL for Support (Read-Only Mindset)

**Kya hai:**
SQL wo language hai jisse aap **database se sawal poochte ho.** Support mein aap aksar database mein jaake dekhte ho: "is user ka record kya keh raha hai? ye transaction hua ya nahi?" Aap **sirf padhne ke liye (SELECT)** jaate ho — kabhi blindly change nahi karte.

**Support role mein kyun important:**
Customer kehta hai "mera payment kat gaya par order nahi dikh raha." Aap database mein `SELECT` chalakar **actual sach** dekh lete ho — order exist karta hai ya nahi, status kya hai. Ye support engineer ko "guess karne wale" se "data se confirm karne wale" mein badal deta hai. **Interviewer ye bhi test karta hai ki aap responsible ho — production DB pe galti se UPDATE/DELETE na chala do.**

**Read-only mindset (SABSE IMPORTANT — ye line interview mein bolna):**
> "Production database pe main sirf SELECT chalata hoon. UPDATE ya DELETE kabhi blindly nahi — wo data permanently badal/mita sakta hai. Koi change zaruri ho to senior/DBA se confirm aur backup ke saath."

**Kaise (basic commands):**

```sql
-- Ek user ka record dhundhna (email se)
SELECT * FROM users WHERE email = 'ujjawal@example.com';

-- Sirf zaruri columns
SELECT id, name, status, created_at FROM users WHERE id = 4821;

-- Ek transaction check karna
SELECT * FROM transactions WHERE order_id = 'ORD-99812';

-- Multiple condition
SELECT * FROM orders WHERE user_id = 4821 AND status = 'failed';

-- Aakhri 10 orders, naye pehle
SELECT * FROM orders WHERE user_id = 4821 ORDER BY created_at DESC LIMIT 10;
```

Tod ke samajhiye:
- `SELECT` = "ye columns dikhao" (`*` = saare columns)
- `FROM users` = "users table se"
- `WHERE` = "is condition pe filter karo" — **ye sabse important, isse aap ek specific record nikalte ho**
- `ORDER BY ... DESC` = sort (DESC = bada/naya pehle)
- `LIMIT 10` = sirf 10 rows

**JAOIN roughly kya hai:**
Data alag-alag tables mein hota hai — `users` table mein naam/email, `orders` table mein order details (par order mein sirf `user_id` likha hota, naam nahi). **JOIN do tables ko ek common column (jaise `user_id`) pe jod deta hai** taaki aap dono ki info ek saath dekh sako.

```sql
-- User ka naam + uske orders ek saath
SELECT users.name, orders.order_id, orders.status
FROM orders
JOIN users ON orders.user_id = users.id
WHERE users.email = 'ujjawal@example.com';
```
Simple words: "orders nikaalo, aur har order ke saath uske user ka naam bhi laga do, dono ko `user_id = id` se match karke."

**Real example:**
Customer: "Maine ₹2000 ka payment kiya, paisa kat gaya, par order confirm nahi hua."
Aap chalaate ho:
```sql
SELECT order_id, amount, status, payment_ref, created_at
FROM transactions
WHERE payment_ref = 'PAY-554120';
```
Result aata hai: `status = 'payment_received', order_id = NULL`. Aha! Paisa to aa gaya par order create nahi hua — ye ek **known bug ya server hiccup** hai order-creation step mein. Aap ye evidence ke saath dev team ko escalate karte ho, **bina database ko khud chhede.**

**Interview Q&A:**

**Q: "How would you look up a customer's failed order in the database?"**
> A: "Main read-only SELECT chalauunga, jaise: `SELECT * FROM orders WHERE user_id = 4821 AND status = 'failed';`. Pehle user ko identify karunga email ya ID se, fir WHERE clause se uske failed orders filter karunga. Main sirf padhne ke liye query karta hoon — koi change nahi."

**Q: "Why should support engineers avoid UPDATE or DELETE on a production database?"**
> A: "Kyunki UPDATE aur DELETE data ko permanently badal ya mita dete hain — ek galat WHERE clause se hazaaron records corrupt ho sakte hain, aur production live customer data hota hai. Support ka kaam diagnose karna hai, fix karna nahi. Agar data change zaruri ho to main senior ya DBA se confirm karunga, backup ke saath, ya dev team ke through karwaunga."

**Q: "What does a JOIN do, in simple terms?"**
> A: "JOIN do tables ko ek common column pe jod deta hai. Jaise users table mein naam hai aur orders table mein sirf user_id — JOIN se main order ke saath user ka naam bhi ek hi result mein dekh sakta hoon, dono ko user_id = id pe match karke. Support mein useful jab info do tables mein bati hoti hai."

**Q: "A customer says they were charged but see no order. Walk me through it."**
> A: "Main transactions table mein unka payment reference SELECT karunga taaki dekh sakoon payment record exist karta hai aur status kya hai. Agar payment 'received' hai par order_id NULL — matlab paisa aaya par order create nahi hua, jo server-side ya bug issue hai. Main ye evidence ke saath dev team ko escalate karunga, database khud modify nahi karunga, aur customer ko refund/resolution timeline communicate karunga."

---

### Quick Self-Check

1. Ek lambe stack trace mein aap sabse pehle kaun-si line padhoge, aur kyun?
2. WARN aur ERROR log level mein kya farak hai — support ke liye dono mein se kis pe zyada dhyaan?
3. Bina dekhe batao: 401, 403, 404, 500, 503 — har ek client-side hai ya server-side, aur ek-line meaning?
4. 50 users ek saath "site down" bol rahe hain aur 503 aa raha hai — ye 4 buckets mein se kaun-sa, aur aapka pehla kaam?
5. Customer ke "charged but no order" case mein aap kaun-si SQL chalaoge, aur production DB pe kaun-se commands se door rahoge aur kyun?

---

## Day 2.3 — Networking Essentials (Software-Support Edition)

> Boss, yeh module deliberately **light** rakha hai — OSI layers, subnetting, routing tables yahan nahi aayenge. Ek software-support engineer ko networking sirf itni chahiye ki woh **"problem app ki hai ya internet ki?"** ka jawab confidently de sake. Interviewer bhi exactly yahi check karta hai. Chaliye shuru karte hain.

---

### 1. Internet Basics — Client, Server, IP, DNS

**Kya hai (simple)**
Jab aap koi app ya website kholte hain, do players hote hain: aapka device (**client**) aur woh computer jahan app ki data/logic rakhi hai (**server**). Client request bhejta hai, server response deta hai. Har device ka ek address hota hai — **IP address** (jaise `142.250.182.78`) — taaki data sahi jagah pahunche. Par numbers yaad rakhna mushkil hai, isliye **DNS** (Domain Name System) ek phonebook ki tarah kaam karta hai: aap `google.com` likhte hain, DNS usko IP address mein translate kar deta hai (`name → address`). Agar DNS fail ho jaaye, toh app khulega hi nahi — bhale internet chal raha ho.

**Support role mein kyun important**
80% support tickets ka root yahi flow hota hai: client → DNS → server. Agar aap yeh samajh gaye, toh "site nahi khul rahi" jaise ticket ko aap turant categorize kar sakte hain — DNS issue, server down, ya client-side problem.

**Kaise (mechanism)**
1. User browser mein `app.company.com` type karta hai.
2. Client DNS se poochta hai: "iska IP kya hai?" → DNS bolta hai `52.x.x.x`.
3. Client us IP par request bhejta hai.
4. Server response bhejta hai → page load.
Koi bhi step toote toh app fail.

**Real example**
User: "Aapka portal bilkul nahi khul raha, par baaki sab websites chal rahi hain." → Iska matlab user ka internet/DNS theek hai, problem aapke **server side** ya us specific domain par hai. Aap status page check karenge ya escalate karenge — user ke ghar ka WiFi blame nahi karenge.

**Interview Q&A**

> **Q: DNS ko simple words mein samjhaiye.**
> A: "DNS internet ka phonebook hai. Humein `google.com` jaise naam yaad rehte hain, lekin computers IP addresses se baat karte hain. DNS naam ko IP mein convert karta hai taaki request sahi server tak pahunche."

> **Q: Client aur server mein kya farak hai?**
> A: "Client woh device hai jahan se request jaati hai — user ka laptop ya phone. Server woh machine hai jo request receive karke response deti hai — jaise jahan application hosted hai. Support mein hum dekhte hain ki problem client side hai (user ka setup) ya server side (hamari app)."

---

### 2. "Is it my internet or the app?" — Quick Triage

**Kya hai**
Sabse pehla aur sabse important sawaal jab koi bole "kuch kaam nahi kar raha." Aapko 60 seconds mein decide karna hai: galti **user ke connection** ki hai ya **app/service** ki.

**Support role mein kyun important**
Yeh aapka pehla diagnostic fork hai. Agar aap internet ko app samajh kar dev team ko escalate karenge, toh aapka time aur unka time dono waste. Interviewer dekhta hai ki aapke paas ek **structured isolation process** hai ya aap randomly guess karte hain.

**Kaise (quick checks — yaad rakhiye yeh order)**

| Check | Kya batata hai |
|---|---|
| **Doosri website kholo** (e.g. google.com) | Khulti hai → internet theek, problem app ki. Nahi khulti → internet/WiFi issue. |
| **App ka status page dekho** (status.app.com) | Red/incident → app ki galti, user kuch nahi kar sakta. |
| **Doosre device/network se try karo** (phone data) | App chalti hai → user ke network/firewall issue. |
| **Router restart** | WiFi/internet flaky hai toh fix. |
| **`ping` chalao** (neeche detail) | Connectivity zinda hai ya nahi. |

**Real example**
User: "Dashboard load nahi ho raha." Aap poochte hain: "Ek kaam kariye, google.com khul raha hai?" → User: "Haan woh toh chal raha hai." → Ab aap jaante hain internet fine hai, ab aap app-specific cheezein dekhenge (cache clear, login refresh, status page).

**Interview Q&A**

> **Q: User bolta hai "internet nahi chal raha par app nahi khul rahi" — aap kaise pata karenge problem kahan hai?**
> A: "Main isolate karunga. Pehle poochunga koi aur website ya app chal rahi hai? Agar haan, toh internet theek hai, problem hamari app mein hai — main status page aur app-side cheezein dekhunga. Agar koi bhi website nahi chal rahi, toh problem user ke connection mein hai — router restart, doosra network try karein. Ek-ek karke variable eliminate karta hoon."

> **Q: Status page kya hota hai aur kab check karte hain?**
> A: "Status page ek public page hota hai jo batata hai service up hai ya down (jaise status.slack.com). Jab multiple users same problem report karein, ya jab koi single user app na khol paaye lekin uska internet theek ho — tab main status page check karta hoon taaki pata chale outage hai ya isolated issue."

---

### 3. `ping` aur `ipconfig` / `flushdns` — Practical Level

**Kya hai**
Yeh do simple command-line tools hain jo aap (ya user ko guide karke) chala sakte hain. Inka matlab samajhna kaafi hai — expert banne ki zaroorat nahi.

- **`ping`** — kisi address ko "hello" bhejta hai aur dekhता hai reply aata hai ya nahi, kitni der mein. Connectivity zinda hai ya nahi, yeh batata hai.
- **`ipconfig`** — aapke device ki network settings dikhata hai (IP address, etc.). (Mac/Linux par `ifconfig` / `ip addr`.)
- **`ipconfig /flushdns`** — DNS ki purani memory (cache) saaf karta hai. Agar website ka address change hua ho ya DNS galat cache ho gaya ho, yeh fix karta hai.

**Support role mein kyun important**
Yeh aapke "haath ke tools" hain. Interviewer poochta hai "user ka site nahi khul raha, kya karenge?" — agar aap `ping` aur `flushdns` confidently bol dein, aap practical lagte hain, ratne wale nahi.

**Kaise (commands)**

```bash
# Connectivity check — kya server tak pahunch ho rahi hai?
ping google.com

# Output samajhiye:
# Reply from 142.250.x.x: time=24ms   → connection theek, 24ms latency
# Request timed out                    → koi reply nahi, connectivity ya server problem

# Apni network settings dekho (Windows)
ipconfig

# DNS cache saaf karo (Windows) — "site move ho gayi par purana address cached hai" fix
ipconfig /flushdns

# Mac
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

**`ping` output ko padhna:**

| Output | Matlab | Action |
|---|---|---|
| `Reply ... time=20ms` | Connection healthy, fast | App-side dekho |
| `time=900ms` (high) | Connection slow/laggy | Network slow — app slow lagega |
| `Request timed out` | Reply nahi aaya | Connectivity down ya server reachable nahi |
| `could not find host` | DNS naam resolve nahi hua | DNS issue — `flushdns` try karo |

**Real example**
User: "Hamari app kal se bilkul nahi khul rahi, doosri sites chal rahi hain." Aap user se `ping app.company.com` chalwate hain → output `could not find host`. Iska matlab DNS resolve nahi ho raha. Aap `ipconfig /flushdns` karwate hain, app khul jaati hai — DNS cache stale tha.

**Interview Q&A**

> **Q: `ping` kya batata hai?**
> A: "`ping` ek address ko chhota packet bhejta hai aur dekhta hai reply aata hai ya nahi, aur kitni der mein. Isse pata chalta hai ki connectivity zinda hai aur kitni fast hai. Reply aaye toh connection theek, 'request timed out' aaye toh kuch beech mein toot raha hai."

> **Q: `ipconfig /flushdns` kab use karenge?**
> A: "Jab DNS cache stale ho — maan lijiye site naye server par move hui par user ke system mein purana IP cached hai, toh galat jagah connect hone se site nahi khulti. `flushdns` cache saaf kar deta hai taaki fresh address mile. 'could not find host' jaisi DNS errors mein yeh first fix hai."

> **Q: `ping` reply aa raha hai par app phir bhi nahi khul rahi — iska kya matlab?**
> A: "Iska matlab basic connectivity toh hai (server reachable hai), lekin problem usse upar hai — shayad app ka service down hai, ek specific port block hai, login/auth issue hai, ya app-level error. Toh main network ko exclude karke app-side troubleshooting par focus karunga."

---

### 4. Wi-Fi vs Wired, VPN, Firewall / Proxy

**Kya hai**

| Cheez | Simple matlab |
|---|---|
| **Wi-Fi** | Wireless connection — convenient par flaky/slow ho sakta hai (signal, interference) |
| **Wired (Ethernet)** | Cable connection — stable, fast, kam drops |
| **VPN** | Ek "tunnel" jo aapka traffic company ke network se route karta hai — secure access ke liye, par extra hop add karta hai |
| **Firewall** | Security guard jo decide karta hai kaunsa traffic andar/bahar jaa sakta hai — galti se app block kar sakta hai |
| **Proxy** | Beech ka server jisse saara traffic guzarta hai (company networks mein common) — kuch apps/URLs block ya slow kar sakta hai |

**Support role mein kyun important**
Corporate users ka 90% setup VPN + firewall + proxy ke peeche hota hai. Bahut saari "app slow hai / connect nahi ho rahi" tickets actually VPN/firewall ki wajah se hoti hain, app ki nahi. Yeh pattern pehchaanna aapko fast troubleshooter banata hai.

**Kaise (key insight + steps)**

- **VPN issue test:** User se bolo VPN **disconnect** karke try karein (agar policy allow kare). App chal jaaye → problem VPN/corporate network mein hai, app mein nahi.
- **Wi-Fi vs Wired test:** Flaky/slow ho toh Ethernet cable se try karein — stable hua toh Wi-Fi signal problem thi.
- **Firewall/proxy:** Agar app sirf office network par fail hoti hai par ghar/mobile-data par chalti hai → strong signal ki firewall/proxy app ka traffic block kar raha hai. Yeh aap IT/network team ko escalate karenge ("please whitelist app.company.com / port X").

**Real example**
User (work from home): "VPN se connect hone ke baad CRM bilkul slow, bina VPN ke sab fast." → Classic VPN bottleneck. App ki galti nahi — VPN saara traffic ek hi gateway se route kar raha hai jo congested hai. Aap user ko reassure karte hain aur network team ko VPN performance ke liye flag karte hain.

**Interview Q&A**

> **Q: Ek VPN par baitha user bolta hai app slow ya connect nahi ho rahi — aap kaise approach karenge?**
> A: "Pehle confirm karunga problem VPN-specific hai ya nahi. Agar policy allow kare, user se VPN off karke try karne ko bolunga. App theek chale toh problem corporate network/VPN routing mein hai, app mein nahi — main network/IT team ko escalate karunga. Agar VPN off karke bhi same problem hai, toh app-side dekhunga. Idea hai ek-ek layer ko isolate karna."

> **Q: Firewall ya proxy ek app ko kaise affect karta hai?**
> A: "Firewall aur proxy decide karte hain kaunsa traffic allow hai. Agar app ka domain ya port block hai, toh app connect hi nahi kar paayegi — bhale internet theek ho. Tell-tale sign: app office network par fail hoti hai par mobile data/ghar par chalti hai. Tab main IT team se app ke domain/port whitelist karne ko bolta hoon."

> **Q: Wi-Fi aur wired mein troubleshooting ke liye farak kyun matter karta hai?**
> A: "Wi-Fi mein signal drops, interference, aur slowdown common hain — intermittent issues aksar Wi-Fi ki wajah se hote hain. Agar user ki problem on-off hai, main usse wired (Ethernet) par try karne ko bolta hoon. Stable ho jaaye toh problem app mein nahi, Wi-Fi connection mein thi."

---

### 5. When a "Software Issue" is Actually a Connectivity Issue

**Kya hai**
Bahut baar user "app mein bug hai" bolkar ticket banata hai, par asli wajah uska network hota hai. Aapko **signs pehchaanne** aane chahiye taaki aap dev team par galat ticket na daalein.

**Support role mein kyun important**
Misrouted tickets = wasted time + frustrated dev team + slow resolution. Ek achha support engineer pehle connectivity rule-out karta hai, fir software bug maanta hai. Yeh maturity interviewer specifically dhoondta hai.

**Kaise — connectivity issue ke tell-tale signs:**

| Sign | Kyun yeh connectivity hai, bug nahi |
|---|---|
| "Loading spinner atka hua hai", timeout errors | App server tak pahunch nahi pa rahi |
| Sirf **kuch users** affected, baaki theek | Unke network/region/VPN ka issue |
| Ghar par chalti hai, office par nahi (ya ulta) | Network-specific = firewall/proxy/VPN |
| Intermittent — kabhi chalti kabhi nahi | Flaky connection (Wi-Fi/VPN drop) |
| "Failed to fetch" / "Network error" / "ERR_CONNECTION" | Literally network-layer errors |
| Page partially load, images/data missing | Connection drop beech mein |

**Bug hone ke signs (contrast):** Error reproducible har network par, specific button/feature par fail, error message app-level (`Invalid input`, `500 server error` consistently), saare users same exact step par atak rahe hain.

**Real example**
User: "App mein bug hai, data save nahi ho raha." Aap dekhte hain error: `Failed to fetch`. Aap poochte hain — "Kya google.com khul raha hai? VPN par hain?" → Pata chalta hai uska Wi-Fi beech beech mein drop ho raha tha, save request timeout ho rahi thi. Yeh dev bug nahi — connectivity tha. Aap user ko stable network par retry karwate hain, save ho jaata hai.

**Interview Q&A**

> **Q: Aap kaise decide karte hain ki problem software bug hai ya connectivity?**
> A: "Main pattern dekhता hoon. Connectivity ke signs: timeout/spinner atakna, 'failed to fetch' jaise network errors, intermittent behaviour, sirf kuch network par fail hona. Bug ke signs: har network par reproducible, specific feature par consistent fail, app-level error message. Pehle main connectivity rule-out karta hoon — doosri site, ping, network switch — fir hi software bug ke roop mein escalate karta hoon. Isse galat tickets nahi banti."

> **Q: User ne 'app crash ho rahi hai' bola — pehla step kya?**
> A: "Pehle reproduce aur clarify — exact error message kya aaya, kis step par, kab se. Saath hi connectivity quick-check — internet theek hai? Kyunki 'crash' aksar timeout/network error hota hai jo crash jaisa dikhta hai. Connectivity exclude karke fir app-side debugging — cache, version, logs."

---

### 6. Ports — One Line You Must Know

**Kya hai**
Ek server par ek hi IP address par bahut saari services chal sakti hain — har service ek **port** number par sunti hai (jaise darwaze ke andar alag-alag kamre). Web traffic usually port **443** (HTTPS) ya **80** (HTTP) use karta hai.

**Ek line jo yaad rakhni hai:** *Har app ek specific port use karti hai; agar woh port firewall/network par block hai, toh app connect hi nahi kar paayegi — bhale internet bilkul theek ho.*

**Support role mein kyun important**
Corporate firewalls aksar non-standard ports block karte hain. Agar app port 8443 jaisa kuch use karti hai aur company firewall usse block karta hai, app sirf office mein fail hogi. Yeh pehchaan aapko "whitelist port X" jaisi sahi escalation banane deti hai.

**Real example**
Company desktop app port `5223` use karti hai (push notifications). Office firewall block karta hai → notifications nahi aate, par baaki app theek. Aap IT ko bolte hain: "Please port 5223 whitelist karein for app.company.com." Bina port concept ke aap yeh diagnose hi nahi kar paate.

**Interview Q&A**

> **Q: Port kya hota hai, ek line mein?**
> A: "Port ek numbered darwaza hai jiske through ek app server se baat karti hai. Agar woh port network/firewall par block ho, app connect nahi kar sakti — internet theek hone ke bawajood."

> **Q: App office network par connect nahi hoti par ghar par karti hai — port se kya link?**
> A: "Strong chance hai ki office firewall app ka port block kar raha hai. Ghar ka network usse allow karta hai, isliye wahan chalti hai. Main IT se confirm karunga aur app ke required port/domain ko whitelist karwaunga."

---

### Quick Self-Check (apne aap ko test kariye)

1. User bolta hai "site nahi khul rahi par baaki sab chal raha hai" — yeh problem client side hai ya server side, aur aap kaise confirm karenge?
2. `ping` ka output `Request timed out` aaya — iska kya matlab hai, aur agla step kya?
3. `ipconfig /flushdns` exactly kya karta hai aur kis tarah ki error mein use hota hai?
4. Ek VPN-connected user bolta hai app slow hai — aapke pehle 2 troubleshooting steps kya honge?
5. Kaun se 3 signs batate hain ki "software bug" actually connectivity issue hai?

---

## Day 2.4 — Support Tools: Ticketing, Remote, SLA & Process

Boss, ye module aapko software/application support ke **tool aur process** side pe poora confident bana dega. Interviewer is din ke topics se bahut poochte hain kyunki ye daily kaam ka actual mechanics hai. Chaliye ek-ek karke samajhte hain.

---

### 1. Ticketing Systems (Jira, Zendesk, Freshdesk, ServiceNow)

**Kya hai (simple)**
Ticketing system ek software hai jahan har customer ka issue ek "ticket" ban jaata hai — ek unique record jiska number hota hai (jaise `INC-4521` ya `#80213`). Har ticket mein issue ki detail, kaun report kiya, kab, status, aur saari baat-cheet (comments) store hoti hai. Socho ye ek **digital diary + to-do list + chat thread** sab ek jagah.

Bina ticketing ke support email/WhatsApp pe chalega — sab kho jaayega, kaun sa issue pending hai pata nahi chalega. Ticketing sab ko **trackable** banata hai.

**Kaun sa tool kahan use hota hai:**

| Tool | Mostly kahan | Khasiyat |
|------|-------------|----------|
| **Zendesk** | Customer support (B2C, SaaS companies) | Email/chat-heavy, customer-facing, simple UI |
| **Freshdesk** | Customer support (startups, mid-size) | Zendesk jaisa, sasta, India mein popular |
| **Jira (Service Management)** | Dev + IT teams | Engineering ke saath tight integration — bug ko dev tak push karna easy |
| **ServiceNow** | Bade enterprises (IT, banks) | Heavy ITIL workflows, change/incident/problem sab built-in |

**Support role mein kyun important**
Interviewer dekhna chahta hai ki aap ek **organised, trackable** tareeke se kaam kar sakte ho. Agar aap bolo "main email pe reply kar deta hoon", to wo red flag hai. Ye tools batate hain ki aap process-driven ho — kuch slip nahi karega.

**Kaise — Ticket Lifecycle (sabse important concept)**

Har ticket ek journey se guzarta hai. Ye **lifecycle** yaad rakhiye:

```
New / Open  →  In Progress  →  Pending / On-Hold  →  Resolved  →  Closed
   |              |                  |                  |            |
ticket aaya   aap kaam     customer/3rd-party     fix de diya   customer ne
              kar rahe ho   ka wait kar rahe ho     (confirm     confirm kiya,
                                                     pending)     ya auto-close
```

- **New/Open** — issue aaya, abhi kisi ne pick nahi kiya / abhi shuru kiya.
- **In Progress** — aap actively investigate/fix kar rahe ho.
- **Pending (On-Hold)** — aap blocked ho: customer se info chahiye, ya kisi aur team ka wait hai. SLA clock yahan aksar "pause" hota hai.
- **Resolved** — aapne solution de diya, par customer ne abhi confirm nahi kiya.
- **Closed** — customer ne confirm kiya issue gaya / ya X din baad auto-close.

> **Resolved vs Closed ka farak interview mein poocha jaata hai:** Resolved = "maine theek kar diya, confirm hona baaki hai." Closed = "customer ne bhi maan liya, case khatam." Kabhi bhi confirm hone se pehle Closed mat karo.

**Kaise — Ek GOOD ticket kaise likhein**

Ye **bahut** important hai. Achha ticket = jaldi fix. Bura ticket = aage-peeche 5 emails. Ek achhe ticket mein hona chahiye:

1. **Clear title** — issue ek line mein. "App not working" ❌. "Invoice PDF download button gives 500 error on Chrome" ✅.
2. **Steps to reproduce** — exact steps, number-wise, taaki koi aur bhi same issue dobara la sake.
3. **Expected vs Actual** — kya hona chahiye tha vs kya hua.
4. **Environment** — browser/OS/app version, kaunsa account, kab hua (time).
5. **Evidence** — screenshot, screen recording, error message, **logs**.

Example of a well-written ticket:

```
Title: Invoice PDF download fails with 500 error (Chrome, all users)

Steps to reproduce:
1. Login to portal as any user
2. Go to Billing > Invoices
3. Click "Download PDF" on any invoice

Expected: PDF downloads
Actual: Page shows "500 Internal Server Error", PDF does not download

Environment:
- Browser: Chrome 138 (also reproduced on Edge)
- Account: acme-corp (and 2 others)
- First seen: 21-Jun 10:15 IST
- Affected: ALL users tested (4/4)

Evidence:
- Screenshot attached (error_500.png)
- Console error: "GET /api/invoice/4521/pdf 500"
- Backend log line: NullPointerException in InvoiceService.java:88
```

**Real example**
Customer chat karta hai: "Mera report export nahi ho raha." Aap us chat ko ek Freshdesk ticket banate ho. Title likhte ho: *"CSV export button unresponsive on Reports page (Safari only)."* Steps add karte ho, ek screen recording maangte ho, customer ke browser-version note karte ho. Ab agar ye L2/dev tak jaaye to unhe poori picture mil jaati hai — koi dobara customer ko tang nahi karna padta.

**Interview Q&A**

**Q: Ek achhe support ticket mein kya hona chahiye?**
A: "Clear, specific title; exact steps to reproduce; expected vs actual behaviour; environment details (browser, OS, app version, account); aur evidence — screenshot ya error logs. Iska maqsad ye hai ki next person bina customer se dobara poochhe issue samajh sake aur reproduce kar sake. Main hamesha 'app not working' jaisi vague line avoid karta hoon, kyunki wo time waste karti hai."

**Q: Resolved aur Closed mein kya farak hai?**
A: "Resolved ka matlab hai maine fix ya solution de diya hai, lekin customer ne abhi confirm nahi kiya. Closed tab hota hai jab customer confirm kar de ya ek defined wait-period ke baad ticket auto-close ho jaaye. Main kabhi customer-confirmation se pehle ticket Closed nahi karta — warna reopen ka risk rehta hai aur metrics galat dikhte hain."

**Q: Aapne kabhi Jira/Zendesk use kiya hai?**
A: (Honest raho) "Main ticketing tools ke core concepts se familiar hoon — lifecycle, priority, SLA, escalation. [Jo use kiya wo bolo.] Naya tool 1-2 din mein pick kar leta hoon kyunki sabka workflow conceptually same hai: ticket banao, categorise karo, work karo, update karo, resolve karo."

---

### 2. Priority = Impact × Urgency (P1–P4 & Severity)

**Kya hai (simple)**
Har ticket equally important nahi hota. **Priority** decide karti hai ki pehle kaunsa attack karna hai. Formula:

> **Priority = Impact × Urgency**

- **Impact** = kitne logon/business pe asar? (1 user vs poori company)
- **Urgency** = kitni jaldi fix chahiye? (abhi-abhi vs next week chalega)

Dono ko mila ke priority milti hai, aksar **P1 → P4** (P1 sabse high).

| Priority | Matlab | Example |
|----------|--------|---------|
| **P1 (Critical)** | Business thap, sab affected, no workaround | Poora payment system down hai, koi order place nahi kar paa raha |
| **P2 (High)** | Major function affected, bahut users, workaround weak | Login slow/intermittent, half users stuck |
| **P3 (Medium)** | Limited impact, workaround hai | Ek report ka filter galat dikha raha, baaki sab fine |
| **P4 (Low)** | Cosmetic / minor | Button ka colour galat, typo on a page |

**Severity vs Priority (interview favourite):**
- **Severity** = technical kitna bada/serious hai (system pe kitna damage).
- **Priority** = business ke liye pehle kya fix karein.
Ye alag ho sakte hain! Ek typo on the homepage = low severity, par agar CEO ki demo aaj hai to high priority. Ek crash in an admin tool koi use nahi karta = high severity, low priority.

**Support role mein kyun important**
Aapke paas 20 tickets hain, time limited. Interviewer dekhta hai ki aap **triage** kar sakte ho — sahi cheez pehle uthate ho. P1 ko chhod ke P4 pe kaam karna = disaster. Sahi priority lagana = mature support engineer ki nishani.

**Kaise — priority set karna**
1. Poocho: **Kitne affected hain?** (1 / kuch / sab) → Impact.
2. Poocho: **Kya workaround hai?** Agar nahi → urgency badhti hai.
3. Poocho: **Business-critical function hai kya?** (payment, login, checkout = haan).
4. Impact × Urgency → P-level. Doubt ho to ek level up rakho aur note karo "escalating to P2 due to no workaround."

**Real example**
Do tickets aaye:
- A: "Ek customer ka profile-photo upload nahi ho raha." → 1 user, cosmetic-ish, workaround hai (baad mein upload). **P4/P3.**
- B: "Checkout pe 'Pay Now' click karne pe error, koi payment nahi ho raha." → sab users, revenue ruk gaya, no workaround. **P1.**

Aap B pehle uthaoge, A ko queue mein rakhoge. Yahi triage hai.

**Interview Q&A**

**Q: Priority kaise decide karte ho?**
A: "Main Impact × Urgency dekhta hoon. Impact matlab kitne users ya business functions affected hain, aur urgency matlab kitni jaldi solve hona chahiye — workaround hai ya nahi. Agar poora business-critical flow down hai aur koi workaround nahi, wo P1 hai. Single user ka cosmetic issue P4. Doubt ho to main thoda upar rakhta hoon aur reason note karta hoon."

**Q: Severity aur Priority mein farak?**
A: "Severity technical seriousness hai — system pe kitna asar. Priority business decision hai — pehle kya fix karein. Ye alag ho sakte hain: ek admin-only tool ka crash high severity par low priority ho sakta hai kyunki use koi nahi karta. Wahi ek homepage typo low severity par high priority ho sakta hai agar koi badi demo aaj hai."

**Q: Ek saath 3 P1 aa gaye, kya karoge?**
A: "Pehle confirm karta hoon ki teeno genuinely P1 hain. Phir business impact se rank karta hoon — sabse zyada revenue/users wala pehle. Turant manager/lead ko inform karta hoon kyunki multiple P1 = possible bigger outage, aur extra hands chahiye ho sakte hain. Har ticket pe status update deta hoon taaki customers ko pata rahe hum on it hain."

---

### 3. SLA — Response Time vs Resolution Time

**Kya hai (simple)**
**SLA = Service Level Agreement** — ek promise/contract jismein likha hota hai ki support kitni jaldi respond karega aur kitni jaldi solve karega. Ye priority ke hisaab se alag hota hai (P1 ka SLA fast, P4 ka relaxed).

Do alag clocks hote hain:

| SLA type | Matlab | Example (P1) |
|----------|--------|--------------|
| **Response time** (First Response) | Pehli baar customer ko reply/acknowledge karne ka time | "15 minutes mein hum reply karenge" |
| **Resolution time** | Issue actually solve karne ka time | "4 ghante mein fix" |

> Yaad rakhiye: **Response ≠ Resolution.** Aap turant respond kar sakte ho ("Hi, hum dekh rahe hain") bina solve kiye. Response SLA pehle hit hota hai — isliye **acknowledge fast karo, chahe solution baad mein aaye.**

**Sample SLA matrix:**

| Priority | First Response | Resolution |
|----------|---------------|-----------|
| P1 | 15 min | 4 hrs |
| P2 | 1 hr | 8 hrs |
| P3 | 4 hrs | 2 days |
| P4 | 1 day | 5 days |

**Support role mein kyun important**
SLA **breach** (deadline miss) = company ko penalty, customer naraaz, kabhi paisa refund. Interviewer dekhta hai ki aap SLA-conscious ho — clock dekhte ho, time pe update dete ho. "Main pehle acknowledge karta hoon taaki response SLA na break ho" — ye sunke wo impress hota hai.

**Kaise — SLA manage karna**
1. Ticket aate hi turant **acknowledge** karo (response SLA save).
2. Priority ke hisaab se SLA clock samjho — kitna time hai.
3. Agar resolution late ho rahi hai → **proactive update** do, customer ko mat chhodo silence mein.
4. Blocked ho (customer/3rd-party ka wait) → ticket "On-Hold" karo taaki SLA clock pause ho.
5. Breach hone wala ho → lead ko warn karo, escalate karo.

**Real example**
P1 ticket aaya 10:00 baje, response SLA 15 min. Aap 10:05 pe reply karte ho: "Hi, humne issue note kiya, team investigate kar rahi hai, update 30 min mein." Response SLA met (5 < 15). Ab resolution 4 ghante mein chahiye. 12:00 pe abhi tak fix nahi → aap customer ko update dete ho aur dev team ko escalate karte ho, taaki 14:00 ke deadline se pehle ho jaaye.

**Interview Q&A**

**Q: SLA kya hota hai, aur response vs resolution time mein farak?**
A: "SLA ek agreed promise hai ki support kitni jaldi respond aur resolve karega. Response time = customer ko pehli baar acknowledge karne ka time; resolution time = issue actually solve karne ka time. Dono alag clocks hain — main hamesha pehle jaldi acknowledge karta hoon taaki customer ko pata rahe hum on it hain, even agar fix mein time lage."

**Q: Agar lagta hai SLA breach ho jaayega to kya karoge?**
A: "Pehle proactively customer ko honest update deta hoon — silence sabse bura hai. Saath hi apne lead ko inform karta hoon aur zaroorat ho to escalate karta hoon taaki extra help mile. Agar blocker customer ya 3rd-party ke wajah se hai, main ticket ko On-Hold karta hoon aur reason document karta hoon, taaki SLA fairly calculate ho."

---

### 4. Support Tiers L1 / L2 / L3 & Escalation

**Kya hai (simple)**
Support layers mein bata hua hota hai, taaki simple issues simple log handle karein aur mushkil issues experts tak jaayein.

| Tier | Kaun | Kya karte hain |
|------|------|----------------|
| **L1 (First line)** | Frontline agents | Basic issues — password reset, how-to, known fixes, ticket logging. Quick wins. |
| **L2 (Technical)** | Senior support / app specialists | Deeper troubleshooting, config issues, logs padhna, known bugs handle karna |
| **L3 (Expert / Dev)** | Engineers, product devs | Code-level bugs, database fixes, real defects. Ticket ko code change chahiye |

> Kabhi-kabhi **L0** hota hai = self-service (knowledge base, chatbot) jahan customer khud solve kar le.

**Escalation** = jab issue aapke tier ke bas se bahar ho, to use **upar** (next tier) bhejna.

**Support role mein kyun important**
Naye log do galtiyaan karte hain: (1) escalate hi nahi karte aur hours waste karte hain, ya (2) bina koshish kiye turant escalate kar dete hain. Interviewer balance dekhna chahta hai — **pehle apna best try, phir clean escalation with full info.**

**Kaise — Kab aur kaise escalate karein**

**Kab escalate karo:**
- Issue aapki access/permission ke bahar hai (e.g., database change chahiye).
- Aap troubleshooting steps exhaust kar chuke ho.
- SLA breach hone wala hai aur fix nahi mil raha.
- Ye ek confirmed bug/defect hai (code fix chahiye → L3/dev).
- Customer high-value/angry hai aur senior intervention chahiye.

**Kaise escalate karo (clean handoff — ye interview gold hai):** Upar wale ko sab dedo taaki wo zero se shuru na kare:

```
Escalation summary:
- Ticket #: INC-4521  | Priority: P1
- Issue: Invoice PDF download → 500 error, ALL users
- Steps to reproduce: [listed]
- What I already tried:
    • Cleared cache / different browser → still fails
    • Checked status page → no known outage
    • Confirmed across 3 accounts → reproducible
- Findings: Console shows 500 on /api/invoice/{id}/pdf;
  backend log = NullPointerException InvoiceService.java:88
- Why escalating: Needs code-level fix (out of L1/L2 scope)
- Customer impact: Billing blocked, SLA resolution 14:00 IST
```

**Real example**
Customer: report export pe error. Aap (L1) ne cache clear karaya, dusra browser try karaya, account check kiya — phir bhi fail, aur error log mein backend exception dikh raha. Ab ye code-level lagta hai. Aap L2/L3 ko upar wala summary ke saath escalate karte ho. Wo bina customer ko dobara tang kiye direct kaam shuru kar dete hain.

**Interview Q&A**

**Q: Aap kab escalate karenge?**
A: "Jab issue mere tier ki scope ya access se bahar ho — jaise confirmed bug jisme code change chahiye, ya database-level fix. Ya jab maine apne saare troubleshooting steps try kar liye ho aur solve na ho raha ho, ya SLA breach ka risk ho. Main pehle khud genuine effort karta hoon, taaki har chhoti cheez upar na jaaye, lekin atke rehkar customer ka time bhi waste nahi karta."

**Q: Escalate karte waqt aap kya information pass karte ho?**
A: "Ticket number aur priority, issue ka clear summary, steps to reproduce, maine kya-kya already try kiya, koi findings/logs, escalate kyun kar raha hoon, aur customer impact plus SLA deadline. Maqsad ye ki next person zero se na shuru kare aur customer ko dobara repeat na karna pade."

**Q: L1, L2, L3 mein farak?**
A: "L1 frontline hai — basic, known issues, password resets, how-to, ticket logging. L2 deeper technical troubleshooting karta hai — config, logs, known bugs. L3 expert/dev level hai — code aur database-level fixes, actual defects. Issue jitna deep, utna upar."

---

### 5. ITIL Basics (Light) — Incident vs Service Request vs Problem vs Change

**Kya hai (simple)**
ITIL ek standard framework hai IT/support kaam organise karne ka. Aapko deep ITIL nahi chahiye — bas **4 terms** ka farak clear ho. Ye interview mein aksar poocha jaata hai.

| Term | 1-line matlab | Example |
|------|--------------|---------|
| **Incident** | Kuch tha jo ab toot gaya / kaam nahi kar raha | "Login page down hai" |
| **Service Request** | Customer kuch maang raha hai (toota kuch nahi) | "Mujhe new user account chahiye" / "access badhao" |
| **Problem** | Kai incidents ke peeche ka **root cause** | "Login roz fail ho raha — root cause ek memory leak hai" |
| **Change** | System mein soch-samajh ke kiya gaya **modification** | "Server upgrade karna, naya feature deploy karna" |

> **Yaad rakhne ka trick:**
> Incident = **toot gaya** (fix it now).
> Service Request = **chahiye** (give it / set it up).
> Problem = **baar-baar kyun toot raha** (find root cause).
> Change = **jaan-boojh ke badal rahe** (planned modification).

**Support role mein kyun important**
Interviewer check karta hai ki aap issues ko sahi **categorise** kar sakte ho. Galat category = galat workflow = galat SLA. "Reset my password" ek **service request** hai, "system down" ek **incident** — ye farak pata hona maturity dikhata hai.

**Kaise — categorise karna**
- Poocho: kuch **toota** hai? → **Incident.**
- Customer kuch **maang** raha hai jo normally provide hota hai? → **Service Request.**
- Same incident **baar-baar** aa raha? → **Problem** raise karo (root cause).
- Hum jaan-boojh ke kuch **deploy/modify** kar rahe? → **Change** (approval ke saath).

**Real example**
- "Email bhej nahi paa raha" → **Incident.**
- "Mujhe ek shared mailbox banwana hai" → **Service Request.**
- "Pichle hafte 5 baar email service down hui" → ek **Problem** open hota hai root cause dhoondhne ko.
- "Email server ko v2 pe upgrade karna" → **Change** (scheduled, approved).

**Interview Q&A**

**Q: Incident aur Service Request mein farak?**
A: "Incident matlab kuch jo kaam kar raha tha ab toot gaya — usse jaldi restore karna hai. Service Request matlab customer kuch standard cheez maang raha hai jisme kuch toota nahi — jaise naya account, access, ya software install. Incident = fix, Service Request = fulfil."

**Q: Problem aur Incident mein farak?**
A: "Incident ek single event hai jisme service down/affected hai — turant restore. Problem us incident (ya kai incidents) ke peeche ka root cause hai. Incident management bolta hai 'pehle service wapas laao', problem management bolta hai 'taaki dobara na ho, root cause fix karo'. Example: roz login fail hona incidents hain; underlying memory leak Problem hai."

**Q: Change kya hota hai support context mein?**
A: "Change ek planned modification hai system mein — feature deploy, upgrade, config update. Ise aksar approval aur scheduling chahiye taaki naya incident na ban jaaye. Difference ye ki incident unplanned aur urgent hota hai, change planned aur controlled."

---

### 6. Remote Support Tools (AnyDesk, TeamViewer, Screen Share)

**Kya hai (simple)**
Kabhi customer ki problem phone/chat pe samajh nahi aati. Tab aap remote tool se uski screen **dekh** sakte ho ya (permission se) uska computer **control** kar sakte ho. Common tools: **AnyDesk, TeamViewer**, ya simple **screen share** (Zoom/Teams/Meet).

| Mode | Kya kar sakte ho | Kab use |
|------|------------------|---------|
| **Screen share (view-only)** | Sirf dekh sakte ho customer ki screen | Aksar enough — guide karte hue dekhna |
| **Remote control (AnyDesk/TeamViewer)** | Uska mouse/keyboard control | Jab khud kar ke dikhana ya fix karna ho |

**Support role mein kyun important**
Application support mein bahut issues "ye button kahan hai", "yahan kya settings hai" type hote hain — screen dekh ke 2 min mein solve. Interviewer ye bhi check karta hai ki aap **security/consent** rule jaante ho — kyunki kisi ka computer control karna sensitive hai.

**Kaise — steps**
1. Customer ko bolo tool install/open kare (AnyDesk ek 9-digit ID deta hai).
2. Customer aapko ID/code share kare → aap connect request bhejo.
3. **Customer apni screen pe "Accept/Allow" daba ke explicit permission de** — ye step skip nahi hota.
4. Pehle view-only se shuru karo; control sirf zaroorat ho aur customer haan kare tab.
5. Kaam ke baad **session disconnect karo** aur confirm karo connection band hai.

**Security & Consent rule (CRITICAL — interview ka favourite):**
- **Kabhi bina explicit consent ke connect mat karo.** Customer ko boldena hi enough nahi — usse screen pe accept karwao.
- Session ke dauraan **kya kar rahe ho bolte raho** ("ab main settings kholta hoon").
- Sensitive cheezein (passwords, banking) **mat dekho/maango** — agar password chahiye, customer khud type kare, aap dekho mat.
- **Scam-awareness:** Sikhana ki random call pe AnyDesk ID kabhi share na karein — ye famous scam hai. Sirf verified support se.
- Session record/log karo (audit ke liye) jahan policy ho, aur customer ko inform karo.
- Kaam khatam = turant disconnect.

**Real example**
Customer: "Report filter set nahi ho raha, samajh nahi aa raha." Phone pe 10 min waste. Aap bolo: "Sir, agar aap permit karein to main aapki screen dekh leta hoon — AnyDesk pe ek ID aayegi, aap mujhe batayein aur screen pe 'Accept' dabayein." Connect hone pe view-only mein dekhte ho — customer galat tab pe tha. 30 second mein guide kar dete ho. Session disconnect, done.

**Interview Q&A**

**Q: Remote support tool kab aur kaise use karoge?**
A: "Jab chat ya phone pe issue clearly samajh na aaye ya samjhana mushkil ho, tab AnyDesk/TeamViewer se screen dekhta hoon. Pehle customer se explicit permission leta hoon — wo screen pe accept karta hai. Aksar view-only kaafi hota hai; control tabhi leta hoon jab zaroori ho aur customer haan kare. Kaam ke baad turant disconnect karta hoon."

**Q: Remote session mein security ka kya dhyaan rakhoge?**
A: "Bina explicit consent connect nahi karta — customer ko screen pe accept karwata hoon. Session ke dauraan bolta rehta hoon ki kya kar raha hoon. Passwords ya banking details main na dekhta hoon na maangta hoon — agar password chahiye to customer khud type karta hai. Customer ko ye bhi aware karta hoon ki random unknown callers ko apni remote ID kabhi na de — ye common scam hai. Kaam ke baad session band karke confirm karta hoon."

---

### 7. Knowledge Base (KB) — Using & Contributing

**Kya hai (simple)**
KB ek **store of solutions** hai — articles, how-to guides, troubleshooting steps, FAQs, known issues + fixes. Do tarah: **internal** (support team ke liye) aur **external** (customers self-help). Tools: Confluence, Zendesk Guide, Notion, Freshdesk Solutions.

**Support role mein kyun important**
KB se aap **fast aur consistent** solve karte ho — same issue ko har baar zero se solve nahi karna padta. Interviewer ye sunna chahta hai ki aap (1) KB pehle check karte ho, (2) naya solution mile to KB mein **contribute** karte ho. Contribution dikhata hai ki aap team ko aage le ja rahe ho, sirf khud ka kaam nahi.

**Kaise**
- **Using:** Naya ticket aaye → pehle KB search karo (keyword/error message). Mil gaya → tested solution apply karo. Customer ko external KB article ka link bhi de sakte ho.
- **Contributing:** Ek naya/tricky issue solve karo jo KB mein nahi tha → ek naya article likho:
  - Clear title (error/symptom-based, jaise customer search karega).
  - Symptom / kab hota hai.
  - Step-by-step solution.
  - Screenshots agar ho.
  - Tags/keywords.
- Purana article galat ho gaya (UI badal gaya) → **update** karo.

**Real example**
Ek naya error "License sync failed (code 0x83)" aata hai. KB mein kuch nahi. Aap troubleshoot karke pata lagate ho ki system clock galat hone se hota hai. Solve karne ke baad ek KB article likhte ho: *"Fixing 'License sync failed (0x83)' — caused by incorrect system date/time"* with steps. Agli baar koi agent (ya customer) wahi error search kare → 30 second mein solve. Aapne poori team ka time bachaya.

**Interview Q&A**

**Q: Knowledge base ka use kaise karte ho?**
A: "Naya ticket aate hi main pehle KB search karta hoon — error message ya keyword se. Agar tested solution mil jaaye to wahi apply karta hoon, isse fast aur consistent solve hota hai. Customer self-help kar sake to external KB article ka link bhi share karta hoon."

**Q: Aap KB mein contribute karte ho?**
A: "Haan. Jab koi naya ya tricky issue solve karta hoon jo KB mein nahi tha, main ek clear article likhta hoon — symptom, step-by-step fix, aur searchable keywords ke saath. Purane article galat ho jaayein to update bhi karta hoon. Isse poori team ka time bachta hai aur same issue dobara zero se solve nahi karna padta."

---

### 8. Email / Chat Support Etiquette (Basics — full deep-dive Day 3)

**Kya hai (simple)**
Aap kya bolte ho utna hi important hai jitna kya fix karte ho. Communication = customer ka experience. (Day 3 mein detail mein, abhi basics.)

**Core etiquette rules:**
- **Acknowledge fast** — "Got it, dekh raha hoon" — silence sabse bura.
- **Empathy pehle** — "I understand ye frustrating hai" customer ko shaant karta hai.
- **Plain language** — jargon avoid karo; customer technical nahi hai.
- **Set expectations** — "30 min mein update doonga", phir us pe khade raho.
- **Confirm before closing** — "Kya ab theek kaam kar raha hai?"
- **Tone:** chat = thoda crisp/friendly; email = thoda zyada structured/formal.
- **Kabhi blame mat karo** ("aapne galat kiya"). Solution pe focus.

**Real example (chat):**
> Customer: "Ye stupid app phir crash ho gaya!! 3rd time!"
> Aap: "I'm really sorry ye baar-baar ho raha hai — main samajh sakta hoon kitna frustrating hai. Chaliye abhi ise theek karte hain. Aap mujhe bata sakte hain crash exactly kab hota hai — kaunsa screen kholne pe?"

Empathy + ownership + next step — sab ek reply mein.

**Interview Q&A**

**Q: Ek angry customer ko chat pe kaise handle karoge?**
A: "Pehle empathy — acknowledge karta hoon ki frustration valid hai, blame nahi karta. Phir ownership leta hoon aur ek clear next step deta hoon. Plain language use karta hoon, expectations set karta hoon, aur calm professional tone rakhta hoon. Maqsad: customer ko mehsoos ho ki main genuinely solve karne ke liye hoon."

**Q: Email aur chat support ke tone mein farak?**
A: "Chat real-time hota hai — thoda crisp, friendly, quick responses, taaki customer wait na kare. Email asynchronous hai — thoda zyada structured aur complete, kyunki har reply standalone samajh aani chahiye: greeting, issue summary, solution/steps, clear next action. Dono mein professional, empathetic, aur jargon-free rehna zaroori hai."

---

### Quick self-check

1. Resolved aur Closed status mein exact farak kya hai, aur confirm hone se pehle Closed kyun nahi karna chahiye?
2. Priority = Impact × Urgency — ek aisa example do jahan severity HIGH ho par priority LOW (aur ulta).
3. Response time aur Resolution time mein farak, aur kyun "fast acknowledge" itna important hai?
4. Aap L2/L3 ko escalate kar rahe ho — exactly kaun-kaun si 5 cheezein handoff mein paas karoge?
5. Incident, Service Request, Problem, Change — har ek ka ek-ek line real example do (alag-alag).
6. Remote session ka sabse important security rule kya hai, aur AnyDesk-related common scam kya hota hai?

---
