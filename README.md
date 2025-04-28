# Fragrance Scraper

A comprehensive tool for scraping fragrance information from Fragrantica.com using parallel processing for high performance.

## Project Overview

This project allows you to collect detailed information about fragrances from Fragrantica.com, including:

- Fragrance name and brand
- Gender and release year
- Ratings and review counts
- Main accords
- Perfumer information
- Notes (top, middle, base)
- Longevity and sillage
- Descriptions and images

The scraper uses a multi-threaded approach to collect data efficiently while respecting Fragrantica's servers.

## Key Components

1. **generate_links.py** - Collects perfume URLs using parallel processing
2. **mac_fra_scraper.py** - Main scraper that extracts detailed fragrance information
3. **test_scraper.py** - Test script to verify the setup with a small sample

## Setup Instructions

### Prerequisites

- macOS (tested on macOS 11+)
- Python 3.9+
- Docker

### Step 1: Clone the Repository

```bash
git clone https://github.com/mmattyV/fragrance-scrape.git
cd fragrance-scrape
```

### Step 2: Set Up the Conda Environment

```bash
# Install Miniconda if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install miniconda
conda init zsh  # Or bash if you use bash

# Create and activate the environment
conda env create -f environment.yaml
conda activate Aroma
```

### Step 3: Install Additional Python Packages

```bash
pip install -r requirements.txt
```

### Step 4: Set Up FlareSolverr (for bypassing Cloudflare protection)

```bash
# Pull the Docker image
docker pull ghcr.io/flaresolverr/flaresolverr:latest

# Run the FlareSolverr container
docker run -d --name flaresolverr -p 8191:8191 -e LOG_LEVEL=info ghcr.io/flaresolverr/flaresolverr:latest

# Verify it's working
curl -X POST http://localhost:8191/v1 -H "Content-Type: application/json" -d '{"cmd": "sessions.create", "session": "test"}'
```

## Usage Guide

### Step 1: Generate Fragrance Links

The first step is to collect fragrance URLs from Fragrantica.com:

```bash
python generate_links.py
```

This will:
- Collect brand links from Fragrantica (if not already present)
- Extract perfume links from each brand page
- Save them to `fra_per_links.txt`
- Use parallel processing for faster execution

### Step 2: Run a Test Scrape

Before scraping all fragrances, verify your setup:

```bash
python test_scraper.py
```

This will scrape a small sample (5 fragrances) and create `data/test_fragrances.csv`.

### Step 3: Run the Full Scraper

Once testing is successful, run the main scraper:

```bash
python mac_fra_scraper.py
```

This will:
- Process all URLs in `fra_per_links.txt`
- Use parallel processing for faster execution
- Save results to `data/fragrance_data.csv`
- Show progress bars for tracking

### Controlling the Scraper

You can control the scraping process through the `control.txt` file:

- Set to `run` for normal operation
- Set to `pause` to temporarily pause (will resume when changed back to `run`)
- Set to `abort` to stop completely

## Understanding the Output

The generated CSV file includes the following fields:

- **Name**: Fragrance name
- **Brand**: Brand name
- **Gender**: Target gender (men, women, unisex)
- **Year**: Release year
- **Rating Value**: Average user rating
- **Rating Count**: Number of ratings
- **Main Accords**: Primary fragrance accords
- **Perfumers**: Names of perfumers
- **Top Notes**: Initial scent notes
- **Middle Notes**: Heart notes
- **Base Notes**: Base notes
- **Longevity**: How long the fragrance lasts
- **Sillage**: How far the fragrance projects
- **Description**: Full description of the fragrance
- **Image URL**: URL to the fragrance image
- **URL**: Link to the fragrance page

## Performance Considerations

- The link generation process is optimized for parallel execution
- The scraper processes multiple fragrances simultaneously
- Batch processing is used to avoid overwhelming Fragrantica's servers
- Progress tracking is provided via tqdm progress bars

## Troubleshooting

- If FlareSolverr stops working, restart the Docker container
- If you encounter rate limiting, adjust the batch size and delays in `mac_fra_scraper.py`
- Check `control.txt` if the scraper seems frozen (it might be paused)

## License

This project is intended for personal use and educational purposes only. Please use responsibly and respect Fragrantica's terms of service.
