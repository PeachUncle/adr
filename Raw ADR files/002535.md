# Decision 004: Interest-Filtered, Elimination Skill Assessment Approach

**Date:** 2025-11-05  
**Status:** Accepted  
**Deciders:** Sadie Flick

## Context
Following Decision 001 to use the CareerOneStop API, the remaining challenge is to efficiently gather accurate skill aptitude data from a high school student within a five-minute window. We need a method that maps the student's experience to the 40 required O\*NET skill ratings (0-5) without asking 40 separate questions. The O\*NET skill levels are generally geared toward professional careers, requiring an adaptation for student experience.

## Options Considered

### 1. Simple Open-Ended LLM Synthesis
* **Pros:**
    * Fastest user experience (3-4 free-text questions).
    * Relies purely on the LLM's inference capabilities.
* **Cons:**
    * **Low Accuracy:** The LLM's 40-point rating would be highly speculative, lacking explicit user confirmation on key skills.
    * High reliance on **prompt engineering** to map vague student answers to specific skill anchors.
    * Does not account for the **high-school level scaling** required.

### 2. Full 40-Question Survey
* **Pros:**
    * Highest potential for raw rating accuracy.
    * Direct data collection for every required skill.
* **Cons:**
    * **Unacceptable User Experience:** Would take 10-15 minutes, violating the 5-minute constraint and leading to high drop-off rates.
    * User fatigue would lead to low-quality, rushed answers.

### 3. Interest-Filtered, Binary-Search Assessment
* **Pros:**
    * **Maximized User Effort Efficiency:** Filters the 40 skills down to 25-30 *relevant* skills based on the user's RAISEC interests first.
    * **Hybrid Approach:** Combines a quick visual panel for breadth (Step 2.2.1) with targeted LLM synthesis for depth/refinement (Step 2.2.2).
    * **Addresses Scaling:** Allows for the adaptation of O\*NET anchors into high school-appropriate **Task Statements** and a custom **Experience/Aptitude** 1-5 scale.
    * Reduces the LLM's task to *refining* scores, rather than guessing them from scratch.
* **Cons:**
    * Requires two distinct API/DB queries (one for Interests, one for Skills).
    * The **skill filtering logic** (removing the bottom 20-30% of skills) adds complexity to the code.

## Decision
We chose **Option 3: Interest-Filtered, Binary-Search Assessment**.

This approach intelligently uses the **RAISEC interests as a filter** to minimize the scope of the skills assessment, ensuring the user only spends time on skills relevant to jobs they'd find engaging. The combination of the **Task Statement Panel** and the **LLM-driven Confidence Probe** is the most robust way to gather 40 ratings quickly and accurately reflect high-school experience.

## Consequences
* **Positive:**
    * **Meets Time Constraint:** Assessment can be completed in approximately 4-5 minutes.
    * **Increased Relevance:** User focuses only on skills defining their likely career path.
    * **Accurate Scaling:** High school performance and experience are correctly mapped to the 1-5 professional skill rating.
* **Negative:**
    * Requires custom code for **Skill Triage/Filtering** (Step 1.4).
    * The LLM prompt design for **Refinement and Implication** (Step 2.2.2) is complex.

## Implementation Notes
* **When:** This assessment logic must be developed immediately following the core API integration.
* **Where:** The logic will be split between the back-end (Skill Triage/LLM Prompting) and the front-end UI (Task Statement Panel).
* **How:**
    1.  **Retrieve:** Fetch 100-150 interest-matched jobs and their 40-skill profiles.
    2.  **Filter:** Triage the 40 skills down to the top $\approx 25-30$ most frequently occurring skills.
    3.  **UI:** Present the remaining skills as **High School Task Statements** for initial scoring (4/5 for "Have done in the past", 2/3 for "Could do").
    4.  **LLM Refinement:** Use the LLM with a detailed, few-shot prompt (Decision 003) to adjust the high scores (keep as 4, 4 to 5, 4 to 3) based on the user's free-form narrative evidence.
    5.  **Submit:** Send the resulting 40-rating string to the CareerOneStop API to retrieve the top 30 occupations with their resulting skills profile.