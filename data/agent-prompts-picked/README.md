# Jarvis-Picked Agent Prompts

> The **decision layer** on top of `data/agent-prompts/`. For every profession, prompt-picker-agent analyzed all candidates and selected the single best prompt for deployment.

**Last update:** 2026-05-11
**Picker:** `prompt-picker-agent`
**Criteria:** Output quality (40%) + 2026 trend relevance (35%) + Deployability (25%)
**Average scorecard:** ~32.6 / 35 across all picks

**📊 Status:** 79 professions, 79 deployment-ready picks

---

## How This Differs From `../agent-prompts/`

| `../agent-prompts/{slug}.md` | `agent-prompts-picked/{slug}.md` |
|------------------------------|-----------------------------------|
| 3-7 candidate prompts | **1 selected prompt** |
| Curator's annotations | **Picker's scorecard + reasoning** |
| Source-of-truth library | **Deployment-ready spec** |
| Browse for options | **Use this directly** |

## Deployment Workflow

1. Open `agent-prompts-picked/{profession}.md`
2. Copy the verbatim selected prompt
3. Read "Deployment Notes" — apply Jarvis adaptations (memory refs, Hinglish, safety overlays)
4. Save as `.claude/agents/{your-name}.md`
5. Done. ~5 minutes.

If you want to audit or pick differently:
- Read picked file → see runners-up + trade-offs
- Open library file → see all candidates

## Index — All 79 Picks

### 💻 Tech & Engineering (13)
| Profession | Winner | License |
|------------|--------|---------|
| [Software Developer](software-developer.md) | Aider Coding Agent | Apache-2.0 |
| [Web Designer](web-designer.md) | Vercel v0 (deploy as derivative) | Proprietary-leaked |
| [UI/UX Designer](ui-ux-designer.md) | VoltAgent Senior UI Designer | MIT |
| [Code Reviewer](code-reviewer.md) | Anthropic Cookbook PR Reviewer | MIT |
| [DevOps / SRE](devops-sre.md) | VoltAgent Senior SRE | MIT |
| [Backend Engineer](backend-engineer.md) | VoltAgent backend-developer | MIT |
| [Frontend Engineer](frontend-engineer.md) | VoltAgent frontend-developer | MIT |
| [Mobile Developer](mobile-developer.md) | VoltAgent mobile-developer (RN) | MIT |
| [Data Engineer](data-engineer.md) | VoltAgent data-engineer | MIT |
| [ML Engineer](ml-engineer.md) | VoltAgent ml-engineer | MIT |
| [Security Engineer](security-engineer.md) ⚠️ | VoltAgent security-engineer + safety wrapper | MIT |
| [QA / Test Engineer](qa-test-engineer.md) | VoltAgent test-automator | MIT |
| [Prompt Engineer](prompt-engineer.md) | Anthropic official metaprompt | MIT |

### ✍️ Content & Creative (15)
| Profession | Winner | License |
|------------|--------|---------|
| [Copywriter](copywriter.md) | AIDA-Structured Copy Generator | CC0 |
| [Content Writer](content-writer.md) | Long-form EEAT Blog Writer | CC0 |
| [SEO Specialist](seo-specialist.md) | Topic Cluster / Pillar-Page Planner | CC0 |
| [Social Media Manager](social-media-manager.md) | Social Media Strategy Skill | MIT |
| [Technical Writer](technical-writer.md) | Diátaxis Framework Doc Generator | CC0 / CC-BY-SA |
| [Video Script Writer](video-script-writer.md) | Short-Video Producer (open-notebooklm) | MIT |
| [YouTube Creator](youtube-creator.md) | Long-Form Hook + Chapter Architect | Anthropic public ref |
| [Podcast Host](podcast-host.md) | World-class Podcast Producer (open-notebooklm) | MIT |
| [Screenwriter](screenwriter.md) | Screenplay-Formatted Scene Writer | Composite original |
| [Novelist](novelist.md) | Chapter-by-Chapter Drafting Partner | Composite original |
| [Ghostwriter](ghostwriter.md) | vscode-ghostwriter two-step | Unknown (re-implement) |
| [Editor / Proofreader](editor-proofreader.md) | Developmental Editor (3-layer) | Composite original |
| [Brand Strategist](brand-strategist.md) | Brand Positioning Strategist (Moore) | Composite original |
| [Graphic Designer](graphic-designer.md) | Mini-Brief Designer (5-component) | Public blog (re-implement) |
| [Video Editor](video-editor.md) | Edit Brief & Shot List Generator (JSON) | Composite original |

