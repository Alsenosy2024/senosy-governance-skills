---
name: msu-thesis
description: >
  Full doctoral dissertation review skill — performs deep academic examination of thesis chapters against MSU Postgraduate Centre guidelines and general doctoral quality standards. Use this skill whenever a user uploads thesis chapters (Chapter 1, 2, or 3) and asks for review, feedback, checking, or assessment — even if they say "just check the structure" or "quick review." The skill performs two-layer analysis in parallel: (1) structural compliance mapping against the MSU PGC template, and (2) substantive content quality at examiner level (argument logic, theoretical depth, measurement validity, internal consistency, citation accuracy, cross-chapter coherence). Always produces a formatted output covering both layers. Trigger on: dissertation chapters uploaded, thesis review requested, academic feedback needed, "check my chapter," "review my thesis," "مراجعة رسالة," "تشيك على الشابتر," or any variant. Always respond in English for academic review reports; use Arabic only for quick conversational clarifications.
---

# MSU Thesis Examiner Skill

Deep academic review of doctoral dissertation chapters against MSU PGC guidelines and doctoral quality standards. Produces examiner-level reports covering structural compliance and content quality simultaneously.

---

## Context

Developed for reviewing dissertations submitted to the Graduate School of Management, Postgraduate Centre, Management and Science University (MSU Malaysia). The MSU PGC thesis guidelines specify a fixed section structure for each chapter. The skill checks compliance with that structure AND evaluates content quality at the level a viva examiner would apply.

---

## MSU Required Structure

### Chapter 1
| Section | Title | Notes |
|---|---|---|
| 1.1 | Introduction | Overview of the chapter, not "Chapter Overview" |
| 1.2 | Background of Study | Must have two subsections |
| 1.2.1 | Background of (Focus Area) | Historical and conceptual background of the research topic |
| 1.2.2 | Background of (Industry/Sector) | Historical background of the industry/sector studied |
| 1.3 | Current Situation of Study | Must have two subsections |
| 1.3.1 | Current Situation of Focus Area in Context | Present-day state with data |
| 1.3.2 | Current Situation of Industry/Sector in Context | Present-day state with data |
| 1.4 | Problem Statement | The specific gap or problem motivating the study |
| 1.5 | Research Objectives | Measurable, action-verb objectives |
| 1.6 | Research Questions | Mapped 1:1 to objectives |
| 1.7 | Significance of Study | Theoretical and practical significance |
| 1.8 | Scope of Research | Geographic, sectoral, methodological boundaries |
| 1.9 | Organization of Study | Map of all thesis chapters |
| 1.10 | Definition of Terms | Key constructs operationally defined |
| 1.11 | Chapter Summary | Summary of Chapter 1 content |

**Common Chapter 1 errors:**
- Section 1.3 (Current Situation) entirely absent — most common critical error
- Section 1.9 (Organization of Study) absent
- Scope buried inside Significance as a subsection
- Cascading numbering errors when 1.3 is missing
- Operational definitions that embed the IV into mediating/dependent variable definitions
- "Develop a framework" as an objective when the study actually tests a pre-specified model
- Causal language in RQs when study is cross-sectional

---

### Chapter 2
| Section | Title | Notes |
|---|---|---|
| 2.1 | Introduction | Chapter structure and purpose |
| 2.2 | Historical Literature Review | NOT a background section — must trace intellectual development |
| 2.2.1 | History of Focus Area | From earliest scholarship to present |
| 2.2.2 | Recent Issues and Development of Focus Area | Last 5–10 years |
| 2.2.3 | History of Industry/Sector | Historical development of the studied sector |
| 2.2.4 | Recent Issues and Development of Industry/Sector | Current state with data |
| 2.2.5 | Empirical and Theoretical Literature Gaps | Specific, precise, defensible gaps |
| 2.3 | Empirical Review | Synthesis of empirical studies |
| 2.3.1 | Definitions and Literature Review per Variable | One subsection per variable with dimensions |
| 2.3.2 | Justification of Relationships Between Variables | Per-hypothesis justification subsections |
| 2.4 | Empirical Literature Matrix | Table of studies with methodology, findings, limitations, relevance |
| 2.5 | Summary of Empirical Review | Closes empirical discussion |
| 2.6 | Theoretical Review | NOT placed before empirical unless justified |
| 2.6.1 | History, Nature, Contents of Each Theory/Model | Intellectual history required |
| 2.6.2 | Theoretical Development, Gaps and Expectations | Evolution and limitations of framework |
| 2.6.3 | Theoretical Justifications and Relationships | Framework applied to study variables |
| 2.7 | Theoretical Literature Matrix | Separate from empirical matrix |
| 2.8 | Summary of Theoretical Review | Closes theoretical discussion |
| 2.9 | Chapter Summary | Full chapter summary leading to Chapter 3 |

