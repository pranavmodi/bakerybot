#!/usr/bin/env python3

from gdrive import get_sheet_contents
import argparse

def main():
    """
    Command line tool to test Google Sheets reading functionality.
    """
    parser = argparse.ArgumentParser(description='Read contents of a Google Sheet')
    parser.add_argument('url', help='URL of the Google Sheet')
    parser.add_argument('--auth', action='store_true', 
                       help='Use authentication (required for private sheets)')
    
    args = parser.parse_args()
    
    print(f"Reading sheet: {args.url}")
    print(f"Using authentication: {args.auth}")
    print("-" * 50)
    
    get_sheet_contents(args.url, require_auth=args.auth)

if __name__ == "__main__":
    main() 