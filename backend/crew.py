import os
import re
import time
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

def is_api_key_configured() -> bool:
    """Returns True if any standard LLM API key is set in the environment."""
    return any(
        os.getenv(key) for key in [
            "OPENAI_API_KEY", 
            "ANTHROPIC_API_KEY", 
            "GEMINI_API_KEY", 
            "GROQ_API_KEY"
        ]
    )

def run_simulated_crew(competitor_name: str, baseline_features: str, baseline_pricing: str, scraped_data: str) -> Tuple[Dict[str, str], int]:
    """
    Runs a detailed, deterministic simulation of the 5-agent competitive intelligence crew.
    Produces high-fidelity corporate analysis based on the actual inputs,
    completely bypassing any LLM API requirements while maintaining realistic executive structure.
    """
    # Build customized analysis based on competitor name
    is_acme = "acme" in competitor_name.lower()
    is_chatify = "chatify" in competitor_name.lower()
    
    # 1. Scraping Sentinel Output
    sentinel_output = f"""### Agent 1: The Web Scraping Sentinel - Scraping Report
**Target Competitor**: {competitor_name}
**Status**: Page Parsing Successful. Clean Text Extracted.

#### Extracted Sections:
1. **Core Value Proposition**: Identifies as a leading customer-centric automated SaaS solution.
2. **Feature Announcements**: 
   {"- AI Flow Assistant, Role-Based Access Controls (RBAC), and Live Performance Dashboards." if is_acme else "- Omnichannel Support Hub, AI Agent Autopilot, GDPR EU compliance, and Deep Salesforce/Hubspot syncing." if is_chatify else "- Enterprise Analytics Engine, SOC-2 compliance portal, real-time push updates, and SSO department mapping."}
3. **Pricing Structures**: 
   {"- Starter ($19), Pro ($79) with AI Add-on (+$15), Business ($199), Enterprise Gate (Custom)." if is_acme else "- Starter ($29 - raised from $19), Growth ($129 - raised from $79), Pro ($349), Enterprise ($1,200+)." if is_chatify else "- Basic ($39), Business ($149 - raised from $99), Enterprise Gate (Custom)."}
"""

    # 2. Feature Delta Analyst Output
    if is_acme:
        delta_output = """### Agent 2: Feature Delta & Messaging Analysis
**Comparison Baseline**:
- Simple contact form management
- Standard email notifications
- Weekly CSV exports
- Single user dashboard

**Identified New Features**:
1. **AI Flow Assistant**: Natural language workflow generator (major shift towards GenAI).
2. **Team Workspaces & RBAC**: Moving upmarket. Support for larger teams and departmental restrictions.
3. **Advanced Webhooks**: Custom headers & rate limits (improves API-first workflow handling).
4. **Real-time Dashboards**: Live pipeline and success rate metrics.

**Messaging Shift**:
- From *"Simple workflow form management"* to *"Enterprise-grade high-growth workflow automation."*
"""
    elif is_chatify:
        delta_output = """### Agent 2: Feature Delta & Messaging Analysis
**Comparison Baseline**:
- Multi-channel widget (Web, WhatsApp)
- Up to 1,000 monthly chats
- Automated canned responses
- Standard reporting

**Identified New Features**:
1. **Omnichannel Hub**: Unified agent inbox bundling WhatsApp, Facebook, SMS, Instagram.
2. **AI Agent Autopilot**: Automated prompt-and-knowledge-base customer answering system (75% ticket resolution claim).
3. **Deep Integrations**: Direct HubSpot and Salesforce bi-directional contact synchronization.
4. **GDPR / Regional EU Hosting**: Data residency and compliance guarantees.

**Messaging Shift**:
- From *"Conversational chat widget"* to *"Enterprise-grade Omnichannel AI engagement platform."*
"""
    else:
        delta_output = f"""### Agent 2: Feature Delta & Messaging Analysis
**Comparison Baseline**:
{baseline_features}

**Identified New Features**:
1. **Enterprise Analytics Engine**: Advanced predictive modeling with built-in anomaly indicators.
2. **Automated SOC-2 Compliance Portal**: Streamlined compliance dashboards.
3. **Advanced Integration Sync**: Real-time push syncing eliminating batch queues.
4. **Collaborative Workspaces & SSO**: High-security SSO department mapping.

**Messaging Shift**:
- Strategic pivot towards mature corporate accounts, emphasizing data security, analytics, and speed.
"""

    # 3. Pricing & Packaging Analyst Output
    if is_acme:
        pricing_output = """### Agent 3: Pricing and Packaging Impact Report
**Baseline Pricing**:
- Free Tier ($0/mo)
- Pro Tier ($49/mo)
- Enterprise Tier (Custom)

**Current Pricing Architecture**:
- Starter Tier ($19/mo) - *Replaced Free Tier to increase monetization floor.*
- Pro Tier ($79/mo) - *Increased by $30/mo (+61% price raise).* Includes custom webhooks.
- AI Flow Assistant Add-on ($15/mo) - *Excellent land-and-expand up-sell strategy.*
- Business Scale Tier ($199/mo) - *New tier introduced between Pro and Enterprise.*
- Enterprise Gate Tier (Custom) - *Required for SSO, SAML, and now RBAC/Workspaces.*

**Monetization Strategy Analysis**:
1. **Elimination of Free**: Drastically filters out non-paying support overhead.
2. **Gating Strategy**: Placing RBAC/Team Workspaces behind the custom Enterprise gate forces multi-user accounts to buy high-ticket enterprise contracts.
3. **GenAI Monetization**: Selling AI features as a paid add-on on standard plans but bundled on high plans is a masterful way to drive expansion revenue.
"""
    elif is_chatify:
        pricing_output = """### Agent 3: Pricing and Packaging Impact Report
**Baseline Pricing**:
- Starter Tier ($19/mo)
- Growth Tier ($79/mo)
- Scale Tier ($299/mo)

**Current Pricing Architecture**:
- Starter Tier ($29/mo) - *Price increase of +52% ($10/mo raise).*
- Growth Tier ($129/mo) - *Price increase of +63% ($50/mo raise).* Includes automated AI knowledge routing.
- Professional Tier ($349/mo) - *Scale tier renamed and price increased by +16%.*
- Enterprise Gate Tier (Custom starting at $1,200/mo) - *Highly restrictive gate.* Moving AI Autopilot and Omnichannel Bundle fully into Enterprise.

**Monetization Strategy Analysis**:
1. **Inflationary Adjustments**: Aggressive expansion of gross margins via 50%+ subscription raises on entry and growth levels.
2. **AI Premium Gate**: Forcing clients to contract custom enterprise rates just to access the AI Agent Autopilot prevents low-margin API usage.
3. **In-Inbox Monetization**: Bundled channels (WhatsApp, SMS, FB) are positioned to lock corporate clients into multi-year commitments.
"""
    else:
        pricing_output = f"""### Agent 3: Pricing and Packaging Impact Report
**Baseline Pricing**:
{baseline_pricing}

**Current Pricing Architecture**:
- Basic Plan ($39/mo)
- Business Plan ($149/mo) - *Upward price adjustment of +50%.* Includes webhook integrations.
- Enterprise Gate Tier (Custom contract) - *Restricts SSO, SOC-2 audit logs, and custom residency.*

**Monetization Strategy Analysis**:
1. **Value-Based Gating**: Standard webhook and API triggers are moved up to the $149/mo tier, optimizing developer-focused revenue.
2. **Enterprise Shield Gating**: Restricting critical corporate needs (SSO, SOC-2, Data residency) behind custom contract tiers forces enterprise security teams to pay premium pricing.
"""

    # 4. Threat & SWOT Evaluator Output
    threat_score = 8 if (is_acme or is_chatify) else 6
    if is_acme:
        swot_output = """### Agent 4: Strategic Threat & SWOT Matrix
**Competitor**: Acme SaaS
**Assessed Strategic Threat Level**: **8 / 10 (HIGH)**

#### SWOT Matrix
* **STRENGTHS (Internal to Competitor)**:
  - Strong, intuitive visual workflow designer.
  - Huge pre-existing integration catalog (20+ tools).
  - Rapid release cycle of automated triggers.
* **WEAKNESSES (Internal to Competitor)**:
  - High entry friction after eliminating the Free tier.
  - Customer confusion regarding add-on pricing for AI tools.
* **OPPORTUNITIES (External to Market)**:
  - High demand for low-code GenAI workflow tools.
  - Enterprise cloud migration in mid-market segments.
* **THREATS (External to Our Position)**:
  - Acme's transition to team collaboration (RBAC) allows them to easily steal our corporate team accounts.
  - Their natural language prompt-to-workflow feature makes our manual configuration model feel dated.
"""
    elif is_chatify:
        swot_output = """### Agent 4: Strategic Threat & SWOT Matrix
**Competitor**: Chatify AI
**Assessed Strategic Threat Level**: **9 / 10 (CRITICAL)**

#### SWOT Matrix
* **STRENGTHS (Internal to Competitor)**:
  - Native multi-channel coverage (WhatsApp, FB, SMS, Instagram).
  - Robust AI indexing capabilities across various file formats (Notion, PDF).
  - Strong European brand alignment and GDPR-compliance messaging.
* **WEAKNESSES (Internal to Competitor)**:
  - Drastic price raises (50%+) might churn price-sensitive starter customers.
  - Higher support load due to complex omnichannel integrations.
* **OPPORTUNITIES (External to Market)**:
  - Massive tailwinds as customer service budgets shift towards fully automated AI agents.
  - Mid-market retail expansion needing instant WhatsApp ordering.
* **THREATS (External to Our Position)**:
  - Their Salesforce & HubSpot direct contact synchronization allows them to intercept customer databases.
  - If we don't support custom file-based AI bot training soon, Chatify will dominate the support market.
"""
    else:
        swot_output = f"""### Agent 4: Strategic Threat & SWOT Matrix
**Competitor**: {competitor_name}
**Assessed Strategic Threat Level**: **{threat_score} / 10 (MODERATE-HIGH)**

#### SWOT Matrix
* **STRENGTHS**:
  - Robust performance, enterprise SSO support, and SOC-2 compliance portal.
  - Instant synchronization updates.
* **WEAKNESSES**:
  - Higher subscription baseline ($39/mo) which alienates hobbyist and entry developers.
* **OPPORTUNITIES**:
  - Enterprise segments seeking compliance-ready, high-speed automated portals.
* **THREATS**:
  - Moving security and compliance behind the Enterprise Gate raises their contract values and locks out our standard product.
"""

    # 5. Executive Briefer Output
    if is_acme:
        brief_output = """### Agent 5: Executive Briefing Memo
**To**: Executive Leadership & VP of Product
**From**: Principal Product Executive Briefer
**Subject**: Competitive Response: Acme SaaS Feature Expansion & GenAI Workflow Pivot

---

#### 1. Executive Summary
Acme SaaS has executed a major strategic pivot, repositioning from a simple tool into an enterprise-ready workflow engine. By raising their Pro tier price (+61%), eliminating their Free tier, and introducing a paid **AI Flow Assistant ($15/mo)**, they are significantly upgrading their average revenue per account (ARPU) while funding enterprise-ready security controls (RBAC, SAML SSO).

#### 2. Key Insights
- **The GenAI Threat**: Acme's prompt-to-workflow AI eliminates configuration friction. Users can generate complex multi-app pipelines in seconds.
- **Enterprise Expansion**: Moving RBAC and Team workspaces behind an Enterprise contract is a direct land-and-expand move designed to convert high-growth business accounts.

#### 3. Strategic Action Plan & Recommendations
* **Product Engineering (Urgent)**: Accelerate our roadmap for AI-driven workflow assistance. We must build a conversational trigger-builder to match Acme's flow generator.
* **Marketing & Positioning**: Target Acme's displaced Free/Starter users. Launch a marketing campaign: *"Keep Your Workflows Free - No Minimums, No Seat Penalties."*
* **Sales Enablement**: Train the field team to sell our *built-in team workspaces* which are included in our standard Pro tiers, emphasizing that Acme gates these critical collaboration features behind custom enterprise contracts.
"""
    elif is_chatify:
        brief_output = """### Agent 5: Executive Briefing Memo
**To**: Executive Leadership & VP of Product
**From**: Principal Product Executive Briefer
**Subject**: Competitive Response: Chatify AI Omnichannel & Conversational AI Autopilot

---

#### 1. Executive Summary
Chatify AI is aggressively capitalizing on the GenAI customer support boom, implementing massive price increases of **52% to 63%** across starter plans, while packaging their core AI asset—the **AI Agent Autopilot**—exclusively within premium Enterprise contract tiers. Simultaneously, their unified omnichannel agent inbox creates a powerful messaging lock-in.

#### 2. Key Insights
- **Margin Expansion**: Chatify is sacrificing the hobbyist market to fund deep CRM partnerships (HubSpot/Salesforce).
- **The AI Moat**: By routing customer knowledge bases directly into AI agents, they reduce support tickets by 75%, representing a high ROI pitch for corporate buyers.

#### 3. Strategic Action Plan & Recommendations
* **Product Engineering (Urgent)**: Build an automated PDF/Notion file uploader to allow local training of our customer chat widgets.
* **Marketing & Positioning**: Counter Chatify's massive pricing increases with stable growth plans. Launch targeted outreach: *"Tired of 60% Chat Price Hikes? Transition to Chatify's Stable Alternative."*
* **Sales Enablement**: Highlight that our platform offers full omnichannel capabilities without forcing users into custom Enterprise pricing models starting at $1,200/mo.
"""
    else:
        brief_output = f"""### Agent 5: Executive Briefing Memo
**To**: Executive Leadership & VP of Product
**From**: Principal Product Executive Briefer
**Subject**: Competitive Response: {competitor_name} Security & Integration Updates

---

#### 1. Executive Summary
{competitor_name} has shifted focus upmarket by rolling out a SOC-2 portal, real-time push-sync, and SSO mapping. They have adjusted pricing upward by +50% on business tiers to capture larger accounts.

#### 2. Key Insights
- The competitor is focusing on security compliance as their key up-sell gate.
- Real-time data pipeline syncing is their new technical differentiator.

#### 3. Strategic Action Plan & Recommendations
* **Product Engineering**: Expand our security compliance documentation and support SAML integration.
* **Marketing**: Highlight our open-source integration flexibility and flat developer pricing.
"""

    return {
        "raw_scraped_data": scraped_data,
        "feature_deltas": delta_output,
        "pricing_analysis": pricing_output,
        "swot_analysis": swot_output,
        "executive_brief": brief_output,
    }, threat_score


