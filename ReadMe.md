# NBA Shot Chart Analysis

An interactive web application that visualizes and analyzes NBA players' shooting patterns and statistics using the NBA API and Flask.

## Features

- 🏀 Interactive shot chart visualization with made/missed shot differentiation
- 🔍 Dynamic player search with Select2 integration
- 📅 Season filtering with automatic updates
- 🎮 Game-by-game analysis and filtering
- 📊 Detailed shooting statistics including:
  - Zone-based shot analysis
  - Shot distance information
  - 2PT/3PT breakdowns with percentages
  - Shot distribution visualization
  - Shot success rate by zone

## Technologies Used

- Flask (Python web framework)
- NBA API (Official NBA statistics)
- Plotly (Interactive visualizations)
- Pandas (Data manipulation)
- Select2 (Enhanced dropdowns)
- CSS Grid/Flexbox (Modern layout)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/nba_analytics.git
cd nba_analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=run.py
export FLASK_ENV=development

# Run the application
flask run
```
