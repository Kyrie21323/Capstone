# PROPHERE DEVELOPMENT ROADMAP

**Last Updated:** 2026-02-05  
**Version:** 1.0  
**Prophere Version:** 1.4.0  
**Target:** v2.0.0 (12 weeks from now)

---

## EXECUTIVE SUMMARY

**Mission:** Transform Prophere from academic prototype → production-ready platform with defensible competitive moat

**Timeline:** 12 weeks (3 sprints × 3-4 weeks)

**Revenue Goal:** $0 → $132K ARR in 4 months (22 events @ $500-1,500 each)

**Moat Goal:** 4/10 → 7.5/10 defensibility

---

## GUIDING PRINCIPLES

### 1. "Do One Thing Exceptionally Well"
**The One Thing:** Get attendees into high-quality 1-on-1 meetings as fast as possible

**NOT Competing On:**
- Messaging (LinkedIn wins)
- Event discovery (Luma wins)
- Ticketing (Eventbrite wins)
- Job search (LinkedIn wins)

---

### 2. Feature Scoring Framework

```
Priority Score = (Competitive Gap × 0.35) + (Moat Strength × 0.30) + (User Impact × 0.25) + (Effort Inverse × 0.10)

Where:
- Competitive Gap: How far behind competitors (1-10, 10 = critical gap)
- Moat Strength: Does this build defensibility? (1-10, 10 = strong moat)
- User Impact: How many users benefit? (1-10, 10 = all users)
- Effort Inverse: 10 - (effort_weeks / 2), capped at 1
```

**Build Threshold:** Score ≥ 7.5

**Omit Threshold:** Score < 6.0

---

## CRITICAL STRATEGIC DECISION: NO FULL MESSAGING

### Original Plan (Rejected)
**Was:** Build full in-app messaging (Week 4-5, 1.5 weeks, Score: 9.2/10)

### Why Rejected
1. **LinkedIn Network Effect Unbeatable:** 900M users vs ~100 per event
2. **User Behavior:** Will coordinate on LinkedIn anyway ("Add me on LinkedIn")
3. **Scope Creep:** Moderation, spam, harassment, long-lived threads
4. **Doesn't Strengthen Moat:** Competes where we can't win

### Revised Plan (Approved)
**Build:** Meeting Coordination Layer (Week 2, 2 days, Score: 8.7/10)

**What to Build:**
```
Meeting-Scoped Coordination:
├── Quick Actions (preset messages):
│   ├── "Running 5 min late"
│   ├── "I'm here at [location]"
│   ├── "Where are you?"
│   └── Custom (100 char limit, meeting-scoped)
├── Location Context:
│   ├── "I'm at Table X" (share meeting point)
│   └── One-tap map link
├── LinkedIn Quick Connect:
│   ├── "View LinkedIn Profile" button
│   ├── Deep link to connection request
│   └── Optional QR code
└── Safety:
    ├── Auto-expire 24h after event
    ├── Rate limit (5 messages/meeting)
    └── Block/report
```

**What NOT to Build:**
- ❌ Global inbox (LinkedIn replacement)
- ❌ Read receipts / typing indicators
- ❌ Attachments / rich media
- ❌ Long-lived threads (post-event chat)

**Positioning:** "Prophere gets you to the meeting. LinkedIn keeps you connected after."

**Financial Impact:** Saved $13K in dev time (1.5 weeks → 2 days)

---

## 12-WEEK IMPLEMENTATION PLAN

### SPRINT 1: FOUNDATION (Weeks 1-3)

**Theme:** Baseline UX polish + critical data collection + technical foundation

#### Week 1: Meeting Experience (2 days)
**Goal:** Prevent no-shows, reduce awkwardness

**Features:**
1. **Meeting Reminders** (1 day)
   - Email reminder (24h, 1h before)
   - Push notification (5 min before with warmup)
   - Warmup includes: other person's photo, icebreaker suggestion, location
   - **Success Metric:** Meeting completion rate 75%+ (vs ~50% baseline)

