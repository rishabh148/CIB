import os
import re
import time
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

# Load environmental variables
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

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

def _clean_line(line: str) -> str:
    """Normalize markdown-ish scrape lines without changing their meaning."""
    return re.sub(r"\s+", " ", line.strip(" \t-*#")).strip()


def _extract_candidate_lines(text: str) -> List[str]:
    candidates: List[str] = []
    for raw_line in text.splitlines():
        line = _clean_line(raw_line)
        if not line or line.startswith("==="):
            continue
        has_signal = (
            raw_line.lstrip().startswith(("-", "1.", "2.", "3.", "4.", "5."))
            or "**" in raw_line
            or "$" in line
            or ":" in line
        )
        if has_signal and len(line) > 6:
            candidates.append(line.replace("**", ""))
    return candidates


def _extract_feature_lines(scraped_data: str) -> List[str]:
    price_words = ("tier", "plan", "$", "pricing", "contract", "custom pricing", "previously", "/mo")
    feature_words = (
        "assistant", "workspace", "access", "rbac", "webhook", "dashboard",
        "integration", "hub", "autopilot", "salesforce", "hubspot", "gdpr",
        "hosting", "analytics", "compliance", "sync", "sso", "ai", "feature",
    )
    features: List[str] = []
    for line in _extract_candidate_lines(scraped_data):
        lower = line.lower()
        if any(word in lower for word in price_words) and not any(word in lower for word in feature_words):
            continue
        if any(word in lower for word in feature_words):
            features.append(line)
    return _dedupe_keep_order(features)


def _extract_pricing_lines(scraped_data: str) -> List[str]:
    pricing_lines: List[str] = []
    in_pricing_section = False
    for raw_line in scraped_data.splitlines():
        stripped = raw_line.strip()
        line = _clean_line(raw_line).replace("**", "")
        lower = line.lower()
        if not line or line.startswith("==="):
            continue

        is_heading = stripped.startswith("#")
        is_pricing_heading = is_heading and any(
            word in lower for word in ("pricing", "plans", "tiers", "subscriptions")
        )
        if is_pricing_heading:
            in_pricing_section = True
            pricing_lines.append(line)
            continue
        if is_heading and in_pricing_section and not is_pricing_heading:
            in_pricing_section = False

        has_math_dollar_markup = "$$$" in line
        explicit_price_line = (
            not has_math_dollar_markup
            and (
                bool(re.search(r"\$\s?\d", line))
                or "/mo" in lower
                or "previously" in lower
                or " usd" in lower
            )
        )
        named_package_line = any(word in lower for word in ("tier", " plan", "gate tier", "custom contract"))
        if explicit_price_line or (in_pricing_section and named_package_line):
            pricing_lines.append(line)

    return _dedupe_keep_order(pricing_lines)


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    deduped: List[str] = []
    for item in items:
        key = re.sub(r"[^a-z0-9]+", " ", item.lower()).strip()
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def _tokens(text: str) -> set:
    stop_words = {
        "the", "and", "with", "for", "from", "this", "that", "into", "your",
        "our", "are", "was", "were", "has", "have", "had", "includes", "up",
        "to", "of", "in", "a", "an", "mo", "tier", "plan",
    }
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in stop_words and len(token) > 2}


def _is_new_against_baseline(item: str, baseline: str) -> bool:
    item_tokens = _tokens(item)
    baseline_tokens = _tokens(baseline)
    if not item_tokens:
        return False
    overlap = len(item_tokens & baseline_tokens) / max(len(item_tokens), 1)
    return overlap < 0.45


def _extract_price_movements(pricing_lines: List[str]) -> List[str]:
    movements: List[str] = []
    for line in pricing_lines:
        previous_match = re.search(r"\$(\d+(?:,\d{3})*)(?:/mo)?\s*\(previously\s*\$(\d+(?:,\d{3})*)", line, re.IGNORECASE)
        if previous_match:
            current = previous_match.group(1)
            previous = previous_match.group(2)
            movements.append(f"{line} (observed increase from ${previous}/mo to ${current}/mo)")
        elif ("$$$" not in line and "$" in line) or "custom" in line.lower() or "gate" in line.lower():
            movements.append(line)
    return _dedupe_keep_order(movements)