**Common Chapter 2 errors:**
- Historical Literature Review replaced with background (continuation of Chapter 1)
- Theory placed before empirical review without justification (reverse of required order)
- No per-variable subsections (2.3.1.1, 2.3.1.2, etc.)
- No relationship justification section (2.3.2)
- Empirical review as rejection catalogue rather than synthesis
- Gaps overstated and contradicted by cited studies
- Forward references to Chapter 3 (logic inversion)
- Missing Theoretical Literature Matrix
- Framework chosen by dismissal of alternatives, not comparative argument
- Mediation role asserted without empirical precedent at the project/context level

---

### Chapter 3
| Section | Title | Notes |
|---|---|---|
| 3.1 | Introduction | Overview of chapter |
| 3.2 | Variables | All study constructs introduced |
| 3.2.1 | Conceptual Framework | Figure and description |
| 3.2.2 | Research Hypotheses | All hypotheses with linkage subsections |
| 3.3 | Research Design Process | Overall design |
| 3.3.1 | Research Approach | Quantitative / qualitative / mixed |
| 3.3.2 | Research Paradigm | Positivist / interpretivist / etc. |
| 3.3.3 | Research Method | Survey / experiment / case study / etc. |
| 3.3.4 | Justification of Research Method | (Optional) |
| 3.3.5 | Type of Data | Primary / secondary / mixed |
| 3.4 | Sampling Design Process | |
| 3.4.1 | Study Population | |
| 3.4.2 | Unit of Analysis | |
| 3.4.3 | Sampling Design | |
| 3.4.4 | Sampling Frame | Separate from design |
| 3.4.5 | Sampling Technique | |
| 3.4.6 | Justification for Sampling Technique | (Optional) |
| 3.4.7 | Sample Size | Must be formally justified |
| 3.5 | Instrument Development Process | |
| 3.5.1 | Instrument Development | Source of items |
| 3.5.2 | Pre-Test and Item Modification | |
| 3.5.3 | Reliability of Questionnaire | |
| 3.5.4 | Validity of Measurement Scale | |
| 3.5.5 | Instrumentation of Measurement Items | Full item table |
| 3.6 | Data Analysis Process | |
| 3.6.1 | Data Collection | |
| 3.6.2 | Data Coding | |
| 3.6.3 | Data Analysis | |
| 3.6.4 | Statistical Technique | |
| 3.6.5 | Justification for Statistical Technique | (Optional) |
| **3.6.6** | **Ethical Considerations** | **Inside 3.6 — not standalone** |
| 3.7 | Findings from the Pilot Study | Actual results — not future plans |
| 3.7.1 | Demographic Information of Pilot Study | |
| 3.7.2 | Company Information of Pilot Study | (Optional) |
| 3.7.3 | Reliability of the Measurements | Actual Cronbach's alpha values |
| 3.8 | Chapter Summary | |

**Common Chapter 3 errors:**
- Extra section inserted before Conceptual Framework displaces numbering
- Ethical Considerations moved to standalone section (should be 3.6.6)
- Sampling Design and Sampling Frame merged (should be separate)
- Pilot study described in future tense — must be conducted and results reported
- Sample size target not justified against PLS-SEM-specific criteria
- DC theorized as multi-dimensional but operationalized as single reflective construct
- Cross-level inference (project-level IV → org-level mediator) without justification
- Item overlap across constructs sharing cognitive content
- CMB treated as statistical test rather than acknowledged as design limitation
- RQ causal language vs. hypothesis association language mismatch

