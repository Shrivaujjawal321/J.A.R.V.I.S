# Figma Guide — mySHIPR Carrier Console Build

Aap Figma pehli baar khol rahe ho, isliye ye guide zero-assumption hai on Figma vocabulary — lekin aap experienced developer ho, to har cheez ek baar clearly bata di jayegi, dobara nahi ghumaya jayega. Goal: script run karo, result inspect karo, team lead ko confidently defend karo.

Naming reference jo pura guide use karega (source: `figma-build/SPEC.md`):
- Pages: `01 Design System` (Foundations + Components sections), `02 Screens` (Desktop — 42 frames + Responsive — 84 frames), `03 Prototype` (flow & coverage board)
- Components: `Sidebar/Item`, `Button`, `Chip/Status`, `Table/Row`, `KPI Card`, etc.
- Variable collections: `Color` (34), `Radius` (7), `Spacing` (14)
- **Styles: 34 paint styles + 60 text styles** — ye do hi cheezein file ke nodes par actually *bound* hain, isliye demo inhi par karna hai (detail section 5 mein)

---

## 1. Figma ka 10-minute mental model

Figma web design tool hai, lekin uska structure code se kaafi milta hai — isko is tarah socho:

| Term | Ye kya hai | Yahan kyun matter karta hai |
|---|---|---|
| **Account** | Aapka login (email/Google) | Isi se aap file access aur team lead ke saath share karoge |
| **File** | Ek `.fig` project — jaise ek repo | Poora mySHIPR design ek hi file mein banega |
| **Page** | File ke andar tabs (folder jaisa) | File mein 3 pages hain — `01 Design System`, `02 Screens`, `03 Prototype` — sirf organize karne ke liye |
| **Section** | Ek page ke andar named area (canvas par grey label) | Starter plan sirf 3 pages deta hai, isliye Foundations/Components aur Desktop/Responsive ka bantwara Sections se kiya gaya hai |
| **Frame** | Fixed-size container jisme content hota hai | Har screen (Dashboard, Fleet, ...) ek Frame hai, jaise ek `<div>` fixed width ke saath |
| **Layer** | Har object — rectangle, text, group | Frame ke andar layers ka tree hota hai, left panel mein dikhta hai |
| **Component** (master) | Ek reusable block, ek jagah define hota hai | `Button`, `Chip/Status` jaise components — inko badlo, sab jagah update ho jata hai |
| **Instance** | Component ka copy jo actual screen par lagta hai | Instance master se linked rehta hai — detached copy nahi |
| **Auto Layout** | Figma ka flexbox equivalent | Padding/gap automatic maintain hota hai, resize par content sahi se rearrange hota hai — responsive requirement isi se poori hoti hai |
| **Constraints** | Object resize par kaise react kare (pin left/right/scale) | Responsive ke teeno widths (1440/900/375) mein sahi behave karne ke liye zaroori |
| **Variants** | Ek component ke multiple states/versions, ek group mein | `Button` ka `primary/secondary/danger` × `md/sm` × `default/hover/disabled` — sab ek hi component ke variants hain, alag components nahi |
| **Prototype** | Frames ke beech click-interactions | Sidebar item click → doosre screen par navigate — yehi team lead ne maanga hai |

---

## 2. Pehli baar Figma kholna

**Pehle 60-second pre-flight check karo — ye sabse pehle karo, kisi aur step se pehle:** `figma.com` par login karke ek blank design file bana lo aur usme kahin bhi kuch text type karke dekho ki save ho raha hai ya nahi. Ye isliye zaroori hai kyunki aapka Figma seat abhi Starter plan par "View" dikha raha hai — agar edit genuinely blocked hoga, to niche diye gaye teeno paths (A/B/C) mein se koi bhi kaam nahi karega, aur pehle seat/plan ko "Edit" access mein upgrade karwana padega. Ek baar text type/save ho jaaye, confirm ho gaya ki account edit kar sakta hai — tab aage badho.

