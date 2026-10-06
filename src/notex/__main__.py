"""Allow python -m notex to use the command-line interface."""

from .cli import main

raise SystemExit(main())