---

## Examiner Red Flags (Run Before Finalizing Report)

### Design-Level Red Flags

**RQ vs. Design Alignment**
- Do Research Questions use causal language ("enhance," "improve," "impact") when the design is cross-sectional?
- Cross-sectional designs support ASSOCIATIONS only — not causation, enhancement, or improvement claims
- Fix: reword RQs to "To what extent is X associated with Y?"

**Objective vs. Method Alignment**
- Does Objective 4 say "develop a framework" when the study tests a pre-specified model?
- "Develop" implies qualitative synthesis, Delphi, or design science — not PLS-SEM
- Fix: change to "test and validate"

**Pilot Study Status**
- Is the pilot study described in future tense?
- MSU requires actual findings: demographics, Cronbach's alpha, item modifications
- Fix: conduct pilot (n≈30), report actual reliability statistics

### Measurement Red Flags

**Circular Operational Definitions**
- Does the operational definition of a mediating variable include the IV? (e.g., "PM Performance is the improvement resulting from use of AI")
- Does the DV definition include "AI-supported" or reference the treatment?
- Fix: define each construct independently of all other constructs in the model

**Construct-Theory Mismatch**
- Is a multi-dimensional theoretical construct (e.g., DC with sensing/seizing/transforming) measured as a single reflective construct?
- Fix: second-order construct in SmartPLS, or justify unidimensional view in theory chapter

**Item Overlap**
- Do items across different constructs reference the same activity?
- Fix: reword items to ensure genuine cognitive separation

**Discriminant Validity Risk**
- Do items from two supposedly distinct constructs reference the same domain?
- HTMT ratio will likely exceed 0.85 — discriminant validity failure
- Fix: reword the overlapping item to focus on what makes its construct unique

**Formative Construct Heterogeneity**
- Does the formative construct mix structural barriers with attitudinal barriers?
- High VIF expected between co-occurring infrastructure items
- Fix: provide conceptual justification for the mixed typology, or sub-group into dimensions

### Theory Red Flags

**Framework Without History**
- Is the chosen theoretical framework described without tracing its intellectual development?
- At doctoral level: origin paper → major critiques → evolution → current version used
- Fix: add intellectual history section; acknowledge known limitations

**Framework Justified by Dismissal**
- Is the chosen framework selected only by saying other frameworks are "insufficient"?
- Fix: comparative argument — what X explains that alternatives cannot

**Mediation Without Precedent**
- Is mediation the central structural claim but no empirical study directly tests it in this specific context?
- Fix: build the mediation justification from closest available empirical evidence + theoretical mechanism

**Gaps Contradicted by Cited Studies**
- Do the gap claims say "no study has..." while the same chapter cites studies that partially address those gaps?
- Fix: reframe gaps as specific to THIS combination of context + construct chain + method

### Cross-Chapter Red Flags

**Chapter 2 → Chapter 3 References**
- Count how many times Chapter 2 says "as Chapter 3 will show" or "Chapter 3 clarifies"
- Any forward reference from LR to methodology is a logic inversion
- Fix: remove all forward references; rewrite so Chapter 2 LEADS to Chapter 3

**Three Definitions Problem**
- Is the key construct defined differently in Chapter 1, Chapter 2, and Chapter 3?
- Fix: one authoritative definition in Chapter 1; all other chapters reference or elaborate it

**Cross-Level Inference**
- Does the structural model connect a project-level construct to an organization-level construct?
- Fix: add key informant / single reference frame justification OR use multilevel SEM

**CMB as Check vs. Limitation**
- Is Common Method Bias treated only as a statistical procedure?
- Fix: acknowledge as design limitation; statistical checks are detection only, not prevention

---

## Execution Protocol

### Step 1 — Read All Uploaded Files
Extract full text from every uploaded chapter. Check file sizes first. Read completely — do not skim.

### Step 2 — Structural Mapping
For each chapter, map submitted sections against the MSU required structure above. Produce a table:

| MSU Required | Submitted As | Status |
|---|---|---|
| 1.1 Introduction | 1.1 Chapter Overview | Renamed — Minor |
| 1.3 Current Situation | (absent) | CRITICAL — Missing |