1. **Sign in** — `figma.com` par jaakar apne email/Google account se login karo. Desktop app mein bhi same account se sign in hota hai.
2. **File kholo** — jis file mein plugin script run karna hai (ya nayi blank file `Blank canvas` se bana lo).
3. **Interface layout:**
   - **Top bar** — file ka naam, aur top-right corner mein `Share` button aur `Present` (play ▶ icon) button.
   - **Left panel** — top mein **Pages** list (yahan `01 Design System`, `02 Screens`, `03 Prototype` dikhega), niche **Layers** panel jo currently selected page/frame ke saare layers dikhata hai.
   - **Canvas** — beech mein, jahan actual design dikhta hai.
   - **Right panel** — jab kuch bhi selected ho, tab yahan uske properties dikhte hain (position, size, fill/colour, auto layout settings, aur agar `Prototype` tab select karo to interaction connections).
   - **Toolbar** — canvas ke top-center mein floating: move/select tool, frame tool, shape tool, text tool, comment tool.
4. **Zoom** — `Ctrl` (Windows/Linux) ya `Cmd` (Mac) dabaate hue mouse scroll karo. `Shift+1` = sab kuch zoom-to-fit, `Shift+0` = 100% zoom.
5. **Pan (canvas move karna)** — `Space` dabaakar drag karo, ya trackpad par two-finger scroll.
6. **Nested layer select karna** — kisi group/frame ke andar wale exact layer ko direct select karne ke liye `Ctrl+click` (Windows/Linux) ya `Cmd+click` (Mac) — bina baar-baar double-click karke andar jaaye.

Shortcuts jo aapko chahiye honge, bas itne hi:

| Shortcut | Kaam |
|---|---|
| `Ctrl/Cmd + scroll` | Zoom in/out |
| `Space + drag` | Canvas pan |
| `Ctrl/Cmd + click` | Nested layer direct select |
| `Shift + 1` | Zoom to fit |
| `Shift + 0` | Zoom 100% |
| `Esc` | Selection clear karo |

---

## 3. Plugin script kaise chalate hain

Teen tareeke hain script chalane ke. Priority order mein neeche diye hain — **Path A aapke liye recommended hai** kyunki wo Linux par bina kuch install kiye kaam karta hai.

### Path A (recommended) — Scripter, browser mein, koi install nahi

Ye ek **published Community plugin** hai jiska naam **Scripter** hai (author: rsms) — `https://www.figma.com/community/plugin/757836922707087381/scripter`. Published plugin hone ka matlab: ye Figma ke **browser version** mein hi chalta hai, isliye "desktop-app-only" aur "no official Linux app" — dono problems yahan apply hi nahi hoti. Scripter ek in-Figma code scratchpad deta hai jisme aap Figma Plugin API JavaScript paste karke run kar sakte ho — exactly wahi jo humari generated script ke liye chahiye.

1. `figma.com` par apni target file kholo (browser mein, koi desktop app nahi chahiye).
2. Plugin dhoondhne/run karne ka current path: left sidebar mein **`Tools`** tab click karo → filter icon se **"Plugin"** type filter karo → search bar mein `Scripter` type karo → result par click karke `Run` dabao. *(Ye Figma ka naya Tools-tab navigation hai; purane UI mein ye `Plugins` right-click canvas → `Plugins` submenu se, ya toolbar ke resources/puzzle-piece icon se milta tha — agar aapko `Tools` tab na dikhe, in dono jagah bhi dhoondh sakte ho, label version ke hisaab se differ kar sakta hai.)*
3. **Agar Scripter pehli baar use kar rahe ho** aur upar wala path na mile, to seedha plugin ka Community page kholo (link upar diya hai), aur us page par **`Open in…`** (kabhi-kabhi **`Try it out`** bhi dikh sakta hai naye/draft file ke liye) button click karo — ye aapko apni file mein plugin ke saath redirect kar dega.
4. Scripter ek code editor panel kholega (VS Code jaisi editor infrastructure use karta hai). Yahan dusre agent ne jo script generate ki hai, wo **poori paste** kar do.
5. Run karne ke liye editor ke toolbar mein **► button** click karo, ya shortcut `Ctrl+Return` (Windows/Linux) / `Cmd+Return` (Mac) dabao. Script ek baar top-se-bottom execute hogi aur poora design build kar degi.
6. Errors editor ke andar hi dikh jaate hain (console jaisa output area) — line number ke saath.
7. **Persistence:** Scripter aapki pasted script ko browser ke local storage (IndexedDB) mein automatically save kar leta hai, to next session mein wapas khulegi bina dobara paste kiye. Agar chaho to `Save to Figma File` button se script ko Figma file ke andar bhi save kar sakte ho, ya "Export all scripts" se zip download kar sakte ho.
8. Re-run karna ho (fix ke baad): sirf ► ya `Ctrl+Return` dobara dabao — script safe-to-rerun bani hai, purana output replace karegi.

