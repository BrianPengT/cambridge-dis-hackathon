import os
import argparse
from dotenv import load_dotenv
from debate import Debate
import utils

# Load environment variables
load_dotenv(override=True)

def main():
    parser = argparse.ArgumentParser(description="FactTrace: Agentic Consensus Hackathon")
    parser.add_argument("--model", type=str, default="gpt-4.1-mini", help="Model to use (default: gpt-4.1-mini)")
    parser.add_argument("--csv", type=str, default="Celestia.csv", help="Path to CSV file (default: Celestia.csv)")
    parser.add_argument("--cases", type=int, default=3, help="Number of cases to process (default: 3)")
    parser.add_argument("--index", type=int, help="Specific case index to run (0-based)")
    
    args = parser.parse_args()
    
    utils.console.print(f"[bold green]Starting FactTrace with {args.model}...[/bold green]")
    
    # Load Data
    all_cases = utils.load_cases(args.csv, num_cases=None) # Load all first
    
    if args.index is not None:
        if 0 <= args.index < len(all_cases):
            cases = [all_cases[args.index]]
            utils.console.print(f"[bold cyan]Selected strictly Case #{args.index + 1}[/bold cyan]")
        else:
            utils.console.print(f"[red]Index {args.index} out of bounds (0-{len(all_cases)-1}). Exiting.[/red]")
            return
    else:
        # If no index, use random sampling or first N logic from utils
        # But since utils.load_cases returns random subset if num_cases argument is used... 
        # Let's just re-implement simple selection here for clarity
        import random
        if len(all_cases) > args.cases:
            cases = random.sample(all_cases, args.cases)
        else:
            cases = all_cases

    if not cases:
        utils.console.print("[red]No cases found. Exiting.[/red]")
        return

    # Initialize Debate System
    debate_system = Debate(model_input=args.model)
    
    # Run Loop
    for i, case in enumerate(cases):
        utils.print_case(i, case['internal_fact'], case['external_claim'])
        debate_system.run_debate(case['internal_fact'], case['external_claim'])
        
        # Wait/Pause logic could go here if needed
        utils.console.print("[dim]--------------------------------------------------[/dim]")

if __name__ == "__main__":
    main()