2. **UX Polish** (1 day)
   - Loading states for matching
   - Error boundaries
   - Accessibility audit (WCAG 2.1 AA)
   - Mobile responsiveness fixes

---

#### Week 2: Data Flywheel + Performance (3 days)

**Goal:** Start collecting feedback, optimize speed

**Features:**
1. **Post-Meeting Feedback** (2 days) - **CRITICAL FOR MOAT**
   - MeetingFeedback model (rating 1-5, outcome, would_recommend)
   - Simple form (auto-email 30 min after meeting)
   - Dashboard: "Your matches are getting better!" (show trend)
   - **Success Metric:** 60%+ feedback completion, 4.2+ avg rating

2. **Meeting Coordination Layer** (2 days) - **REVISED FROM MESSAGING**
   - See "Critical Strategic Decision" section above
   - **Success Metric:** 75%+ meeting completion, 80%+ click "Connect on LinkedIn"

3. **NLP Embedding Cache** (1 day)
   - Redis cache for user embeddings
   - Cache invalidation on keyword/resume update
   - **Success Metric:** P95 matching load <500ms, 10-50x speedup

---

#### Week 3: Safety Net (4 days)

**Goal:** Build confidence to ship fast

**Features:**
1. **Test Coverage** (2 days)
   - Unit tests for models (User, Event, Match, Meeting)
   - Integration tests for matching engine
   - Route tests for critical flows (auth, matching, scheduling)
   - **Target:** 70%+ code coverage

2. **CI/CD Pipeline** (1 day)
   - GitHub Actions workflow
   - Automated testing on PR
   - Linting (flake8, black, mypy)
   - Deploy preview environments

3. **Monitoring** (1 day)
   - Sentry for error tracking
   - Metrics dashboard (Prometheus + Grafana)
   - Uptime monitoring (UptimeRobot)

---

### SPRINT 2: PARITY + REVENUE (Weeks 4-6)

**Theme:** Match competitor baselines + enable monetization

#### Week 4: Differentiation + Revenue (5 days)

**Goal:** Build unique features + organizer value

**Features:**
1. **Icebreaker Suggestions** (2 days) - **UNIQUE TO PROPHERE**
   - Generate 3 icebreakers per match (NLP-based)
   - Common keywords, resume entities, event context
   - Display in match modal
   - **Success Metric:** 40%+ use icebreakers, +0.3 star rating boost

2. **Whitelabel Branding** (3 days) - **REVENUE ENABLER**
   - Custom domain (events.company.com)
   - Custom colors (CSS variables)
   - Logo upload
   - Hide "Powered by Prophere" (paid tier)
   - **Revenue:** $500-1,000/event for enterprise tier

---

#### Week 5: UX Excellence (4 days)

**Goal:** Make Tinder UI best-in-class

**Features:**
1. **Enhanced Swipe Gestures** (3 days)
   - Touch/mouse swipe detection
   - Card slide animations (left/right)
   - Undo last swipe
   - Keyboard shortcuts (space = like, backspace = pass)
   - **Success Metric:** 80%+ mobile users swipe, +30% session length

2. **Pre-commit Hooks** (0.5 days)
   - Lint check (flake8, black)
   - Test check (pytest)
   - Migration check

3. **Background Job Queue** (0.5 days)
   - Celery setup
   - Async email sending
   - Scheduled tasks (reminders, cache warming)

---

#### Week 6: Integration + Polish (4 days)

**Goal:** Reduce friction, improve performance

**Features:**
1. **Export Connections** (1 day)
   - CSV export (name, email, LinkedIn, keywords, match date)
   - "Connect on LinkedIn" bulk action
   - **Success Metric:** 50%+ of users export connections

2. **Beautiful Event Cards** (2 days) - **LUMA-INSPIRED**
   - Gradient backgrounds
   - Event preview image upload
   - Attendee count, match stats
   - AI-generated "match potential" score

3. **Redis Caching** (1 day)
   - Session caching
   - Query result caching
   - Rate limiting

