<div align="center">
  <h1>🎯 DorkHunter</h1>
  <p><b>Offensive Intelligence & Dork Automation Tool</b></p>
  <p><i>Coded By Umut ÖZEN</i></p>
</div>

## 📖 Overview
**DorkHunter** is a powerful automated exploitation and intelligence gathering tool designed for bug bounty hunters and penetration testers. It seamlessly pulls over 3000+ top-tier search queries (Dorks) compiled by the [ProjectDiscovery](https://github.com/projectdiscovery/awesome-search-queries) community and executes them against multiple Internet mapping engines to harvest vulnerable IPs. 

With native support for **Shodan**, **FOFA**, and **Censys** REST APIs, DorkHunter completely automates your footprinting phase. Once IPs are collected, they are deduplicated and saved directly to `targets.txt`, making it extremely easy to pipeline into tools like `nuclei`.

---

## ✨ Features
* 🚀 **Multi-Engine Support:** Native integration with Shodan, FOFA, and Censys APIs.
* 🧠 **Fuzzy Target Search:** Don't remember the exact product name? Just type `forti` and let DorkHunter automatically match and scan `fortinet`, `fortigate`, `fortisandbox`, etc.
* 🔄 **Live Sync:** Fetches the absolute latest queries directly from GitHub on every run.
* 🎨 **Beautiful CLI:** Built with Python `rich` for an incredibly smooth, Matrix-style terminal UX, complete with animated progress bars.
* 🛡️ **Fail-Safe Processing:** If a specific Engine's API key is missing, DorkHunter gracefully ignores it and falls back to whatever engines are configured.

---

## ⚙️ Installation

**1. Clone the repository:**
```bash
git clone https://github.com/umutozen/DorkHunter.git
cd DorkHunter
```

**2. Install dependencies:**
```bash
python -m pip install -r requirements.txt
```

**3. Configure API Keys:**
Rename the provided `.env.example` file to `.env` and fill in your API credentials.
```env
SHODAN_API_KEY="YOUR_SHODAN_API_KEY_HERE"
FOFA_EMAIL="YOUR_FOFA_EMAIL_HERE"
FOFA_API_KEY="YOUR_FOFA_API_KEY_HERE"
CENSYS_API_ID="YOUR_CENSYS_API_ID_HERE"
CENSYS_API_SECRET="YOUR_CENSYS_API_SECRET_HERE"
```
*(Note: You only need keys for the engines you intend to use!)*

---

## 🐳 Docker Usage
Don't want to install Python dependencies? You can seamlessly run DorkHunter using Docker!

**1. Build the image:**
```bash
docker build -t dorkhunter .
```

**2. Run it interactively:**
```bash
docker run -it --rm --env-file .env -v ${PWD}:/app dorkhunter
```
*(This commands runs DorkHunter, maps your `.env` file credentials dynamically, and saves the output `targets.txt` to your host machine).*

---

## 🎮 Usage

Simply run the main python script:
```bash
python main.py
```

### Typical Workflow:
1. **Engine Selection:** You will be prompted to select the target search engine: `shodan / fofa / censys / all`.
2. **Target Selection:** Enter a Keyword (e.g., `apache`, `microsoft`, `cisco`, `wordpress`).
3. **Limit Definition:** Pick how many results you want per dork rule.
4. **Execution:** DorkHunter will search the internet array and output vulnerable hosts into `targets.txt`.

### Piping to Nuclei (Example)
```bash
nuclei -l targets.txt -t http/cves/
```

---

## ⚠️ Disclaimer
This tool is created for **educational purposes and authorized ethical hacking only**. The author (Umut ÖZEN) is not responsible for any misuse, damage, or illegal activities caused by utilizing this tool. Always ensure you have explicit permission before scanning any target networks.

## 🙏 Credits
- **Core Logic & CLI Engine:** [Umut ÖZEN](https://github.com/umutozen)
- **Search Queries Dataset:** [ProjectDiscovery Community](https://github.com/projectdiscovery/awesome-search-queries)
