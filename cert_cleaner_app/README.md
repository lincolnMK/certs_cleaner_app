# Certificate Cleaner App
cert_cleaner_app/
├── cert_cleaner/                  # Core logic modules
│   ├── __init__.py
│   ├── cert_cleaner.py            # Script 1: Certificate renaming
│   ├── titleplan_cleaner.py       # Script 2: Title plan renaming
│   ├── merger.py                  # Script 3: Merge cert + title plan
│   ├── verifier.py                # Script 4: UPIN verification
│   └── utils.py                   # Shared helpers (e.g., UPIN extract, logging)
│
├── gui/                           # GUI interface
│   ├── __init__.py
│   ├── main_gui.py                # Tkinter GUI wrapper
│   └── widgets.py                 # Optional: reusable GUI components
│
├── assets/                        # Icons, logos, sample PDFs
│   └── logo.png
│
├── logs/                          # Runtime logs
│   └── run.log
│
├── tests/                         # Unit tests
│   ├── __init__.py
│   ├── test_cert_cleaner.py
│   ├── test_titleplan_cleaner.py
│   ├── test_merger.py
│   └── test_verifier.py
│
├── README.md                      # Project overview and usage
├── requirements.txt               # Dependencies
├── run.py                         # Entry point to launch GUI
└── config.py                      # Optional: central config (paths, flags)