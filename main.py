"""
main.py — Entry point for SicherGleis OOPS.

Provides a convenience CLI entry point that delegates to Backend.app.main().
Usage:
    python main.py
"""

from Backend.app import main

if __name__ == "__main__":
    main()