Note: missing sections, renamed sections, merged sections, misplaced sections, and cascading numbering errors caused by missing sections.

### Step 3 — Content Deep Analysis
Read between the lines. For each section evaluate:

**Argument logic** — claims supported by citations? logical leaps? argument leads to what follows?

**Theoretical grounding** — framework's intellectual history traced? limitations acknowledged? alternatives compared not dismissed?

**Measurement validity** — operational definitions embed IV into mediating constructs? questionnaire items capture distinct constructs? formative vs. reflective classification justified?

**Internal consistency** — constructs defined consistently across all chapters? objectives/RQs/hypotheses/analysis method align? study design matches objectives?

**Cross-chapter coherence** — Chapter 2 forward-references Chapter 3? same term defined differently in different chapters? "develop" vs "test" framings conflict?

**Citation accuracy** — in-text citations in reference list? year mismatches? orphaned citation fragments?

### Step 4 — Issue Classification

- **Critical**: Will likely fail examination or require major revision before acceptance
- **Significant**: Will generate direct examiner challenge requiring satisfactory answer
- **Minor**: Presentational or technical, correctable without restructuring argument

### Step 5 — Report Structure

1. **Executive Summary Table** — issue counts by chapter and severity
2. **Chapter 1** — Structural Issues (S1-xx), Content Issues (C1-xx), Citation Issues (R1-xx)
3. **Chapter 2** — Structural Issues (S2-xx), Content Issues (C2-xx), Citation Issues (R2-xx)
4. **Chapter 3** — Structural Issues (S3-xx), Content Issues (C3-xx), Citation Issues (R3-xx)
5. **Cross-Chapter Coherence Issues** (CC-xx)
6. **Master Priority Checklist** — all issues ranked by priority

### Step 6 — Issue Format

Every issue must follow this format:

```
[Code] — [Title] [Severity]
Section: [location]
Problem: [what is wrong and why it matters]
Submitted text (quote if specific): "..."
How it should read: [guidance — not text to copy verbatim]
```

Add this note to every report:
> All examples in this report are for guidance only. They illustrate the direction, structure, and academic level required. The student must rewrite in their own words based on their own reading, data, and analysis.

---

## Key Examiner Questions (Run Mentally Before Each Section)

1. Does the study design (cross-sectional survey) match the language of the objectives and RQs (causal vs. associational)?
2. Are mediating variables defined independently of the independent variable they mediate?
3. Is the chosen theoretical framework justified comparatively or just asserted?
4. Does Chapter 2 lead to Chapter 3, or does Chapter 3 explain Chapter 2?
5. Are constructs theorized as multi-dimensional but operationalized as unidimensional?
6. Is there a cross-level inference problem (project-level IV → org-level mediator) without multilevel justification?
7. Is the pilot study presented as plans or actual findings?
8. Are gap claims contradicted by studies cited in the same chapter?
9. Is "develop a framework" used when the study actually "tests" a pre-specified model?
10. Are any items across different constructs sharing cognitive content?

---

## Output Format

- English throughout (academic register)
- Issue codes: S = Structural, C = Content, R = Reference/Citation, CC = Cross-Chapter
- Each chapter section separated with a clear heading
- Master checklist as final table with columns: # | Issue | Chapter | Severity
- No filler text, no compliments, no hedging — direct academic language

---

## Scope Notes

- Calibrated for MSU PGC doctoral dissertations in management sciences
- Applies equally to DBA, PhD, and MBM theses at MSU
- Structural template reflects MSU PGC guidelines as of 2025
- Content quality standards are universal doctoral level (not MSU-specific)
- If only some chapters are uploaded, review only what is provided and note which are missing
- If no chapter is uploaded, ask for the files

---

## Output File

When producing a full review (all 3 chapters), generate a formatted Word document (English content, LTR, Calibri font) including:
- Cover page with thesis title, institution, and reviewer name
- Important note about examples being illustrative only
- Full report content with formatted issue headings, quote boxes, and fix guidance boxes
- Master checklist as formatted table at the end
