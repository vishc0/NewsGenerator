"""Token usage estimation and reporting for LLM API calls."""

import logging
from datetime import datetime, timezone


def utc_now():
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class TokenUsageTracker:
    """Track and estimate token usage across pipeline runs."""
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls = 0
        self.failed_calls = 0
        self.provider_usage = {}  # Track usage per provider (hf, openai, etc.)
    
    def estimate_tokens(self, text):
        """Rough token estimation: ~0.75 tokens per word for English text."""
        words = text.split()
        return int(len(words) * 0.75)
    
    def record_call(self, input_text, output_text, provider='unknown', success=True):
        """Record an API call with input and output text."""
        input_tokens = self.estimate_tokens(input_text)
        output_tokens = self.estimate_tokens(output_text) if output_text else 0
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.api_calls += 1
        
        if not success:
            self.failed_calls += 1
        
        # Track per-provider usage
        if provider not in self.provider_usage:
            self.provider_usage[provider] = {
                'input_tokens': 0,
                'output_tokens': 0,
                'calls': 0
            }
        
        self.provider_usage[provider]['input_tokens'] += input_tokens
        self.provider_usage[provider]['output_tokens'] += output_tokens
        self.provider_usage[provider]['calls'] += 1
    
    def get_report(self):
        """Generate a usage report."""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        
        report = [
            "="* 60,
            "Token Usage Report",
            "="* 60,
            f"Total API Calls: {self.api_calls}",
            f"Failed Calls: {self.failed_calls}",
            f"Total Input Tokens: {self.total_input_tokens:,}",
            f"Total Output Tokens: {self.total_output_tokens:,}",
            f"Total Tokens: {total_tokens:,}",
            ""
        ]
        
        if self.provider_usage:
            report.append("Usage by Provider:")
            for provider, usage in self.provider_usage.items():
                total = usage['input_tokens'] + usage['output_tokens']
                report.append(f"  {provider}:")
                report.append(f"    Calls: {usage['calls']}")
                report.append(f"    Input Tokens: {usage['input_tokens']:,}")
                report.append(f"    Output Tokens: {usage['output_tokens']:,}")
                report.append(f"    Total Tokens: {total:,}")
            report.append("")
        
        # Add cost estimates (approximate)
        report.extend([
            "Estimated Costs (approximate):",
            "  Hugging Face Inference API: FREE (with rate limits)",
            f"  OpenAI GPT-3.5-Turbo: ~${(total_tokens / 1000) * 0.002:.4f}",
            f"    (assuming $0.002 per 1K tokens average)",
            "="* 60
        ])
        
        return '\n'.join(report)
    
    def log_report(self):
        """Log the usage report."""
        logging.info("\n" + self.get_report())
    
    def save_report(self, output_path):
        """Save the usage report to a file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Token Usage Report - {utc_now().isoformat()}\n")
            f.write(self.get_report())


# Global tracker instance
_global_tracker = None


def get_tracker():
    """Get the global token usage tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = TokenUsageTracker()
    return _global_tracker


def reset_tracker():
    """Reset the global tracker."""
    global _global_tracker
    _global_tracker = TokenUsageTracker()
