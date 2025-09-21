#!/usr/bin/env python3

import multiprocessing
from .service import AnalysisService


def main():
    """Main entry point for the startup analysis service"""
    # Required for multiprocessing on Windows and ensures compatibility
    multiprocessing.set_start_method('spawn', force=True)
    
    service = AnalysisService()
    try:
        service.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Service failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()