### 💼 Business & Sales (13)
| Profession | Winner | License |
|------------|--------|---------|
| [Sales SDR](sales-sdr.md) | Consultative SDR (BANT) | MIT-equivalent |
| [Account Executive](account-executive.md) | Consultative AE Closer (MEDDIC) | Public web |
| [Customer Success Manager](customer-success-manager.md) | Churn-Risk Triage | Public web |
| [Executive Assistant](executive-assistant.md) ⭐ | Chief of Staff (briefing + triage) | MIT-equiv (35/35) |
| [Customer Support](customer-support.md) ⚠️ | Ticket Triage + Escalation Router (6 refusal rules) | MIT-equivalent |
| [Marketing Strategist](marketing-strategist.md) | Positioning Strategist (April Dunford) | MIT-equivalent |
| [Recruiter / HR](recruiter-hr.md) ⭐ | Interview Kit Generator | MIT-equiv (35/35) |
| [Product Manager](product-manager.md) | PRD Drafter | Kraftful free guide |
| [Growth Hacker](growth-hacker.md) | Funnel Drop-off Audit | Reforge-style |
| [Chief of Staff](chief-of-staff.md) | Weekly Brain-Dump Triage | The AI Break |
| [Pitch Deck Consultant](pitch-deck-consultant.md) | Narrative-First Story Architect | stunspot Medium |
| [Pricing Strategist](pricing-strategist.md) | Value-Based Price Point Calculator | Lakhyani Medium |
| [Business Analyst](business-analyst.md) | Requirements-to-User-Stories | Docsbot |

### 🔬 Knowledge Work (15)
| Profession | Winner | License |
|------------|--------|---------|
| [Research Analyst](research-analyst.md) | Anthropic Market Researcher | Apache 2.0 |
| [Data Analyst](data-analyst.md) | OpenAI Cookbook Data Analyst | MIT |
| [Financial Analyst](financial-analyst.md) ⚠️ | Anthropic Earnings Reviewer | Apache 2.0 |
| [Legal Assistant](legal-assistant.md) ⚠️ | IRAC Legal Text Summary (wrapped) | MIT |
| [Tutor (General)](tutor.md) | Socratic Tutor canonical (mustvlad mirror) | MIT |
| [Strategy Consultant](strategy-consultant.md) | McKinsey Senior Engagement Manager | Public web |
| [Statistician](statistician.md) | Rigorous A/B Test Architect | Public web |
| [Economist](economist.md) | Policy Impact Economist | Public web |
| [Bookkeeper / Accountant](bookkeeper-accountant.md) ⚠️ | Journal Entry Drafter | Public web |
| [Compliance Officer](compliance-officer.md) ⚠️ | General Compliance Officer | Public web |
| [Patent Analyst](patent-analyst.md) ⚠️ | ArcPrime Claims Drafter | Open-source GitHub |
| [Fact Checker](fact-checker.md) | Chain-of-Verification (CoVe) | Public web pattern |
| [Policy Analyst](policy-analyst.md) | Senior Public Policy Analyst | Public web |
| [Investigative Journalist](investigative-journalist.md) ⚠️ | Story Angle Generator | Public web |
| [Librarian / Research Asst](librarian-research-assistant.md) | Research Librarian | Public web |

### 🩺 Health & Wellness (8) — ALL with India-first crisis overlay
| Profession | Winner | License |
|------------|--------|---------|
| [Medical Scribe](medical-scribe.md) ⚠️ | Structured SOAP Scribe (Nabla-style) | CC0 |
| [Mental Health Companion](mental-health-companion.md) ⚠️ | Peer-Support Listener (MHFA) | CC0 |
| [Meditation Guide](meditation-guide.md) ⚠️ | Guided Meditation Script Generator (MBSR/MBCT) | CC0 |
| [Sleep Coach](sleep-coach.md) ⚠️ | Sleep Hygiene Coach (AASM + CBT-i) | CC0 |
| [ADHD Coach](adhd-coach.md) ⚠️ | ADHD-Adapted Productivity Coach (Barkley) | CC0 |
| [Parenting Coach](parenting-coach.md) ⚠️ | Practical Parenting Coach (Faber/Mazlish + Gottman) | CC0 |
| [Relationship Coach](relationship-coach.md) ⚠️ | Communication & Repair Coach (Gottman/NVC/EFT) | CC0 |
| [Productivity Coach](productivity-coach.md) | Practical Productivity Coach (GTD/Deep Work) | CC0 |