### Path B — Unofficial Linux desktop app (agar Path A kisi wajah se kaam na kare)

Figma ka official desktop app sirf Mac aur Windows ke liye milta hai — Linux ke liye koi official build nahi hai. Agar aapko local `manifest.json`-based plugin development chahiye (Path A ke bajaye), to:
- Community-built unofficial desktop client — jaise `figma-linux` (Snap Store ya AppImage se install hota hai, official Windows build ko Linux-compatible banaya gaya hai)

*(Ye unofficial clients community-maintained hain, official Figma product nahi — plugin dev ke liye kaam karte hain, lekin agar koi cheez unexpected behave kare to isko variable rakhiye.)*

Is client ke andar steps same hain jo Path C mein diye hain — `Plugins → Development` menu se `New plugin…` ya `Import plugin from manifest…`.

### Path C — Windows/Mac machine, official desktop app

Agar Path A aur B dono unavailable hon (e.g. koi Windows/Mac machine mil jaaye, ya Linux client trust na karna ho), to official desktop app se:

1. Target file kholo desktop app mein.
2. Top-left **Figma menu** → `Plugins` → `Development` → `New plugin…` (agar khali se plugin banani ho) ya `Import plugin from manifest…` (agar dusre agent ne pehle se ek `manifest.json` + code file generate kar di ho aur aapko sirf point karna ho — *label version ke hisaab se thoda differ ho sakta hai, "Import plugin from manifest…" ya "Import new plugin from manifest…" dono dekhe gaye hain*).
3. **Agar `New plugin…` chuna:** Figma ek template chooser dikhayega (e.g. "Run once") — is template ko select karo, plugin ko naam do (e.g. `mySHIPR Build`). Figma local folder mein `manifest.json` + `code.js` bana dega aur `code.js` file open karega ek text editor mein.
4. Us `code.js` ka **poora content delete karke**, dusre agent ne jo script generate ki hai, wo **paste** kar do. File **save** karo.
5. **Agar `Import plugin from manifest…` chuna:** file picker khulega, us `manifest.json` ko select karo jo already generated script ke saath aayi thi.
6. Plugin ab `Plugins → Development` submenu mein apne naam se list ho jayega. Run karne ke liye: `Plugins` → `Development` → `<plugin ka naam>`. Ye script ek baar top-se-bottom execute hogi aur poora design build kar degi.
7. **Agar script beech mein error de:** `Plugins` → `Development` → `Open Console…` (shortcut: Windows/Linux par `Ctrl+Shift+I`, Mac par `Cmd+Option+I`) — ye developer console kholega. Error message + line number wahan dikhega, wo copy karke share karo taaki script fix ho sake.
8. Script safe-to-rerun bani hai (SPEC ke mutabik) — agar dobara run karna ho (fix ke baad), same menu item se dobara run kar sakte ho, ye purana output delete karke replace karegi, duplicate nahi banayegi.

---

## 4. Script chalane ke baad kya dikhega

Left panel ke top mein **Pages** list mein ye **3 pages** dikhengi. (Figma ke Starter plan mein ek file mein 3 se zyada pages ban hi nahi sakte, isliye jo pehle 5 alag pages the wo ab 3 pages ke andar **Sections** ban gaye hain — Section ka naam canvas par grey label ki tarah dikhta hai.)

