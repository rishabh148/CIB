# 🛡️ Corporate Competitive Intelligence Bureau

An automated, multi-agent competitor scraper, baseline pricing auditor, strategic SWOT mapper, and executive product brief generator. Powered by **CrewAI**, **FastAPI**, and **Streamlit**.

## 🌟 Key Capabilities
- **Agent 1 (The Web Scraping Sentinel)**: Crawls specified competitor landing pages and pricing tables to retrieve recent product changes. Includes rich dynamic mock fallbacks to ensure reliable runs even during server outages or IP blocks.
- **Agent 2 (The Feature Delta Analyst)**: Compares current scraped data against a defined baseline config to extract newly rolled-out features and messaging shifts.
- **Agent 3 (The Pricing & Packaging Analyst)**: Identifies tier cost updates, subscription pivots, and feature-gating strategies (e.g. enterprise gating).
- **Agent 4 (The Threat & SWOT Evaluator)**: Compiles Strengths, Weaknesses, Opportunities, and Threats into a visual SWOT matrix and assigns an executive threat score (1 to 10).
- **Agent 5 (The Executive Briefer)**: Synthesizes findings into a professional, structured product briefing memo for executive decisions.

---

## 🛠️ Tech Stack & Directory Structure
- **Backend Orchestrator**: `FastAPI` (exposed at `http://localhost:8000`)
- **Multi-Agent Flow**: `CrewAI`
- **Executive Control Deck**: `Streamlit` (exposed at `http://localhost:8501`)
- **Database**: Lightweight JSON file persistence (`backend/db.json`)

---

## 🚀 Setup & Launch Instructions

### 1. Configure Environmental Variables (Optional)
Create a `.env` file in the root directory to set standard LLM API keys if you wish to run actual LLMs. Otherwise, the system runs a highly realistic dynamic corporate simulator out-of-the-box.
```env
OPENAI_API_KEY=your-openai-api-key-here
# Optional: ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.
```

### 2. Install Dependencies
Run the package installations for both backend and frontend:
```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. Launch Locally (Development)
Run our unified Python manager script, which boots the FastAPI API server and Streamlit dashboard in parallel:
```bash
python run.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser to access the control deck!

### 4. Deploy with Docker (Production Ready)
For a production-ready deployment, you can use Docker and Docker Compose. This will containerize both the backend and frontend services, making them isolated and scalable.

1. **Build and Run Docker Containers**:
   ```bash
   docker-compose up --build -d
   ```
   This command builds the Docker images (if not already built) and starts the services in detached mode.

2. **Access the Application**:
   - FastAPI Backend: `http://localhost:8000`
   - Streamlit Dashboard: `http://localhost:8501`

3. **Stop the Application**:
   ```bash
   docker-compose down
   ```
   This command stops and removes the containers, networks, and volumes created by `up`.

### 5. Deploy with Render (Production Ready - Alternative)
For deploying your application on Render, follow these steps:

**Backend (FastAPI) Deployment on Render:**

1.  **Configure `backend/render.yaml`**:
    A `render.yaml` file has been created in the `backend` directory. This file defines the Render service for your FastAPI backend. Ensure you configure your environment variables (like `OPENAI_API_KEY`) in the Render dashboard for security.

2.  **Connect to Render**:
    *   Create a new Web Service on Render and connect your GitHub repository.
    *   Select "Blueprint" for the deployment method and point it to the `backend/render.yaml` file.
    *   Render will automatically detect your service and deploy it.

**Frontend (Streamlit) Deployment on Streamlit Community Cloud:**

1.  **Prepare `frontend/app.py`**:
    The `frontend/app.py` has been updated to use an environment variable `API_URL` for the backend API endpoint. When deploying to Streamlit Community Cloud, you'll need to set this environment variable.

2.  **Deploy to Streamlit Community Cloud**:
    *   Ensure your `frontend` directory is in a GitHub repository.
    *   Go to [Streamlit Community Cloud](https://share.streamlit.io/).
    *   Click "New app" and select your repository and `frontend/app.py` as the main file.
    *   In the "Advanced settings -> Secrets" section, add `API_URL` with the URL of your deployed Render backend (e.g., `https://your-backend-service.onrender.com/api`).
    *   Click "Deploy!"

---
