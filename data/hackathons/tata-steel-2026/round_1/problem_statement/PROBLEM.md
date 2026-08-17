# Tata Steel AI Hackathon 2026 — Round 1 Problem Statement

**Scraped:** 2026-05-22 18:35 IST (via Jarvis browser-autopilot, HackerEarth logged-in session)
**Source URL:** https://www.hackerearth.com/challenges/competitive/tata-steel-ai-hackathon/machine-learning/fd-a5a6dcb2/

---

## 📌 Problem Title: **Defect Detection in Hot Rolling**

**Max Score:** 100
**Challenge Window:** 22 May 2026, 6:00 PM IST → 1 June 2026, 12:00 AM IST (9 days 5 hours remaining at scrape time)

---

## 🏭 Problem Background

In Hot Rolling Mills, one specific defect (referred to as the **"Alpha defect"**) is a critical quality challenge. This defect cannot be detected through the existing system because the coil remains under tension in the inspection zones.

Since it is not possible to detect Alpha defects inline, current quality control relies on sample observations at the recoiling line, where only a certain percentage of the total coils produced are inspected. In addition, manual inspection involves a significant delay, and defect generation cannot be identified and stopped in time.

Although the Alpha defect accounts for only a small percentage of the total production volume, it can still lead to **customer complaints and product downgrades**.

## 🎯 Task

Detect the occurrence of the Alpha defect during rolling to prevent customer complaints and reduce downgrades through proactive action.

During hot rolling, each stage has different process parameters that can contribute to the formation of the defect. Therefore, all stages must be considered to effectively detect the formation of Alpha defects.

---

## 📊 Dataset Description

| File | Dimensions |
|------|------------|
| `train.csv` | 1352 × 51 |
| `test.csv` | 339 × 50 |
| `sample_submission.csv` | 339 × 2 |

### Variable Description

| Column Name | Description |
|-------------|-------------|
| `CoilID` | Unique identifier for each coil |
| `X1–X49` | Process parameters across rolling, cooling, and down-coiler stages |
| `Y` | **Target variable:** Alpha defect occurrence (1 = Defect, 0 = No Defect) |

---

## 📏 Evaluation Metric (CRITICAL — NOT a leaderboard score!)

> A model which will have **0 false negative** and **less than 10% false positive** will be accepted.
>
> - **Recall = 100%**
> - **Precision > 90%**

This is a **hard pass/fail constraint**, NOT a soft maximization metric like F1 or accuracy.

## 📤 Submission Criteria

- CSV format only
- File size: **339 × 2** (CoilID, Y)
- Correct CoilID values per test file
- Correct column names per `sample_submission.csv`
- Plus: source code (.ipynb) + presentation (zip/tar archive)

## 📦 Dataset Download URL (presigned, expires in 1 hour from scrape)

https://he-s3-ap-south-1.s3.amazonaws.com/media/hackathon/tata-steel-ai-hackathon/fd-a5a6dcb2/169df72b552611f1.zip
(presigned signature valid until 2026-05-22T14:28:02Z UTC ≈ 19:58 IST)
