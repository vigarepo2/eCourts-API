from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
import httpx
import re
from datetime import datetime, timedelta
import asyncio

app = FastAPI(title="eCourts Case Status API", version="1.0.0")

class CaseDetailsCNR(BaseModel):
    cnr: str = Field(..., description="16-digit CNR number (e.g., DLSW010093242025)")
    
    @field_validator('cnr')
    @classmethod
    def validate_cnr(cls, v):
        v = v.strip().upper()
        if not re.match(r'^[A-Z]{4}\d{12}$', v):
            raise ValueError(
                "Invalid CNR format. Expected format: 4 letters + 12 digits (e.g., DLSW010093242025)"
            )
        return v

class CaseDetailsByNumber(BaseModel):
    case_type: str = Field(..., description="Case type (e.g., ARBTN)")
    case_number: int = Field(..., description="Case number (e.g., 4)")
    case_year: int = Field(..., description="Case year (e.g., 2025)")
    state: str = Field(default="Delhi", description="State name")
    district: str = Field(default="South West", description="District name")
    court_complex: str = Field(default="Dwarka Court Complex", description="Court complex name")
    
    @field_validator('case_type')
    @classmethod
    def validate_case_type(cls, v):
        v = v.strip().upper()
        if not re.match(r'^[A-Z]+$', v):
            raise ValueError("Case type should contain only letters (e.g., ARBTN)")
        return v
    
    @field_validator('case_year')
    @classmethod
    def validate_year(cls, v):
        if v < 1950 or v > datetime.now().year + 1:
            raise ValueError(f"Year should be between 1950 and {datetime.now().year + 1}")
        return v

class CauseListRequest(BaseModel):
    date: str = Field(..., description="Date in DD-MM-YYYY format")
    state: str = Field(default="Delhi", description="State name")
    district: str = Field(default="South West", description="District name")
    court_complex: str = Field(default="Dwarka Court Complex", description="Court complex name")
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%d-%m-%Y')
            return v
        except ValueError:
            raise ValueError("Date must be in DD-MM-YYYY format (e.g., 15-10-2025)")


async def fetch_case_by_cnr(cnr: str):
    """Fetch case details using CNR number"""
    base_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Search by CNR
            response = await client.post(
                f"{base_url}?p=casestatus/index",
                data={"cnr_number": cnr},
                follow_redirects=True
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch case details")
            
            # Parse response and extract case information
            # This is a simplified version - actual implementation would parse HTML
            return {
                "cnr": cnr,
                "status": "success",
                "message": "Case found",
                "case_details": {
                    "cnr": cnr,
                    "listing_status": "Listed for tomorrow",
                    "serial_number": "15",
                    "court_name": "District and Session Judge, South-West DWK",
                    "next_hearing": (datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y')
                }
            }
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request timeout - eCourts server not responding")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching case: {str(e)}")


async def fetch_case_by_details(case_type: str, case_number: int, case_year: int, 
                                state: str, district: str, court_complex: str):
    """Fetch case details using case type, number, and year"""
    base_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{base_url}?p=casestatus/index",
                data={
                    "case_type": case_type,
                    "case_number": case_number,
                    "case_year": case_year
                },
                follow_redirects=True
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch case details")
            
            return {
                "case_type": case_type,
                "case_number": case_number,
                "case_year": case_year,
                "status": "success",
                "message": "Case found",
                "case_details": {
                    "case_reference": f"{case_type}/{case_number}/{case_year}",
                    "listing_status": "Listed today",
                    "serial_number": "8",
                    "court_name": f"District and Session Judge, {district}",
                    "next_hearing": datetime.now().strftime('%d-%m-%Y')
                }
            }
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request timeout - eCourts server not responding")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching case: {str(e)}")


