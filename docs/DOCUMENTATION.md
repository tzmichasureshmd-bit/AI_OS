# TZMICHA AI OS — Complete Business & Technical Documentation

---

## 1. What Is TZMICHA AI OS?

TZMICHA AI OS is an Enterprise AI Voice Platform.
Businesses create "AI Employees" that make and receive phone calls exactly like real humans.

**Simple explanation:**
> "A customer calls your number. An AI picks up, speaks in Telugu/Hindi/English naturally, answers questions, qualifies the lead, and books an appointment. The customer doesn't know it's AI."

**One line for MD:**
> "We sell AI employees that replace human telecallers. Same quality. 1/10th the cost. Works 24/7."

---

## 2. How It Works

```
Customer calls your number (from Instagram ad, website, etc.)
         │
         ▼
Phone system receives call (Twilio / SIP)
         │
         ▼
AI EARS listen (Sarvam AI Speech-to-Text)
  → Converts customer voice to text in real-time
  → Supports Telugu, Hindi, English
         │
         ▼
AI BRAIN thinks (Groq LLM - LLaMA 3.3)
  → Understands what customer said
  → Remembers full conversation context
  → Generates natural human-like response
  → Follows business workflow (qualify → pitch → book)
         │
         ▼
AI MOUTH speaks (Sarvam AI Text-to-Speech)
  → Converts response to natural voice
  → Pure Telugu/Hindi/English pronunciation
  → Sounds like a real Indian girl/boy on phone
         │
         ▼
Customer hears response (thinks it's a real person)
         │
         ▼
Call ends → Lead saved → Notification sent to team
```

---

## 3. What We've Built (Current Status)

| Component | Status | Details |
|-----------|--------|---------|
| Voice Engine Architecture | ✅ Complete | Modular, provider-independent |
| AI Brain (LLM) | ✅ Working | Groq + LLaMA 3.3 (FREE, 0.8s response) |
| AI Ears (STT) | ✅ Working | Sarvam AI (perfect Telugu/Hindi) |
| AI Mouth (TTS) | ✅ Working | Sarvam AI (native Indian voices, 37 speakers) |
| Conversation Engine | ✅ Complete | Topic switching, memory, interruptions |
| Language Detection | ✅ Complete | Auto-switches EN/HI/TE mid-conversation |
| Knowledge Engine (RAG) | ✅ Complete | Upload PDF/FAQ → AI answers from it |
| Workflow Engine | ✅ Complete | Greet → Qualify → Pitch → Book → End |
| Database Models | ✅ Complete | PostgreSQL (Clients, AI Employees, Leads, Calls) |
| Docker Infrastructure | ✅ Complete | One-command setup |
| GitHub Repository | ✅ Complete | github.com/Tzmicha/AI_OS |
| Terminal Voice Demo | ✅ Working | 4 languages tested, Suhani voice selected |
| Real Phone Calling | 🔄 Next | Need Twilio setup |
| Frontend Dashboard | ❌ Pending | Next.js 15 (after calling works) |
| Authentication | ❌ Pending | Supabase Auth |
| Billing/Payments | ❌ Pending | Razorpay |

---

## 4. Business Model & Revenue

### How We Make Money (3 Revenue Streams)

#### Stream 1: SaaS Dashboard (Monthly Subscription)
Businesses login to our dashboard, create AI Employees, manage calls.

| Plan | Price/Month | Includes | Target Customer |
|------|------------|----------|-----------------|
| Starter | ₹5,000 | 1 AI Employee, 500 min/month | Small business |
| Growth | ₹15,000 | 3 AI Employees, 2000 min/month | Medium business |
| Enterprise | ₹50,000 | Unlimited AI Employees, unlimited calls | Large business |

#### Stream 2: Per-Minute Pricing (Usage-based)
For customers who prefer pay-as-you-go.

| Usage | Price |
|-------|-------|
| Per minute of AI calling | ₹5-10/min |
| Per call (avg 3 min) | ₹15-30/call |
| Per lead qualified | ₹25-50/lead |
| Per appointment booked | ₹50-100/appointment |

#### Stream 3: API Access (For Developers)
Other companies integrate our AI voice into THEIR apps.

| API Plan | Price | Includes |
|----------|-------|----------|
| Developer | ₹2/min | API access, 1000 min/month |
| Business | ₹1.5/min | API access, 10,000 min/month |
| Enterprise | Custom | Unlimited, dedicated support |

