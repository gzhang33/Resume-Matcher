#!/usr/bin/env python3
"""
AI Configuration Checker Script

This script checks if the AI agent configuration is correct and the services are available.
Run this script to diagnose issues with job description parsing.

Usage:
    python check_ai_config.py
"""

import asyncio
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.agent import AgentManager


async def check_llm_config():
    """Check LLM configuration"""
    print("=" * 60)
    print("LLM Configuration Check")
    print("=" * 60)
    
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print(f"LLM Model: {settings.LL_MODEL}")
    print(f"LLM Base URL: {settings.LLM_BASE_URL or 'Not set (using default)'}")
    print(f"LLM API Key: {'Set' if settings.LLM_API_KEY else 'Not set'}")
    print()
    
    if not settings.LLM_PROVIDER:
        print("❌ ERROR: LLM_PROVIDER is not set!")
        return False
    
    if not settings.LL_MODEL:
        print("❌ ERROR: LL_MODEL is not set!")
        return False
    
    print("✓ LLM configuration appears to be set")
    return True


async def check_embedding_config():
    """Check embedding configuration"""
    print("=" * 60)
    print("Embedding Configuration Check")
    print("=" * 60)
    
    print(f"Embedding Provider: {settings.EMBEDDING_PROVIDER}")
    print(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    print(f"Embedding Base URL: {settings.EMBEDDING_BASE_URL or 'Not set (using default)'}")
    print(f"Embedding API Key: {'Set' if settings.EMBEDDING_API_KEY else 'Not set'}")
    print()
    
    if not settings.EMBEDDING_PROVIDER:
        print("❌ ERROR: EMBEDDING_PROVIDER is not set!")
        return False
    
    if not settings.EMBEDDING_MODEL:
        print("❌ ERROR: EMBEDDING_MODEL is not set!")
        return False
    
    print("✓ Embedding configuration appears to be set")
    return True


async def test_llm_connection():
    """Test LLM connection by making a simple request"""
    print("=" * 60)
    print("LLM Connection Test")
    print("=" * 60)
    
    try:
        agent_manager = AgentManager()
        test_prompt = "Say 'Hello, world!' and nothing else."
        
        print("Sending test prompt to LLM...")
        response = await agent_manager.run(prompt=test_prompt)
        
        print(f"✓ LLM responded successfully!")
        print(f"Response: {response}")
        print()
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to LLM")
        print(f"Error message: {e}")
        print()
        return False


async def test_job_parsing():
    """Test job description parsing with a simple example"""
    print("=" * 60)
    print("Job Parsing Test")
    print("=" * 60)
    
    test_job_description = """
    Software Engineer Position
    
    We are looking for a skilled Software Engineer to join our team.
    
    Requirements:
    - Bachelor's degree in Computer Science
    - 3+ years of experience with Python
    - Experience with FastAPI and React
    - Knowledge of SQL databases
    
    Responsibilities:
    - Develop and maintain web applications
    - Write clean, maintainable code
    - Collaborate with team members
    """
    
    try:
        from app.services.job_service import JobService
        
        # Note: This is a simplified test without database connection
        job_service = JobService(db=None)
        
        print("Testing fallback keyword extraction...")
        keywords = job_service._extract_fallback_keywords(test_job_description)
        
        print(f"✓ Extracted {len(keywords)} keywords:")
        print(f"Keywords: {', '.join(keywords[:10])}...")
        print()
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to extract keywords")
        print(f"Error message: {e}")
        print()
        return False


async def main():
    """Run all checks"""
    print("\n🔍 Resume Matcher AI Configuration Checker\n")
    
    # Check configurations
    llm_config_ok = await check_llm_config()
    embedding_config_ok = await check_embedding_config()
    
    # Test connections if config is OK
    llm_connection_ok = False
    if llm_config_ok:
        llm_connection_ok = await test_llm_connection()
    
    # Test job parsing
    job_parsing_ok = await test_job_parsing()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_checks = [
        ("LLM Configuration", llm_config_ok),
        ("Embedding Configuration", embedding_config_ok),
        ("LLM Connection", llm_connection_ok),
        ("Fallback Keyword Extraction", job_parsing_ok),
    ]
    
    for check_name, status in all_checks:
        status_icon = "✓" if status else "❌"
        print(f"{status_icon} {check_name}")
    
    print()
    
    all_ok = all(status for _, status in all_checks[:3])  # First 3 are critical
    
    if all_ok:
        print("✓ All critical checks passed! AI services should work correctly.")
    else:
        print("❌ Some checks failed. Please review the errors above.")
        print("\nCommon solutions:")
        print("1. Make sure Ollama is running: `ollama serve`")
        print("2. Check if the model is installed: `ollama list`")
        print("3. Verify .env file configuration")
        print("4. Check backend logs for detailed error messages")
    
    print()
    return 0 if all_ok else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

