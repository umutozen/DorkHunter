import os
import requests
import shodan
import base64
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import track

console = Console()
BANNER = """
[bold red]
██████╗  ██████╗ ██████╗ ██╗  ██╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
██║  ██║██║   ██║██████╔╝█████╔╝     ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██║  ██║██║   ██║██╔══██╗██╔═██╗     ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██████╔╝╚██████╔╝██║  ██║██║  ██╗    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
[/bold red]
[cyan]Offensive Intelligence & Dork Automation Tool[/cyan]
[bold yellow]Coded By Umut ÖZEN[/bold yellow]
[dim italic]Thanks to ProjectDiscovery community for the awesome search queries list.[/dim italic]
"""

RAW_JSON_URL = "https://raw.githubusercontent.com/projectdiscovery/awesome-search-queries/main/QUERIES.json"

def load_queries():
    console.print("\n[cyan][*] Disconnecting from Matrix and fetching latest Dorks from GitHub...[/cyan]")
    response = requests.get(RAW_JSON_URL)
    response.raise_for_status()
    return response.json()

def search_fofa(query, email, key, limit):
    qbase64 = base64.b64encode(query.encode('utf-8')).decode('utf-8')
    url = f"https://fofa.info/api/v1/search/all?email={email}&key={key}&qbase64={qbase64}&size={limit}"
    res = requests.get(url).json()
    ips = []
    if "results" in res:
        for item in res["results"]:
            ips.append(item[0] if ":" in item[0] else f"{item[1]}:{item[2]}")
    return ips

def search_censys(query, api_id, api_secret, limit):
    auth = (api_id, api_secret)
    safe_limit = min(limit, 100) 
    url = f"https://search.censys.io/api/v2/hosts/search?q={query}&per_page={safe_limit}"
    
    ips = []
    try:
        res = requests.get(url, auth=auth)
        res.raise_for_status()
        data = res.json()
        if "result" in data and "hits" in data["result"]:
            for hit in data["result"]["hits"]:
                ip = hit.get("ip", "")
                if ip:
                    ips.append(ip)
    except Exception:
        pass
    return ips

