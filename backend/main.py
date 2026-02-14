from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import os
import logging
import importlib
from typing import Dict, Set, List, Tuple

# Import error handlers
from app.error_handlers import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

# Import database utilities
from app.database import test_db_connection, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RouterManager:
    """Manages router imports and prevents duplicates"""
    
    def __init__(self):
        self.loaded_routers: Dict[str, any] = {}
        self.registered_prefixes: Set[str] = set()
        self.failed_imports: List[str] = []
    
    def safe_import_router(self, module_name: str, alias: str = None) -> Tuple[bool, any]:
        """Safely import a router module with proper error handling"""
        try:
            # Use importlib instead of __import__ for better performance and debugging
            module = importlib.import_module(f'app.routers.{module_name}')
            
            if not hasattr(module, 'router'):
                logger.warning(f"Module {module_name} has no 'router' attribute")
                return False, None
            
            router = module.router
            router_name = alias or module_name
            
            # Check for duplicate router names
            if router_name in self.loaded_routers:
                logger.warning(f"Router {router_name} already loaded, skipping duplicate")
                return False, None
            
            # Check for prefix conflicts
            router_prefix = getattr(router, 'prefix', f'/{module_name}')
            if router_prefix in self.registered_prefixes:
                logger.error(f"Prefix conflict: {router_prefix} already registered")
                return False, None
            
            self.loaded_routers[router_name] = router
            self.registered_prefixes.add(router_prefix)
            logger.info(f"✓ Successfully loaded router: {router_name} (prefix: {router_prefix})")
            return True, router
            
        except ImportError as e:
            logger.warning(f"✗ Import failed for {module_name}: {e}")
            self.failed_imports.append(module_name)
            return False, None
        except Exception as e:
            logger.error(f"✗ Unexpected error importing {module_name}: {e}")
            self.failed_imports.append(module_name)
            return False, None
    
    def get_summary(self) -> Dict[str, any]:
        """Get summary of loaded routers"""
        return {
            "loaded_count": len(self.loaded_routers),
            "loaded_routers": list(self.loaded_routers.keys()),
            "registered_prefixes": list(self.registered_prefixes),
            "failed_imports": self.failed_imports
        }

# Initialize router manager
router_manager = RouterManager()

# Core routers that must load successfully
CORE_ROUTERS = [
    'auth',
    'users', 
    'employees',
    'attendance',
    'leave',
    'announcements',
    'assets',
    'mobile_api'
]

# Optional routers with priority order (higher priority first)
OPTIONAL_ROUTERS = [
    # High priority - commonly used features
    ('ai_assistant', 'ai_assistant'),
    ('notifications', 'notifications'),
    ('admin', 'admin'),
    ('dashboard', 'dashboard'),
    
    # Medium priority - business features
    ('performance', 'performance'),
    ('onboarding', 'onboarding'),
    ('meetings', 'meetings'),
    ('payroll', 'payroll'),
    ('recruitment', 'recruitment'),
    
    # Lower priority - additional features
    ('infrastructure', 'infrastructure'),
    ('learning', 'learning'),
    ('engagement', 'engagement'),
    ('career', 'career'),
    ('predictive_analytics', 'predictive_analytics'),
    ('acknowledgments', 'acknowledgments'),
    ('attendance_extensions', 'attendance_extensions'),
    ('meeting_rooms', 'meeting_rooms'),
    ('documents', 'documents'),
    ('analysis_enhanced', 'analysis_enhanced'),
]

# Simple/fallback routers (only load if main version fails)
SIMPLE_ROUTERS = [
    ('dashboard_simple', 'dashboard_fallback'),
    ('recruitment_simple', 'recruitment_fallback'),
    ('performance_simple', 'performance_fallback'),
    ('career_simple', 'career_fallback'),
    ('onboarding_simple', 'onboarding_fallback'),
    ('meetings_simple', 'meetings_fallback'),
    ('documents_simple', 'documents_fallback'),
    ('predictive_analytics_simple', 'predictive_analytics_fallback'),
    ('analysis_simple', 'analysis_fallback'),
    ('engagement_simple', 'engagement_fallback'),
    ('learning_simple', 'learning_fallback'),
    ('admin_simple', 'admin_fallback'),
]

app = FastAPI(
    title="HR Management System API",
    description="Comprehensive HR Management System with secure authentication and role-based access control",
    version="2.0.0"
)

