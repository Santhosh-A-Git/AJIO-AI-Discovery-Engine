# Detailed Problem Statement

## AI-Powered Discovery Engine for AJIO Wishlist-to-Purchase Conversion

### 1. Business Context

AJIO is a large-scale fashion commerce platform where millions of users discover, evaluate, save, and purchase fashion products across categories such as apparel, footwear, accessories, beauty, and lifestyle.

One of the strongest signals of user interest on the platform is the **wishlist**. When a user adds a product to their wishlist, they have demonstrated explicit interest in that product. However, adding an item to a wishlist does not necessarily translate into a purchase.

Users may accumulate dozens or even hundreds of wishlisted products, while only a small proportion of these products are ultimately purchased. This creates a significant gap between **expressed purchase intent and realized purchase behavior**.

AJIO has identified an important growth opportunity:

> **Increase the percentage of users who purchase at least one item from their wishlist within 30 days of adding it.**

Improving this metric can potentially increase purchase frequency, strengthen user engagement, improve monetization from existing users, and unlock value from demand that already exists on the platform.

However, the core problem is not yet known.

The business has identified **the outcome it wants to improve**, but it has not identified **why users fail to convert wishlist intent into purchases**.

Therefore, the first challenge is not to build a recommendation feature, notification system, discount mechanism, or conversion campaign.

The first challenge is to **discover the underlying user problem**.

---

# 2. Core Challenge

The product team currently knows that:

**Wishlist → Purchase conversion within 30 days is lower than desired.**

But the team does not yet know:

* Why users add products to their wishlist.
* What users are trying to accomplish when they wishlist an item.
* Whether every wishlist addition represents genuine purchase intent.
* What prevents a user from purchasing a wishlisted item.
* What uncertainties remain after a product has been shortlisted.
* What causes users to postpone or abandon the purchase.
* Whether users require additional information before making a decision.
* Whether users compare multiple products before purchasing.
* Whether users leave AJIO to obtain information or validation elsewhere.
* How factors such as size, fit, styling, price, reviews, occasion, quality, availability, social validation, and perceived value influence the decision.
* Whether different user segments experience different barriers.
* Which unmet needs represent the strongest product opportunities.

There is therefore a **discovery gap** between the business metric and the underlying user problem.

The team must bridge this gap before designing a solution.

---

# 3. Problem Statement

## Primary Problem Statement

**AJIO needs to understand why users who explicitly express interest in fashion products by adding them to their wishlist do not convert that intent into a purchase within 30 days.**

The underlying reasons are currently not sufficiently understood or quantified.

User feedback and conversations are distributed across multiple sources, including app-store reviews, social media, Reddit, fashion communities, YouTube comments, product reviews, Q&A discussions, and other publicly available conversations.

These sources contain valuable qualitative signals about user motivations, frustrations, uncertainties, objections, and decision-making behaviors. However, the volume and diversity of these conversations make it difficult for product teams to manually analyze them at scale.

As a result, the team lacks a systematic mechanism to:

1. **Discover recurring user problems.**
2. **Identify the unmet needs behind those problems.**
3. **Quantify the prevalence of important themes where possible.**
4. **Understand how different user segments experience these problems.**
5. **Distinguish high-intent purchase barriers from low-intent bookmarking behavior.**
6. **Compare opportunity areas based on their potential impact on wishlist-to-purchase conversion.**
7. **Translate unstructured user conversations into actionable product insights.**

Therefore, AJIO needs an **AI-Powered Discovery Engine** that can analyze large-scale, multi-source user conversations and transform unstructured feedback into a structured view of the problems preventing wishlist users from purchasing.

---

# 4. Objective of the AI-Powered Discovery Engine

The objective is to build an AI-powered discovery system that can:

> **Continuously collect, process, analyze, cluster, quantify, and prioritize user problems related to fashion shopping and wishlist-to-purchase behavior, enabling the product team to identify the most important unmet needs that could influence the 30-day wishlist-to-purchase conversion metric.**

The engine should not merely answer:

> "What are users saying?"

It should help answer:

> **"What problems are users experiencing, how significant are those problems, which users experience them, and which problems represent the strongest opportunities for improving the target business outcome?"**

---

# 5. Key Discovery Questions

