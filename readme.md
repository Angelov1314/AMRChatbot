# CHATSCi-AMI: AI-based Chatbot for Community Antibiotic Usage Data Collection in LMICs

## Project Overview

This repository contains the complete implementation of CHATSCi-AMI, an AI-powered chatbot designed for collecting community antibiotic usage data in Thailand. The system integrates web scraping, natural language processing, and data analytics to provide comprehensive insights into antimicrobial resistance patterns.

## Installation & Setup

### Prerequisites
```bash
Python 3.8+
Chrome WebDriver
OpenAI API key
```

### Dependencies
```bash
pip install -r requirements.txt
```

### Configuration
1. Create `api_keys.json` with your credentials:
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
2. The project structure is organized with supplementary materials in the "Supplementary S10-16" folder:
   - All code files are located in `Supplementary S10-16/`
   - Data files are in `Supplementary S10-16/Data/`
   - Example data is in `Supplementary S10-16/S16 Example Data/`     
      

## Project Directory

```
Line-Chabot-Code/
├── .git/                            # Git repository
├── Supplementary S10-16/            # Supplementary materials for academic submission
│   ├── S10 Email Code.py            # Email automation system using Google SMTP
│   ├── S11 Data Analysis Code.py    # Data analysis and visualization
│   ├── S12 REDCap API Code.py       # REDCap API integration for data export
│   ├── S13 Webscraper Code.py       # Webscraping from webhook, parsing and AI-based data structuring
│   ├── S14 Data Join Code.py        # Data merging between Registration and conversation data
│   ├── S15 Data Generator Code.R    # R script for simulated data generation
│   ├── Data/                        # Output data directory (ignored by git)
│   │   ├── structured_conversations.csv # Processed conversation data ready for merging
│   │   ├── raw_conversations.csv        # Raw conversation logs
│   │   ├── merged_data.csv             # Combined demographic and conversation data
│   │   ├── Demographics.csv            # Participant information from Microsoft Forms
│   │   └── simulated_data.csv          # Simulated survey data
│   └── S16 Example Data/            # Sample data for demonstration
│       ├── S16.1 Simulated Data.csv    # Example simulated survey data
│       ├── S16.2 Raw Conversations.csv # Example raw conversation data
│       ├── S16.3 Structured Conversations.csv # Example processed conversation data
│       ├── S16.4 Demographics.csv      # Example demographic information
│       ├── S16.5 Merged Data.csv       # Example merged dataset
│       └── Data dictionary.md           # Data field descriptions
├── Assets/                          # Images and resources
│   └── image/                       # Medication images and UI assets
├── Prompts/                         # System prompts and templates
│   ├── Chatbot prompt               # Conversation processing prompts
│   └── Email prompt                 # Email reminder templates
├── api_keys.json                    # API credentials (not in repo)
├── api_keys_censored.json           # Censored API keys template
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
└── readme.md                        # Project documentation
```

## Authors

- **Research Team**: Oxford University/ Mahidol Oxford Tropical Medicine Research Unit (MORU)
- **Technical Implementation**: C.Y.
- **Supervision**: M.O., R.A., B.G., B.S.C., C.L., S.S.

*This project represents a proof-of-concept study demonstrating the feasibility of AI-based chatbots for community antibiotic usage data collection in LMICs. The findings contribute to the development of scalable solutions for AMR monitoring in resource-limited settings.*