---

### SPRINT 3: NETWORK EFFECT (Weeks 7-9)

**Theme:** Build cross-event persistence + mobile experience

#### Week 7: Network Persistence (5 days)

**Goal:** Enable network effect (users return for multiple events)

**Features:**
1. **Persistent Profiles** (4 days) - **CRITICAL FOR RETENTION**
   - UserProfile model (bio, LinkedIn URL, portfolio, cross-event keywords)
   - Profile page (view all events attended)
   - "Mutual events" discovery
   - Privacy settings (public/events-only/private)
   - **Success Metric:** 30% attend 2+ events within 6 months

2. **Leaderboard** (1 day) - **GAMIFICATION**
   - Top matchers per event
   - "Most connected" badge
   - Points system (match = 10, meeting = 50, feedback = 25)

3. **PostgreSQL Migration** (2 days)
   - Migrate from SQLite to PostgreSQL
   - Update deployment config
   - Test export/import

---

#### Week 8: Mobile + Analytics (5 days)

**Goal:** Mobile-first experience + organizer value

**Features:**
1. **Mobile PWA** (3 days)
   - Service worker (offline support)
   - App manifest (add to home screen)
   - Push notification permission flow
   - Mobile-optimized gestures

2. **Calendar Integration** (1 day) - **LUMA-INSPIRED**
   - Google Calendar API
   - Apple Calendar deep link
   - "Add all meetings" button

3. **Enhanced Analytics Dashboard** (1 day) - **ORGANIZER VALUE**
   - Network density graph (Cytoscape.js)
   - Match completion funnel
   - Top keywords by matches
   - Export analytics as PDF

---

#### Week 9: Polish + Scale (4 days)

**Goal:** Production readiness

**Features:**
1. **Match "Moments"** (2 days) - **REAL-TIME COORDINATION**
   - Quick status updates ("At the networking lounge for 30 min")
   - Visible to matches only
   - Auto-expire after event
   - **Success Metric:** 40%+ post moments, 20%+ engagement rate

2. **QR Check-In** (1 day) - **DATA QUALITY**
   - QR code generation per event
   - Check-in unlocks matching
   - Attendance tracking

3. **Performance Optimization** (1 day)
   - Database query optimization (N+1 fixes)
   - Image compression (Pillow)
   - CDN setup (Cloudflare)

---

## WHAT NOT TO BUILD (Strategic Omissions)

### Tier 1: OMIT (Scope Creep)

| Feature | Why Omit | Competitor | Risk if Built |
|---------|----------|------------|---------------|
| **Full In-App Messaging** | LinkedIn network effect unbeatable | All | Scope creep, can't compete, moat -2/10 |
| **Job Board** | LinkedIn's moat | LinkedIn | Distraction, low ROI for events |
| **Ticketing/Payments** | Not core value prop | Luma, Eventbrite | Compete with established players |
| **Video Calls** | Events are in-person | Zoom | Wrong direction |
| **Social Feed** | Generic, unfocused | LinkedIn | Becomes LinkedIn clone |

---

### Tier 2: DEFER (Low Priority)

| Feature | Why Defer | Revisit When |
|---------|-----------|--------------|
| **Event Discovery Marketplace** | Depends on critical mass | Month 6 (after 50+ events) |
| **Native Mobile Apps** | PWA sufficient for now | Month 9 (after product-market fit) |
| **Advanced Availability Calendars** | Session checkboxes work | User complaints (if any) |
| **Multi-timezone Support** | Events are local | International expansion (Month 15) |

---

## REVENUE MODEL

### Pricing Tiers

| Tier | Price | Features | Target |
|------|-------|----------|--------|
| **Free** | $0 | Unlimited attendees, basic matching, email invites | Universities, small events |
| **Pro** | $500/event | Whitelabel branding, analytics, priority support | Mid-size events (100-300) |
| **Enterprise** | $1,500/event | Custom domain, sponsor profiles, dedicated account manager | Large events (300-500) |

---

### Revenue Projections (4 Months)

