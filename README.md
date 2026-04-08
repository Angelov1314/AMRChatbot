<div align="center">

# CHATSCi-AMI

**Community Health AI Tool for Structured Collection of Individual Antimicrobial Information**

An AI-powered chatbot for collecting community antibiotic usage data in Thailand

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI API](https://img.shields.io/badge/OpenAI-API-412991?logo=openai&logoColor=white)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## Abstract

Antimicrobial resistance (AMR) is a critical global health threat, yet community-level antibiotic usage data in low- and middle-income countries (LMICs) remains scarce and difficult to collect at scale. **CHATSCi-AMI** is a proof-of-concept AI-powered chatbot system designed to address this gap by enabling structured, conversational data collection on antibiotic usage patterns in community settings in Thailand. The system leverages large language models (OpenAI API) to conduct natural-language interviews, integrates with REDCap for secure data management, and employs automated web scraping and data processing pipelines to transform unstructured conversation logs into analysis-ready datasets. This work demonstrates the feasibility of deploying AI chatbots as scalable, low-cost tools for AMR surveillance in resource-limited settings.

## Research Context

- **Domain**: Antimicrobial Resistance (AMR) surveillance in community settings
- **Setting**: Thailand, as a representative low- and middle-income country (LMIC)
- **Institution**: [Mahidol Oxford Tropical Medicine Research Unit (MORU)](https://www.tropmedres.ac/), University of Oxford
- **Objective**: Demonstrate that AI-based conversational agents can feasibly collect structured antibiotic usage data from community members, reducing reliance on costly in-person surveys

## Tech Stack

| Component | Technology |
|---|---|
| Chatbot engine | Python, OpenAI API |
| Web scraping | Selenium, BeautifulSoup |
| Data management | REDCap API, pandas |
| Geospatial analysis | geopandas |
| Statistical modelling | statsmodels |
| Simulated data generation | R |

## Repository Structure

```
AMRChatbot/
├── Supplementary S10-16/               # Code and data supplements
│   ├── S10 Email Code.py               # Email automation (Google SMTP)
│   ├── S11 Data Analysis Code.py       # Data analysis and visualisation
│   ├── S12 REDCap API Code.py          # REDCap API integration for data export
│   ├── S13 Webscraper Code.py          # Webhook scraping and AI-based structuring
│   ├── S14 Data Join Code.py           # Merging registration and conversation data
│   ├── S15 Data Generator Code.R       # R script for simulated data generation
│   ├── Data/                           # Output data directory (git-ignored)
│   └── S16 Example Data/              # Sample datasets for demonstration
│       ├── S16.1 Simulated Data.csv
│       ├── S16.2 Raw Conversations.csv
│       ├── S16.3 Structured Conversations.csv
│       ├── S16.4 Demographics.csv
│       ├── S16.5 Merged Data.csv
│       └── Data dictionary.md
├── Assets/
│   └── image/                          # Medication images and UI assets
├── Prompts/
│   ├── Chatbot prompt                  # Conversation processing prompts
│   └── Email prompt                    # Email reminder templates
├── api_keys_censored.json              # API keys template (credentials removed)
├── requirements.txt                    # Python dependencies
└── LICENSE
```

## Getting Started

### Prerequisites

- Python 3.8+
- Chrome WebDriver (for Selenium-based scraping)
- OpenAI API key
- REDCap API token (for data export)

### Installation

```bash
git clone https://github.com/Angelov1314/AMRChatbot.git
cd AMRChatbot
pip install -r requirements.txt
```

### Configuration

Create an `api_keys.json` file in the project root using `api_keys_censored.json` as a template:

```json
{
  "openai_api_key": "your_openai_key",
  "email_smtp_server": "smtp.gmail.com",
  "email_port": 587,
  "email_sender": "your_email@gmail.com",
  "email_password": "your_app_password",
  "chatbean_email": "your_chatbean_email",
  "chatbean_password": "your_chatbean_password",
  "redcap_token": "your_redcap_token"
}
```

### Pipeline Overview

| Step | Script | Description |
|---|---|---|
| 1 | `S13 Webscraper Code.py` | Scrapes conversation logs from the chatbot webhook and structures them using the OpenAI API |
| 2 | `S12 REDCap API Code.py` | Exports participant registration data from REDCap |
| 3 | `S14 Data Join Code.py` | Merges conversation data with demographic records |
| 4 | `S11 Data Analysis Code.py` | Runs descriptive and statistical analyses |
| 5 | `S10 Email Code.py` | Sends automated email reminders to participants |
| 6 | `S15 Data Generator Code.R` | Generates simulated data for methods validation |

## Authors

| Role | Contributor |
|---|---|
| **Technical implementation** | Jerry Yang (C.Y.) |
| **Supervision** | M.O., R.A., B.G., B.S.C., C.L., S.S. |

**Affiliation**: Mahidol Oxford Tropical Medicine Research Unit (MORU), Centre for Tropical Medicine and Global Health, Nuffield Department of Medicine, University of Oxford

## Citation

If you use this work, please cite:

```bibtex
@mastersthesis{yang2025chatsciami,
  title     = {{CHATSCi-AMI}: An {AI}-Powered Chatbot for Community Antibiotic Usage Data Collection in {LMICs}},
  author    = {Yang, Jerry C.},
  school    = {University of Oxford},
  year      = {2025},
  type      = {{MSc} dissertation},
  note      = {Mahidol Oxford Tropical Medicine Research Unit (MORU)}
}
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
