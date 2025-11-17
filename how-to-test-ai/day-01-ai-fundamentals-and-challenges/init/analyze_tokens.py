#!/usr/bin/env python3
"""
Token Usage Analysis Script for Promptfoo Results

This script analyzes token usage from promptfoo eval results and compares
providers to show which models use the most tokens and cost savings percentages.

Usage:
    python analyze_tokens.py [results.json]
    
If no file is specified, it defaults to 'results.json' in the current directory.
"""

import json
import sys
from collections import defaultdict
from typing import Dict, List, Tuple


def load_results(filepath: str) -> dict:
    """Load and parse the promptfoo results JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filepath}': {e}")
        sys.exit(1)


def extract_provider_data(results_data: dict) -> Dict[str, Dict]:
    """
    Extract token usage and cost data per provider from results.
    
    Returns a dictionary mapping provider IDs to their aggregated metrics.
    """
    provider_data = defaultdict(lambda: {
        'total_tokens': 0,
        'prompt_tokens': 0,
        'completion_tokens': 0,
        'assertion_tokens': 0,
        'cost': 0.0,
        'test_count': 0,
        'total_latency_ms': 0
    })
    
    # Extract data from results array
    results = results_data.get('results', {}).get('results', [])
    
    for result in results:
        provider_id = result.get('provider', {}).get('id', 'unknown')
        
        # Get response token usage
        response = result.get('response', {})
        token_usage = response.get('tokenUsage', {})
        
        # Get assertion/grading token usage
        grading_result = result.get('gradingResult', {})
        assertion_tokens = grading_result.get('tokensUsed', {}).get('total', 0)
        
        # Aggregate data
        provider_data[provider_id]['total_tokens'] += token_usage.get('total', 0)
        provider_data[provider_id]['prompt_tokens'] += token_usage.get('prompt', 0)
        provider_data[provider_id]['completion_tokens'] += token_usage.get('completion', 0)
        provider_data[provider_id]['assertion_tokens'] += assertion_tokens
        provider_data[provider_id]['cost'] += response.get('cost', 0.0)
        provider_data[provider_id]['test_count'] += 1
        provider_data[provider_id]['total_latency_ms'] += result.get('latencyMs', 0)
    
    return dict(provider_data)


def format_provider_name(provider_id: str) -> str:
    """Format provider ID into a more readable name."""
    # Remove common prefixes and format
    name = provider_id.replace('anthropic:', '').replace('openai:chat:', '').replace('openai:', '')
    return name


def calculate_percentages(provider_data: Dict[str, Dict]) -> Dict[str, float]:
    """
    Calculate percentage savings compared to the most expensive provider.
    
    Returns a dictionary mapping provider IDs to their percentage savings.
    """
    if not provider_data:
        return {}
    
    # Find the provider with the highest total tokens
    max_tokens_provider = max(provider_data.items(), key=lambda x: x[1]['total_tokens'])
    max_tokens = max_tokens_provider[1]['total_tokens']
    
    if max_tokens == 0:
        return {}
    
    percentages = {}
    for provider_id, data in provider_data.items():
        tokens = data['total_tokens']
        if tokens == max_tokens:
            percentages[provider_id] = 0.0  # This is the most expensive
        else:
            # Calculate percentage cheaper (savings)
            savings = ((max_tokens - tokens) / max_tokens) * 100
            percentages[provider_id] = savings
    
    return percentages


def print_comparison_table(provider_data: Dict[str, Dict], percentages: Dict[str, float]):
    """Print a formatted comparison table."""
    if not provider_data:
        print("No provider data found in results.")
        return
    
    # Find the provider with the most tokens
    max_tokens_provider = max(provider_data.items(), key=lambda x: x[1]['total_tokens'])
    max_provider_id = max_tokens_provider[0]
    
    # Sort providers by total tokens (descending)
    sorted_providers = sorted(
        provider_data.items(),
        key=lambda x: x[1]['total_tokens'],
        reverse=True
    )
    
    print("\n" + "=" * 100)
    print("TOKEN USAGE COMPARISON - PROMPTFOO RESULTS")
    print("=" * 100)
    print(f"\nMost Token-Intensive Provider: {format_provider_name(max_provider_id)}")
    print(f"  Total Tokens: {provider_data[max_provider_id]['total_tokens']:,}")
    print()
    
    # Table header
    print(f"{'Provider':<50} {'Total Tokens':<15} {'Cost ($)':<12} {'Savings %':<12} {'Tests':<8}")
    print("-" * 100)
    
    # Table rows
    for provider_id, data in sorted_providers:
        provider_name = format_provider_name(provider_id)
        total_tokens = data['total_tokens']
        cost = data['cost']
        savings = percentages.get(provider_id, 0.0)
        test_count = data['test_count']
        
        # Mark the most expensive with an indicator
        indicator = " ⭐ (Most)" if provider_id == max_provider_id else ""
        
        print(f"{provider_name:<50} {total_tokens:>14,} {cost:>11.6f} {savings:>11.2f}% {test_count:>7}{indicator}")
    
    print("-" * 100)
    
    # Summary statistics
    print("\nDETAILED BREAKDOWN:")
    print("-" * 100)
    for provider_id, data in sorted_providers:
        provider_name = format_provider_name(provider_id)
        print(f"\n{provider_name}:")
        print(f"  Prompt Tokens:        {data['prompt_tokens']:,}")
        print(f"  Completion Tokens:    {data['completion_tokens']:,}")
        print(f"  Assertion Tokens:     {data['assertion_tokens']:,}")
        print(f"  Total Tokens:         {data['total_tokens']:,}")
        print(f"  Total Cost:          ${data['cost']:.6f}")
        print(f"  Number of Tests:      {data['test_count']}")
        if data['test_count'] > 0:
            avg_latency = data['total_latency_ms'] / data['test_count']
            print(f"  Avg Latency:          {avg_latency:.0f} ms")
            avg_cost_per_test = data['cost'] / data['test_count']
            print(f"  Avg Cost per Test:    ${avg_cost_per_test:.6f}")
    
    print("\n" + "=" * 100)


def main():
    """Main function to run the analysis."""
    # Get filepath from command line or use default
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = 'results.json'
    
    print(f"Loading results from: {filepath}")
    
    # Load and parse results
    results_data = load_results(filepath)
    
    # Extract provider data
    provider_data = extract_provider_data(results_data)
    
    if not provider_data:
        print("No provider data found in results. Make sure the results file contains test results.")
        sys.exit(1)
    
    # Calculate percentage savings
    percentages = calculate_percentages(provider_data)
    
    # Print comparison table
    print_comparison_table(provider_data, percentages)


if __name__ == '__main__':
    main()