def _format_bullets(items: List[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def _build_structured_scrape(competitor_name: str, scraped_data: str, feature_lines: List[str], pricing_lines: List[str]) -> str:
    return (
        f"Scraping Sentinel Report: {competitor_name}\n\n"
        "Observed product, feature, and positioning signals:\n"
        f"{_format_bullets(feature_lines, 'No explicit feature signals were found in the scraped content.')}\n\n"
        "Observed pricing and packaging signals:\n"
        f"{_format_bullets(pricing_lines, 'No explicit pricing signals were found in the scraped content.')}\n\n"
        "Source scrape used by downstream agents:\n"
        f"{scraped_data}"
    )


def _score_threat(new_features: List[str], price_movements: List[str], pricing_lines: List[str]) -> int:
    score = 3
    score += min(len(new_features), 5)
    if price_movements:
        score += 1
    if any("enterprise" in line.lower() or "gate" in line.lower() for line in pricing_lines):
        score += 1
    if any("ai" in line.lower() or "automation" in line.lower() for line in new_features):
        score += 1
    return max(1, min(10, score))


def _crawl_failed_without_evidence(scraped_data: str) -> bool:
    return "=== LIVE CRAWL FAILED FOR CUSTOM COMPETITOR:" in scraped_data


def run_simulated_crew(competitor_name: str, baseline_features: str, baseline_pricing: str, scraped_data: str) -> Tuple[Dict[str, str], int]:
    """
    Runs a detailed, deterministic simulation of the 5-agent competitive intelligence crew.
    Produces high-fidelity corporate analysis based on the actual inputs,
    completely bypassing any LLM API requirements while maintaining realistic executive structure.
    """
    if _crawl_failed_without_evidence(scraped_data):
        no_evidence = (
            f"No verified competitive intelligence could be produced for {competitor_name} because the live crawl failed. "
            "No simulated features, pricing, SWOT claims, or recommendations were generated."
        )
        return {
            "raw_scraped_data": scraped_data,
            "feature_deltas": (
                f"Feature Delta Analyst Report: {competitor_name}\n\n"
                f"{no_evidence}\n\n"
                "Action required: use a publicly crawlable URL or provide manually captured source text."
            ),
            "pricing_analysis": (
                f"Pricing and Packaging Analyst Report: {competitor_name}\n\n"
                f"{no_evidence}\n\n"
                "No pricing movement can be asserted from the available scrape."
            ),
            "swot_analysis": (
                f"Threat and SWOT Evaluator Report: {competitor_name}\n\n"
                "SWOT unavailable: no verified source evidence was captured.\n\n"
                "Threat Score: 1/10"
            ),
            "executive_brief": (
                f"Executive Brief: {competitor_name}\n\n"
                f"{no_evidence}\n\n"
                "Recommended next step: rerun with a crawlable page or add a manual evidence capture workflow before drawing conclusions."
            ),
        }, 1

    feature_lines = _extract_feature_lines(scraped_data)
    pricing_lines = _extract_pricing_lines(scraped_data)
    new_features = [line for line in feature_lines if _is_new_against_baseline(line, baseline_features)]
    pricing_changes = [line for line in pricing_lines if _is_new_against_baseline(line, baseline_pricing)]
    price_movements = _extract_price_movements(pricing_changes or pricing_lines)
    threat_score = _score_threat(new_features, price_movements, pricing_lines)

    structured_scrape = _build_structured_scrape(competitor_name, scraped_data, feature_lines, pricing_lines)

    feature_deltas = (
        f"Feature Delta Analyst Report: {competitor_name}\n\n"
        "Baseline compared:\n"
        f"{baseline_features or 'No baseline features supplied.'}\n\n"
        "New or materially expanded scraped feature signals:\n"
        f"{_format_bullets(new_features, 'No feature delta was found beyond the supplied baseline.')}\n\n"
        "Evidence discipline: every item above is copied or condensed from the scraping sentinel source."
    )

    pricing_analysis = (
        f"Pricing and Packaging Analyst Report: {competitor_name}\n\n"
        "Baseline compared:\n"
        f"{baseline_pricing or 'No baseline pricing supplied.'}\n\n"
        "Scraped pricing and packaging observations:\n"
        f"{_format_bullets(pricing_changes or pricing_lines, 'No pricing or packaging data was found in the scrape.')}\n\n"
        "Explicit price movement or gating signals:\n"
        f"{_format_bullets(price_movements, 'No explicit price movement or gating signal was found.')}"
    )

    strength_items = new_features[:3] or feature_lines[:2]
    weakness_items = price_movements[:2] or pricing_changes[:2]
    opportunities = [
        f"Counter-position against {competitor_name}'s scraped launches with roadmap, enablement, or packaging updates."
    ] if new_features or pricing_lines else ["Maintain monitoring until more competitor evidence is available."]
    threats = [
        f"{competitor_name} is showing {len(new_features)} feature delta signal(s) and {len(price_movements)} pricing/package signal(s) in the latest scrape."
    ]

    swot_analysis = (
        f"Threat and SWOT Evaluator Report: {competitor_name}\n\n"
        "Strengths observed in competitor scrape:\n"
        f"{_format_bullets(strength_items, 'No clear competitor strength was found.')}\n\n"
        "Weaknesses or friction points observed:\n"
        f"{_format_bullets(weakness_items, 'No clear weakness or pricing friction was found.')}\n\n"
        "Opportunities for our response:\n"
        f"{_format_bullets(opportunities, 'No specific opportunity was identified.')}\n\n"
        "Threats:\n"
        f"{_format_bullets(threats, 'No specific threat was identified.')}\n\n"
        f"Threat Score: {threat_score}/10"
    )

    executive_brief = (
        f"Executive Brief: {competitor_name}\n\n"
        f"Summary: The latest scrape for {competitor_name} shows "
        f"{len(new_features)} feature delta signal(s) and {len(price_movements)} pricing/package signal(s) versus the configured baseline.\n\n"
        "Product actions:\n"
        f"{_format_bullets(new_features[:4], 'No immediate product action is supported by the scrape.')}\n\n"
        "Commercial actions:\n"
        f"{_format_bullets(price_movements[:4], 'No immediate pricing action is supported by the scrape.')}\n\n"
        f"Recommended priority: Treat as threat level {threat_score}/10 and keep the next analysis tied to fresh scrape evidence."
    )

    simulated_output = {
        "raw_scraped_data": structured_scrape,
        "feature_deltas": feature_deltas,
        "pricing_analysis": pricing_analysis,
        "swot_analysis": swot_analysis,
        "executive_brief": executive_brief,
    }
    return simulated_output, threat_score


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
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Configure the LLM to use Gemini
        # Ensure GEMINI_API_KEY is set in your .env file or environment variables
        gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro", verbose=True, temperature=0.1, google_api_key=os.getenv("GEMINI_API_KEY"))
        
        # Agent 1: The Scraping Sentinel
        sentinel = Agent(
            role="The Web Scraping Sentinel",
            goal=f"Parse, structure, and organize raw competitor scraped text for {competitor_name}. Focus on extracting factual information regarding features, blog posts, and pricing tables, avoiding any speculative content.",
            backstory="You are an elite competitive intelligence data extractor. Your primary function is to meticulously analyze raw web scrapes and extract only verifiable, clean, and structured data, specifically focusing on competitor features, blog posts, and pricing. You are designed to prevent hallucination by strictly adhering to the provided text and not inferring or generating information not explicitly present.",
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )
        
        # Agent 2: The Feature Delta Analyst
        delta_analyst = Agent(
            role="The Feature Delta Analyst",
            goal=f"Compare newly structured updates of {competitor_name} against known baseline features: {baseline_features}. Focus on identifying concrete new features, messaging pivots, and platform additions that are explicitly stated in the structured data, without making assumptions or extrapolations.",
            backstory="You are a highly detailed and fact-checking product analyst. Your role is to rigorously inspect updates and identify new features, messaging pivots, and platform additions based *only* on the structured data provided. You must avoid any form of hallucination by sticking strictly to the evidence and not generating information that isn't directly supported by the input.",
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )
        
        # Agent 3: The Pricing & Packaging Analyst
        pricing_analyst = Agent(
            role="The Pricing and Packaging Analyst",
            goal=f"Compare current scraped pricing models against baseline pricing: {baseline_pricing}. Your analysis must be purely factual, detailing only observed price increases, subscription tier changes, feature gating, and upsell mechanisms as presented in the data, without speculation.",
            backstory="You are a precise monetization consultant. Your expertise lies in accurately identifying pricing adjustments, subscription tier changes, feature gating, and upsell mechanisms directly from the provided data. You are programmed to be highly accurate and to avoid hallucination by only reporting what is explicitly evident in the pricing structures.",
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )
        
        # Agent 4: The Threat & SWOT Evaluator
        threat_evaluator = Agent(
            role="The Threat and SWOT Evaluator",
            goal=f"Synthesize the feature deltas and pricing changes for {competitor_name} to generate a factual SWOT matrix and a strategic threat level score from 1 to 10. Every point in the SWOT matrix and the threat score must be directly derivable from the preceding agent outputs, ensuring no new or unsubstantiated information is introduced.",
            backstory="You are a principal corporate strategist with a commitment to factual reporting. You translate competitive actions into clear threat matrices and strategic risk scores, but only based on the verified data provided by previous agents. You are strictly against hallucination, ensuring all insights are evidence-based and directly traceable to the input.",
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )
        
        # Agent 5: The Executive Briefer
        executive_briefer = Agent(
            role="The Executive Briefer",
            goal=f"Synthesize all agent outputs to draft a high-impact, professional executive memo with action recommendations for leadership. The memo must strictly adhere to the factual information provided by the preceding agents, avoiding any form of hallucination or introduction of new, unverified details. All recommendations must be directly supported by the synthesized data.",
            backstory="You are the VP of Product's chief competitive strategist, renowned for drafting highly actionable, high-leverage business briefs that strictly adhere to verified data. You inspire engineering and sales roadmaps by ensuring all insights and recommendations are grounded in factual competitive intelligence, thereby preventing any hallucination in strategic guidance.",
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )
        
        # TASKS
        t1 = Task(
            description=f"Analyze this raw scraped webpage and pricing data: \n{scraped_data}\nStructure it into clean sections. The output must strictly contain information found in the input, without any embellishment or fabrication.",
            expected_output="Structured text accurately dividing the landing page information, announcements, and pricing tables, directly reflecting the content of the scraped data.",
            agent=sentinel
        )
        
        t2 = Task(
            description=f"Compare the structured updates from Agent 1 against these baselines: \n{baseline_features}\nList all new features, enhancements, and shifts. Ensure every item listed is directly verifiable from the provided inputs, and do not introduce any new information.",
            expected_output="A list of newly identified features, product additions, and messaging adjustments, all of which are explicitly supported by the comparison data.",
            agent=delta_analyst,
            context=[t1]
        )
        
        t3 = Task(
            description=f"Compare the structured pricing from Agent 1 against these baselines: \n{baseline_pricing}\nDetail price increases, tier changes, and gating strategies. The report must be strictly factual, based only on the provided pricing data, and must not include any speculative analysis.",
            expected_output="Detailed, factual report explaining package modifications, precise price changes, and explicit expansion strategies as identified from the structured pricing data.",
            agent=pricing_analyst,
            context=[t1]
        )
        
        t4 = Task(
            description="Use the factual feature updates and pricing reports to produce a detailed SWOT matrix and a distinct threat level score (1 to 10) for our product. Ensure all points in the SWOT analysis and the threat score are directly supported by the preceding reports, without introducing any external or unverified information.",
            expected_output="A clean, evidence-based Strengths, Weaknesses, Opportunities, and Threats matrix, followed by a final numeric score (e.g., Threat Score: 8/10), all derived solely from the provided reports.",
            agent=threat_evaluator,
            context=[t2, t3]
        )
        
        t5 = Task(
            description="Combine the factual SWOT matrix, feature delta, and pricing changes to draft an Executive Memo with clear, evidence-based product and sales action items. The memo must not contain any new information not present in the preceding agent outputs, ensuring all recommendations are directly supported by the gathered intelligence.",
            expected_output="A complete, fact-based product executive brief with standard business headers, a summary, and competitive playbook items, all strictly derived from the inputs of previous agents.",
            agent=executive_briefer,
            context=[t2, t3, t4]
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


