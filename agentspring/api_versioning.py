"""
API Versioning for Enterprise Agent API
"""
from enum import Enum
from typing import Dict, Any, Optional, Callable
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class APIVersion(str, Enum):
    """API version enumeration"""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"

class VersionedResponse(BaseModel):
    """Base model for versioned responses"""
    version: str
    timestamp: datetime
    data: Dict[str, Any]

class VersionedRequest(BaseModel):
    """Base model for versioned requests"""
    version: str = Field(default="v1", description="API version")

class VersionManager:
    """Manages API versioning and compatibility"""
    
    def __init__(self):
        self.versions = {
            APIVersion.V1: {
                "deprecated": False,
                "sunset_date": None,
                "features": ["basic_analysis", "sync_processing"],
                "response_format": "legacy"
            },
            APIVersion.V2: {
                "deprecated": False,
                "sunset_date": None,
                "features": ["basic_analysis", "async_processing", "batch_processing", "admin_dashboard"],
                "response_format": "enhanced"
            },
            APIVersion.V3: {
                "deprecated": False,
                "sunset_date": None,
                "features": ["basic_analysis", "async_processing", "batch_processing", "admin_dashboard", "multi_tenancy", "configurable_routing"],
                "response_format": "modern"
            }
        }
        self.default_version = APIVersion.V2
        self.latest_version = APIVersion.V3
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Get information about a specific version"""
        if version not in self.versions:
            raise ValueError(f"Unknown API version: {version}")
        return self.versions[APIVersion(version)]
    
    def is_deprecated(self, version: str) -> bool:
        """Check if a version is deprecated"""
        version_info = self.get_version_info(version)
        return version_info.get("deprecated", False)
    
    def get_sunset_date(self, version: str) -> Optional[datetime]:
        """Get sunset date for a version"""
        version_info = self.get_version_info(version)
        return version_info.get("sunset_date")
    
    def get_supported_features(self, version: str) -> list:
        """Get features supported by a version"""
        version_info = self.get_version_info(version)
        return version_info.get("features", [])
    
    def transform_request(self, version: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform request data for specific version compatibility"""
        if version == APIVersion.V1:
            # V1 compatibility transformations
            if "customer_id" not in request_data:
                request_data["customer_id"] = "unknown"
            if "message" not in request_data:
                request_data["message"] = ""
        elif version == APIVersion.V2:
            # V2 compatibility transformations
            if "priority" not in request_data:
                request_data["priority"] = "Medium"
        elif version == APIVersion.V3:
            # V3 uses modern format, no transformations needed
            pass
        
        return request_data
    
    def transform_response(self, version: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform response data for specific version compatibility"""
        if version == APIVersion.V1:
            # V1 legacy format
            return {
                "summary": response_data.get("summary", ""),
                "category": response_data.get("category", ""),
                "priority": response_data.get("priority", ""),
                "routed_to": response_data.get("routed_to", ""),
                "escalation": response_data.get("escalation", "")
            }
        elif version == APIVersion.V2:
            # V2 enhanced format
            return {
                "summary": response_data.get("summary", ""),
                "category": response_data.get("category", ""),
                "priority": response_data.get("priority", ""),
                "routed_to": response_data.get("routed_to", ""),
                "escalation": response_data.get("escalation", ""),
                "confidence": response_data.get("confidence", 0.8),
                "processing_time": response_data.get("processing_time", 0.0),
                "metadata": {
                    "version": "v2",
                    "timestamp": datetime.now().isoformat()
                }
            }
        elif version == APIVersion.V3:
            # V3 modern format
            return {
                "summary": response_data.get("summary", ""),
                "category": response_data.get("category", ""),
                "priority": response_data.get("priority", ""),
                "routed_to": response_data.get("routed_to", ""),
                "escalation": response_data.get("escalation", ""),
                "confidence": response_data.get("confidence", 0.8),
                "processing_time": response_data.get("processing_time", 0.0),
                "tenant_id": response_data.get("tenant_id", ""),
                "routing_rules_applied": response_data.get("routing_rules_applied", []),
                "metadata": {
                    "version": "v3",
                    "timestamp": datetime.now().isoformat(),
                    "features_used": response_data.get("features_used", [])
                }
            }
        
        return response_data
    
    def validate_version(self, version: str) -> bool:
        """Validate if a version is supported"""
        try:
            self.get_version_info(version)
            return True
        except ValueError:
            return False
    
    def get_version_from_header(self, request: Request) -> str:
        """Extract API version from request headers"""
        # Check Accept header for version
        accept_header = request.headers.get("Accept", "")
        if "application/vnd.api.v3+json" in accept_header:
            return APIVersion.V3
        elif "application/vnd.api.v2+json" in accept_header:
            return APIVersion.V2
        elif "application/vnd.api.v1+json" in accept_header:
            return APIVersion.V1
        
        # Check X-API-Version header
        version_header = request.headers.get("X-API-Version", "")
        if version_header in [APIVersion.V1, APIVersion.V2, APIVersion.V3]:
            return version_header
        
        # Check URL path for version
        path = request.url.path
        if "/v3/" in path:
            return APIVersion.V3
        elif "/v2/" in path:
            return APIVersion.V2
        elif "/v1/" in path:
            return APIVersion.V1
        
        # Default to V2
        return self.default_version

# Global version manager
version_manager = VersionManager()

def get_api_version(request: Request) -> str:
    """Dependency to get API version from request"""
    version = version_manager.get_version_from_header(request)
    
    # Check if version is deprecated
    if version_manager.is_deprecated(version):
        sunset_date = version_manager.get_sunset_date(version)
        warning_msg = f"API version {version} is deprecated"
        if sunset_date:
            warning_msg += f" and will be sunset on {sunset_date}"
        
        logger.warning(warning_msg)
    
    return version

def create_versioned_router(prefix: str = "/api") -> APIRouter:
    """Create a versioned API router"""
    router = APIRouter(prefix=prefix)
    
    @router.get("/versions")
    async def get_versions():
        """Get information about all API versions"""
        versions_info = {}
        for version, info in version_manager.versions.items():
            versions_info[version] = {
                "deprecated": info["deprecated"],
                "sunset_date": info["sunset_date"],
                "features": info["features"],
                "response_format": info["response_format"]
            }
        
        return {
            "versions": versions_info,
            "default_version": version_manager.default_version,
            "latest_version": version_manager.latest_version
        }
    
    @router.get("/versions/{version}")
    async def get_version_info(version: str):
        """Get information about a specific API version"""
        try:
            info = version_manager.get_version_info(version)
            return {
                "version": version,
                "deprecated": info["deprecated"],
                "sunset_date": info["sunset_date"],
                "features": info["features"],
                "response_format": info["response_format"]
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    return router

def versioned_response(version: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a versioned response"""
    transformed_data = version_manager.transform_response(version, data)
    
    return VersionedResponse(
        version=version,
        timestamp=datetime.now(),
        data=transformed_data
    ).model_dump()

def versioned_request(version: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform request data for version compatibility"""
    return version_manager.transform_request(version, request_data) 