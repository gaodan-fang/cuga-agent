# Travel Agent - AI-Powered Corporate Travel Planning

AI-powered corporate travel planning system built using CUGA's multi-agent supervisor architecture. This system coordinates 5 specialized agents to provide end-to-end travel planning with automated policy enforcement and Slack-based approval workflows.

---

## 🎯 Overview

The Travel Agent demonstrates CUGA's multi-agent supervisor pattern, featuring:

- 🛫 **Flight Search** - Real-time flight search using SerpAPI (Google Flights)
- 🏨 **Hotel Search** - Hotel search and filtering using SerpAPI (Google Hotels)
- 🌤️ **Weather Forecasts** - Destination weather information via OpenWeatherMap
- 💰 **Expense Calculation** - Automated cost calculation and budget validation
- 📋 **Policy Enforcement** - Role-based travel policies using CUGA Tool Guides
- ✅ **Approval Workflow** - Manager approval system with Slack notifications
- 🤖 **Multi-Agent Coordination** - Supervisor orchestrates 5 specialized agents

---

## 📋 Prerequisites

- Python 3.10+
- CUGA framework installed
- API Keys:
  - [SerpAPI](https://serpapi.com/) - 100 free searches/month
  - [OpenWeatherMap](https://openweathermap.org/api) - 1000 free calls/day
  - OpenAI or Groq (for LLM)
- Slack workspace (for approval workflow)

---

## 🚀 Quick Start

### 1. Get API Keys

#### SerpAPI (Required)
1. Sign up at https://serpapi.com/
2. Get your API key from the dashboard
3. Add to `.env`: `SERPAPI_API_KEY=your_key_here`

#### OpenWeatherMap (Required)
1. Sign up at https://openweathermap.org/api
2. Get your API key (may take 10-15 min to activate)
3. Add to `.env`: `OPENWEATHER_API_KEY=your_key_here`

#### LLM (Already configured in CUGA)
- Groq (default): `GROQ_API_KEY=gsk-...`
- Or OpenAI: `OPENAI_API_KEY=sk-...`

### 2. Configure Environment

Edit your `.env` file in the project root:

```bash
# Travel Agent API Keys
SERPAPI_API_KEY=your_serpapi_key_here
OPENWEATHER_API_KEY=your_openweather_key_here

# Database Configuration (optional - defaults to data/itineraries.db)
DATABASE_PATH=data/itineraries.db

# Application Settings
DEFAULT_USER_ROLE=employee
CACHE_TTL=900
DEBUG_MODE=true
```

### 3. Initialize Database

The database is automatically initialized when you first save an itinerary. However, you can manually initialize it:

```bash
# The database will be created at: data/itineraries.db
# No manual setup required - it's created automatically!
```

**Database Schema:**
- `itineraries` - Stores travel itineraries with approval status
- `approval_history` - Tracks all approval actions for audit

### 4. Set Up Slack Integration (Optional)

<details>
<summary><b>Click to expand Slack setup instructions</b></summary>

For the approval workflow to work via Slack:

#### Step 1: Create Slack App
1. Go to https://api.slack.com/apps → "Create New App" → "From scratch"
2. Name: "Travel Agent Approvals", select your workspace
3. Go to "OAuth & Permissions" → Add Bot Token Scopes:
   - `chat:write`
   - `chat:write.public`
   - `users:read`
   - `im:write`
4. Click "Install to Workspace" → Copy the Bot Token (starts with `xoxb-`)

#### Step 2: Get Manager's Slack User ID
1. Open Slack, click on the manager's profile
2. Click "More" → "Copy member ID"
3. Save this ID (looks like `U01234ABCDE`)

#### Step 3: Configure Environment
Add to your `.env` file:
```bash
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_MANAGER_USER_ID=U01234ABCDE
```

#### Step 4: Start Slack Handler
**Terminal 1:**
```bash
uv run python docs/examples/travel_agent/agents/slack_handler.py
```
You should see: `🚀 Starting Slack Interactive Components Handler`

#### Step 5: Expose with ngrok
**First time setup:**
```bash
# Sign up at https://dashboard.ngrok.com/signup
# Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

**Terminal 2:**
```bash
ngrok http 3001
```
Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

**Note:** ngrok URL changes each restart. For alternatives (localtunnel, cloudflare tunnel) or production deployment, see `NGROK_SETUP.md`

#### Step 6: Enable Interactive Components
1. Back in your Slack app settings: https://api.slack.com/apps
2. Go to "Interactivity & Shortcuts"
3. Toggle ON
4. Request URL: `https://abc123.ngrok.io/slack/interactive` (use YOUR ngrok URL)
5. Save Changes

✅ **Done!** Test by making a travel request and confirming your selection.

</details>

### 5. Start the Travel Agent

```bash
# Start the Travel Agent
cuga start travel_agent

# Access at: http://localhost:7860
```

---

## 📁 Project Structure

```
docs/examples/travel_agent/
├── agents/                          # Agent tool implementations
│   ├── flight_agent_tools.py       # Flight search & filtering
│   ├── hotel_agent_tools.py        # Hotel search & filtering
│   ├── weather_agent_tools.py      # Weather forecasts
│   ├── finance_agent_tools.py      # Expense calculations
│   ├── compliance_agent_tools.py   # Policy enforcement
│   ├── database_tools.py           # Itinerary storage (SQLite)
│   ├── slack_tools.py              # Slack notifications
│   ├── slack_handler.py            # Slack interactive handler
│   └── approval_agent.py           # Approval workflow orchestration
├── config/                          # Configuration files
│   └── supervisor_travel_agent.yaml # Supervisor configuration
├── .cuga/                           # CUGA Tool Guides
│   └── tool_guides/                 # Policy enforcement guides
│       └── compliance_policy_guide.md  # Role-based policies
├── models/                          # Data models
├── examples/                        # Example scripts
│   ├── basic_travel_request.py
│   ├── demo_approval_workflow.py
│   └── policy_comparison.py
├── QUICK_START_SLACK.md            # Quick Slack setup guide
├── SLACK_SETUP.md                  # Detailed Slack setup
├── NGROK_SETUP.md                  # ngrok setup guide
└── README.md                        # This file
```

---

## 🎭 Role-Based Policies

The system enforces different policies based on user roles using **CUGA Tool Guides**. Policies are defined in `docs/examples/travel_agent/.cuga/tool_guides/compliance_policy_guide.md` and automatically injected into the compliance agent's context.

| Policy Item | Employee | Manager | Executive | Approving Manager |
|------------|----------|---------|-----------|-------------------|
| **Flight Class** | Economy | Economy/Premium | Business | Business |
| **Max Flight Cost** | $500 | $800 | $1500 | $1500 |
| **Max Hotel/Night** | $150 | $250 | $400 | $400 |
| **Total Budget** | $2000 | $4000 | $8000 | $8000 |
| **Meal Per Diem** | $50/day | $75/day | $100/day | $100/day |
| **Approval Required** | Yes | Yes | Yes | No (auto-approved) |

---

## 🔄 Workflow

### Standard Travel Request Flow

1. **User Request** → "Plan a trip from NYC to LAX, April 15-20"
2. **Policy Loading** → System loads role-based policies via Tool Guides
3. **Parallel Search** → Agents search flights, hotels, and weather simultaneously
4. **Filtering** → Results filtered by policy constraints
5. **User Selection** → User reviews and selects options
6. **Expense Calculation** → Finance agent calculates total costs
7. **Compliance Check** → Validates against budget and policies
8. **User Approval** → User confirms their selection
9. **Storage** → Saves to database (`data/itineraries.db`)
10. **Slack Notification** → Sends interactive message to manager
11. **Manager Approval** → Manager clicks "Approve" or "Reject" in Slack
12. **Conversation Continues** → Agent automatically detects approval and continues
13. **Next Steps** → Agent asks if user wants to proceed with booking

### Interactive Approval Experience

The Travel Agent provides a **seamless, interactive approval experience**:

```
You: "Please book this trip for me"

Agent: "I've saved your itinerary and sent it to your manager for approval.
        Let me wait for their response... ⏳"

[Agent waits... Manager approves via Slack...]

Agent: "Great news! Your manager has approved your trip! 🎉
        Manager's comment: 'Looks good! Approved for business travel.'
        Would you like me to proceed with booking?"

You: "Yes, please proceed"

Agent: "Perfect! I'll help you with the booking process..."
```

**Key Features:**
- No need to refresh - conversation continues automatically
- Real-time updates when manager approves
- Seamless experience - feels like natural conversation
- No manual status checking required

---

## 💻 Usage Examples

### Basic Travel Request

```bash
# Start the agent
cuga start travel_agent

# In the chat interface:
"Plan a trip from San Francisco to Seattle, March 15-18, 2026. I'm an employee."
```

The agent will:
1. Search for flights and hotels
2. Filter by employee policy
3. Show weather forecast
4. Calculate total costs
5. Present compliant options
6. Handle approval workflow

### Example Conversations

**Simple Request:**
```
You: "I need to travel from NYC to Boston next week for a client meeting"

Agent: "I'll help you plan that trip. A few questions:
- What are your specific travel dates?
- How many days will you be staying?
- What is your role? (This determines your travel policy)"

You: "March 20-22, I'm an employee"

Agent: [Searches and presents options within employee policy]
```

**Policy Violation:**
```
You: "Book me a business class flight to Miami"

Agent: "I found business class flights, but they exceed the employee policy 
limit of $500. Here are compliant alternatives:
1. Economy flight - $380
2. Premium economy - $480

Would you like to proceed with one of these options?"
```

---

## 🗄️ Database

### Automatic Setup

The database is **automatically created** when you first save an itinerary. No manual setup required!

**Location:** `data/itineraries.db` (SQLite)

### Schema

**itineraries table:**
- `id` - Primary key
- `user_name`, `user_email`, `user_role` - User information
- `origin`, `destination` - Travel locations
- `departure_date`, `return_date` - Travel dates
- `flight_details`, `hotel_details` - JSON strings with booking details
- `weather_info`, `expense_report` - Additional information
- `compliance_status` - Policy compliance result
- `total_cost` - Total trip cost
- `approval_status` - Current approval status (pending/approved/rejected)
- `manager_id`, `manager_comments` - Approval information
- `created_at`, `updated_at`, `approved_at` - Timestamps

**approval_history table:**
- `id` - Primary key
- `itinerary_id` - Foreign key to itineraries
- `action` - Action taken (created/approved/rejected)
- `actor` - Who performed the action
- `comments` - Optional comments
- `timestamp` - When action occurred


---

## 🧪 Testing

### Test API Connections

```bash
# Verify all API keys are working
uv run python tests/test_api_connections.py

# Expected output:
# ✅ SerpAPI connection successful
# ✅ OpenWeatherMap connection successful
# ✅ LLM API key format valid
```

### Test Slack Integration

```bash
# Test Slack approval workflow
uv run python docs/examples/travel_agent/test_slack_integration.py

# This will:
# 1. Check Slack configuration
# 2. Send a test approval message
# 3. Verify handler is running
# 4. Test button interactions
```

---

## 🔧 Configuration

### Environment Variables

All configuration is in the `.env` file:

```bash
# Travel Agent API Keys
SERPAPI_API_KEY=your_serpapi_key_here
OPENWEATHER_API_KEY=your_openweather_key_here

# LLM Configuration (already in CUGA)
GROQ_API_KEY=gsk-your-groq-key
# or
OPENAI_API_KEY=sk-your-openai-key

# Slack Configuration (optional)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_MANAGER_USER_ID=U01234ABCDE
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_HANDLER_PORT=3001

# Database
DATABASE_PATH=data/itineraries.db

# Application Settings
DEFAULT_USER_ROLE=employee
CACHE_TTL=900
DEBUG_MODE=true
```

---

## 🐛 Troubleshooting

### Database Issues

**"Database not found"**
- The database is created automatically on first use
- Check `DATABASE_PATH` in `.env`
- Ensure `data/` directory exists (created automatically)

**"Database locked"**
- Close any other connections to the database
- Restart the application

### API Issues

**SerpAPI: "Invalid API key"**
- Verify key in `.env` file
- Check for extra spaces or quotes
- Regenerate key from dashboard

**SerpAPI: "Rate limit exceeded"**
- Free tier: 100 searches/month
- Wait for reset or upgrade plan

**OpenWeatherMap: "401 Unauthorized"**
- New keys take 10-15 minutes to activate
- Wait and try again

### Slack Issues

**"Slack not configured"**
- Check `.env` has `SLACK_BOT_TOKEN` and `SLACK_MANAGER_USER_ID`
- Token should start with `xoxb-`

**Manager doesn't receive messages**
- Verify manager's user ID is correct
- Check bot has all required scopes
- Try sending a test DM to the manager in Slack first

**Buttons don't work**
- Verify the Slack handler is running: `uv run python docs/examples/travel_agent/agents/slack_handler.py`
- Check ngrok is running: `ngrok http 3001`
- Verify Request URL in Slack app settings

**Agent doesn't continue after approval**
- Check handler logs for errors
- Verify database is being updated
- Ensure `wait_for_approval` tool is being called

---

## 📚 Documentation

- **[QUICK_START_SLACK.md](QUICK_START_SLACK.md)** - Quick Slack setup (5 minutes)
- **[SLACK_SETUP.md](SLACK_SETUP.md)** - Detailed Slack integration guide
- **[NGROK_SETUP.md](NGROK_SETUP.md)** - ngrok setup and alternatives
- **[USER_GUIDE.md](../USER_GUIDE.md)** - User guide with examples
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture
- **[FUNCTIONAL_REQUIREMENTS.md](../FUNCTIONAL_REQUIREMENTS.md)** - Requirements

---

## 🎯 Architecture

```
Travel Agent Supervisor
├── Flight Agent (SerpAPI - Google Flights)
├── Hotel Agent (SerpAPI - Google Hotels)
├── Weather Agent (OpenWeatherMap API)
├── Finance Agent (Expense calculations)
├── Compliance Agent (Policy enforcement via Tool Guides)
└── Approval Agent (Slack workflow)
    ├── Database Tools (SQLite storage)
    └── Slack Tools (Interactive messages)
```

**Key Components:**

1. **Supervisor** - Orchestrates all agents and manages workflow
2. **Search Agents** - Find flights, hotels, and weather data
3. **Compliance Agent** - Enforces role-based policies using CUGA Tool Guides
4. **Approval Agent** - Handles approval workflow with Slack integration
5. **Database** - Stores itineraries and approval history
6. **Slack Handler** - Receives button clicks and updates database


---
