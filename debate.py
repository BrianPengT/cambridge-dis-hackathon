from typing import Dict, List
from agents import Agent
import utils

class Debate:
    def __init__(self, model_input: str = "gpt-4o-mini"):
        self.skeptic = Agent("Skeptic", model_name=model_input)
        self.fact_checker = Agent("Fact-Checker", model_name=model_input)
        self.common_sense = Agent("Common Sense", model_name=model_input)
        self.jury = Agent("Jury", model_name=model_input)

    def run_debate(self, internal_fact: str, external_claim: str) -> Dict[str, str]:
        """
        Runs the debate for a single case.
        """
        results = {}
        
        # Round 1: Initial Opinions
        utils.console.print("[bold]Round 1: Initial Analysis[/bold]")
        
        # Run sequentially for now to print progress, could be parallelized
        skeptic_opinion = self.skeptic.analyze(internal_fact, external_claim)
        results['Skeptic'] = skeptic_opinion
        utils.print_agent_opinion("Skeptic", "", skeptic_opinion, "red") # Verdict is embedded in text
        
        fact_opinion = self.fact_checker.analyze(internal_fact, external_claim)
        results['Fact-Checker'] = fact_opinion
        utils.print_agent_opinion("Fact-Checker", "", fact_opinion, "blue")

        common_opinion = self.common_sense.analyze(internal_fact, external_claim)
        results['Common Sense'] = common_opinion
        utils.print_agent_opinion("Common Sense", "", common_opinion, "yellow")

        # Round 2: Cross-Examination / Debate
        utils.console.print("[bold]Round 2: Cross-Examination[/bold]")
        
        # Prepare context for each agent (others' opinions)
        skeptic_context = f"FACT-CHECKER: {fact_opinion}\nCOMMON SENSE: {common_opinion}"
        fact_context = f"SKEPTIC: {skeptic_opinion}\nCOMMON SENSE: {common_opinion}"
        common_context = f"SKEPTIC: {skeptic_opinion}\nFACT-CHECKER: {fact_opinion}"
        
        # Agents respond
        skeptic_debate = self.skeptic.debate(internal_fact, external_claim, skeptic_context)
        utils.print_agent_opinion("Skeptic (Round 2)", "", skeptic_debate, "red")
        
        fact_debate = self.fact_checker.debate(internal_fact, external_claim, fact_context)
        utils.print_agent_opinion("Fact-Checker (Round 2)", "", fact_debate, "blue")
        
        common_debate = self.common_sense.debate(internal_fact, external_claim, common_context)
        utils.print_agent_opinion("Common Sense (Round 2)", "", common_debate, "yellow")

        # Round 3: Jury Deliberation
        utils.console.print("[bold]Round 3: Jury Deliberation[/bold]")
        transcript = f"""
        --- ROUND 1 ---
        SKEPTIC: {skeptic_opinion}
        FACT-CHECKER: {fact_opinion}
        COMMON SENSE: {common_opinion}
        
        --- ROUND 2 (DEBATE) ---
        SKEPTIC: {skeptic_debate}
        FACT-CHECKER: {fact_debate}
        COMMON SENSE: {common_debate}
        """
        
        jury_verdict = self.jury.analyze(internal_fact, external_claim, context=transcript)
        results['Jury'] = jury_verdict
        
        # Parse verdict slightly to print nicely
        utils.print_verdict("See below", jury_verdict)
        
        return results