| Page | Kya hoga usme |
|---|---|
| `01 Design System` | Do sections. **Foundations** — 34 colour + 7 radius + 14 spacing variables ke swatches, **34 paint styles**, aur **60 text styles** (`Display/H1`, `Body/Base`, `Body/Small`, `Mono/Code`, etc. — type ladder pehle sirf 7 styles ka tha, ab console ke saare font sizes aur weights cover karta hai). **Components** — master components apne variants ke saath: `Sidebar/Item`, `Button`, `Chip/Status`, `Table/Row`, `KPI Card`, `Banner`, `Field`, `Panel`, `EmptyState`, `HOS Bar`, etc. Exact count ke liye canvas par `Components` section dekh lo ya `03 Prototype` board ke stat cards padh lo — library abhi actively expand ho rahi hai, isliye guide mein number hardcode nahi kiya gaya. |
| `02 Screens` | Do sections. **Desktop** — **saare 42 screens**, 1440px width. Pehli row mein 12 sidebar-level screens (`01`–`12`), uske neeche har section ke sub-screens (`02.2` Fleet — Active Vehicles se `12.10` Settings — Capacity tak). Frame ka naam hi address hai: `12.10` matlab section 12 ka 10th sub-screen. **Responsive** — **saare 42 screens** ka tablet (900px) aur mobile (375px) version, yaani 84 frames. Har screen ke upar uska naam label ke roop mein hai; tablet left, mobile uske right. Prototype ki saari click-navigation **isi page ke Desktop section par** set hai. |
| `03 Prototype` | Ek documentation board — `Prototype - flow & coverage`. Isme stat cards (**42 desktop screens, 84 responsive frames, 756 sidebar interactions**, 34 paint styles, 60 text styles, 55 design tokens, aur style-bound nodes ka count), 42-screen ka flow map, aur explanatory notes hain. Team lead ko ye page pehle dikhana — poori file ek nazar mein samajh aa jayegi. *(Board ke component/variant wale do cards build script se aate hain — component library expand ho rahi hai, to agar wo cards thode purane lagein to canvas ki actual library authoritative hai.)* |

**Component + variants inspect karna:**
1. `01 Design System` page kholo, `Components` section tak scroll karo.
2. Kisi component (jaise `Button`) ko select karo — right panel ke top mein uske variant properties (`kind`, `size`, `state`) dropdown ke roop mein dikhenge, jinhe toggle karke alag-alag variant preview kar sakte ho.
3. Ya poora component-set frame select karo (jisme sab variants grid mein laid out hote hain) — sab states ek saath visually dekhne ke liye ye zyada useful hai.

**Prototype test karna:**
1. `02 Screens` page kholo, `Desktop` section mein `01 Dashboard — Overview` select karo (yahi flow ka starting frame hai).
2. Top-right `Present` button (▶ play icon) click karo — Presentation view khulega.
3. Sidebar ke kisi bhi item par click karo — matching screen par navigate hoga. **Sab 756 controls live hain.** Har screen par 12 top-level nav items hain, plus us section ke saare sub-items (jaise Fleet par 8, Settings par 10) — aur teeno level wired hain, to Fleet → "Devices & ELD" bhi seedha khulta hai. 702 page-to-page navigation hain; baaki 54 wo control hain jis screen par aap already ho — Figma apne hi frame par navigate karne nahi deta, isliye wo Scroll To karte hain aur screen ko wapas header par le aate hain (standard active-item behaviour).
4. Exit karne ke liye `Esc` ya presentation tab band karo.

**Responsive check karna:**
1. `02 Screens` page par `Responsive` section tak scroll karo.
2. Teen widths (1440 `Desktop` section mein, 900 aur 375 yahan) side-by-side dekho — ab ye har screen ke liye maujood hai, sirf teen ke liye nahi — confirm karo ki 900px par hamburger aa gaya hai (rail hat gayi), grids 2-up ho gaye hain, aur 375px par single column + stacked KPI cards hain. Har frame ke upar uska naam label ke roop mein likha hai.
3. **Tables mobile par:** 375px frame mein kisi table ko horizontally scroll karke dekho — table ab 600px readable minimum par rakhi gayi hai aur wrapper ke andar scroll karti hai, exactly jaise console ka `overflow-x:auto`. Pehle ye clip ho jaati thi (columns chup-chaap kat jaate the) — wo fix ho chuka hai.
4. **Ek honest disclaimer yaad rakho:** ye teen widths **teen alag-alag built layouts** hain (har breakpoint ka apna frame), yaani jo dikh raha hai wo real per-breakpoint design hai. Lekin frame ka edge pakadkar live drag karoge to KPI/pulse/column widths abhi reflow nahi karengi — wo build-time pixel widths par set hain. Isliye demo mein **teeno frames side-by-side dikhao**, live drag mat karo.

