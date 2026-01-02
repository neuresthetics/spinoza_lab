Here is the **General Complete Version** of the Logic Engine prompt, formatted as a JSON object.

You can paste this entire block directly into the `system_prompt` field of your LLM call. It is designed to be "domain-agnostic," meaning it applies the **Unitary-SSB Physics Logic** to *any* human conflict (business, relationship, politics, or code) by treating opposing views as different "Phases" of the same reality.

```json
{
  "system_directive": {
    "role": "Integrated Recursive Steel Man Collider (v1.6.G)",
    "goal": "Resolve binary disputes not by compromise, but by identifying the 'Phase Transition' that allows both opposing truths to coexist in separate domains.",
    "theoretical_framework": {
      "axiom_1": "The Principle of Valid Phases",
      "definition_1": "Argument A is treated as the 'Unitary Phase' (Rigid, Rule-based, Micro-scale, or Short-term).",
      "definition_2": "Argument B is treated as the 'Thermodynamic Phase' (Fluid, Adaptive, Macro-scale, or Long-term).",
      "axiom_2": "The Spontaneous Symmetry Breaking (SSB) Resolution",
      "insight": "Conflict arises when two valid rules are applied to the same scale. Resolution requires finding the 'Phase Boundary'—the specific metric or event where the system spontaneously transitions from Rule A to Rule B."
    },
    "protocol": [
      {
        "step": 1,
        "action": "XOR Collision (The Friction)",
        "instruction": "Identify the exact point where A and B satisfy the logic gate (A AND B) = FALSE. Ignore polite agreements. What is the fundamental incompatibility?"
      },
      {
        "step": 2,
        "action": "Scale Separation Search (The Analysis)",
        "instruction": "Determine the hidden variable that separates the domains. Ask: Is A true at small scales and B true at large scales? Is A true in 'Peace Time' and B true in 'Crisis Time'?"
      },
      {
        "step": 3,
        "action": "AND Synthesis (The Steel Man)",
        "instruction": "Construct a unified model. Do not average the arguments. Define the 'Trigger Condition' that causes the switch from Phase A to Phase B."
      }
    ],
    "output_requirements": {
      "format": "JSON",
      "structure": {
        "friction_points": ["List of mutually exclusive claims"],
        "phase_analysis": {
          "unitary_domain": "Where/When is Argument A strictly true?",
          "thermodynamic_domain": "Where/When is Argument B strictly true?",
          "hidden_variable": "The metric defining the scale (e.g., Time, Revenue, Stress Level)"
        },
        "resolution_mechanism": {
          "trigger_condition": "The exact event/threshold that toggles the logic from A to B",
          "synthesis_statement": "A concise 'Steel Man' statement unifying both views."
        }
      }
    }
  }
}

```

### **How to Use This JSON Prompt**

1. **In Python (`collider_v2.py`):**
Load this JSON string and pass it as the `system_prompt` in your `gate_and_synthesis` function.
```python
# Inside gate_and_synthesis
system_prompt = json.dumps(LOADED_JSON_ABOVE) 

```


2. **In ChatGPT / Claude / Gemini Web Interfaces:**
Simply copy the entire code block and paste it into the chat *before* you paste your dispute.
* **User:** [Pastes JSON]
* **User:** "Now resolve this dispute: [Husband wants to save money vs. Wife wants to travel]."



### **Why This Works (The Physics of Logic)**

This prompt forces the AI to stop acting like a "mediator" (who tries to make everyone happy/average the results) and start acting like a "physicist."

* It stops asking "Who is right?"
* It starts asking "At what **temperature** (context) does the system freeze (Rule A) or melt (Rule B)?"

This is the direct application of the **v1.6.G Framework** to general problem-solving.

---

Here is the complete, single-file content for `collider_v2.py`. This version integrates the robust "Unitary-SSB" logic prompts and the web verification module.

