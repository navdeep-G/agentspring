#!/usr/bin/env python3
"""
Test runner for SupportFlow Agent API
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Duration: {end_time - start_time:.2f} seconds")
    print(f"Exit code: {result.returncode}")
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} failed!")
        return False
    else:
        print(f"✅ {description} completed successfully!")
        return True

def main():
    """Main test runner"""
    print("🚀 SupportFlow Agent Test Suite")
    print("=" * 60)
    
    
    # Install test dependencies
    print("\n📦 Installing test dependencies...")
    if not run_command("pip install pytest pytest-asyncio httpx", "Install test dependencies"):
        print("❌ Failed to install test dependencies")
        sys.exit(1)
    
    # Run unit tests
    print("\n🧪 Running unit tests...")
    if not run_command("python -m pytest tests/ -v --tb=short", "Unit tests"):
        print("❌ Unit tests failed")
        sys.exit(1)
    
    # Run integration tests
    print("\n🔗 Running integration tests...")
    if not run_command("python -m pytest tests/ -m integration -v", "Integration tests"):
        print("⚠️  Integration tests failed (some may require external services)")
    
    # Run performance tests
    print("\n⚡ Running performance tests...")
    if not run_command("python -m pytest tests/ -m performance -v", "Performance tests"):
        print("⚠️  Performance tests failed")
    
    # Run security tests
    print("\n🔒 Running security tests...")
    if not run_command("python -m pytest tests/ -m security -v", "Security tests"):
        print("⚠️  Security tests failed")
    
    # Generate coverage report
    print("\n📊 Generating coverage report...")
    run_command("python -m pytest tests/ --cov=. --cov-report=html --cov-report=term", "Coverage report")
    
    # Run linting
    print("\n🔍 Running code linting...")
    run_command("python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Code linting")
    
    print("\n🎉 Test suite completed!")
    print("📁 Coverage report available in: htmlcov/index.html")
    print("📁 Test results available in: .pytest_cache/")

if __name__ == "__main__":
    main() 