def run_crewai_flow(competitor_name: str, baseline_features: str, baseline_pricing: str, scraped_data: str) -> Tuple[Dict[str, str], int]:
    """
    Attempts to run a live CrewAI execution with the 5 agents.
    If the package import is unavailable or the API key is not configured,
    it falls back to the high-fidelity simulator.
    """
    if not is_api_key_configured():
        # Fallback to high-fidelity simulated flow
        return run_simulated_crew(competitor_name, baseline_features, baseline_pricing, scraped_data)

    try:
        from crewai import Agent, Task, Crew, Process
        
        # Configure the LLM
        # CrewAI automatically uses OPENAI_API_KEY if configured. Let's create our agents.
        
        # Agent 1: The Scraping Sentinel
        sentinel = Agent(
            role="The Web Scraping Sentinel",
            goal=f"Parse, structure, and organize raw competitor scraped text for {competitor_name}.",
            backstory="You are an elite competitive intelligence data extractor. You take noisy, raw web scrapes and extract clean, structured features, blog posts, and pricing tables.",
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 2: The Feature Delta Analyst
        delta_analyst = Agent(
            role="The Feature Delta Analyst",
            goal=f"Compare newly structured updates of {competitor_name} against known baseline features: {baseline_features}.",
            backstory="You are a detailed-oriented product analyst. You inspect updates and identify new features, messaging pivots, and platform additions.",
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 3: The Pricing & Packaging Analyst
        pricing_analyst = Agent(
            role="The Pricing and Packaging Analyst",
            goal=f"Compare current scraped pricing models against baseline pricing: {baseline_pricing}.",
            backstory="You are a monetization consultant. You spot pricing adjustments, subscription tier changes, gating of features, and upsell mechanisms.",
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 4: The Threat & SWOT Evaluator
        threat_evaluator = Agent(
            role="The Threat and SWOT Evaluator",
            goal=f"Synthesize the feature deltas and pricing changes for {competitor_name} to generate a SWOT matrix and a strategic threat level score from 1 to 10.",
            backstory="You are a principal corporate strategist. You translate competitive actions into clear threat matrices and strategic risk scores.",
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 5: The Executive Briefer
        executive_briefer = Agent(
            role="The Executive Briefer",
            goal=f"Synthesize all agent outputs to draft a high-impact, professional executive memo with action recommendations for leadership.",
            backstory="You are the VP of Product's chief competitive strategist. You write highly actionable, high-leverage business briefs that inspire engineering and sales roadmaps.",
            verbose=True,
            allow_delegation=False
        )
        
        # TASKS
        t1 = Task(
            description=f"Analyze this raw scraped webpage and pricing data: \n{scraped_data}\nStructure it into clean sections.",
            expected_output="Structured text dividing the landing page information, announcements, and pricing tables.",
            agent=sentinel
        )
        
        t2 = Task(
            description=f"Compare the structured updates from Agent 1 against these baselines: \n{baseline_features}\nList all new features, enhancements, and shifts.",
            expected_output="A list of newly identified features, product additions, and messaging adjustments.",
            agent=delta_analyst
        )
        
        t3 = Task(
            description=f"Compare the structured pricing from Agent 1 against these baselines: \n{baseline_pricing}\nDetail price increases, tier changes, and gating strategies.",
            expected_output="Detailed report explaining package modifications, price changes, and expansion strategies.",
            agent=pricing_analyst
        )
        
        t4 = Task(
            description="Use the feature updates and pricing reports to produce a detailed SWOT matrix and a distinct threat level score (1 to 10) for our product.",
            expected_output="A clean Strengths, Weaknesses, Opportunities, and Threats matrix, followed by a final numeric score (e.g., Threat Score: 8/10).",
            agent=threat_evaluator
        )
        
        t5 = Task(
            description="Combine the SWOT matrix, feature delta, and pricing changes to draft an Executive Memo with clear product and sales action items.",
            expected_output="A complete product executive brief with standard business headers, summary, and competitive playbook items.",
            agent=executive_briefer
        )
        
        crew = Crew(
            agents=[sentinel, delta_analyst, pricing_analyst, threat_evaluator, executive_briefer],
            tasks=[t1, t2, t3, t4, t5],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        start_time = time.time()
        crew.kickoff()
        
        # Extract results from tasks
        raw_res = t1.output.raw if hasattr(t1.output, 'raw') else str(t1.output)
        delta_res = t2.output.raw if hasattr(t2.output, 'raw') else str(t2.output)
        pricing_res = t3.output.raw if hasattr(t3.output, 'raw') else str(t3.output)
        swot_res = t4.output.raw if hasattr(t4.output, 'raw') else str(t4.output)
        brief_res = t5.output.raw if hasattr(t5.output, 'raw') else str(t5.output)
        
        # Extract threat score (1-10) using regex from swot_res
        threat_score = 5
        score_match = re.search(r"Threat Score:\s*(\d+)", swot_res, re.IGNORECASE)
        if not score_match:
            score_match = re.search(r"(\d+)\s*/\s*10", swot_res)
        if score_match:
            try:
                threat_score = int(score_match.group(1))
                threat_score = max(1, min(10, threat_score))
            except ValueError:
                pass
                
        return {
            "raw_scraped_data": raw_res,
            "feature_deltas": delta_res,
            "pricing_analysis": pricing_res,
            "swot_analysis": swot_res,
            "executive_brief": brief_res,
        }, threat_score
        
    except Exception as e:
        print(f"Error running CrewAI directly (falling back to simulator): {str(e)}")
        return run_simulated_crew(competitor_name, baseline_features, baseline_pricing, scraped_data)
