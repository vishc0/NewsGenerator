#!/usr/bin/env python3
"""
Validate that copilot-instructions.md is properly configured according to GitHub best practices.
"""

import sys
from pathlib import Path


def validate_copilot_instructions():
    """Validate the copilot-instructions.md file against GitHub best practices."""
    repo_root = Path(__file__).resolve().parents[1]
    copilot_file = repo_root / '.github' / 'copilot-instructions.md'
    
    errors = []
    warnings = []
    
    # Check 1: File exists
    if not copilot_file.exists():
        errors.append("❌ File .github/copilot-instructions.md does not exist")
        return errors, warnings
    
    print("✅ File exists at .github/copilot-instructions.md")
    
    # Check 2: File is readable
    try:
        content = copilot_file.read_text(encoding='utf-8')
    except Exception as e:
        errors.append(f"❌ Cannot read file: {e}")
        return errors, warnings
    
    print("✅ File is readable")
    
    # Check 3: File size (should be under 1000 lines)
    lines = content.split('\n')
    line_count = len(lines)
    if line_count > 1000:
        warnings.append(f"⚠️  File has {line_count} lines (recommended: under 1000)")
    else:
        print(f"✅ File size is appropriate ({line_count} lines)")
    
    # Check 4: Has proper heading
    if not content.strip().startswith('#'):
        warnings.append("⚠️  File should start with a Markdown heading")
    else:
        print("✅ File starts with a Markdown heading")
    
    # Check 5: Has recommended sections (based on best practices)
    recommended_sections = [
        'purpose',
        'tech stack',
        'architecture',
        'conventions',
        'workflows',
        'security',
    ]
    
    content_lower = content.lower()
    missing_sections = []
    
    for section in recommended_sections:
        if section not in content_lower:
            missing_sections.append(section)
    
    if missing_sections:
        warnings.append(f"⚠️  Consider adding sections for: {', '.join(missing_sections)}")
    else:
        print("✅ Contains recommended sections")
    
    # Check 6: Has proper Markdown structure
    headers = [line for line in lines if line.strip().startswith('#')]
    if len(headers) < 3:
        warnings.append("⚠️  File should have multiple sections with headers")
    else:
        print(f"✅ Has good structure ({len(headers)} headers)")
    
    # Check 7: Not empty
    if len(content.strip()) < 100:
        errors.append("❌ File content is too short to be useful")
    else:
        print("✅ File has substantial content")
    
    return errors, warnings


def main():
    print("Validating GitHub Copilot instructions setup...\n")
    
    errors, warnings = validate_copilot_instructions()
    
    print("\n" + "="*60)
    
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  {warning}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  {error}")
        print("\n❌ Validation FAILED")
        return 1
    
    if not warnings:
        print("\n✨ All checks passed! Copilot instructions are properly configured.")
    else:
        print("\n✅ Validation PASSED (with warnings)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
