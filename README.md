# Agentic HR System

A decision-making and task-routing backend for HR operations. The system behaves like a digital HR employee: it understands requests, classifies them, delegates to specialist agents, and remembers context.

## Architecture

```
User Request
     │
     ▼
┌─────────────┐
│ Orchestrator │  ← classifies intent (policy / employee_data / recruitment / grievance)
└──────┬──────┘
       │
  ┌────┴────┬────────────┬──────────────┐
  ▼         ▼            ▼              ▼
Policy   Employee    Recruitment    Grievance
Agent    Data Agent    Agent          Agent
  │         │            │              │
  ▼         ▼            ▼              ▼
Tools    Tools         Tools          Tools
(policies) (employees) (positions)  (grievances)
```

## Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e .

# 3. Configure API key
cp .env.example .env
# Edit .env with your OpenAI API key

# 4. Run
python main.py
```

## Project Structure

```
├── main.py                 # CLI entry point
├── agents/
│   ├── orchestrator.py     # Central brain — classifies & routes
│   ├── base_agent.py       # Shared agent logic
│   ├── policy_agent.py     # HR policy Q&A
│   ├── employee_data_agent.py  # Employee lookup
│   ├── recruitment_agent.py    # Open positions & candidates
│   └── grievance_agent.py     # File & track grievances
├── tools/
│   ├── llm_client.py       # OpenAI API wrapper
│   ├── logger.py           # Centralised logging
│   ├── memory_tools.py     # Conversation persistence
│   ├── policy_tools.py     # Policy search
│   ├── employee_tools.py   # Employee data access
│   ├── recruitment_tools.py # Recruitment data
│   └── grievance_tools.py  # Grievance filing
├── prompts/                # System prompts per agent
├── config/                 # Settings & env loading
├── data/                   # JSON data files (policies, employees, etc.)
├── memory/                 # Conversation history (runtime)
└── logs/                   # Application logs (runtime)
```

## Example Usage

```
[You] > What is our leave policy?
[HR Assistant] According to our Annual Leave Policy (POL-001), all full-time
employees are entitled to 20 days of paid annual leave per calendar year...

[You] > Who is Alice Johnson's manager?
[HR Assistant] Alice Johnson's manager is Bob Williams (Engineering Manager)...

[You] > What positions are open right now?
[HR Assistant] We currently have 2 open positions: Backend Engineer and Product Designer...

[You] > I want to file a complaint about my workspace conditions
[HR Assistant] I've recorded your grievance (GRV-XXXXXX). Our team will review it...
```