def main():
    console.clear()
    console.print(Panel.fit(BANNER, border_style="red"))
    load_dotenv()
    
    try:
        queries_data = load_queries()
        console.print(f"[green][+] Successfully loaded rules for {len(queries_data)} target profiles![/green]")
    except Exception as e:
        console.print(f"[red][!] Error fetching queries: {e}[/red]")
        return
        
    engine = Prompt.ask("\n[bold yellow]Select Engine (shodan / fofa / censys / all)[/bold yellow]", choices=["shodan", "fofa", "censys", "all"], default="all").lower()
    
    shodan_key = os.getenv("SHODAN_API_KEY")
    fofa_email = os.getenv("FOFA_EMAIL")
    fofa_key = os.getenv("FOFA_API_KEY")
    censys_id = os.getenv("CENSYS_API_ID")
    censys_secret = os.getenv("CENSYS_API_SECRET")
    
    api_shodan = None
    if engine in ["shodan", "all"]:
        if not shodan_key or "YOUR_" in shodan_key:
            console.print("[red][!] SHODAN_API_KEY is missing in .env but shodan engine was selected![/red]")
            if engine == "shodan": return
        else:
            api_shodan = shodan.Shodan(shodan_key)
            
    if engine in ["fofa", "all"]:
        if not fofa_email or not fofa_key or "YOUR_" in fofa_email:
            console.print("[red][!] FOFA credentials missing in .env but fofa engine was selected![/red]")
            if engine == "fofa": return
            
    if engine in ["censys", "all"]:
        if not censys_id or not censys_secret or "YOUR_" in censys_id:
            console.print("[red][!] CENSYS credentials missing in .env but censys engine was selected![/red]")
            if engine == "censys": return
    
    vendors = list(set([str(item.get('vendor')) for item in queries_data if item.get('vendor')]))
    vendors.sort()
    
    console.print("\n[bold magenta]Select a Vendor/Technology to Hunt:[/bold magenta]")
    sample_vendors = [v for v in vendors if v in ['fortinet', 'apache', 'cisco', 'oracle', 'microsoft', 'php', 'wordpress']]
    console.print(f"[dim]Popular targets: {', '.join(sample_vendors)}[/dim]")
    
    choice = Prompt.ask("\n[bold yellow]Target Keyword (Vendor or Product)[/bold yellow]", default="forti").lower()
    
    selected_targets = [
        item for item in queries_data 
        if choice in str(item.get('vendor', '')).lower() or choice in str(item.get('name', '')).lower()
    ]
    
    if not selected_targets:
        console.print("[red][!] No intelligence found matching that keyword.[/red]")
        return
        
    found_names = list(set([str(item.get('name', '')) for item in selected_targets if item.get('name')]))
    console.print(f"[green][+] Found {len(selected_targets)} sub-products/services matching '{choice}'.[/green]")
    console.print(f"[dim]Matched: {', '.join(found_names[:7])}{' ...and more' if len(found_names) > 7 else ''}[/dim]")
    
    dorks_by_engine = {"shodan": [], "fofa": [], "censys": []}
    for target in selected_targets:
        for eng in target.get('engines', []):
            platform = eng.get('platform')
            if platform in dorks_by_engine:
                dorks_by_engine[platform].extend(eng.get('queries', []))
    
    all_ips = set()
    limit = int(Prompt.ask("[bold yellow]Max IP results to fetch per rule[/bold yellow]", default="50"))
    console.print("\n[bold red][!] LAUNCHING INDEX HARVESTER...[/bold red]\n")
    
    with open("targets.txt", "w") as f:
        if engine in ["shodan", "all"] and api_shodan:
            shodan_rules = dorks_by_engine["shodan"]
            if shodan_rules:
                for dork in track(shodan_rules, description="[cyan]Querying Shodan API...[/cyan]"):
                    try:
                        results = api_shodan.search(dork, limit=limit)
                        for match in results.get('matches', []):
                            ip_port = f"{match['ip_str']}:{match['port']}"
                            if ip_port not in all_ips:
                                all_ips.add(ip_port)
                                f.write(ip_port + "\n")
                    except Exception: pass
            else:
                console.print("[yellow][!] No Shodan dorks found for this target.[/yellow]")

        if engine in ["fofa", "all"] and fofa_email and fofa_key and "YOUR_" not in fofa_email:
            fofa_rules = dorks_by_engine["fofa"]
            if fofa_rules:
                for dork in track(fofa_rules, description="[magenta]Querying FOFA API...[/magenta]"):
                    try:
                        fofa_results = search_fofa(dork, fofa_email, fofa_key, limit)
                        for res in fofa_results:
                            if res not in all_ips:
                                all_ips.add(res)
                                f.write(res + "\n")
                    except Exception: pass
            else:
                console.print("[yellow][!] No FOFA dorks found for this target.[/yellow]")
                
        if engine in ["censys", "all"] and censys_id and censys_secret and "YOUR_" not in censys_id:
            censys_rules = dorks_by_engine["censys"]
            if censys_rules:
                for dork in track(censys_rules, description="[blue]Querying Censys API...[/blue]"):
                    try:
                        censys_results = search_censys(dork, censys_id, censys_secret, limit)
                        for res in censys_results:
                            if res not in all_ips:
                                all_ips.add(res)
                                f.write(res + "\n")
                    except Exception: pass
            else:
                console.print("[yellow][!] No Censys dorks found for this target.[/yellow]")

    console.print(f"\n[bold green][SUCCESS] Hunt Complete![/bold green]")
    console.print(f"[cyan][+] Harvested {len(all_ips)} unique vulnerable IPs. Saved to targets.txt[/cyan]")
    console.print(f"\n[bold white]Next Step:[/bold white] [yellow]nuclei -l targets.txt -t http/cves/[/yellow]\n")

if __name__ == "__main__":
    main()
