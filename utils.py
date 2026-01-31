import pandas as pd
from rich.console import Console
from rich.table import Table
from typing import List, Dict

console = Console()

def load_cases(csv_path: str, num_cases: int = None) -> List[Dict]:
    """
    Loads cases from the CSV file.
    
    Args:
        csv_path: Path to the CSV file.
        num_cases: Number of cases to load (default None = all).
        
    Returns:
        List of dictionaries containing 'internal_fact' and 'external_claim'.
    """
    try:
        df = pd.read_csv(csv_path)
        # Assuming CSV has 'claim' and 'truth' columns based on previous file view
        # truth -> Internal Fact, claim -> External Claim
        
        # Renaissance check: ensure columns exist
        if 'truth' not in df.columns or 'claim' not in df.columns:
            raise ValueError("CSV must contain 'truth' and 'claim' columns.")
            
        subset = df
        if num_cases is not None and len(df) > num_cases:
            subset = df.sample(n=num_cases, random_state=42)
            
        cases = []
        for _, row in subset.iterrows():
            cases.append({
                "internal_fact": row['truth'],
                "external_claim": row['claim']
            })
            
        return cases
    except Exception as e:
        console.print(f"[bold red]Error loading data:[/bold red] {e}")
        return []

def print_case(case_num: int, fact: str, claim: str):
    """Prints the case details nicely."""
    console.rule(f"[bold cyan]Case #{case_num + 1}[/bold cyan]")
    console.print(f"[bold yellow]Internal Fact:[/bold yellow] {fact}")
    console.print(f"[bold orange1]External Claim:[/bold orange1] {claim}")
    console.print("")

def print_agent_opinion(role: str, verdict: str, reason: str, color: str = "white"):
    """Prints an agent's opinion."""
    console.print(f"[{color}][bold]{role}:[/bold] {verdict}[/{color}]")
    console.print(f"[{color}]Reason: {reason}[/{color}]")
    console.print("")

def print_verdict(verdict: str, reason: str):
    """Prints the final jury verdict."""
    color = "green" if "Faithful" in verdict else "red"
    console.rule("[bold magenta]Final Verdict[/bold magenta]")
    console.print(f"[bold {color}]Verdict: {verdict}[/bold {color}]")
    console.print(f"[italic]Reason: {reason}[/italic]")
    console.print("")
