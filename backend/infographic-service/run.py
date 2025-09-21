#!/usr/bin/env python3

import multiprocessing
from dotenv import load_dotenv
load_dotenv()

from app.main import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
