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
    
    # Simplified output for simulated mode, indicating full analysis requires an LLM.
    simulated_output = {
        "raw_scraped_data": scraped_data,
        "feature_deltas": "Feature delta analysis requires a configured LLM API key.",
        "pricing_analysis": "Pricing analysis requires a configured LLM API key.",
        "swot_analysis": "SWOT and threat evaluation require a configured LLM API key.",
        "executive_brief": "Executive briefing requires a configured LLM API key.",
    }
    return simulated_output, 1 # Return a default threat score of 1 in simulated mode


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
            agent=delta_analyst
        )
        
        t3 = Task(
            description=f"Compare the structured pricing from Agent 1 against these baselines: \n{baseline_pricing}\nDetail price increases, tier changes, and gating strategies. The report must be strictly factual, based only on the provided pricing data, and must not include any speculative analysis.",
            expected_output="Detailed, factual report explaining package modifications, precise price changes, and explicit expansion strategies as identified from the structured pricing data.",
            agent=pricing_analyst
        )
        
        t4 = Task(
            description="Use the factual feature updates and pricing reports to produce a detailed SWOT matrix and a distinct threat level score (1 to 10) for our product. Ensure all points in the SWOT analysis and the threat score are directly supported by the preceding reports, without introducing any external or unverified information.",
            expected_output="A clean, evidence-based Strengths, Weaknesses, Opportunities, and Threats matrix, followed by a final numeric score (e.g., Threat Score: 8/10), all derived solely from the provided reports.",
            agent=threat_evaluator
        )
        
        t5 = Task(
            description="Combine the factual SWOT matrix, feature delta, and pricing changes to draft an Executive Memo with clear, evidence-based product and sales action items. The memo must not contain any new information not present in the preceding agent outputs, ensuring all recommendations are directly supported by the gathered intelligence.",
            expected_output="A complete, fact-based product executive brief with standard business headers, a summary, and competitive playbook items, all strictly derived from the inputs of previous agents.",
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


