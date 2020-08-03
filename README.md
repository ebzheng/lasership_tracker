# A Lasership Tracker
Send email notifications to yourself for Lasership packages.

## Usage:
```
usage: lasership_tracker.py [-h] [--pollfreq POLLFREQ] [--console]
                            [--no-email]
                            LSID email

Monitor a Lasership package via the JSON API.

positional arguments:
  LSID                 Lasership tracking number (e.g. '1LS1234567890000-1')
  email                email address to notify

optional arguments:
  -h, --help           show this help message and exit
  --pollfreq POLLFREQ  polling interval (in seconds); default: 60
  --console            log records to console
  --no-email           disable emailing
```

## Example:
**Basic usage from a \*nix terminal:**
`./lasership_tracker.py 1LS1234567890123-1 you@example.com`

## Installation & Use:
Simply download `lasership_tracker.py` and ensure it has executable privileges. 
It depends on core python3 packages as well as the external `requests` library. 
This was developed to run from a \*nix-like terminal, 
but should work on any terminal when run as a python script 
(via `python lasership_tracker.py ...`).

## Caveats:
Sending emails directly from random computers may well look spammy and fail.
Successful delivery in your environment is not necessarily guaranteed. 
This will not work as-is for cloud environments due to anti-spam protections.