The discovery engine should generate evidence that helps answer the following questions.

### A. Wishlist Intent

* Why do users add fashion products to wishlists?
* What jobs are users trying to accomplish through wishlisting?
* Is the wishlist primarily a purchase-intent mechanism, a comparison mechanism, a reminder mechanism, or a bookmarking mechanism?
* What signals distinguish genuine purchase intent from casual saving?

### B. Purchase Barriers

* What prevents users from purchasing a wishlisted product?
* What doubts arise after the product has been shortlisted?
* What causes users to postpone the purchase?
* What causes users to remove or abandon wishlisted products?
* Which barriers are functional, emotional, informational, financial, or contextual?

### C. Decision-Making Uncertainty

The engine should identify uncertainties related to:

* Size and fit
* Material and quality
* Color and appearance
* Product authenticity
* Styling and how the product looks when worn
* Return and exchange confidence
* Reviews and ratings
* User-generated content
* Price/value perception
* Product availability
* Delivery expectations
* Occasion suitability
* Social validation
* Brand trust
* Comparison with alternatives
* Confidence that the product is the "right choice"

### D. Evaluation and Comparison

* Do users compare wishlisted products with other products?
* What dimensions do they compare?
* Are users waiting for more information before selecting one product?
* Do users use multiple shopping platforms to compare products?
* What role do external reviews, social media, influencers, or communities play?

### E. External Information Seeking

The engine should identify whether users leave AJIO to answer questions such as:

* "Will this fit me?"
* "How does this actually look?"
* "Is the quality good?"
* "Is the product worth the price?"
* "What size should I buy?"
* "How should I style this?"
* "Is this suitable for this occasion?"
* "Do other people recommend this product?"
* "Is there a better alternative?"

This is important because external information-seeking behavior may indicate **unmet information needs inside the product experience**.

---

# 6. Proposed System: AI-Powered Discovery Engine

The proposed discovery engine should function as a research and insight layer rather than as a direct customer-facing conversion feature.

At a high level, the system should transform:

**Raw User Conversations → Structured Evidence → User Problems → Opportunity Areas → Prioritized Product Insights**

The system should ingest large volumes of unstructured conversations from multiple sources and use AI to extract meaningful signals.

### Conceptual Flow

**Data Sources**
↓
**Data Collection & Normalization**
↓
**Noise Filtering & Deduplication**
↓
**AI Understanding & Topic Extraction**
↓
**Problem / Need Identification**
↓
**Behavior & Intent Classification**
↓
**Theme Clustering**
↓
**Segment Analysis**
↓
**Evidence & Quantification**
↓
**Opportunity Scoring**
↓
**Discovery Dashboard / Insights**

---

# 7. Data Sources

The discovery engine should be designed to analyze publicly available conversations and feedback such as:

### Primary Sources

* App Store reviews
* Google Play Store reviews
* Reddit discussions
* Fashion communities
* Shopping forums
* Social media conversations
* YouTube comments
* Public product reviews
* Public product Q&A
* Fashion discussion communities
* Public blogs and discussion threads

### Potential AJIO-Internal Data

Where permitted and available, the discovery layer could later be enriched with first-party behavioral data such as:

* Wishlist additions
* Wishlist removals
* Product views
* Search behavior
* Add-to-cart events
* Purchases
* Time between wishlist and purchase
* Product category
* Price range
* Size selections
* Returns
* Repeat visits
* User segment characteristics

The initial challenge, however, should primarily focus on **discovering the problem from user-generated feedback and publicly available conversations**, rather than assuming the problem from internal behavioral data.

---

# 8. What the AI System Must Do

## 8.1 Collect and Normalize Feedback

The system should ingest feedback from different platforms and transform it into a common structure.

For each piece of feedback, the system should ideally capture:

* Source
* Timestamp
* Text
* Topic/category
* Product/category context where identifiable
* User intent
* Problem expressed
* Emotional signal
* Purchase stage
* Evidence/source link
* Confidence score

The system should also identify and remove:

* Duplicate content
* Spam
* Irrelevant conversations
* Promotional content
* Bot-generated content where identifiable
* Conversations unrelated to fashion shopping

---

# 9. Problem Discovery Layer

The core intelligence of the system should go beyond sentiment analysis.

