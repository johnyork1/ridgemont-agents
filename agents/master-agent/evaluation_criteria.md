# Agent Evaluation Criteria

## Health Score Dimensions (each scored 1-10)

### 1. Clarity (Rules Quality)
| Score | Definition |
|-------|-----------|
| 9-10  | Rules are precise, well-structured, no ambiguity. Agent knows exactly what to do in any scenario. |
| 7-8   | Rules are solid with minor gaps. Occasional ambiguity in edge cases. |
| 5-6   | Rules are functional but vague in places. Agent may misinterpret some requests. |
| 3-4   | Rules are disorganized or contradictory. Agent frequently needs clarification. |
| 1-2   | Rules are minimal, missing, or incoherent. Agent is essentially guessing. |

### 2. Scope (Focus)
| Score | Definition |
|-------|-----------|
| 9-10  | Agent has a single, well-defined domain. Every rule and file supports that domain. |
| 7-8   | Agent covers 1-2 related domains with clear boundaries. |
| 5-6   | Agent covers 2-3 domains with some blurring between them. |
| 3-4   | Agent tries to do too many unrelated things. Rules are bloated. |
| 1-2   | Agent has no clear purpose. It's a catch-all dumping ground. |

### 3. Data Quality
| Score | Definition |
|-------|-----------|
| 9-10  | All data files are current, well-organized, properly named, and referenced in rules. |
| 7-8   | Data is mostly current. Minor organizational issues. |
| 5-6   | Some data is outdated or poorly organized. Orphan files exist. |
| 3-4   | Significant data quality issues. Files are stale, duplicated, or misplaced. |
| 1-2   | Data is largely unusable, missing, or contradicts itself. |

### 4. Utilization
| Score | Definition |
|-------|-----------|
| 9-10  | Used daily. Core to John's workflow. |
| 7-8   | Used multiple times per week. Important but not critical. |
| 5-6   | Used weekly. Serves a recurring but infrequent need. |
| 3-4   | Used occasionally. May be a candidate for merging. |
| 1-2   | Rarely or never used. Consider archiving or merging. |

### 5. Effectiveness
| Score | Definition |
|-------|-----------|
| 9-10  | Consistently produces high-quality, accurate outputs. Minimal corrections needed. |
| 7-8   | Produces good outputs with occasional minor issues. |
| 5-6   | Outputs are adequate but often need refinement. |
| 3-4   | Outputs frequently miss the mark. Rules need significant rework. |
| 1-2   | Agent fails to accomplish its stated purpose. |

---

## Merge Evaluation Matrix

When comparing two agents for potential merger, score these factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Data Overlap | 25% | How much data do they share? |
| Rules Overlap | 25% | How similar are their instructions? |
| Workflow Overlap | 20% | Does the user switch between them for the same task? |
| Domain Proximity | 15% | How related are their subject areas? |
| Complexity Impact | 15% | Would merging make the combined agent too complex? |

**Merge Threshold:** Weighted score > 7.0 = Strong merge candidate
**Caution Zone:** 5.0-7.0 = Consider but evaluate carefully
**Keep Separate:** < 5.0 = Agents serve distinct purposes

---

## Split Evaluation Matrix

When evaluating whether an agent should be divided:

| Factor | Weight | Description |
|--------|--------|-------------|
| Rule Complexity | 25% | How long/complex are the rules? |
| Domain Count | 25% | How many distinct domains does it cover? |
| Data Separation | 20% | Can the data be cleanly divided? |
| Workflow Independence | 15% | Do the workflows operate independently? |
| Conflict Level | 15% | Do rules contradict each other? |

**Split Threshold:** Weighted score > 7.0 = Strong split candidate
**Caution Zone:** 5.0-7.0 = Consider but evaluate carefully
**Keep Together:** < 5.0 = Agent is appropriately scoped

---

## Ecosystem-Level Checks

### Redundancy Check
- Are any two agents doing the same thing differently?
- Are data files duplicated across agent folders?
- Do multiple agents reference the same external sources?

### Coverage Gap Check
- Are there workflows John performs manually that could be automated by an agent?
- Are there domains in John's work/life not covered by any agent?
- Are there agent skills that are defined but never triggered?

### Dependency Check
- Does any agent depend on another agent's data?
- Are there circular dependencies?
- If one agent is removed, would another break?

### Naming & Organization Check
- Are folder names descriptive and consistent?
- Are file names following a convention?
- Is there a clear hierarchy within each agent's folder?
