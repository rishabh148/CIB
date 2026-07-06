import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

MOCK_PROFILES = {
    "Acme SaaS": {
        "website_raw": """
# Acme SaaS - The Modern Workflow Management Platform
Welcome to Acme SaaS. We streamline your corporate workflows and integrate with over 20+ tools.

## Latest Updates (July 2026):
We are thrilled to announce major features and capabilities:
1. **AI Flow Assistant**: Let our new conversational AI build workflows for you. Just type a prompt, and the platform scaffolds the trigger, action, and integrations.
2. **Team Workspaces & Role-Based Access Control (RBAC)**: Organize workflows by departments (Sales, Marketing, Dev) and assign precise permissions.
3. **Advanced Webhook Triggers**: Connect with any REST endpoint with custom headers, retries, and rate-limiting options.
4. **Real-time Performance Dashboards**: Track pipeline efficiency, success rates, and API usage live.
        """,
        "pricing_raw": """
# Acme SaaS - Flexible Plans for High Growth Teams
Choose a plan that fits your execution speed. All prices are in USD.

## Standard Tiers
- **Starter Tier**: $19/mo. Up to 500 workflow runs, 3 active integration connections, and standard support.
- **Pro Tier**: $79/mo. Up to 10,000 workflow runs. Includes:
  - High priority execution
  - Custom webhook triggers
  - 15 integration connections
  - Email & Slack support (under 4-hour response time)
  - **NEW: AI Flow Assistant Add-on** (available for +$15/mo)
  
## Executive & Corporate Tiers
- **Business Scale Tier**: $199/mo. Up to 50,000 workflow runs. Includes:
  - Complete AI Flow Assistant (included by default)
  - Unlimited active connections
  - Custom SLA responses
- **Enterprise Gate Tier**: Custom pricing. Required for:
  - Team Workspaces & RBAC controls
  - Single Sign-On (SAML/OIDC)
  - Dedicated cloud instances & HIPAA compliance
        """
    },
    "Chatify AI": {
        "website_raw": """
# Chatify AI - Conversational Customer Engagement Platform
Chatify AI helps scale customer support, marketing, and sales using multi-agent conversational workflows.

## Product Blog (Q2 2026 Announcements):
Our platform is evolving rapidly:
- **Omnichannel Support Hub**: Manage Web chat, WhatsApp, Facebook Messenger, SMS, and Instagram DM in a single, unified agent inbox.
- **AI Agent Autopilot**: Give the AI access to your knowledge base (PDFs, Notion, Websites), and it will automatically answer 75% of incoming customer queries with custom tone guidelines.
- **Deep Salesforce & HubSpot Integration**: Automatically sync conversation records, customer sentiments, and create opportunities directly from active chat interfaces.
- **GDPR compliance and regional EU hosting**: Host data fully within European datacenters for corporate compliance.
        """,
        "pricing_raw": """
# Chatify AI - Pricing That Scales with Your Contacts
Choose the plan optimized for your active monthly conversational volume.

## Subscriptions
- **Starter Tier**: $29/mo (previously $19/mo). Includes 1,500 active chats, 2 seats, and web widget.
- **Growth Tier**: $129/mo (previously $79/mo). Includes 5,000 active chats, 5 seats, WhatsApp connector, and automated AI knowledge base routing.
- **Professional Tier**: $349/mo. Up to 20,000 active chats, 15 seats, advanced Shopify/Salesforce integrations, and Custom CSS widget layouts.
- **Enterprise Gate Tier**: Custom contract (Starting at $1,200/mo). Required for:
  - AI Agent Autopilot (advanced model fine-tuning and infinite knowledge indexing)
  - Omnichannel Unified Inbox (Facebook, WhatsApp, SMS, Instagram bundle)
  - Dedication Account Manager and custom team roles
        """
    }
}

