# Installed Skills & Resources

> **Last Updated:** 2026-06-21
> **Location:** `/Users/giaphat1980/Documents/GitHub/Backend/`

## 📦 Repository Inventory

### 1. Google Official Skills (`google-skills/`)
- **Source:** https://github.com/google/skills
- **Contains:** 36 official Google Cloud Agent Skills
- **Purpose:** Provides curated documentation and instructions for AI agents to work with Google Cloud services

#### Key Skills for This Project:
| Skill Directory | What It Does |
|----------------|--------------|
| `gemini-api/` | Gemini API patterns, model selection, streaming |
| `gemini-agents-api/` | Building multi-agent systems with Gemini |
| `gemini-interactions-api/` | Real-time conversation & interaction patterns |
| `agent-platform-rag-engine-management/` | RAG pipeline configuration & management |
| `agent-platform-deploy/` | Production deployment patterns |
| `firebase-basics/` | Firebase integration (auth, Firestore, hosting) |
| `cloud-run-basics/` | Serverless deployment on Cloud Run |

---

### 2. Antigravity Awesome Skills (`awesome-skills/`)
- **Source:** https://github.com/sickn33/antigravity-awesome-skills
- **Contains:** 1,595+ community-contributed skills
- **Purpose:** Broad collection of development patterns, security, testing, and AI skills

#### Categories Most Relevant:
- **Architecture:** System design patterns for multi-service apps
- **Data/AI:** RAG pipelines, embeddings, LLM integration patterns
- **Security:** OWASP checks, API security, auth patterns
- **Testing:** Automated testing strategies, QA workflows

---

### 3. Google ADK Python (`adk-python/`)
- **Source:** https://github.com/google/adk-python
- **Contains:** Core Agent Development Kit framework
- **Purpose:** Build, test, and deploy AI agents using Python

#### Key Directories:
- `src/google/adk/` — Core framework code
- `tests/` — Test examples and patterns
- `examples/` — Example agent implementations

---

### 4. ADK Samples (`adk-samples/`)
- **Source:** https://github.com/google/adk-samples
- **Contains:** Sample agent implementations
- **Purpose:** Reference patterns for common agent architectures

#### Relevant Samples to Study:
- RAG-based agents
- Multi-agent workflows
- Voice interaction agents
- Tool integration patterns

---

### 5. Agent Starter Pack (`agent-starter-pack/`)
- **Source:** https://github.com/GoogleCloudPlatform/agent-starter-pack
- **Contains:** Production-ready templates
- **Purpose:** Scaffolding for CI/CD, monitoring, and deployment

#### Key Templates:
- CI/CD pipeline configurations
- Monitoring dashboards
- Infrastructure as Code (Terraform)
- Deployment scripts

---

### 6. Skill Creator (`skill-creator/`)
- **Pre-existing in project**
- **Purpose:** Create and test custom skills for this project

#### Custom Skills to Create:
1. **presentation-signal-detector** — Detects presenter difficulty signals
2. **document-grounding** — Grounds AI responses in uploaded documents  
3. **lyrics-formatter** — Formats answers in lyrics-style display
4. **brand-safety-checker** — Detects brand name mismatches for KOLs

---

## 🔧 Installation Commands

```bash
# Install Google ADK
pip install google-adk

# Install individual skills (if needed)
npx skills add google/skills

# Install awesome skills
npx skills install github.com/sickn33/antigravity-awesome-skills
```

## 📋 Usage Guidelines

1. **Don't modify cloned repos directly** — Reference them, don't fork them
2. **Copy patterns, don't import** — Extract relevant code into your own modules
3. **Keep updated** — Pull latest changes periodically with `git pull`
4. **Credit sources** — Reference the source repo in your code comments
