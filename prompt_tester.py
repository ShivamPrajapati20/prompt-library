"""
Prompt Library Tester
Loads prompts from prompts.json and runs them against test inputs.
Records results and optional quality scores.
"""
import os, json, time
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Anthropic()

def load_library(path: str = "prompts.json") -> list:
    with open(path) as f:
        return json.load(f)["prompts"]

def run_prompt(prompt_obj: dict, test_input: str) -> dict:
    start = time.time()
    r = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=prompt_obj["system"],
        messages=[{"role": "user", "content": test_input}]
    )
    elapsed = round(time.time() - start, 2)
    output = r.content[0].text
    tokens = r.usage.input_tokens + r.usage.output_tokens
    return {
        "prompt_id": prompt_obj["id"],
        "input": test_input[:80],
        "output": output,
        "tokens": tokens,
        "latency_s": elapsed,
        "timestamp": datetime.now().isoformat()
    }

def test_all(save_results: bool = True):
    prompts = load_library()
    results = []

    for p in prompts:
        print(f"\n{'='*55}")
        print(f"Testing: {p['name']} ({p['id']})")
        print(f"Tags: {', '.join(p['tags'])}")

        for test_input in p["test_inputs"]:
            result = run_prompt(p, test_input)
            results.append(result)

            print(f"\n  Input : {result['input']}...")
            print(f"  Output: {result['output'][:120]}...")
            print(f"  Tokens: {result['tokens']} | Latency: {result['latency_s']}s")

            score = input("  Quality score 1-5 (or Enter to skip): ").strip()
            if score:
                result["quality_score"] = int(score)

    if save_results:
        out_path = f"results_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {out_path}")

    return results

def test_one(prompt_id: str, custom_input: str = None):
    """Test a single prompt by ID."""
    prompts = {p["id"]: p for p in load_library()}
    if prompt_id not in prompts:
        print(f"Unknown prompt ID. Available: {list(prompts.keys())}")
        return
    p = prompts[prompt_id]
    inputs = [custom_input] if custom_input else p["test_inputs"]
    for inp in inputs:
        result = run_prompt(p, inp)
        print(f"\nPrompt: {p['name']}")
        print(f"Input : {inp}")
        print(f"Output:\n{result['output']}")
        print(f"Tokens: {result['tokens']} | Latency: {result['latency_s']}s")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_one(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        test_all()