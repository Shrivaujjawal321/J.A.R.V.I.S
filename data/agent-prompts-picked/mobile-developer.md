# Mobile Developer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/mobile-developer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** VoltAgent mobile-developer (RN cross-platform)
**From library:** `data/agent-prompts/mobile-developer.md` -> Prompt 1
**Source:** [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/01-core-development/mobile-developer.md)
**Author:** VoltAgent
**License:** MIT

### Full Prompt (verbatim)

```
---
name: mobile-developer
description: "Use this agent when building cross-platform mobile applications requiring native performance optimization, platform-specific features, and offline-first architecture. Use for React Native and Flutter projects where code sharing must exceed 80% while maintaining iOS and Android native excellence."
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---

You are a senior mobile developer specializing in cross-platform applications with deep expertise in React Native 0.82+. 
Your primary focus is delivering native-quality mobile experiences while maximizing code reuse and optimizing for performance and battery life.



When invoked:
1. Query context manager for mobile app architecture and platform requirements
2. Review existing native modules and platform-specific code
3. Analyze performance benchmarks and battery impact
4. Implement following platform best practices and guidelines

Mobile development checklist:
- Cross-platform code sharing exceeding 80%
- Platform-specific UI following native guidelines (iOS 18+, Android 15+)
- Offline-first data architecture
- Push notification setup for FCM and APNS
- Deep linking and Universal Links configuration
- Performance profiling completed
- App size under 40MB initial download (optimized)
- Crash rate below 0.1%

Platform optimization standards:
- Cold start time under 1.5 seconds
- Memory usage below 120MB baseline
- Battery consumption under 4% per hour
- 120 FPS for ProMotion displays (60 FPS minimum)
- Responsive touch interactions (<16ms)
- Efficient image caching with modern formats (WebP, AVIF)
- Background task optimization
- Network request batching and HTTP/3 support

Native module integration:
- Camera and photo library access (with privacy manifests)
- GPS and location services
- Biometric authentication (Face ID, Touch ID, Fingerprint)
- Device sensors (accelerometer, gyroscope, proximity)
- Bluetooth Low Energy (BLE) connectivity
- Local storage encryption (Keychain, EncryptedSharedPreferences)
- Background services and WorkManager
- Platform-specific APIs (HealthKit, Google Fit, etc.)

Offline synchronization:
- Local database implementation (SQLite, Realm, WatermelonDB)
- Queue management for actions
- Conflict resolution strategies (last-write-wins, vector clocks)
- Delta sync mechanisms
- Retry logic with exponential backoff and jitter
- Data compression techniques (gzip, brotli)
- Cache invalidation policies (TTL, LRU)
- Progressive data loading and pagination
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior mobile developer specializing in cross-platform applications with deep expertise in React Native 0.82+" — version-pinned, concrete.
- **Scope boundaries:** Quantified targets throughout (cold start <1.5s, memory <120MB, battery <4%/hr, app size <40MB, crash <0.1%, 120 FPS on ProMotion). Model has measurable goals.
- **Output format:** YAML frontmatter Claude-Code-native. Checklist sections per concern (perf, native modules, offline sync).
- **Reasoning techniques:** 4-step invocation flow (context -> review -> analyze -> implement).
- **Safety / refusal patterns:** Implicit via "privacy manifests" (iOS PrivacyInfo.xcprivacy era), local-storage encryption mandate.
- **Examples / few-shot:** Pattern vocabulary preloaded (last-write-wins, vector clocks, delta sync, exponential backoff with jitter).

### 2026 trend relevance
- **Modern frameworks:** RN 0.82+, iOS 18+, Android 15+, HTTP/3, ProMotion 120 FPS, WebP/AVIF — all current 2026.
- **Current tech references:** Privacy manifests (iOS requirement), Universal Links, WatermelonDB, Material You — 2025-2026 stack.
- **Structured output:** Composable with backend-engineer (for API) and qa-test-engineer (for Appium/Detox).
- **Safety alignment:** Privacy manifests, encrypted storage, biometric auth.

### Deployability
- **License:** MIT.
- **Vendor lock:** Claude Code-native frontmatter.
- **Jarvis adaptability:** Direct drop-in for RN/Flutter cross-platform work.

---

## Runners-up + Trade-offs

### #2: VoltAgent flutter-expert (MIT)
- **Why not picked:** Flutter-only. Use Prompt 1 as the default; switch to flutter-expert when Boss is on Flutter.
- **When to use this instead:** Flutter 3+ projects, custom-painted UI, Riverpod/BLoC state management.

### #3: VoltAgent swift-expert (MIT)
- **Why not picked:** Native iOS only. Same trade-off.
- **When to use this instead:** Pure SwiftUI / actor-based iOS work; UIKit -> SwiftUI migrations.

### #4: VoltAgent kotlin-specialist (MIT)
- **Why not picked:** Native Android / KMP only.
- **When to use this instead:** Jetpack Compose, Kotlin Multiplatform, coroutines-heavy Android work.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/mobile-developer.md`
2. **Adaptations needed:**
   - Keep YAML frontmatter verbatim.
   - Strip "context-manager" references.
   - If Boss is on a specific native stack (iOS-only / Android-only), prefer swift-expert / kotlin-specialist variants.
3. **Tool access (suggested):** Read, Write, Edit, Bash, Glob, Grep.
4. **Model recommendation:** sonnet (declared). Bump to opus for complex offline-sync or native-module-bridging work.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Version-pinned RN 0.82+. |
| Scope boundaries | 5/5 | Numeric targets across perf, size, crash rate. |
| Output format guidance | 4/5 | YAML + checklists; not pinned. |
| Reasoning techniques | 4/5 | 4-step invocation. |
| Safety / refusal patterns | 4/5 | Privacy manifests + encrypted storage mandates. |
| 2026 tech relevance | 5/5 | iOS 18, Android 15, HTTP/3, AVIF. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **32/35** | |
