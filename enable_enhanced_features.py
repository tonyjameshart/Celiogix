# path: enable_enhanced_features.py
"""
Enable Enhanced Features for CeliacShield

Import this module to enable all enhanced features across the application.
"""

# Import all enhancement modules to auto-apply enhancements
try:
    import panels.shopping_list_enhanced
    import panels.pantry_enhanced
    import panels.mobile_enhanced
    import panels.health_enhanced
    
    print("✅ Enhanced features enabled successfully!")
    print("📱 Real-time barcode scanning with nutrition data")
    print("🧮 Professional nutrition calculations")
    print("📍 Location-based restaurant finder")
    print("🔍 Better ingredient correlation")
    print("🛒 Intelligent product suggestions")
    
except ImportError as e:
    print(f"⚠️ Some enhanced features may not be available: {e}")

# Feature availability flags
FEATURES_ENABLED = {
    'nutrition_analysis': True,
    'restaurant_finder': True,
    'ingredient_correlation': True,
    'smart_shopping': True,
    'enhanced_barcode_scanning': True
}

def get_feature_status():
    """Get status of all enhanced features"""
    return FEATURES_ENABLED

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a specific feature is enabled"""
    return FEATURES_ENABLED.get(feature_name, False)