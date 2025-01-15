from typing import List, Dict, Optional, Union
import os
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import re
from dotenv import load_dotenv
from decimal import Decimal
import decimal

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_credentials() -> Optional[Credentials]:
    """
    Get or refresh Google API credentials.
    
    Returns:
        Optional[Credentials]: Google API credentials if successful, None if failed
        
    Note:
        Requires credentials.json file in the project root with Google API credentials
        Will create/update token.json for persistent authentication
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def extract_sheet_id(sheet_url: str) -> Optional[str]:
    """
    Extract the sheet ID from a Google Sheets URL.
    """
    print("\n=== URL Processing Debug ===")
    print(f"Original URL: {sheet_url}")
    
    # Clean the URL first - remove any fragments or query parameters
    sheet_url = sheet_url.split('#')[0]  # Remove fragment
    print(f"After removing fragment: {sheet_url}")
    
    sheet_url = sheet_url.split('?')[0]  # Remove query parameters
    print(f"After removing query params: {sheet_url}")
    
    # Pattern to match sheet ID in various Google Sheets URL formats
    patterns = [
        r"/spreadsheets/d/([a-zA-Z0-9-_]+)",  # Standard web URL
        r"^([a-zA-Z0-9-_]+)$"                 # Direct ID
    ]
    
    for i, pattern in enumerate(patterns):
        print(f"\nTrying pattern {i+1}: {pattern}")
        match = re.search(pattern, sheet_url)
        if match:
            sheet_id = match.group(1)
            print(f"Match found! Sheet ID: {sheet_id}")
            return sheet_id
        print("No match found with this pattern")
            
    print("Failed to extract sheet ID from URL")
    return None

def read_public_sheet(sheet_id: str) -> Optional[List[List[str]]]:
    """
    Read a public Google Sheet without authentication.
    """
    print("\n=== Sheet Reading Debug ===")
    try:
        # URL for public sheets CSV export
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        print(f"1. Constructed URL: {url}")
        
        print("2. Sending HTTP request...")
        response = requests.get(url)
        print(f"3. Response status code: {response.status_code}")
        print(f"4. Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            if response.status_code == 404:
                print("Sheet not found - please check if the URL is correct")
            elif response.status_code == 403:
                print("Access denied - please check sheet permissions")
            print(f"Response content: {response.text[:200]}...")  # First 200 chars
            return None
            
        # Parse CSV content
        content = response.text
        print(f"\n5. Response content type: {type(content)}")
        print(f"6. Content preview: {content[:200]}...")  # First 200 chars
        
        if not content.strip():
            print("7. Error: Received empty content")
            return None
            
        print(f"8. Content length: {len(content)} characters")
        
        # Split into lines and handle different line endings
        lines = [line for line in content.splitlines() if line.strip()]
        print(f"9. Found {len(lines)} non-empty lines")
        if lines:
            print("10. First line preview:", lines[0][:100])
            if len(lines) > 1:
                print("11. Second line preview:", lines[1][:100])
        
        if not lines:
            print("Error: No data found in sheet after parsing")
            return None
            
        # Parse CSV more carefully
        parsed_rows = []
        print("\n=== CSV Parsing Debug ===")
        for i, line in enumerate(lines):
            print(f"\nProcessing line {i+1}:")
            print(f"Raw line: {line[:100]}...")
            
            # Handle quoted values that might contain commas
            in_quotes = False
            current_value = []
            row_values = []
            
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                    print(f"Quote found, in_quotes now: {in_quotes}")
                elif char == ',' and not in_quotes:
                    value = ''.join(current_value).strip().strip('"')
                    print(f"Found value: {value}")
                    row_values.append(value)
                    current_value = []
                else:
                    current_value.append(char)
                    
            # Add the last value
            value = ''.join(current_value).strip().strip('"')
            print(f"Last value in row: {value}")
            row_values.append(value)
            print(f"Complete row: {row_values}")
            parsed_rows.append(row_values)
            
        print(f"\nFinal result: {len(parsed_rows)} rows parsed successfully")
        return parsed_rows
        
    except Exception as e:
        print(f"\nError reading public sheet:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("Traceback:")
        print(traceback.format_exc())
        return None

def read_google_sheet(sheet_url: str, range_name: str = 'A1:Z1000', require_auth: bool = False) -> Optional[List[List[str]]]:
    """
    Read contents of a Google Sheet given its URL.
    
    Args:
        sheet_url (str): The URL of the Google Sheet to read
        range_name (str): The range to read in A1 notation. Defaults to 'A1:Z1000'.
                         Only used when require_auth is True.
        require_auth (bool): Whether to use authentication. Set to True for private sheets,
                           False for public sheets.
        
    Returns:
        Optional[List[List[str]]]: List of rows, where each row is a list of cell values.
                                  Returns None if there's an error.
        
    Example:
        >>> # For public sheet
        >>> url = "https://docs.google.com/spreadsheets/d/your_sheet_id/edit"
        >>> data = read_google_sheet(url)
        
        >>> # For private sheet
        >>> data = read_google_sheet(url, require_auth=True)
        
    Raises:
        ValueError: If the sheet URL is invalid
        Exception: If there's an error accessing the sheet
    """
    try:
        # Get sheet ID from URL
        sheet_id = extract_sheet_id(sheet_url)
        if not sheet_id:
            raise ValueError("Invalid Google Sheets URL")
        
        if not require_auth:
            return read_public_sheet(sheet_id)
            
        # Get credentials and build service for authenticated access
        creds = get_credentials()
        if not creds:
            raise Exception("Failed to get Google API credentials")
        
        service = build('sheets', 'v4', credentials=creds)
        
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print('No data found in the sheet.')
            return None
            
        return values
        
    except Exception as e:
        print(f"Error reading Google Sheet: {str(e)}")
        return None

def get_sheet_contents(sheet_url: str, require_auth: bool = False) -> None:
    """
    Print the contents of a Google Sheet in a formatted way.
    
    Args:
        sheet_url (str): The URL of the Google Sheet to read and print
        require_auth (bool): Whether to use authentication. Set to True for private sheets,
                           False for public sheets.
        
    Example:
        >>> # For public sheet
        >>> url = "https://docs.google.com/spreadsheets/d/your_sheet_id/edit"
        >>> print_sheet_contents(url)
        
        >>> # For private sheet
        >>> print_sheet_contents(url, require_auth=True)
    """
    data = read_google_sheet(sheet_url, require_auth=require_auth)
    if data:
        for i, row in enumerate(data, 1):
            print(f"Row {i}: {row}")
    else:
        print("Failed to read sheet contents")

def load_product_inventory(sheet_url: str, require_auth: bool = False) -> List[Dict[str, Union[str, Decimal, int]]]:
    """
    Load and validate product inventory from a Google Sheet.
    
    Args:
        sheet_url (str): The URL of the Google Sheet containing product inventory
        require_auth (bool): Whether to use authentication
        
    Returns:
        List[Dict]: List of validated product dictionaries with the following structure:
            - name (str): Product name
            - price (Decimal): Product price
            - description (str): Product description
            - quantity (int): Available quantity
            - image (Optional[str]): Image URL if available
            
    Raises:
        ValueError: If sheet format is invalid or required data is missing
        
    Example:
        >>> url = "https://docs.google.com/spreadsheets/d/your_sheet_id/edit"
        >>> products = load_product_inventory(url)
        >>> for product in products:
        ...     print(f"{product['name']}: ${product['price']} (Qty: {product['quantity']})")
    """
    data = read_google_sheet(sheet_url, require_auth=require_auth)
    if not data:
        raise ValueError("Failed to read product inventory sheet")
        
    if len(data) < 2:  # Need at least header and one product
        raise ValueError("Sheet must contain header row and at least one product")
        
    # Validate header row
    headers = [h.strip().lower() for h in data[0]]
    required_fields = {'name', 'price', 'description', 'quantity'}
    if not required_fields.issubset(set(headers)):
        raise ValueError(f"Sheet must contain required fields: {required_fields}")
        
    # Get column indices
    name_idx = headers.index('name')
    price_idx = headers.index('price')
    desc_idx = headers.index('description')
    qty_idx = headers.index('quantity')
    image_idx = headers.index('image') if 'image' in headers else None
    
    products = []
    
    # Process each product row
    for row_num, row in enumerate(data[1:], 2):  # Start from 2 for error messages
        try:
            # Ensure row has enough columns
            if len(row) < len(required_fields):
                print(f"Warning: Skipping row {row_num} - insufficient columns")
                continue
                
            # Clean and validate data
            name = row[name_idx].strip()
            if not name:
                print(f"Warning: Skipping row {row_num} - missing product name")
                continue
                
            try:
                price = Decimal(row[price_idx].strip())
                if price < 0:
                    raise ValueError("Price cannot be negative")
            except (ValueError, decimal.InvalidOperation):
                print(f"Warning: Skipping row {row_num} - invalid price format")
                continue
                
            try:
                quantity = int(row[qty_idx].strip())
                if quantity < 0:
                    raise ValueError("Quantity cannot be negative")
            except ValueError:
                print(f"Warning: Skipping row {row_num} - invalid quantity format")
                continue
                
            # Create product dictionary
            product = {
                'name': name,
                'price': price,
                'description': row[desc_idx].strip(),
                'quantity': quantity
            }
            
            # Add image if available
            if image_idx is not None and len(row) > image_idx:
                image_url = row[image_idx].strip()
                if image_url:
                    product['image'] = image_url
                    
            products.append(product)
            
        except Exception as e:
            print(f"Warning: Error processing row {row_num}: {str(e)}")
            continue
            
    if not products:
        raise ValueError("No valid products found in sheet")
        
    return products

def print_inventory(sheet_url: str, require_auth: bool = False) -> str:
    """
    Format and return the product inventory as a string.
    
    Args:
        sheet_url (str): The URL of the Google Sheet containing product inventory
        require_auth (bool): Whether to use authentication
        
    Returns:
        str: Formatted string containing the inventory data or error message
    """
    output = []
    try:
        # First try to read the sheet
        data = read_google_sheet(sheet_url, require_auth=require_auth)
        if not data:
            return "Could not read the sheet. Please check if the URL is correct and the sheet is accessible."
            
        # Validate headers
        if len(data) < 1:
            return "Sheet appears to be empty."
            
        headers = [h.strip().lower() for h in data[0]]
        required_fields = {'name', 'price', 'description', 'quantity'}
        
        if not required_fields.issubset(set(headers)):
            missing = required_fields - set(headers)
            return f"Sheet is missing required columns: {', '.join(missing)}\nFound columns: {', '.join(headers)}"
            
        # Get column indices
        name_idx = headers.index('name')
        price_idx = headers.index('price')
        desc_idx = headers.index('description')
        qty_idx = headers.index('quantity')
        image_idx = headers.index('image') if 'image' in headers else None
        
        # Process products
        products = []
        errors = []
        
        for row_num, row in enumerate(data[1:], 2):
            try:
                if len(row) < len(required_fields):
                    errors.append(f"Row {row_num}: Insufficient columns")
                    continue
                    
                name = row[name_idx].strip()
                if not name:
                    errors.append(f"Row {row_num}: Missing product name")
                    continue
                    
                try:
                    price = Decimal(row[price_idx].strip())
                    if price < 0:
                        errors.append(f"Row {row_num}: Price cannot be negative")
                        continue
                except (ValueError, decimal.InvalidOperation):
                    errors.append(f"Row {row_num}: Invalid price format")
                    continue
                    
                try:
                    quantity = int(row[qty_idx].strip())
                    if quantity < 0:
                        errors.append(f"Row {row_num}: Quantity cannot be negative")
                        continue
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid quantity format")
                    continue
                    
                product = {
                    'name': name,
                    'price': price,
                    'description': row[desc_idx].strip(),
                    'quantity': quantity
                }
                
                if image_idx is not None and len(row) > image_idx:
                    image_url = row[image_idx].strip()
                    if image_url:
                        product['image'] = image_url
                        
                products.append(product)
                
            except Exception as e:
                errors.append(f"Row {row_num}: Error processing row - {str(e)}")
                
        # Format results
        output.append("\nInventory Loading Results:")
        output.append("-" * 80)
        output.append(f"Total rows processed: {len(data) - 1}")
        output.append(f"Successfully loaded products: {len(products)}")
        
        if errors:
            output.append(f"\nErrors encountered ({len(errors)}):")
            for error in errors:
                output.append(f"- {error}")
        
        if products:
            output.append("\nProduct Inventory:")
            output.append("-" * 80)
            for product in products:
                output.append(f"Name: {product['name']}")
                output.append(f"Price: ${product['price']}")
                output.append(f"Description: {product['description']}")
                output.append(f"Quantity: {product['quantity']}")
                if 'image' in product:
                    output.append(f"Image: {product['image']}")
                output.append("-" * 80)
        else:
            output.append("\nNo valid products found in the sheet.")
            
        return "\n".join(output)
            
    except Exception as e:
        error_msg = [
            f"Error loading inventory: {str(e)}",
            "Please check that:",
            "1. The sheet URL is correct",
            "2. The sheet is accessible",
            "3. The sheet has the required columns: name, price, description, quantity"
        ]
        return "\n".join(error_msg)
