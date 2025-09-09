# 🎰 Blackjack Analysis API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Deployment](https://img.shields.io/badge/Deployed-Render-00d4aa.svg)](https://render.com)

> **RESTful API for blackjack strategy simulation data and analysis**

A Flask-based backend API that serves pre-processed blackjack simulation results with statistical analysis. This API powers the interactive dashboard for exploring different blackjack strategies and their performance metrics.

---

## 🚀 Live API

**API Base URL:** `https://blackjack-backend-jzt6.onrender.com/`

**Health Check:** `GET /` - Returns API status and configuration

---

## 📋 Table of Contents

- [🎯 Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📊 API Endpoints](#-api-endpoints)
- [🔧 Local Development](#-local-development)
- [🚀 Deployment](#-deployment)
- [📁 Project Structure](#-project-structure)

---

## 🎯 Features

- **Pre-processed Data**: Optimized JSON responses for fast loading
- **Multiple Strategies**: Support for 9+ different blackjack strategies
- **Statistical Analysis**: ROI, volatility, win rates, and more
- **CORS Enabled**: Ready for frontend integration
- **Production Ready**: Configured for Render deployment

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11+ required
python --version
```

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-backend-repo-url>
   cd blackjack-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Pre-process data** (if not already done)
   ```bash
   python preprocess_data.py
   ```

4. **Run the server**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5001`

---

## 📊 API Endpoints

### Health Check
```http
GET /
```
Returns API status and configuration information.

### Get All Strategies
```http
GET /api/strategies
```
Returns a list of all available blackjack strategies with summary statistics.

**Response:**
```json
{
  "basic": {
    "name": "Basic Strategy",
    "description": "Follows the mathematically optimal decisions...",
    "avgNetPerHand": -0.10235,
    "roi": -1.02,
    "stdDeviation": 1.15,
    "winRate": 0.4297
  }
}
```

### Get Specific Strategy
```http
GET /api/strategy/{strategy_key}
```
Returns detailed data for a specific strategy.

**Example:** `GET /api/strategy/basic`

### Get Comparison Data
```http
GET /api/comparison
```
Returns comparison data for all strategies, optimized for dashboard display.

### Get Quick Comparison
```http
GET /api/quick-comparison
```
Returns lightweight comparison data for faster initial page loads.

---

## 🔧 Local Development

### Development Server

```bash
# Run with auto-reload
python app.py

# Or use Flask's development server
flask run --host=0.0.0.0 --port=5001
```

### Environment Variables

```bash
# Optional: Set custom port
export PORT=5001

# Optional: Set debug mode
export FLASK_DEBUG=1
```

### Data Processing

The API uses pre-processed data for optimal performance. To regenerate:

```bash
python preprocess_data.py
```

This creates optimized JSON files in the `processed_data/` directory.

---

## 🚀 Deployment

### Render.com (Current)

1. **Connect Repository**: Link your GitHub repository to Render
2. **Create Web Service**: 
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Python Version**: 3.11
3. **Deploy**: Automatic deployment on git push

### Other Platforms

#### Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
git push heroku main
```

#### Fly.io
```bash
# Install Fly CLI
fly auth signup
fly launch
fly deploy
```

---

## 📁 Project Structure

```
backend/
├── 📄 README.md                    # This file
├── 📄 app.py                      # Main Flask application
├── 📄 preprocess_data.py          # Data preprocessing script
├── 📄 requirements.txt            # Python dependencies
├── 📄 runtime.txt                 # Python version specification
├── 📄 Procfile                    # Process configuration
├── 📁 processed_data/             # Pre-processed JSON files
│   ├── basic_summary.json
│   ├── card-counter_summary.json
│   └── ...
└── 📁 results/                    # Original simulation results
    ├── basic_results.json
    ├── card_counter_results.json
    └── ...
```

---

## 🔧 Configuration

### API Configuration

The API automatically detects the environment:
- **Production**: Uses Render URL
- **Development**: Uses `localhost:5001`

### CORS Settings

CORS is enabled for all origins to support frontend integration.

### Data Directory

- **Results Directory**: Contains original simulation JSON files
- **Processed Directory**: Contains optimized summary files for API responses

---

## 📊 Supported Strategies

| Strategy | Key | Description |
|----------|-----|-------------|
| Basic Strategy | `basic` | Mathematically optimal decisions |
| Card Counter | `card-counter` | Adjusts based on card count |
| Dealer Weakness | `dealer-weakness` | Stands on 12+ vs dealer 2-6 |
| Mimic Dealer | `mimic-dealer` | Hits until 17 like dealer |
| Martingale | `martingale` | Doubles bet after losses |
| Fixed Threshold 12-20 | `fixed-threshold-{n}` | Stands at specific threshold |

---

## 🐛 Troubleshooting

### Common Issues

1. **Data Not Found**: Run `python preprocess_data.py`
2. **CORS Errors**: Ensure Flask-CORS is installed
3. **Port Issues**: Check if port 5001 is available
4. **Import Errors**: Verify all dependencies are installed

### Logs

Check application logs for detailed error information:
- **Local**: Console output
- **Render**: Dashboard logs section

---

## 🤝 Contributing

This project is part of an academic course assignment. For questions or issues, please contact the development team.

---

## 📄 License

This project is part of an academic course assignment. All rights reserved.

---

<div align="center">

**🎰 Blackjack Analysis API 🎰**

*Powered by Flask & Deployed on Render*

</div>