Instead of simply classifying feedback as:

**Positive / Neutral / Negative**

the system should determine:

> **What problem is the user experiencing?**

For example:

**Raw feedback**

> "I really like this dress, but I'm confused about which size to order because the reviews have completely different opinions on the fit."

The engine should potentially identify:

**Intent:** High product interest
**Stage:** Pre-purchase evaluation
**Problem:** Size/fit uncertainty
**Need:** Higher confidence in sizing
**Potential barrier:** Fear of making the wrong purchase
**Potential conversion impact:** High

This transformation from **comment → problem → unmet need** is central to the system.

---

# 10. Distinguishing User Intent

An important requirement is that the system should understand that **not every wishlist action represents the same level of intent**.

Potential intent categories could include:

### High Purchase Intent

The user is actively evaluating a product and appears close to making a purchase.

### Consideration Intent

The user likes the product but requires more information or validation.

### Comparison Intent

The user is evaluating the product against alternatives.

### Deferred Purchase Intent

The user intends to buy later but is waiting for an appropriate trigger or circumstance.

### Bookmarking Intent

The wishlist is primarily being used to save or organize products without meaningful near-term purchase intent.

The discovery engine should identify signals associated with each behavior.

---

# 11. Problem Taxonomy

The system should dynamically discover themes rather than relying entirely on a predefined taxonomy.

However, an initial taxonomy may include:

### Product Understanding

* Fit
* Size
* Material
* Quality
* Color
* Appearance
* Authenticity

### Decision Confidence

* Reviews
* Ratings
* Customer photos
* Social proof
* Brand trust
* Product confidence

### Value Perception

* Price
* Value for money
* Product quality relative to price
* Comparison with alternatives

### Contextual Needs

* Occasion
* Season
* Styling
* Personal preferences
* Wardrobe compatibility

### Transactional Concerns

* Availability
* Delivery
* Return policy
* Exchange
* Stock uncertainty

### Behavioral Drivers

* Delayed purchase
* Comparison shopping
* Bookmarking
* Reminder behavior
* Future purchase planning

The AI system should be capable of discovering **new themes that do not exist in the initial taxonomy**.

---

# 12. Quantification

The engine should attempt to quantify problems rather than merely describe them.

For each major problem theme, the system should estimate metrics such as:

* Number of relevant conversations
* Percentage of analyzed conversations
* Growth or decline over time
* Frequency across platforms
* Frequency across categories
* User sentiment/intensity
* Purchase-stage relevance
* Association with high purchase intent
* Recurrence across independent sources

For example:

| Problem              | Evidence Volume | Intent Relevance |     Growth | Potential Opportunity |
| -------------------- | --------------: | ---------------: | ---------: | --------------------: |
| Size/fit uncertainty |            High |             High | Increasing |                  High |
| Styling uncertainty  |          Medium |           Medium | Increasing |                Medium |
| Price concern        |       Very High |             High |     Stable |                  High |
| Social validation    |          Medium |             High | Increasing |                  High |

These numbers should be treated as **evidence estimates**, not automatically interpreted as causal proof.

---

# 13. Cross-Platform Comparison

The same problem may appear differently across platforms.

For example:

* App reviews may highlight product usability issues.
* Reddit may reveal deeper shopping frustrations.
* YouTube comments may expose styling and appearance concerns.
* Fashion communities may reveal decision-making patterns.
* Product reviews may reveal fit and quality issues.

The discovery engine should therefore identify:

* Problems common across multiple sources.
* Problems unique to specific platforms.
* Differences in language and intensity.
* Whether a problem is widespread or concentrated in a niche community.

Cross-source recurrence should strengthen confidence in an opportunity area.

---

# 14. User Segment Analysis

Where sufficient evidence exists, the system should identify how problems differ across segments.

Potential dimensions include:

* New vs returning users
* High vs low purchase frequency
* Fashion enthusiast vs occasional shopper
* Category
* Product price range
* Brand preference
* Purchase intent
* Occasion
* Device/platform
* Demographic characteristics where legally and appropriately available

For example:

> Size uncertainty may be particularly significant for apparel shoppers, while authenticity concerns may be more important for premium categories.

The goal is to avoid assuming that a single problem applies equally to every user.

