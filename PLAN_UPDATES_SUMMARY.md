# Plan Updates Summary

## What Changed

### 1. ✅ Workflow Restructured

**Before:** 9 steps, unclear flow
**After:** 6-step corrected workflow with explicit gates

```
1. Signal Intake
2. Signal Qualification (NEW - thresholds)
3. Insight Extraction (NEW - gated transition)
4. Canonical Asset Creation
5. Native Derivatives + Distribution
6. Learning Loop → feeds Signal Intake
```

**Key Addition:** Step 3 (Insight Extraction) is now **non-negotiable** - no Insight Card = no long-form.

---

### 2. ✅ Signal Qualification Added

**New Component:**
- Multi-axis scoring (5 axes: engagement, comment quality, follower delta, topic, format)
- Promotion thresholds (2 of 3 must pass)
- Automated + manual hybrid approach
- Database schema for `signal_scores` and `is_qualified_signal`

**Implementation:** `content/signal_scorer.py` with qualification logic

---

### 3. ✅ Insight Card Structure Defined

**New Mandatory Output:**
```json
{
  "core_belief": "...",
  "tension": "...",
  "why_people_cared": "...",
  "proof": [...],
  "practical_implication": "...",
  "framework_hidden": "...",
  "timeless_value": "..."
}
```

**Database:** New `insights` table with full schema

**Rule:** No Insight Card → No content creation

---

### 4. ✅ Native Derivatives Precisely Defined

**Before:** Vague "platform-specific formatting"
**After:** Concrete templates with emotional triggers

| Platform | Native Constraint | Format | Emotional Trigger |
|----------|------------------|--------|-------------------|
| X | Speed + sharp beliefs | One claim + proof | Contrarian |
| LinkedIn | Identity + career | Story → lesson | "I learned..." |
| Instagram | Visual cognition | Framework diagram | Visual pattern |
| Threads | Conversation | Question-led | Open loop |
| Substack Feed | Reflection | "Here's what I learned" | Personal reflection |

**Operational Rule:** One Insight → One Angle Per Platform (never port same angle)

---

### 5. ✅ Canonical Strategy Clarified

**Before:** "Same content everywhere"
**After:** Clear canonical stack

- **Website = Canonical** (SEO hub, internal linking, evergreen)
- **Substack = Distribution Mirror** (summary + link, NOT duplicate)
- **Beehiiv = Email Version** (with canonical link back)

**Key Change:** Substack no longer gets full content - gets summary + link to website

---

### 6. ✅ Learning Loop Schema Defined

**New Component:** Learning Entry structure

```json
{
  "winning_element": {belief, hook, format, cta},
  "quant_signal": {saves/impressions, comments/views, follower_delta},
  "qual_signal": {comment_themes, dms, shares},
  "verdict": {reuse_belief, reuse_format, kill_angle, platform_fit}
}
```

**Database:** New `learning_entries` table

**Retrieval:** Pattern queries ("Top beliefs that convert", "Formats with highest save rate")

**Timing:** 7 days (engagement), 14 days (conversion), 30 days (long-term)

---

### 7. ✅ Signal Intake Fully Defined

**Before:** "High-performing tweets identified"
**After:** Automated + Manual hybrid

- **Automated (Daily):** Top 10%, threads with X saves, abnormal follower delta
- **Manual (Weekly, 30 min):** "Did this shift beliefs?", "Would this matter in a year?"

**Thresholds:** 2 of 3 must pass (save rate ≥ 0.5%, meaningful comments, follower gain)

---

### 8. ✅ Mental Model Updated

**Before:** "Content workflow system"
**After:** "Belief discovery engine with distribution arms"

**Core Principle:** Content is disposable. Insights compound.

---

## Implementation Impact

### New Files Needed

1. `content/signal_scorer.py` - Multi-axis scoring
2. `content/insight_extractor.py` - Insight Card extraction
3. `content/learning_loop.py` - Learning extraction & pattern queries

### Database Migrations Needed

1. `x_tweets` table: Add `signal_scores`, `is_qualified_signal`, `qualification_date`
2. `insights` table: New table (full schema in plan)
3. `learning_entries` table: New table (full schema in plan)
4. `posts` table: Add `insight_id` foreign key
5. `derivatives` table: Add `insight_id`, `native_angle`, `emotional_trigger`

### Updated Files

1. `content/center_post.py` - Gate on Insight Card, use Insight Card as outline
2. `content/derivative_generator.py` - Use native templates, one angle per platform
3. `content/ai_client.py` - New prompts for insight extraction, native derivatives
4. `content/publisher.py` - Substack = summary + link (not full content)

---

## Key Rules Added

1. **No Insight Card → No Content** (Gated transition)
2. **One Insight → One Angle Per Platform** (Never port same angle)
3. **Website = Canonical, Substack = Mirror** (SEO clarity)
4. **2 of 3 Thresholds** (Signal qualification)
5. **Learning Feeds Filters** (Compounding loop)

---

## Next Steps

The plan is now **implementation-ready** with:
- ✅ Explicit workflow steps
- ✅ Concrete definitions
- ✅ Database schemas
- ✅ Implementation code examples
- ✅ Clear rules and gates

Ready to start Phase 1: Signal Qualification.