**Month 1:** 2 events × $500 = $1,000  
**Month 2:** 5 events × $700 = $3,500  
**Month 3:** 8 events × $900 = $7,200  
**Month 4:** 10 events × $1,200 = $12,000  

**Total (4 months):** $23,700  
**ARR (extrapolated):** ~$132,000

---

## SUCCESS METRICS (WEEKLY TRACKING)

### Week 1-3 (Foundation)
- ✅ Meeting completion rate: 75%+
- ✅ Feedback collection rate: 60%+
- ✅ Test coverage: 70%+
- ✅ P95 page load: <500ms

### Week 4-6 (Parity + Revenue)
- ✅ First paying customer ($500)
- ✅ Icebreaker usage: 40%+
- ✅ Swipe gesture usage (mobile): 80%+
- ✅ Connection export rate: 50%+

### Week 7-9 (Network Effect)
- ✅ Cross-event users: 20%+
- ✅ Mobile PWA installs: 30%+
- ✅ QR check-in adoption: 70%+
- ✅ Match moments posted: 40%+

---

## RISK MITIGATION

### Technical Risks

| Risk | Mitigation | Timeline |
|------|-----------|----------|
| NLP model too slow at scale | Redis cache (Week 2) | Addressed Week 2 |
| Database bottleneck | PostgreSQL + indexing (Week 7) | Addressed Week 7 |
| No test coverage | 70%+ tests (Week 3) | Addressed Week 3 |

---

### Business Risks

| Risk | Mitigation | Timeline |
|------|-----------|----------|
| LinkedIn adds event networking | Move fast, patent filing (Week 4) | Ongoing |
| Luma adds matching | Own "Tinder for Events" brand (Week 6 PR) | Week 6 |
| Low organizer retention | Whitelabel lock-in (Week 4) | Addressed Week 4 |

---

## ESCALATION TRIGGERS

**Only reconsider full messaging IF:**
1. Meeting completion rate <60% after coordination layer (Week 4)
2. 30%+ of users explicitly request "need more than quick messages"
3. Non-LinkedIn segment emerges (30%+ don't have LinkedIn)

**Current Assessment:** UNLIKELY (LinkedIn dominance is structural)

---

## RESOURCE ALLOCATION

### Developer Time (12 weeks)

- **Week 1-3:** 60% features, 40% infrastructure
- **Week 4-6:** 70% features, 20% revenue, 10% polish
- **Week 7-9:** 50% features, 30% mobile, 20% scale prep

---

### Budget Estimate

| Category | Cost | Notes |
|----------|------|-------|
| Development Time | $0 | Capstone project (academic) |
| Infrastructure (Render) | $20/month | Production deployment |
| Redis Cloud | $15/month | Caching tier |
| Domain | $15/year | prophere.app |
| Email (SendGrid) | $20/month | Transactional emails |
| Monitoring (Sentry) | $0 | Free tier (10K events/month) |

**Total (3 months):** ~$200

---

## POST-LAUNCH PLAN (Month 4+)

### Month 4-6: Growth
- University partnerships (10 schools)
- ProductHunt launch ("Tinder for Events")
- TechCrunch pitch (AI networking)

### Month 7-9: Scale
- Enterprise sales (target: 5 customers @ $1,500)
- International expansion (EU, MENA)
- Advanced features (sponsor booths, exhibitor tracking)

### Month 10-12: Platform
- API for third-party integrations
- Eventbrite sync
- LinkedIn profile import
- CRM exports (Salesforce, HubSpot)

---

## CONCLUSION

**Critical Path:** Foundation → Parity → Network Effect

**Success Criteria (12 weeks):**
- ✅ 75%+ meeting completion rate
- ✅ 4.2+ average match quality rating
- ✅ 10+ paying customers
- ✅ 30% cross-event user retention
- ✅ 70%+ test coverage
- ✅ Moat strength: 7.5/10

**Next Steps:** See Week 1 sprint tasks

---

**For strategic context, see:** STRATEGY.md