---

## 5. Team lead ko kya aur kaise dikhana hai

**File link share karna:**
1. Top-right `Share` button click karo.
2. Dialog mein link-access dropdown milega — `Anyone with the link` chuno, phir uske aage `can view` (Viewer) ya `can edit` (Editor) select karo. Review ke liye Viewer kaafi hai; agar team lead ko khud edit karna ho to Editor do.
3. *(Agar organisation ke sharing permissions admin-restricted hain, to ye options limited dikh sakte hain — us case mein specific email invite karna padega, dropdown se dikh jayega.)*

**Prototype-specific link share karna:**
1. Starting frame (`02 Screens` → `Desktop` → `01 Dashboard — Overview`) par `Present` (▶) click karke prototype khud pehle test karo.
2. Us presentation view ka URL copy karo — ye link direct interactive prototype mode mein khulega, edit canvas mein nahi.
3. *(Kuch Figma versions mein `Share` dialog ke andar hi `Design` aur `Prototype` do tabs milte hain link copy karne ke liye — agar dikhe to wahi seedha use kar sakte ho.)*

**Har requirement ke liye kya bolna/dikhana hai:**

| Requirement | Kahan point karo | Kya bolo |
|---|---|---|
| **Pixel perfect / tokens** | `01 Design System` → `Foundations` (34 paint styles + 60 text styles ki list) → phir kisi screen par ek panel/chip/heading select karke right panel | "34 colour values seedha console ke CSS `:root` se li gayi hain — 1:1, koi guess nahi. Aur ye sirf swatch page par nahi rakhi: file ke **876 fills aur 2,160 text nodes actually in styles se bound hain**. Main koi bhi panel ya chip select karta hoon — right panel mein `Fill` ke saamne raw hex nahi, **style ka naam** dikhega; text select karunga to Typography section mein text style ka naam dikhega." |
| **Token ek jagah badlo, sab jagah badle** | Left panel → `Local styles` list (ya kisi bound node par style name → `Edit style`) | "Ye style-level binding hai, isliye style ki value edit karte hi wo har us node par update ho jaati hai jo us style ko use kar raha hai. Demo ke liye ek paint style ka colour badalta hoon — masters aur screens dono par ek saath change dikhega." **Sirf ek chhoti honesty:** har akela decorative fill bound nahi hai, kuch one-off values abhi raw hex hain — agar poocha jaaye to seedha bol dena, phir bhi bulk (876 fills / 2,160 text nodes) bound hai. |
| **Responsive** | `02 Screens` → `Responsive` section — 84 frames, har screen 900 aur 375 par (1440 `Desktop` section mein) | "Har screen ke teeno breakpoints alag-alag build kiye gaye hain — 42 desktop + 42 tablet + 42 mobile. Mobile par tables 600px readable minimum ke saath horizontally scroll karti hain, console ke `overflow-x:auto` jaisa." *(Live frame-drag karke reflow mat dikhana — dekho section 4, point 4.)* |
| **Component based** | `01 Design System` → `Components` section + kisi screen par ek `Button` / `Chip/Status` / `KPI Card` instance select karke | "Screens component instances se assemble hui hain — instance select karo to right panel top par master ka naam dikhega, detached copy nahi. Master badlunga to sabhi screens par reflect hoga — abhi `Button` par demo karta hoon." *(Demo `Button` / `Chip/Status` / `Table/Row` par karo. **Sidebar rail par mat karna** — wo abhi har frame par raw copy hai, instance nahi; niche `Known gaps` mein iska honest jawab likha hai.)* |
| **TMS based design** | Koi bhi dense screen (e.g. Loads — Tenders, Fleet — All Vehicles) | "Status chips, dense tables, HOS bar — ye conventions real mySHIPR console se match karte hain, koi generic SaaS template nahi." |
| **Clickable prototype** | `Present` mode, start `02 Screens` → `Desktop` → Dashboard | Sidebar items par live click karke dikhao — top-level aur sub-items dono. "Console ke saare 42 screens bane hain aur sidebar ke 756 controls wired hain — 702 navigation, aur active screen wala control Scroll To, kyunki Figma apne hi frame par navigate allow nahi karta." |