---

# 15. Opportunity Identification

The system must ultimately connect discovered problems to the business objective.

A frequent complaint is not necessarily a valuable product opportunity.

Therefore, the discovery engine should help prioritize problems based on dimensions such as:

### Problem Prevalence

How frequently is the problem observed?

### Intent Relevance

How strongly is the problem associated with users who demonstrate purchase intent?

### Conversion Proximity

Does the problem occur close to the purchasing decision?

### Severity

How significantly does the problem prevent or delay purchase?

### Segment Reach

How broadly does the problem affect valuable user segments?

### Evidence Strength

Is the problem consistently observed across independent sources?

### Trend

Is the problem increasing over time?

### Solvability

Can a product intervention realistically address the problem?

A conceptual opportunity score could therefore be expressed as:

> **Opportunity Score = Prevalence × Intent Relevance × Severity × Evidence Strength × Conversion Proximity**

The exact formula should be treated as a prioritization mechanism rather than a claim of causal impact.

---

# 16. Required Output of the Discovery Engine

The final output should not be a collection of summarized reviews.

Instead, the system should generate a structured **Problem Landscape**.

For every significant problem, the engine should ideally produce:

### Problem

A clear statement of the user problem.

### User Need

What the user is trying to accomplish.

### Evidence

Representative examples from multiple conversations and sources.

### Frequency

How commonly the problem appears.

### User Segment

Which types of users experience it.

### Purchase Stage

Where in the journey the problem occurs.

### Intent Relationship

Whether it appears associated with high, medium, or low purchase intent.

### Business Relevance

How plausibly the issue could influence wishlist-to-purchase conversion.

### Opportunity Size

Estimated relative importance.

### Confidence

How strong and consistent the evidence is.

### Open Questions

What still needs to be validated through primary research or experimentation.

---

# 17. Example of Desired Insight

The system should be capable of producing insights such as:

> **Problem:** Users who strongly like fashion products often hesitate to purchase because they cannot confidently predict how the product will fit or look on them.

> **Evidence:** The issue appears repeatedly across app reviews, fashion communities, product discussions, and social conversations.

> **Affected Segment:** Apparel shoppers evaluating products with uncertain fit.

> **Purchase Stage:** Post-discovery, pre-purchase evaluation.

> **Underlying Need:** Users need greater confidence that the product will suit them before committing to purchase.

> **Behavioral Consequence:** Users may save the product, compare alternatives, seek external validation, postpone the purchase, or abandon the item.

> **Opportunity Hypothesis:** Reducing uncertainty at the evaluation stage may improve wishlist-to-purchase conversion.

Notice that this output identifies an **opportunity hypothesis**, not a predetermined solution.

The system should not immediately conclude:

> "Build an AI stylist."

It should first establish:

> **"What user problem is important enough to solve?"**

---

# 18. Key Product Requirement

The discovery engine must preserve a clear separation between:

### Evidence

What users actually said or did.

### Insight

What those observations suggest.

### Hypothesis

What may explain the behavior.

### Opportunity

What user problem may be worth solving.

### Solution

What product intervention could potentially address the problem.

The AI system should **not jump directly from a review to a product feature**.

For example:

**Incorrect approach**

> Users want better recommendations → Build recommendation engine.

**Desired approach**

> Users save multiple products → compare them later → remain uncertain about fit/styling → search external sources → postpone purchase → potentially convert less often.

This creates a stronger foundation for identifying the actual opportunity.

---

# 19. Success Criteria for the Discovery Engine

The discovery engine should be considered successful if it enables the product team to:

1. Analyze large volumes of heterogeneous user feedback at scale.
2. Identify recurring user problems beyond simple sentiment.
3. Distinguish user motivations and purchase intent.
4. Quantify problem prevalence where possible.
5. Identify differences across user segments.
6. Detect unmet information and decision-making needs.
7. Compare multiple opportunity areas.
8. Surface evidence-backed hypotheses linked to wishlist-to-purchase behavior.
9. Reduce dependence on manual review analysis.
10. Give Product Managers a prioritized problem landscape that can guide subsequent discovery, validation, and solution design.

---

# 20. Primary Success Metric

The ultimate business metric that motivates this discovery initiative is:

