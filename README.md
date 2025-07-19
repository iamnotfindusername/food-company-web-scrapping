# Web Scraping Project - Proveedores.com  
 
This project scrapes supplier information related to "Fresas" (strawberries) from proveedores.com.  
 
## Features  
- Navigate through multiple pages to scrape data  
- Extract phone numbers, emails, websites, and addresses  
- Decode Cloudflare-protected emails  
- Use random user-agents to reduce blocking risks  
- Save contact data into CSV files  
- Show colored progress bar in the terminal  
 
## Requirements  
- Python 3.8+  
- requests  
- beautifulsoup4  
- termcolor  
 
Install dependencies with:  
```bash  
pip install -r requirements.txt  
```  
 
## Usage  
1. Go to the project folder  
2. Run the script:  
```bash  
python scrapper.py  
```  
3. The scraped data will be saved as a timestamped CSV file inside the `data/` folder.  
 
## File Description  
- `scrapper.py`: Main scraping and data processing script  
- `user_agent.txt`: List of user-agents for random selection  
- `data/`: Folder where CSV output files are saved  
- `.venv/`: Virtual environment (ignored by git)  
 
## Notes  
- The `.venv` folder should not be included in git.  
- `user_agent.txt` must exist, otherwise a default user-agent is used.  
- Internet connection and target site availability are required during scraping.  
 
## Contact  
For any issues or suggestions, feel free to contact me.  
 
---  
 
*Created on: 2025-07-19* 