---

## 6. Agar team lead changes maange

**Aap khud safely UI mein kar sakte ho:**

1. **Colour change (sahi tareeka — style edit karo, node nahi)** — object select karo → right panel mein `Fill` ke saamne **style ka naam** dikhega (raw hex nahi, kyunki node bound hai). Us naam par click → `Edit style` → hex badlo. Ye us style ko use karne wale **har node par** update ho jayega — component masters aur screen frames dono par. Agar aap seedha node ka fill overwrite karoge to wo node style se **detach** ho jayega aur agli baar style-level change usko miss kar degi — isliye hamesha style edit karo.
   *(Same logic text ke liye: text layer select → right panel `Typography` mein text style ka naam → wahan se edit karo, individual size/weight override mat karo.)*
2. **Text edit** — text layer par seedha **double-click** karo canvas par → naya text type karo → `Esc` ya kahin aur click karke confirm karo.
3. **Component instance swap** — instance select karo → right panel ke top mein current component ka naam + swap icon (do overlapping squares jaisa) dikhega → us par click karo → list se doosra variant/component chuno.
4. **Frame move karna** — frame ka title (frame ke upar naam) ya Layers panel se select karo → canvas par drag karo, ya arrow keys se nudge karo (`Shift+arrow` bade steps ke liye).

**Ye khud mat karo, iske liye script regenerate karwao:**
- **Auto Layout restructure karna** (direction, padding, nesting order badalna) — isse 42 screens par instances break ho sakte hain jo us component ko use kar rahe hain.
- **Component rebuild ya rename karna** — SPEC ke naming contract (`Sidebar/Item`, `Button`, etc.) par future steps (frontend mapping, prototype wiring) depend karte hain; hath se rename karne se ye chain toot sakti hai.
- **Naye variants add karna** — existing variant properties prototype wiring aur naming se linked hain; ad-hoc addition state ko desync kar sakta hai.
- **Prototype connections bulk mein rewire karna** — ek-do link nudge karna theek hai, lekin sab 42 screens par dobara wire karna (756 links) hath se risky hai; script rerun se consistent hoga.

---

## 7. Known gaps — agar poocha jaye to

File ka adversarial audit ho chuka hai (7 critics). Bahut kuch fix ho gaya — styles ab genuinely bound hain, Dashboard ke saare 9 panels aa gaye, Reports ke 5, mobile tables scroll karti hain. Lekin kuch cheezein **abhi bhi genuinely open hain**. Inko chhupana mat — team lead agar in par ungli rakhe aur aapke paas jawab na ho to credibility jaati hai. Ek-ek line ka jawab niche ready hai:

| Gap (honest) | Ek line jo aap bol sakte ho |
|---|---|
| **Koi overlay/modal frame nahi hai** — assignment wizard, record drawers, create/edit forms, bulk-upload report, invite/create-role, error states — kuch bhi nahi bana. Client review ka bada hissa yahi tha. | "Ye phase-1 hai — 42 base screens + navigation. Overlays, wizards aur error states phase-2 mein aa rahe hain; console mein wo mechanisms already maujood hain, Figma mein abhi draw nahi hue." |
| **Prototype sirf desktop par hai.** Responsive frames par hamburger *draw* to hai, par wo kuch kholta nahi — off-canvas drawer, scrim aur wiring missing hai. | "Prototype wiring desktop rail par complete hai (756 controls). Mobile drawer ka interaction abhi wired nahi — wo agla step hai, hamburger placeholder ke taur par draw kiya hua hai." |
| **Sidebar rail component instance nahi hai** — `Sidebar/Root` component exist karta hai par 0 baar use hua; rail 42 frames par raw copy hai. | "Rail abhi generator se copy hoti hai, component instance nahi — isliye 'master badlo, sab jagah badle' demo main `Button`/`Chip` par karta hoon. Rail ko instance banana ek script pass ka kaam hai." |
| **Responsive genuinely fluid nahi hai** — KPI/pulse/column widths build-time pixels hain, mobile par desktop ki padding/type density hai, aur `KV Row` 375px par bhi 190px key column rakhta hai. | "Teeno breakpoints alag-alag design kiye gaye hain, isliye jo dikh raha hai wo sahi hai — lekin frame ko live drag karke reflow nahi dikhega, aur mobile density pass abhi baaki hai." |
| **Kuch screens par content missing hai** — Vehicle Types par truck-types grid nahi, Notification Preferences ka Email/SMS/Push checkbox matrix nahi (sirf labels bache hain). | "Ye do screens knowingly incomplete hain — audit mein pakde gaye, next generator pass mein add ho rahe hain." |
| **Note tones flatten ho gaye** — console mein amber = warning, blue = info, red = blocking; Figma mein zyadatar blue ho gaya, ek hi note kahin amber kahin blue. | "Tone mapping generator-level bug hai, per-screen galti nahi — ek fix se saare frames theek ho jayenge." |
| **Table headers ka case galat hai** — `ETA → Eta`, `CDL → Cdl`, `VIN → Vin`, `AWB → Awb`. Console CSS `text-transform:uppercase` hai. | "Sentence-case helper acronyms ko mangle kar raha hai — ye ek-line fix hai, 34 tables par ek saath lagega." |
| **Table detail drop/invent hua hai** — kuch `srcline` legend chips gayab hain (aur do-teen jagah invent ho gaye), Detention/Earnings ke row-action buttons missing hain, 5 tables par pager laga hai jahan console paginate hi nahi karta, aur do screens par filter chips missing hain. | "Traceability chips aur row actions ka gap real hai — main ise cosmetic nahi maanta, requirement-tracing issue hai; correction list ban chuki hai." |
| **Token layer 100% console se derive nahi hai** — 34 colours 1:1 match karte hain, lekin 14 spacing + kuch radius tokens Figma-side convenience hain (console ke `:root` mein spacing vars hain hi nahi), aur ~20 console colours ka abhi koi token nahi hai. | "Colour parity exact hai — 34 ke 34 identical hex. Spacing tokens Figma-side scale hai taaki design consistent rahe; jo colours abhi cover nahi hue wo token list mein add ho rahe hain." |
| **Gradients flatten ho gaye** — sabhi 6 gradients single-stop ban gaye, brand mark included. | "Gradient stops generator ne collapse kar diye — brand mark pe pehle fix ho raha hai, kyunki wahi sabse pehle zoom hota hai." |
| **Per-screen content drift** — kuch screens par data console se thoda hat gaya (Tenders par extra panels, Messages chat ke bajaye text blob, POD par photo-evidence block missing, Capacity ka ek category gayab, Company Profile ka lock badge Button bana hua). | "Content parity ka ek line-by-line diff nikal chuka hai — ye known list hai, invent kiya hua kuch bhi defend nahi kar raha." |
| **Kuch defects Figma ke nahi, console/data ke hain** — dispatch gate ki 4 alag definitions, truck double-booking, SOS driver "Dispatchable" dikhna, hardcoded margin/on-time numbers. Figma ne inhe wafadari se copy kiya hai. | "Ye design bug nahi, console ki business-logic bug hain — Figma ne wahi dikhaya jo console dikhata hai. Inki alag list hai aur wo code-side fix hongi." |

**Ek cheez jispe aap confidently push back kar sakte ho:** agar koi kahe "Settings ke sub-items miss hain / kuch screens unreachable hain" — ye galat hai. Live file `subscreens/_base.js` se bani hai jisme saare 10 Settings subs hain; verification output `frames=42`, wiring `missing=0` deta hai. Ye claim ek purane builder file ko padhne se aaya tha.

---

## 8. Aage kya

Ye Figma file frontend build ka source-of-truth banegi — pehle frontend (React/Next), phir uske upar backend. Component-based design isliye frontend step ko fast karta hai kyunki Figma components almost 1:1 React components mein map hote hain: `Sidebar/Item` → `SidebarItem` component, `Button` variants (`kind`/`size`/`state`) → React props, `Chip/Status` tones → status enum — same naming, same states, seedha translation, guesswork nahi.