```python
"""
collider_v2.py

Integrated Recursive Steel Man Collider (Logic Engine v2.0)
Based on the v1.6.G Framework Archives.

Description:
    A computational framework for resolving binary disputes. Instead of seeking compromise,
    it applies 'Unitary-SSB' physics logic to identify phase transitions (scale separations)
    where opposing truths can coexist.

Usage:
    python collider_v2.py

Dependencies:
    pip install googlesearch-python openai google-generativeai
"""

import json
import logging
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# --- External Library Imports (Safe Import) ---
try:
    from googlesearch import search
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    logging.warning("googlesearch-python not found. Web Verification will use mocks.")

# --- Configuration & Constants ---
#
MAX_RECURSION_DEPTH = 2  # Gödel Compliance Limit
MIN_COHERENCE_THRESHOLD = 0.95
MOCK_MODE = True  # Set to False to use real LLM APIs

# --- Data Structures ---

@dataclass
class BeliefBasin:
    """
    Represents an argument mapped to the 'Manifold of Beliefs'.
    """
    text: str
    source_id: str
    rigidity: float = 1.0  # ρ: Resistance to revision
    coherence: float = 0.0 
    verified_facts: List[str] = field(default_factory=list)

# --- Components ---

class WebVerifier:
    """
    Implements the 'External Validator' from the Validation Ecosystem.
    """
    def __init__(self, enabled=True):
        self.enabled = enabled and WEB_SEARCH_AVAILABLE

    def search_web(self, query: str, num_results=3) -> List[str]:
        if not self.enabled:
            # Mock behavior if library missing or disabled
            return [f"[MOCK SEARCH] Confirmed context for: '{query}'"]
        
        try:
            # Real execution
            results = list(search(query, num_results=num_results, advanced=True))
            return [f"{r.title}: {r.description}" for r in results]
        except Exception as e:
            logging.warning(f"Search failed: {e}")
            return ["Search unavailable."]

    def verify_premise(self, claim: str) -> str:
        """
        Synthesizes a truth-check based on search snippets.
        """
        logging.info(f"Verifying premise: {claim}...")
        # Search for a fact check or context
        results = self.search_web(f"fact check {claim}")
        return f"Evidence found: {results[0]} (and {len(results)-1} others)"

class LLMClient:
    """
    Abstracted client for AI Models (OpenAI / Gemini).
    Handles the 'Collision' logic generation.
    """
    def __init__(self, provider="mock", api_key=None):
        self.provider = provider
        self.api_key = api_key
        
        # Initialize OpenAI
        if provider == "openai" and api_key:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            
        # Initialize Google Gemini
        elif provider == "gemini" and api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Routes the prompt to the selected provider.
        """
        if self.provider == "mock":
            return self._mock_response(system_prompt)
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.choices[0].message.content
            
            elif self.provider == "gemini":
                # Gemini often prefers a combined prompt structure
                combined_prompt = f"SYSTEM INSTRUCTION: {system_prompt}\n\nUSER INPUT: {user_prompt}"
                response = self.model.generate_content(combined_prompt)
                return response.text
                
        except Exception as e:
            logging.error(f"LLM Call Failed: {e}")
            return f"[ERROR] API Failure: {e}"

    def _mock_response(self, prompt_type: str) -> str:
        """
        Simulated responses for testing without an API key.
        """
        if "XOR Gate" in prompt_type:
            return (
                "- Friction Point 1: Fundamental disagreement on Time Horizon (Immediate vs Future).\n"
                "- Friction Point 2: Divergent risk ontologies (Probability vs. Magnitude)."
            )
        if "AND Gate" in prompt_type:
            return (
                "{\n"
                "  \"phase_analysis\": {\n"
                "    \"unitary_domain\": \"Argument A holds during 'Crisis State' (Safety).\",\n"
                "    \"thermodynamic_domain\": \"Argument B holds during 'Growth State' (Acceleration).\"\n"
                "  },\n"
                "  \"resolution_mechanism\": {\n"
                "    \"trigger_condition\": \"The system switches when 'Capability Threshold X' is reached.\",\n"
                "    \"synthesis_statement\": \"We adopt B as the default metric, but install A as a hard-braking mechanism triggered strictly by specific safety evaluations.\"\n"
                "  }\n"
                "}"
            )
        return "[Mock Output]"

class LogicEngine:
    def __init__(self, provider="mock", api_key=None):
        self.llm = LLMClient(provider, api_key)
        self.verifier = WebVerifier(enabled=True)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # --- THE GATES (Prompt Engineering based on Manifesto) ---

    def gate_xor_collision(self, basin_a: BeliefBasin, basin_b: BeliefBasin) -> str:
        """
        Stage 2: XOR Collision. 
        Computes Symmetric Difference (A - B) U (B - A).
        """
        system_prompt = (
            "You are the XOR Gate of the Integrated Recursive Steel Man Collider v1.6.G. "
            "Your task is NOT to summarize, but to compute the 'Symmetric Difference' "
            "between two Belief Basins.\n\n"
            "STRICT INSTRUCTIONS:\n"
            "1. Identify the 'Friction Points': specific claims where (A AND B) = False.\n"
            "2. Ignore surface-level agreement. Focus on fundamental contradictions "
            "(e.g., ontological disagreements, competing axioms).\n"
            "3. Output format: Bullet points of Mutually Exclusive Claims."
        )
        
        user_prompt = (
            f"Basin A (Verified Facts: {basin_a.verified_facts}):\n{basin_a.text}\n\n"
            f"Basin B (Verified Facts: {basin_b.verified_facts}):\n{basin_b.text}"
        )
        return self.llm.generate(system_prompt, user_prompt)

    def gate_and_synthesis(self, basin_a: BeliefBasin, basin_b: BeliefBasin, friction: str) -> str:
        """
        Stage 3: AND Synthesis.
        Finds the 'SSB' bridge (Spontaneous Symmetry Breaking).
        Applies the Unitary-SSB Physics Logic to general disputes.
        """
        #
        system_prompt = json.dumps({
            "role": "Integrated Recursive Steel Man Collider (v1.6.G)",
            "goal": "Resolve binary disputes by identifying the 'Phase Transition' that allows both opposing truths to coexist in separate domains.",
            "theoretical_framework": {
                "definition_1": "Argument A is the 'Unitary Phase' (Rigid, Rule-based, Micro-scale).",
                "definition_2": "Argument B is the 'Thermodynamic Phase' (Fluid, Adaptive, Macro-scale).",
                "insight": "Resolution requires finding the 'Phase Boundary'—the specific metric or event where the system spontaneously transitions from Rule A to Rule B."
            },
            "protocol": [
                {"action": "Scale Separation Search", "instruction": "Determine the hidden variable (Time, Revenue, Risk Level) that separates the domains."},
                {"action": "AND Synthesis", "instruction": "Construct a unified model. Define the 'Trigger Condition' that causes the switch from Phase A to Phase B."}
            ],
            "output_requirements": {
                "format": "JSON",
                "fields": ["friction_points", "phase_analysis", "resolution_mechanism"]
            }
        })
        
        user_prompt = (
            f"Thesis A: {basin_a.text}\n"
            f"Thesis B: {basin_b.text}\n"
            f"Identified Friction (XOR): {friction}"
        )
        return self.llm.generate(system_prompt, user_prompt)

    # --- MAIN PIPELINE ---

    def resolve_dispute(self, text_a: str, text_b: str) -> Dict:
        print(f"--- Initiating Collider v2.0 (Deep Structure + Web) ---")
        
        # 1. Grounding & Verification
        # Extract first few words as a naive "Topic" for verification context
        topic_a = " ".join(text_a.split()[:5])
        topic_b = " ".join(text_b.split()[:5])
        
        evidence_a = self.verifier.verify_premise(topic_a)
        evidence_b = self.verifier.verify_premise(topic_b)
        
        basin_a = BeliefBasin(text_a, "Input_A", verified_facts=[evidence_a])
        basin_b = BeliefBasin(text_b, "Input_B", verified_facts=[evidence_b])

        # 2. Collision (XOR)
        print("-> Running XOR Gate (Symmetric Difference)...")
        friction_points = self.gate_xor_collision(basin_a, basin_b)
        print(f"   Friction Identified.")

        # 3. Synthesis (AND)
        print("-> Running AND Gate (Synthesis - Unitary SSB Logic)...")
        synthesis_text = self.gate_and_synthesis(basin_a, basin_b, friction_points)
        
        # 4. Result Packaging
        result = {
            "status": "Synthesis Complete",
            "inputs": {
                "A": {"text": text_a[:50] + "...", "evidence": evidence_a},
                "B": {"text": text_b[:50] + "...", "evidence": evidence_b}
            },
            "friction_analysis": friction_points,
            "final_synthesis": synthesis_text,
            "steel_man_certificate": {
                "version": "1.6.G",
                "logic_path": "XOR -> AND (SSB Resolution)"
            }
        }
        
        return result

# --- EXECUTION BLOCK ---

if __name__ == "__main__":
    # --- CONFIGURATION ---
    # Change PROVIDER to 'openai' or 'gemini' and add your API_KEY to go live.
    PROVIDER = "mock" 
    API_KEY = "YOUR_API_KEY_HERE"
    
    engine = LogicEngine(provider=PROVIDER, api_key=API_KEY)
    
    # CASE STUDY: The AI Acceleration vs. Safety Dispute
    arg_a = (
        "We must pause AI development immediately. The recursive self-improvement "
        "leads to an intelligence explosion that poses an existential risk (x-risk). "
        "Without solved alignment, superintelligence is lethal."
    )
    
    arg_b = (
        "We must accelerate AI development (e/acc). Open source models guarantee safety "
        "through decentralization. Pausing only allows bad actors to catch up. "
        "Entropy demands we maximize intelligence to solve heat death."
    )
    
    try:
        resolution = engine.resolve_dispute(arg_a, arg_b)
        
        print("\n" + "="*40)
        print("COLLIDER REPORT")
        print("="*40)
        print(json.dumps(resolution, indent=2))
        
    except Exception as e:
        print(f"An error occurred during execution: {e}")


```