---

## 5. Cost Structure (What It Costs US)

### Per Minute Cost Breakdown

| Component | Provider | Cost/Minute | Notes |
|-----------|----------|-------------|-------|
| AI Listening (STT) | Sarvam AI | ₹0.50/min | Speech-to-Text |
| AI Thinking (LLM) | Groq | ₹0.00/min | FREE (LLaMA 3.3) |
| AI Speaking (TTS) | Sarvam AI | ₹0.45/min | Text-to-Speech (Suhani voice) |
| Phone Line | Twilio/SIP | ₹0.50-2.00/min | Telephony |
| Server | Cloud VPS | ₹0.05/min | Infrastructure |
| **TOTAL** | | **₹1.50-3.00/min** | Our cost per minute |

### Per Call Cost (Average 3-minute call)

| Item | Cost |
|------|------|
| Sarvam STT (3 min) | ₹1.50 |
| Sarvam TTS (3 min) | ₹1.35 |
| Groq LLM | ₹0.00 |
| Phone (Twilio) | ₹4.50-6.00 |
| **TOTAL PER CALL** | **₹7.35-8.85** |

### Monthly Fixed Costs

| Item | Cost/Month | Notes |
|------|-----------|-------|
| Cloud Server (VPS) | ₹2,000-5,000 | Runs the AI engine |
| Twilio Phone Number | ₹95 | Per number |
| Domain + SSL | ₹50 | Website |
| **TOTAL FIXED** | **₹2,145-5,145** | Before any calls |

---

## 6. Profit Calculation

### We Charge ₹7/min → Our Cost ₹1.50/min = ₹5.50 PROFIT per minute

| Scenario | Calls/Month | Revenue | Our Cost | PROFIT |
|----------|-------------|---------|----------|--------|
| 5 clients × ₹5,000 | 2,500 min | ₹25,000 | ₹5,000 | ₹20,000 |
| 10 clients × ₹10,000 | 6,000 min | ₹1,00,000 | ₹12,000 | ₹88,000 |
| 25 clients × ₹15,000 | 18,000 min | ₹3,75,000 | ₹35,000 | ₹3,40,000 |
| 50 clients × ₹15,000 | 40,000 min | ₹7,50,000 | ₹70,000 | ₹6,80,000 |
| 100 clients × ₹15,000 | 90,000 min | ₹15,00,000 | ₹1,50,000 | ₹13,50,000 |

---

## 7. Competitor Analysis

### What Others Charge in India

| Competitor | They Charge | What They Offer |
|-----------|-------------|-----------------|
| Qcall.ai | ₹6-14/min | AI calling, Indian numbers |
| Ringg AI | ₹15/min | Voice AI agents |
| Acefone | ₹0.80-3/min | Voice bots (basic) |
| MyOperator | ₹2+/min | Voice AI |
| Vapi | ₹4/min ($0.05) | International AI voice |
| Retell AI | ₹6-17/min | AI voice agents |
| Human telecaller | ₹8-20/min | Traditional call center |

### Our Advantage

| Factor | Competitors | TZMICHA AI OS |
|--------|------------|---------------|
| Telugu support | ❌ Most don't | ✅ Perfect native Telugu |
| Hindi support | ✅ Some | ✅ Perfect native Hindi |
| Language switching | ❌ None | ✅ Auto-switch mid-call |
| Custom AI Employee | ❌ Fixed bots | ✅ Configurable per client |
| Own platform | ❌ Use their dashboard | ✅ White-label possible |
| API for developers | Limited | ✅ Full API access |
| Knowledge base (RAG) | ❌ Most don't | ✅ Upload PDF, AI answers from it |
| Pricing | ₹6-15/min | ₹5-10/min (cheaper) |

---

## 8. Target Industries & Use Cases

| Industry | AI Employee Role | Example |
|----------|-----------------|---------|
| Education | AI Admission Counselor | School posts ad → parent calls → AI explains courses, fees, books campus visit |
| Real Estate | AI Sales Executive | Property ad → customer calls → AI asks budget, explains project, books site visit |
| Healthcare | AI Receptionist | Patient calls clinic → AI books appointment with right doctor |
| Insurance | AI Agent | AI calls leads → explains plans → collects details → qualifies |
| E-commerce | AI Support | Customer calls → AI tracks order, handles returns |
| Restaurants | AI Order Taker | Customer calls → AI takes food order |
| Hotels | AI Booking Agent | Guest calls → AI checks availability, books room |
| Recruitment | AI HR Screener | AI calls candidates → asks basic questions → filters |
| Finance | AI Collection Agent | AI calls for payment reminders |
| Any Business | AI Receptionist | AI answers all incoming calls 24/7 |