> **% of users who purchase at least one wishlisted item within 30 days of adding it.**

However, the AI discovery engine itself should initially be evaluated using **discovery quality metrics**, because it is not directly responsible for changing conversion.

Potential discovery-level metrics include:

* Problem discovery precision
* Evidence coverage
* Theme consistency
* Cross-source validation
* Insight usefulness rated by Product/Research teams
* Percentage of insights supported by multiple independent evidence sources
* Time required to identify and prioritize major problems
* Percentage of generated opportunities that survive subsequent validation

The actual impact on wishlist-to-purchase conversion should be measured later through product experimentation after an opportunity has been validated.

---

# 21. Constraints

The problem has an explicit business constraint:

> **No monetary incentives may be offered to users to increase conversion.**

Therefore, potential solutions should not rely on:

* Discounts
* Coupons
* Cashback
* Wallet credits
* Reward points
* Promotional cash incentives
* Price reductions specifically designed to force conversion

This constraint intentionally pushes the team toward discovering **non-monetary barriers and unmet needs**.

Potential areas may include reducing uncertainty, improving decision confidence, improving product understanding, reducing cognitive load, improving personalization, helping users compare options, or providing better contextual information—but these are **hypotheses to investigate, not predetermined solutions**.

---

# 22. Non-Goals

The first phase of this challenge is **not** intended to:

* Build the final conversion feature.
* Build a discount or incentive engine.
* Optimize notifications.
* Design a recommendation algorithm.
* Improve the wishlist UI without evidence.
* Perform sentiment analysis alone.
* Produce a generic review-summary system.
* Assume that price is the primary problem.
* Assume that recommendations are the solution.
* Optimize wishlist conversion before identifying the underlying user problem.

The immediate goal is **problem discovery and opportunity identification**.

---

# 23. Expected Product Manager Outcome

At the end of this discovery phase, the Product Manager should be able to answer:

> **Who are the users failing to convert from wishlist to purchase?**

> **What are they trying to accomplish?**

> **What prevents them from purchasing?**

> **Which problems occur most frequently?**

> **Which problems are most strongly connected to purchase intent?**

> **Which user segments are affected?**

> **What evidence supports each problem?**

> **Which opportunity areas are most promising?**

> **What assumptions still need validation?**

Only after answering these questions should the team proceed to solution discovery.

---

# 24. Final Problem Statement

### Final Version

**AJIO wants to increase the percentage of users who purchase at least one product from their wishlist within 30 days of adding it. While wishlist additions represent an explicit signal of user interest, a large proportion of wishlisted products do not convert into purchases. The underlying reasons for this conversion gap are currently not well understood.**

**User feedback relevant to fashion-shopping decisions is fragmented across app-store reviews, social media, Reddit, fashion communities, YouTube comments, product reviews, Q&A discussions, and other public conversations. The volume and unstructured nature of this information make it difficult for Product Managers to systematically discover, quantify, compare, and prioritize the problems preventing users from moving from product interest to purchase.**

**Therefore, the first challenge is to build an AI-Powered Discovery Engine that can analyze these diverse user conversations at scale, identify the motivations and behaviors behind wishlist usage, uncover recurring purchase barriers and unmet needs, distinguish genuine purchase intent from bookmarking behavior, understand differences across user segments, quantify the prevalence and relevance of potential problems where possible, and prioritize opportunity areas based on their potential relationship to the 30-day wishlist-to-purchase conversion metric.**

**The system must go beyond sentiment analysis or review summarization. It should transform unstructured user conversations into evidence-backed problem statements and opportunity hypotheses that help the Product Manager determine what user problem is worth solving before any solution is proposed.**

**The solution must not rely on monetary incentives such as discounts, cashback, coupons, or rewards.**

---

# 25. One-Line Challenge Definition

> **Build an AI-powered discovery engine that identifies, quantifies, and prioritizes the user problems preventing high-intent wishlist users from converting to purchase within 30 days—without assuming the problem or relying on monetary incentives.**

# 26. Product Management Principle Behind the Challenge

> **Do not start with "What feature should AJIO build?" Start with "What is preventing the user from completing the job they are trying to accomplish?"**

The AI Discovery Engine exists to answer that question with **evidence, scale, and prioritization** before the team moves into solution design.