def clean_html(html_content: str) -> str:
    """Parses HTML content, extracts text, and returns a clean, structured string."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style", "meta", "noscript", "header", "footer"]):
        script.decompose()
        
    text = soup.get_text(separator="\n")
    
    # Clean up excess whitespace
    lines = [line.strip() for line in text.splitlines()]
    chunks = [phrase for phrase in lines if phrase]
    return "\n".join(chunks)[:8000] # Cap raw text to keep it manageable

def fetch_live_page(url: str) -> str:
    """Attempts to fetch and parse the text content of a live URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return clean_html(response.text)
        else:
            return f"Error: Unable to fetch page. HTTP Status Code {response.status_code}"
    except Exception as e:
        return f"Error occurred during live crawl: {str(e)}"

def scrape_competitor_data(name: str, website_url: str, pricing_url: str) -> str:
    """
    Main entry point for competitor data gathering.
    Tries to crawl the real websites. If they are mock-URLs or live crawls fail,
    it falls back to highly-detailed simulated outputs tailored to the competitor.
    """
    is_mock = "demo.com" in website_url or "localhost" in website_url or "test" in website_url or not website_url.startswith("http")
    
    # 1. Attempt Live Scrape if not a mock domain
    scraped_web = ""
    scraped_pricing = ""
    
    if not is_mock:
        scraped_web = fetch_live_page(website_url)
        if not scraped_web.startswith("Error"):
            scraped_pricing = fetch_live_page(pricing_url) if pricing_url else ""
    
    # 2. Check if we have standard mock profiles for the demo competitors
    matched_profile = None
    for key in MOCK_PROFILES:
        if key.lower() in name.lower():
            matched_profile = MOCK_PROFILES[key]
            break
            
    # 3. Assemble the payload
    result_parts = []
    
    # If live scraping succeeded, incorporate it
    if scraped_web and not scraped_web.startswith("Error"):
        result_parts.append(f"=== LIVE CRAWL DATA FOR {name.upper()} WEBSITE ===")
        result_parts.append(scraped_web)
        if scraped_pricing and not scraped_pricing.startswith("Error"):
            result_parts.append(f"\n=== LIVE CRAWL DATA FOR {name.upper()} PRICING ===")
            result_parts.append(scraped_pricing)
        return "\n".join(result_parts)
        
    # If live scraping failed/was a mock domain, use mock profiles
    if matched_profile:
        result_parts.append(f"=== SIMULATED CURRENT DATA FOR {name.upper()} ===")
        result_parts.append(matched_profile["website_raw"])
        result_parts.append("\n=== SIMULATED PRICING DATA ===")
        result_parts.append(matched_profile["pricing_raw"])
    else:
        # Generate a high-quality generic mock profile if the competitor is custom-created
        # but the crawl failed.
        result_parts.append(f"=== SIMULATED CURRENT DATA FOR CUSTOM COMPETITOR: {name.upper()} ===")
        result_parts.append(f"""
# {name} - Core Corporate Value Proposition
Providing next-generation intelligent enterprise solutions. Our system automates administrative backlogs and unifies operations.

## New Feature Rollouts:
- **Enterprise Analytics Engine**: Deep predictive charting with AI anomaly detection.
- **Automated SOC-2 compliance portal**: Generates security postures automatically.
- **Advanced Integration Sync**: Real-time push updates with zero queue times.
- **Collaborative Workspaces**: Multi-department support with SSO role mapping.
        """)
        result_parts.append("\n=== SIMULATED PRICING DATA ===")
        result_parts.append(f"""
# {name} Pricing Tiers
- **Basic Plan**: $39/mo. 1,000 monthly executions, single integration bridge, community support.
- **Business Plan**: $149/mo (previously $99/mo). 10,000 monthly executions, 5 team members, custom webhook integrations.
- **Enterprise Gate Tier**: Custom contract pricing. Mandatory for SSO (SAML), custom data residency guarantees, SOC-2 dashboard, and SLA support logs.
        """)
        
    return "\n".join(result_parts)