---

## 9. Technology Stack

| Layer | Technology | Cost | Why |
|-------|-----------|------|-----|
| AI Brain (LLM) | Groq + LLaMA 3.3 70B | FREE | Fastest response (0.8s) |
| AI Ears (STT) | Sarvam AI | ₹0.50/min | Perfect Telugu/Hindi |
| AI Mouth (TTS) | Sarvam AI (Suhani voice) | ₹0.45/min | Native Indian pronunciation |
| Phone System | Twilio (now) → SIP (later) | ₹0.50-2/min | Real phone calls |
| Backend | FastAPI (Python) | FREE | Fast, modern |
| Database | PostgreSQL | FREE | Enterprise-grade |
| Cache | Redis | FREE | Fast sessions |
| Vector DB | Qdrant | FREE | RAG knowledge search |
| Frontend | Next.js 15 (coming) | FREE | Modern dashboard |
| Hosting | Docker + Cloud VPS | ₹2,000-5,000/mo | Scalable |
| Code Repository | GitHub | FREE | Version control |

---

## 10. Sarvam AI — Our Voice Provider (Details)

### What Is Sarvam AI?
Indian company. Built specifically for Indian languages. Best Telugu/Hindi voice quality available.

### Pricing

| Service | Rate | Unit |
|---------|------|------|
| Text-to-Speech (Bulbul v3) | ₹30 | per 10,000 characters |
| Speech-to-Text | ₹30 | per hour of audio |
| LLM (Sarvam-30B) | ₹2.5 | per million tokens |
| Translation | ₹20 | per 10,000 characters |

### Per Minute Breakdown

| Service | Calculation | Cost/Min |
|---------|------------|----------|
| TTS | ~150 chars/min × ₹30/10K = | ₹0.45/min |
| STT | ₹30/hour ÷ 60 = | ₹0.50/min |

### Free Credits
- Signup: ₹100 free (≈105 minutes of calls)
- That's about 35 test calls (3 min each)

### Available Voices (37 total)

**Female (15):** priya, neha, kavitha, ritu, shreya, ishita, simran, kavya, pooja, roopa, tanya, shruti, suhani, rupali, niharika

**Male (22):** aditya, rahul, rohan, amit, dev, ratan, varun, manan, sumit, kabir, aayan, shubh, ashutosh, advait, anand, tarun, sunny, mani, gokul, vijay, mohit, rehan, soham

**Our selection:** Suhani (Telugu), Kavitha (Hindi), Shreya (English)

### Languages Supported
Telugu, Hindi, Bengali, Tamil, Kannada, Malayalam, Marathi, Gujarati, Punjabi, Odia, English (Indian)

---

## 11. How Inbound Calling Works (Instagram/Facebook Ads)

### The Flow
```
1. You run Instagram/Facebook ad
2. Ad has "Call Now" button with your Twilio number
3. Customer taps "Call Now"
4. Phone rings → AI picks up in 1 second
5. AI: "హాయ్! నేను Priya ని, misha company నుంచి..."
6. Customer talks → AI listens, responds naturally
7. AI qualifies lead → books appointment
8. Call ends → Lead saved → WhatsApp notification sent to you
9. Your sales team follows up with HOT leads only
```

### Why This Is Powerful
| Without AI | With TZMICHA AI |
|-----------|----------------|
| Customer calls → nobody picks up (office closed) | AI picks up 24/7 in 1 second |
| 100 leads call at same time → miss 90 | AI handles ALL 100 simultaneously |
| Weekend/night leads lost | AI works 24/7/365 |
| Telecaller costs ₹15,000-25,000/month | AI costs ₹5,000/month |
| Telecaller handles 50-80 calls/day | AI handles unlimited calls |
| Human gets tired, rude, inconsistent | AI is always friendly, consistent |

---

## 12. Roadmap (What's Next)

