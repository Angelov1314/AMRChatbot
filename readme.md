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
2. Creat the "Data" folder with the following structure:
├── Data/                           
    ├── structured_conversations.csv 
    ├── raw_conversations.csv        
    ├── merged_data.csv             
    └── Demographics.csv     
      

## Project Directory

```
Line-Chabot-Code/
├── webscraper.py                    # Webscraping from webhook, parsing and AI-based data structuring
├── Email.py                         # Email automation system using Google STMP
├── Join.py                          # Data merging between demographics form and conversation data
├── Data analysis.py                 # Pseudo Data analysis and visualization
├── Generator.r                      # R script for data generation
├── redcap_api.py                    # Request REDCap API to export data
├── api_keys.json                    # API credentials (not in repo)
├── api_keys_censored.json           # Censored API keys template
├── requirements.txt                 # Python dependencies
├── .gitignore                      # Git ignore rules
├── Assets/                         # Images and resources
│   └── image/                      # Medication images and UI assets
├── Data/                           # Output data directory (ignored by git)
│   ├── structured_conversations.csv # Processed conversation data ready for merging
│   ├── raw_conversations.csv        # Raw conversation logs
│   ├── merged_data.csv             # Combined demographic and conversation data
│   └── Demographics.csv            # Participant demographic information from Microsoftforms
├── Example Data/                   # Sample data for demonstration 
│   ├── raw_conversations.csv       # Example raw conversation data
│   ├── structured_conversations.csv # Example processed conversation data
│   ├── merged_data.csv            # Example merged dataset
│   └── Demographics.csv           # Example demographic information
└── Prompts/                        # System prompts and templates
    ├── Email prompt                # Email reminder templates
    └── Chatbot prompt              # Conversation processing prompts
```

## Authors

- **Research Team**: Oxford University/ Mahidol Oxford Tropical Medicine Research Unit (MORU)
- **Technical Implementation**: C.Y.
- **Supervision**: M.O., R.A., B.G., B.S.C., C.L., S.S.

*This project represents a proof-of-concept study demonstrating the feasibility of AI-based chatbots for community antibiotic usage data collection in LMICs. The findings contribute to the development of scalable solutions for AMR monitoring in resource-limited settings.*
