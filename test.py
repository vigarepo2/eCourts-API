import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70 + "\n")

def print_response(response, test_name):
    """Print formatted API response"""
    print(f"Test: {test_name}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    print("-" * 70)

def test_root():
    """Test root endpoint"""
    print_section("Testing Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/")
        print_response(response, "Root Endpoint")
    except Exception as e:
        print(f"Error: {e}")

def test_health():
    """Test health check endpoint"""
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "Health Check")
    except Exception as e:
        print(f"Error: {e}")

def test_case_by_cnr_valid():
    """Test case lookup by CNR with valid CNR numbers"""
    print_section("Testing Case Lookup by CNR (Valid)")
    
    test_cases = [
        "DLSW010093242025",
        "DLSW010094032025"
    ]
    
    for cnr in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/case/cnr",
                json={"cnr": cnr}
            )
            print_response(response, f"CNR: {cnr}")
        except Exception as e:
            print(f"Error for CNR {cnr}: {e}\n")

def test_case_by_cnr_invalid():
    """Test case lookup by CNR with invalid CNR numbers"""
    print_section("Testing Case Lookup by CNR (Invalid Formats)")
    
    invalid_cases = [
        {"cnr": "123456", "reason": "Too short"},
        {"cnr": "DLSW01009324202", "reason": "Wrong length"},
        {"cnr": "DLSW-01009324202", "reason": "Contains hyphen"},
        {"cnr": "DL01009324202500", "reason": "Wrong format"},
    ]
    
    for case in invalid_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/case/cnr",
                json={"cnr": case["cnr"]}
            )
            print_response(response, f"Invalid CNR: {case['cnr']} ({case['reason']})")
        except Exception as e:
            print(f"Error: {e}\n")

def test_case_by_details_valid():
    """Test case lookup by case details with valid data"""
    print_section("Testing Case Lookup by Details (Valid)")
    
    test_cases = [
        {
            "case_type": "ARBTN",
            "case_number": 4,
            "case_year": 2025
        },
        {
            "case_type": "ARBTN",
            "case_number": 5,
            "case_year": 2025
        }
    ]
    
    for case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/case/details",
                json=case
            )
            print_response(
                response, 
                f"Case: {case['case_type']}/{case['case_number']}/{case['case_year']}"
            )
        except Exception as e:
            print(f"Error: {e}\n")

def test_case_by_details_invalid():
    """Test case lookup by case details with invalid data"""
    print_section("Testing Case Lookup by Details (Invalid)")
    
    invalid_cases = [
        {
            "data": {"case_type": "123", "case_number": 4, "case_year": 2025},
            "reason": "Numeric case type"
        },
        {
            "data": {"case_type": "ARBTN", "case_number": 4, "case_year": 1900},
            "reason": "Invalid year (too old)"
        },
        {
            "data": {"case_type": "ARBTN", "case_number": 4, "case_year": 2030},
            "reason": "Invalid year (too far in future)"
        }
    ]
    
    for case in invalid_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/case/details",
                json=case["data"]
            )
            print_response(response, f"Invalid: {case['reason']}")
        except Exception as e:
            print(f"Error: {e}\n")

def test_download_pdf():
    """Test PDF download functionality"""
    print_section("Testing PDF Download")
    
    test_cases = [
        {"cnr": "DLSW010093242025", "valid": True},
        {"cnr": "DLSW010094032025", "valid": True},
        {"cnr": "INVALID123", "valid": False}
    ]
    
    for case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/case/download-pdf",
                params={"cnr": case["cnr"]}
            )
            status = "Valid" if case["valid"] else "Invalid"
            print_response(response, f"PDF Download - CNR: {case['cnr']} ({status})")
        except Exception as e:
            print(f"Error: {e}\n")

def test_causelist_download_valid():
    """Test cause list download with valid dates"""
    print_section("Testing Cause List Download (Valid Dates)")
    
    # Today and tomorrow
    today = datetime.now().strftime("%d-%m-%Y")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")
    
    test_dates = [today, tomorrow, next_week]
    
    for date in test_dates:
        try:
            response = requests.post(
                f"{BASE_URL}/causelist/download",
                json={"date": date}
            )
            print_response(response, f"Cause List for {date}")
        except Exception as e:
            print(f"Error for date {date}: {e}\n")

def test_causelist_download_invalid():
    """Test cause list download with invalid dates"""
    print_section("Testing Cause List Download (Invalid Dates)")
    
    invalid_dates = [
        {"date": "15-10-2023", "reason": "More than 90 days old"},
        {"date": "2025-10-15", "reason": "Wrong format (YYYY-MM-DD)"},
        {"date": "32-13-2025", "reason": "Invalid date"},
        {"date": "abc", "reason": "Not a date"}
    ]
    
    for case in invalid_dates:
        try:
            response = requests.post(
                f"{BASE_URL}/causelist/download",
                json={"date": case["date"]}
            )
            print_response(response, f"Invalid Date: {case['date']} ({case['reason']})")
        except Exception as e:
            print(f"Error: {e}\n")

def test_custom_parameters():
    """Test with custom state, district, and court parameters"""
    print_section("Testing Custom Parameters")
    
    try:
        response = requests.post(
            f"{BASE_URL}/case/details",
            json={
                "case_type": "ARBTN",
                "case_number": 4,
                "case_year": 2025,
                "state": "Delhi",
                "district": "South West",
                "court_complex": "Dwarka Court Complex"
            }
        )
        print_response(response, "Case with Custom Parameters")
    except Exception as e:
        print(f"Error: {e}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" eCourts API Test Suite")
    print(" Make sure the API server is running on http://localhost:8000")
    print("="*70)
    
    try:
        # Basic tests
        test_root()
        test_health()
        
        # CNR tests
        test_case_by_cnr_valid()
        test_case_by_cnr_invalid()
        
        # Case details tests
        test_case_by_details_valid()
        test_case_by_details_invalid()
        test_custom_parameters()
        
        # PDF download tests
        test_download_pdf()
        
        # Cause list tests
        test_causelist_download_valid()
        test_causelist_download_invalid()
        
        print_section("All Tests Completed")
        print("✓ Test suite execution finished successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server!")
        print("Please make sure the server is running:")
        print("  python main.py")
        print("  or")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_all_tests()