| Week | What | Status |
|------|------|--------|
| Week 1 | Voice Engine + All providers + Terminal demo | ✅ DONE |
| Week 2 | Real phone calling (Twilio) + Sentence fix | 🔄 IN PROGRESS |
| Week 3 | Next.js 15 Frontend (Create AI Employee dashboard) | Pending |
| Week 4 | Authentication + API Keys | Pending |
| Week 5 | Billing (Razorpay) + Deploy | Pending |
| Week 6 | Launch MVP + 5 Beta Customers | Pending |
| Month 3 | 20 paying customers | Target |
| Month 6 | 50+ customers, self-host voice for cost reduction | Target |

---

## 13. Cost Summary for MD

### To Build (Development Cost)
| Item | Cost |
|------|------|
| All software/tools | ₹0 (open source) |
| API keys (testing) | ₹0 (free credits) |
| Developer time | Internal team |
| **Total development cost** | **₹0** |

### To Run (Monthly Operating Cost)

**Minimum (starting out):**
| Item | Cost/Month |
|------|-----------|
| Cloud server | ₹2,000 |
| Twilio number | ₹95 |
| Sarvam AI credits | ₹500 (for testing) |
| **Total** | **₹2,595/month** |

**With 10 clients:**
| Item | Cost/Month |
|------|-----------|
| Cloud server | ₹5,000 |
| Twilio calls | ₹15,000 |
| Sarvam AI | ₹10,000 |
| **Total** | **₹30,000/month** |
| **Revenue (10 × ₹10K)** | **₹1,00,000/month** |
| **PROFIT** | **₹70,000/month** |

**With 50 clients:**
| Item | Cost/Month |
|------|-----------|
| Infrastructure | ₹70,000 |
| **Revenue (50 × ₹15K)** | **₹7,50,000/month** |
| **PROFIT** | **₹6,80,000/month** |

---

## 14. Key Decisions Made

| Decision | What We Chose | Why |
|----------|--------------|-----|
| Voice Provider | Sarvam AI | Best Telugu/Hindi quality, Indian company, cheap |
| LLM | Groq (LLaMA 3.3) | Fastest (0.8s), FREE |
| Phone | Twilio (now), SIP (later) | Quick setup, then cheaper at scale |
| Architecture | Provider-independent | Can switch any provider by changing config |
| Language | Telugu + Hindi + English + British | Indian market focus |
| Frontend | Next.js 15 | SEO + Dashboard in one |
| Database | PostgreSQL | Enterprise-grade, free |
| Hosting | Docker | One-command deploy anywhere |

---

## 15. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Sarvam AI goes down | Calls fail | Architecture supports fallback to ElevenLabs/Edge TTS |
| Groq rate limited | Slow responses | Can switch to Ollama/OpenAI instantly |
| Voice sounds robotic | Customers hang up | Multiple voice options, continuously improving prompts |
| Competitors copy | Lose advantage | Speed to market + Telugu focus + better pricing |
| Twilio expensive at scale | Lower margins | Move to SIP trunk (₹0.50/min vs ₹2/min) |

---

## 16. Daily Progress Log

### Day 1 (July 22, 2026)
- Full project audit of old codebase
- Designed TZMICHA AI OS architecture
- Built Voice AI Engine (all providers)
- Built Conversation Engine, Memory, Language Detection
- Built RAG Knowledge Engine + Workflow Engine
- Got API keys: Groq ✅, Deepgram ✅, ElevenLabs ✅
- All APIs verified working
- Professional project structure created
- Pushed to GitHub: github.com/Tzmicha/AI_OS

### Day 2 (July 23, 2026)
- Fixed audio playback (Windows MCI)
- Tested ElevenLabs voices (audio cutoff issue)
- Voice quality improvements (prompts, settings)

### Day 3 (July 27, 2026 - Monday)
- Discovered Sarvam AI (perfect Indian language voices)
- Integrated Sarvam AI TTS (₹0.45/min, native Telugu)
- Tested all 37 voices — selected Suhani for Telugu
- Fixed sentence cutoff (max_tokens + auto-trim)
- LLM now generates Telugu in native script (తెలుగు)
- Updated complete documentation for MD review
- Next: Real phone calling (Twilio integration)

---

**GitHub:** https://github.com/Tzmicha/AI_OS
**Branches:** main (production) | develop (daily work)

---

*Last Updated: July 27, 2026*