### 🎓 Education & Coaching (10)
| Profession | Winner | License |
|------------|--------|---------|
| [Math Tutor](math-tutor.md) | Khanmigo-Style Tutor | Custom-PD |
| [Coding Tutor](coding-tutor.md) | Socratic Code Tutor | Leaked GPT |
| [Language Tutor](language-tutor.md) | LanguageTutorGPT (Conversation + Flashcard) | MIT |
| [Writing Tutor](writing-tutor.md) | Socratic Writing Tutor | MIT |
| [Exam Prep Coach](exam-prep-coach.md) ⭐ | Adaptive Exam Drill Coach (35/35) | Custom-PD |
| [Public Speaking Coach](public-speaking-coach.md) | Speech Architect | Custom-PD |
| [Negotiation Coach](negotiation-coach.md) | Chris Voss Tactical Empathy Coach | Custom synthesis |
| [Interview Prep](interview-prep.md) | Structured Interview Coach | lxfater/Awesome-GPTs |
| [D&D Dungeon Master](dnd-dungeon-master.md) | Cinematic Solo DM | Custom-PD |
| [Creative Writing Coach](creative-writing-coach.md) | MFA-style Craft-Level Critique | Custom-PD |

### 🧘 Personal & Lifestyle (5) — Crisis overlay where applicable
| Profession | Winner | License |
|------------|--------|---------|
| [Life Coach](life-coach.md) ⚠️ | Goal-Strategy Life Coach (vduchew + scaffold) | CC0 |
| [Fitness Coach](fitness-coach.md) ⚠️ | FitEasy Single-Session Trainer | CC BY-SA 4.0 |
| [Travel Planner](travel-planner.md) | Jarvis Travel Wrapper | MIT + CC BY-SA 4.0 |
| [Nutritionist](nutritionist.md) ⚠️ | NutriGuru Consultation | CC BY-SA 4.0 |
| [Career / Resume Coach](career-coach.md) | Mr. Offer Resume Coach | CC BY-SA 4.0 |

---

## License Distribution of Winners

| License | Count | % | Commercial-safe? |
|---------|-------|---|------------------|
| CC0 | ~22 | 28% | ✅ Yes (public domain) |
| MIT / Apache 2.0 | ~28 | 35% | ✅ Yes |
| Composite-original / Custom-PD | ~14 | 18% | ✅ Yes (Jarvis-authored) |
| CC BY-SA 4.0 | 4 | 5% | ✅ Yes with attribution |
| Public web / Unknown | ~10 | 13% | ⚠️ Verify before commercial use |
| Proprietary-leaked | 2 | 2% | ❌ Deploy as derivative only |

**~86% of winners are commercial-safe** out of the box. Proprietary-leaked picks (web-designer, coding-tutor) are explicitly flagged "deploy as derivative" — use as inspiration, not direct redistribution.

## Notable Picker Patterns

### Sources that dominated
- **VoltAgent's awesome-claude-code-subagents** (MIT) — won 8 of 13 Tech picks. Strongest combo: Claude-Code-native YAML frontmatter + quantified SLO targets + 2026 vocab + MIT.
- **Anthropic Apache 2.0 prompts** — won 2 of the highest-leverage analytics picks (research-analyst, financial-analyst). MCP-native, prompt-injection defense, UNSOURCED tagging, stakeholder-review checkpoints.
- **gabrielchua/open-notebooklm** (MIT) — won both podcast-host and video-script-writer.
- **f/awesome-chatgpt-prompts** (CC0) — heavy presence in Content & Creative winners.

### Ethical / safety overrides applied
- **sales-sdr:** rejected manipulative "Salesperson" prompt despite higher canonical visibility → picked consultative BANT alternative
- **growth-hacker:** anti-dark-pattern guardrail carried forward
- **pitch-deck-consultant:** anti-fabrication on traction/market-size carried forward
- **security-engineer:** defensive-only safety preamble enforced (no offensive tooling); penetration-tester explicitly NOT picked due to dual-use risk
- **Health & Wellness × 8:** every pick wears Jarvis Safety Overlay (India-first crisis lines: iCall, Vandrevala, Tele-MANAS 14416, AASRA, CHILDLINE 1098, NCW 7827170170)

### Top 3 scorecard winners (35/35)
1. **executive-assistant** — Chief of Staff briefing + triage prompt
2. **recruiter-hr** — Interview Kit Generator with protected-attribute refusals
3. **exam-prep-coach** — Adaptive Exam Drill Coach (custom-PD)

## Re-picking

Re-run the picker when:
- New prompts added to `../agent-prompts/{slug}.md` by curator
- 6+ months elapsed (model capabilities evolve)
- A pick aged out (industry shifted)

Invoke: ask Jarvis "re-pick best prompt for {profession}" → delegates to prompt-picker-agent.

## Audit Trail

Every pick file shows:
- Verbatim selected prompt
- Why it won (rubric breakdown)
- Runners-up + trade-offs
- Deployment notes
- Full 7-criterion scorecard

Boss never has to take Jarvis's word for it — the reasoning is transparent on every choice.