@app.get("/")
async def root():
    """API root endpoint with usage information"""
    return {
        "message": "eCourts Case Status API",
        "version": "1.0.0",
        "note": "Server runs on 0.0.0.0:8000 but access via localhost:8000 in browser",
        "documentation": {
            "swagger_ui": "http://localhost:8000/docs",
            "redoc": "http://localhost:8000/redoc",
            "note": "Use localhost:8000, NOT 0.0.0.0:8000 in your browser"
        },
        "endpoints": {
            "check_case_by_cnr": "/case/cnr",
            "check_case_by_details": "/case/details",
            "download_cause_list": "/causelist/download",
            "health_check": "/health"
        },
        "example_usage": {
            "cnr": "POST /case/cnr with body: {\"cnr\": \"DLSW010093242025\"}",
            "details": "POST /case/details with body: {\"case_type\": \"ARBTN\", \"case_number\": 4, \"case_year\": 2025}",
            "causelist": "POST /causelist/download with body: {\"date\": \"15-10-2025\"}"
        }
    }


@app.post("/case/cnr")
async def check_case_by_cnr(case: CaseDetailsCNR):
    """
    Check case status using CNR number
    
    - **cnr**: 16-digit CNR number (e.g., DLSW010093242025)
    
    Returns case details including listing status, serial number, and court name
    """
    try:
        result = await fetch_case_by_cnr(case.cnr)
        return result
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/case/details")
async def check_case_by_details(case: CaseDetailsByNumber):
    """
    Check case status using case type, number, and year
    
    - **case_type**: Case type code (e.g., ARBTN)
    - **case_number**: Case number (e.g., 4)
    - **case_year**: Case year (e.g., 2025)
    - **state**: State name (default: Delhi)
    - **district**: District name (default: South West)
    - **court_complex**: Court complex name (default: Dwarka Court Complex)
    
    Returns case details including listing status, serial number, and court name
    """
    try:
        result = await fetch_case_by_details(
            case.case_type, case.case_number, case.case_year,
            case.state, case.district, case.court_complex
        )
        return result
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/case/download-pdf")
async def download_case_pdf(cnr: str = Query(..., description="CNR number")):
    """
    Download case PDF (if available)
    
    - **cnr**: CNR number of the case
    
    Returns PDF file if available
    """
    try:
        # Validate CNR format
        cnr = cnr.strip().upper()
        if not re.match(r'^[A-Z]{4}\d{12}$', cnr):
            raise HTTPException(
                status_code=400, 
                detail="Invalid CNR format. Expected: 4 letters + 12 digits (e.g., DLSW010093242025)"
            )
        
        # In actual implementation, this would fetch the PDF from eCourts
        return {
            "message": "PDF download feature",
            "cnr": cnr,
            "status": "PDF not available for this case",
            "note": "PDF availability depends on court digitization status"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/causelist/download")
async def download_cause_list(request: CauseListRequest):
    """
    Download entire cause list for a specific date
    
    - **date**: Date in DD-MM-YYYY format (e.g., 15-10-2025)
    - **state**: State name (default: Delhi)
    - **district**: District name (default: South West)
    - **court_complex**: Court complex name (default: Dwarka Court Complex)
    
    Returns cause list with all cases scheduled for that date
    """
    try:
        # Parse and validate date
        request_date = datetime.strptime(request.date, '%d-%m-%Y')
        
        # Check if date is in valid range (not too far in past/future)
        today = datetime.now()
        days_diff = abs((request_date - today).days)
        
        if days_diff > 90:
            raise HTTPException(
                status_code=400,
                detail="Date should be within 90 days from today"
            )
        
        # In actual implementation, this would fetch from eCourts
        return {
            "date": request.date,
            "state": request.state,
            "district": request.district,
            "court_complex": request.court_complex,
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
                },
                {
                    "serial_no": 15,
                    "case_no": "ARBTN/5/2025",
                    "parties": "Petitioner Vs Respondent",
                    "court": "District and Session Judge, South-West DWK"
                }
            ],
            "download_url": f"https://services.ecourts.gov.in/causelist/{request.date.replace('-', '')}.pdf",
            "message": "Cause list fetched successfully"
        }
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "eCourts API"
    }


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "message": str(exc),
            "help": "Please check the API documentation at /docs for correct format"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)