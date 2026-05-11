#!/bin/bash
# Jarvis Setup Script
# Run from project root: bash scripts/setup.sh

set -e

echo "🤖 Jarvis Setup Starting..."
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code not installed."
    echo "   Install: npm install -g @anthropic-ai/claude-code"
    exit 1
fi
echo "  ✅ Claude Code installed"

if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not installed (needed for some MCP servers)"
    echo "   Install from nodejs.org or via: brew install node@20"
fi

if ! command -v git &> /dev/null; then
    echo "⚠️  Git not installed (recommended for version control)"
fi

if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python 3 not installed (needed for Telegram bridge)"
fi

echo ""

# Create needed directories
echo "📁 Creating directory structure..."
mkdir -p data/{memory,conversations,briefings,notes,plans,reviews,triages,logs,backup}
mkdir -p data/learning
mkdir -p data/memory/archive
echo "  ✅ Directories created"
echo ""

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo "📦 Initializing git..."
    git init
    
    # Create gitignore
    cat > .gitignore << 'EOF'
# Secrets
.env
credentials.json
*token*.json
*_token.json

# Data (your personal info)
data/conversations/
data/briefings/
data/triages/
data/logs/
data/notes/
data/plans/
data/reviews/

# Keep memory templates in repo, but allow local edits to be gitignored if you prefer
# Uncomment next line if you don't want to commit your memory:
# data/memory/

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node
node_modules/
package-lock.json

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# Bridge .env
bridge/.env
EOF
    
    git add .gitignore
    git commit -m "Initial Jarvis setup"
    echo "  ✅ Git initialized"
else
    echo "  ✅ Git already initialized"
fi
echo ""

# Verify Claude Code can read the project
echo "🧪 Testing Claude Code..."
if [ -f "CLAUDE.md" ]; then
    echo "  ✅ CLAUDE.md present"
else
    echo "  ❌ CLAUDE.md missing!"
    exit 1
fi

if [ -d ".claude/agents" ]; then
    AGENT_COUNT=$(ls -1 .claude/agents/*.md 2>/dev/null | wc -l)
    echo "  ✅ Found $AGENT_COUNT subagents"
else
    echo "  ❌ .claude/agents/ directory missing!"
    exit 1
fi

if [ -d ".claude/commands" ]; then
    CMD_COUNT=$(ls -1 .claude/commands/*.md 2>/dev/null | wc -l)
    echo "  ✅ Found $CMD_COUNT slash commands"
fi

echo ""

# Check authentication
echo "🔐 Authentication check..."
echo "  Run 'claude /status' to verify your Claude subscription is active"
echo "  If you have ANTHROPIC_API_KEY set, you may want to unset it:"
echo "    unset ANTHROPIC_API_KEY"
echo ""

# Final instructions
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit your memory files with personal info:"
echo "   - data/memory/facts.md"
echo "   - data/memory/preferences.md"
echo "   - data/memory/projects.md"
echo "   - data/memory/people.md"
echo "   - data/memory/habits.md"
echo ""
echo "2. Test Jarvis:"
echo "   claude"
echo "   > Read CLAUDE.md and introduce yourself"
echo ""
echo "3. (Optional) Configure MCP servers in .mcp.json"
echo ""
echo "4. (Optional) Set up Telegram bridge:"
echo "   cd bridge && pip install -r requirements.txt"
echo "   cp .env.example .env  # then edit"
echo "   python telegram_bridge.py"
echo ""
echo "5. (Optional) Set up cron jobs:"
echo "   crontab -e  # paste from scripts/crontab.example"
echo ""
echo "🚀 Ready to build your Jarvis. Read README.md for detailed guide."
