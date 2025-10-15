# eCourts Case Status API

A FastAPI-based REST API for fetching court case status from the eCourts India portal.

## Problem Statement

The eCourts India Services website (https://services.ecourts.gov.in) provides case status information but lacks a programmatic API. This project creates a REST API that allows users to:

1. Check if a case is listed today or tomorrow
2. View the serial number and court name for listed cases
3. Download case PDFs (if available)
4. Download entire cause lists for specific dates

## API Information

**Base URL**: `http://localhost:8000`

**Framework**: FastAPI 0.104.1

**Documentation**: Available at `http://localhost:8000/docs` (Swagger UI)

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python main.py
```

or

```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

Note: Access the API using `localhost:8000`, not `0.0.0.0:8000`

## API Endpoints

### 1. Root Endpoint
**GET** `/`

Returns API information and available endpoints.

**Response**: API documentation links and endpoint list

---

### 2. Health Check
**GET** `/health`

Check if the API server is running.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-15T10:45:18.459234",
  "service": "eCourts API"
}
```

---

### 3. Check Case by CNR
**POST** `/case/cnr`

Search for a case using its CNR (Case Number Reference).

**Request Body**:
```json
{
  "cnr": "DLSW010093242025"
}
```

**CNR Format**: 4 letters + 12 digits (e.g., DLSW010093242025)

**Response**:
```json
{
  "cnr": "DLSW010093242025",
  "status": "success",
  "message": "Case found",
  "case_details": {
    "cnr": "DLSW010093242025",
    "listing_status": "Listed for tomorrow",
    "serial_number": "15",
    "court_name": "District and Session Judge, South-West DWK",
    "next_hearing": "16-10-2025"
  }
}
```

---

### 4. Check Case by Details
**POST** `/case/details`

Search for a case using case type, number, and year.

**Request Body**:
```json
{
  "case_type": "ARBTN",
  "case_number": 4,
  "case_year": 2025,
  "state": "Delhi",
  "district": "South West",
  "court_complex": "Dwarka Court Complex"
}
```

**Parameters**:
- `case_type` (required): Case type code (see list below)
- `case_number` (required): Case number (integer)
- `case_year` (required): Year (1950-2026)
- `state` (optional): State name (default: "Delhi")
- `district` (optional): District name (default: "South West")
- `court_complex` (optional): Court complex name (default: "Dwarka Court Complex")

**Response**:
```json
{
  "case_type": "ARBTN",
  "case_number": 4,
  "case_year": 2025,
  "status": "success",
  "message": "Case found",
  "case_details": {
    "case_reference": "ARBTN/4/2025",
    "listing_status": "Listed today",
    "serial_number": "8",
    "court_name": "District and Session Judge, South West",
    "next_hearing": "15-10-2025"
  }
}
```

---

### 5. Download Case PDF
**POST** `/case/download-pdf?cnr=DLSW010093242025`

Download PDF document for a specific case (if available).

**Query Parameter**:
- `cnr`: CNR number of the case

**Response**:
```json
{
  "message": "PDF download feature",
  "cnr": "DLSW010093242025",
  "status": "PDF not available for this case",
  "note": "PDF availability depends on court digitization status"
}
```

---

### 6. Download Cause List
**POST** `/causelist/download`

Download the complete cause list for a specific date.

**Request Body**:
```json
{
  "date": "15-10-2025",
  "state": "Delhi",
  "district": "South West",
  "court_complex": "Dwarka Court Complex"
}
```

**Date Format**: DD-MM-YYYY (e.g., 15-10-2025)

**Date Range**: Within 90 days from today

**Response**:
```json
{
  "date": "15-10-2025",
  "state": "Delhi",
  "district": "South West",
  "court_complex": "Dwarka Court Complex",
  "total_cases": 116,
  "cause_list": [
    {
      "serial_no": 1,
      "case_no": "Bail Matters/1702/2025",
      "parties": "STATE Vs S.K. DUBEY",
      "court": "District and Session Judge, South-West DWK"
    },
    {
      "serial_no": 8,
      "case_no": "ARBTN/4/2025",
      "parties": "MITU SATAPATHY Vs DJA COOPERATIVE GROUP HOUSING SOCIETY LTD",
      "court": "District and Session Judge, South-West DWK"
    }
  ],
  "download_url": "https://services.ecourts.gov.in/causelist/15102025.pdf",
  "message": "Cause list fetched successfully"
}
```

---

## Case Type Codes

The following case type codes are supported:

| Code | Full Name |
|------|-----------|
| ARBEP | Arbitration Execution Petition |
| A.R.B.O.P | Arbitration OP |
| ARBTN | Arbitration Cases |
| AS | Appeal Suit |
| ATA | Andhra Tenancy Appeal |
| A.T.C | Andhra Tenancy Case |
| CA | Copy Application |
| CC | Calendar Case |
| CC.APT | Calendar Case - AP Transco |
| CC.LG | Calendar Case - Land Grabbing |
| CMA | Civil Miscellaneous Appeal |
| CO.OP | Cooperative OP |
| COS | Commercial Suit (More than one Crore) |
| CRIME NO | Crime Number |
| CRLA | Criminal Appeal |

Note: Case types can contain letters, dots (.), hyphens (-), and spaces.

---

## Test Suite

The `test.py` file contains comprehensive tests for all API endpoints.

### Running Tests

```bash
python test.py
```

### Test Coverage

The test suite validates the following scenarios:

**1. Root Endpoint Test**
   - Verifies API is accessible and returns documentation

**2. Health Check Test**
   - Confirms server is running

**3. CNR Lookup Tests**
   - Valid CNRs: DLSW010093242025, DLSW010094032025
   - Invalid CNRs: Too short, wrong length, contains hyphen, wrong format

**4. Case Details Tests**
   - Valid cases:
     - ARBTN/4/2025
     - ARBTN/5/2025
     - A.R.B.O.P/1/2025
     - CO.OP/10/2025
     - AS/25/2025
     - CMA/50/2025
     - CC/100/2025
     - CC.APT/5/2025
     - ATA/12/2025
     - CRIME NO/123/2025
   - Invalid cases: Numeric case type, special characters, invalid years

**5. PDF Download Tests**
   - Valid CNRs: DLSW010093242025, DLSW010094032025
   - Invalid CNR: INVALID123

**6. Cause List Download Tests**
   - Valid dates: Today, tomorrow, next week
   - Invalid dates: Too old, wrong format, invalid date values

**7. Custom Parameters Test**
   - Tests with custom state, district, and court complex values

### Test Results

**Status**: All tests passing

**Total Test Scenarios**: 20+

**Test Categories**:
- Root endpoint: 1 test (Pass)
- Health check: 1 test (Pass)
- CNR lookup (valid): 2 tests (Pass)
- CNR lookup (invalid): 4 tests (Pass)
- Case details (valid): 10 tests (Pass)
- Case details (invalid): 5 tests (Pass)
- PDF download: 3 tests (Pass)
- Cause list (valid dates): 3 tests (Pass)
- Cause list (invalid dates): 4 tests (Pass)
- Custom parameters: 1 test (Pass)

**Validation Tests**:
- CNR format validation: Working
- Case type validation: Working
- Year range validation: Working
- Date format validation: Working
- Error handling: Working

All endpoints respond correctly with proper status codes (200 for success, 400/422 for validation errors, 500 for server errors).

---

## Error Handling

The API provides clear error messages for invalid inputs:

**Invalid CNR Format**:
```json
{
  "detail": "Invalid CNR format. Expected format: 4 letters + 12 digits (e.g., DLSW010093242025)"
}
```

**Invalid Case Type**:
```json
{
  "detail": [
    {
      "msg": "Value error, Case type should contain only letters, dots, hyphens, or spaces (e.g., ARBTN, A.R.B.O.P, CO.OP)"
    }
  ]
}
```

**Invalid Year**:
```json
{
  "detail": [
    {
      "msg": "Value error, Year should be between 1950 and 2026"
    }
  ]
}
```

**Invalid Date Format**:
```json
{
  "detail": [
    {
      "msg": "Value error, Date must be in DD-MM-YYYY format (e.g., 15-10-2025)"
    }
  ]
}
```

---

## Project Structure

```
.
├── main.py             # FastAPI application
├── test.py             # Test suite
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

---

## Dependencies

- fastapi==0.104.1
- uvicorn==0.24.0
- pydantic==2.5.0
- httpx==0.25.2
- python-multipart==0.0.6
- requests==2.31.0

---

## Notes

1. This is currently a mock implementation that returns sample data
2. To integrate with the actual eCourts website, web scraping and HTML parsing logic needs to be implemented
3. The eCourts website uses captcha which would need to be handled for real integration
4. All dates must be within 90 days from the current date for cause list downloads

---

## License

This project is created for educational and development purposes.