# Add error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Secure CORS configuration
def setup_cors():
    """Setup CORS with security considerations"""
    # Default secure origins
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5175",
        "https://dhanush-hr.netlify.app",
    ]
    
    # Add environment-specific origins
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)
    
    # Additional allowed origins from environment
    additional_origins = os.getenv("ADDITIONAL_CORS_ORIGINS", "").split(",")
    for origin in additional_origins:
        if origin.strip():
            origins.append(origin.strip())
    
    # Security check for wildcard CORS
    environment = os.getenv("ENVIRONMENT", "development").lower()
    cors_allow_all = os.getenv("CORS_ALLOW_ALL", "false").lower()
    
    if cors_allow_all == "true":
        if environment == "production":
            logger.error("🚨 SECURITY RISK: CORS_ALLOW_ALL=true in production environment!")
            logger.error("🚨 This exposes your HR data to cross-site attacks!")
            # Force secure origins in production even if CORS_ALLOW_ALL is set
            logger.info("🛡️ Forcing secure CORS origins in production")
        else:
            logger.warning("⚠️ CORS_ALLOW_ALL=true - only use in development!")
            origins = ["*"]
    
    logger.info(f"CORS Configuration: Environment={environment}, Origins={origins}")
    
    return origins

# Setup CORS
cors_origins = setup_cors()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint with system information"""
    return {
        "message": "HR Management System API",
        "version": "2.0.0",
        "status": "operational",
        "loaded_routers": len(router_manager.loaded_routers),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    """Comprehensive health check endpoint"""
    router_summary = router_manager.get_summary()
    
    # Test database connection
    db_status = "connected" if test_db_connection() else "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "routers": router_summary,
        "database": db_status,
        "cors_origins_count": len(cors_origins)
    }

@app.get("/debug/routers")
def debug_routers():
    """Debug endpoint to show router status (development only)"""
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        return {"error": "Debug endpoints disabled in production"}
    
    return router_manager.get_summary()

# Load core routers first
logger.info("Loading core routers...")
for router_name in CORE_ROUTERS:
    success, router = router_manager.safe_import_router(router_name)
    if success:
        try:
            app.include_router(router)
            logger.info(f"✓ Core router included: {router_name}")
        except Exception as e:
            logger.error(f"✗ Failed to include core router {router_name}: {e}")
    else:
        logger.error(f"✗ CRITICAL: Core router {router_name} failed to load!")

# Load optional routers with fallback logic
logger.info("Loading optional routers...")
for router_name, alias in OPTIONAL_ROUTERS:
    success, router = router_manager.safe_import_router(router_name, alias)
    if success:
        try:
            app.include_router(router)
            logger.info(f"✓ Optional router included: {alias}")
        except Exception as e:
            logger.error(f"✗ Failed to include optional router {alias}: {e}")

# Load simple/fallback routers only if main versions failed
logger.info("Loading fallback routers for failed imports...")
for router_name, alias in SIMPLE_ROUTERS:
    # Extract base name (remove _simple suffix)
    base_name = router_name.replace('_simple', '')
    
    # Only load if the main version failed or wasn't attempted
    if base_name in router_manager.failed_imports or base_name not in router_manager.loaded_routers:
        success, router = router_manager.safe_import_router(router_name, alias)
        if success:
            try:
                app.include_router(router)
                logger.info(f"✓ Fallback router included: {alias}")
            except Exception as e:
                logger.error(f"✗ Failed to include fallback router {alias}: {e}")

# Create uploads directory
uploads_dir = "uploads"
try:
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
    logger.info("✓ Static files mounted: /uploads")
except Exception as e:
    logger.error(f"✗ Failed to setup uploads directory: {e}")

# Log final summary
final_summary = router_manager.get_summary()
logger.info("=" * 60)
logger.info("🚀 HR Management System API Started")
logger.info(f"📊 Loaded Routers: {final_summary['loaded_count']}")
logger.info(f"✅ Successful: {', '.join(final_summary['loaded_routers'])}")
if final_summary['failed_imports']:
    logger.info(f"ℹ️  Using fallback routers for: {', '.join(final_summary['failed_imports'])}")
    logger.info(f"💡 Tip: Advanced features available via fallback routers. App is fully functional.")
logger.info(f"🌐 CORS Origins: {len(cors_origins)} configured")
logger.info(f"🔒 Environment: {os.getenv('ENVIRONMENT', 'development')}")

# Test database connection on startup
logger.info("=" * 60)
logger.info("🔌 Testing Database Connection...")
if test_db_connection():
    logger.info("✓ Database connection successful!")
    # Initialize database tables
    logger.info("📋 Initializing database tables...")
    if init_db():
        logger.info("✓ Database tables initialized!")
    else:
        logger.warning("⚠️ Database table initialization had issues")
else:
    logger.error("✗ Database connection failed! Check your DATABASE_URL in .env")
    logger.error("   Expected format: postgresql://user:password@host:port/database")

logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    
    # Production-ready configuration
    config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", 8000)),
        "reload": os.getenv("ENVIRONMENT", "development").lower() != "production",
        "workers": 1 if os.getenv("ENVIRONMENT", "development").lower() != "production" else int(os.getenv("WORKERS", 4)),
        "log_level": "info",
        "access_log": True
    }
    
    logger.info(f"Starting server with config: {config}")
    uvicorn.run(**config)