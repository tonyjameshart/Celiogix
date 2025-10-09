package com.glutenguardian.mobile.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.glutenguardian.mobile.data.BarcodeScan
import com.glutenguardian.mobile.database.AppDatabase
import com.glutenguardian.mobile.dao.BarcodeScanDao
import com.glutenguardian.mobile.network.ProductApiService
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class BarcodeScanViewModel(application: Application) : AndroidViewModel(application) {
    
    private val database = AppDatabase.getDatabase(application)
    private val barcodeScanDao: BarcodeScanDao = database.barcodeScanDao()
    private val productApiService = ProductApiService()
    
    private val _scanResult = MutableStateFlow<BarcodeScan?>(null)
    val scanResult: StateFlow<BarcodeScan?> = _scanResult.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    fun analyzeBarcode(barcode: String) {
        viewModelScope.launch {
            _isLoading.value = true
            
            try {
                // Check if we already have this barcode in database
                val existingScan = barcodeScanDao.getScanByBarcode(barcode)
                if (existingScan != null) {
                    _scanResult.value = existingScan
                    _isLoading.value = false
                    return@launch
                }
                
                // Fetch product information from API
                val productInfo = productApiService.getProductInfo(barcode)
                
                // Analyze gluten safety
                val safetyAnalysis = analyzeGlutenSafety(productInfo)
                
                // Create scan result
                val scan = BarcodeScan(
                    barcode = barcode,
                    productName = productInfo.name ?: "Unknown Product",
                    brand = productInfo.brand ?: "Unknown Brand",
                    ingredients = productInfo.ingredients ?: "No ingredients listed",
                    safetyStatus = safetyAnalysis.status,
                    confidence = safetyAnalysis.confidence,
                    warnings = safetyAnalysis.warnings.joinToString(", ")
                )
                
                _scanResult.value = scan
                
            } catch (e: Exception) {
                // Handle error - create unknown result
                val scan = BarcodeScan(
                    barcode = barcode,
                    productName = "Unknown Product",
                    brand = "Unknown Brand",
                    ingredients = "No ingredient information available",
                    safetyStatus = "UNKNOWN",
                    confidence = 0.0,
                    warnings = "Unable to retrieve product information"
                )
                _scanResult.value = scan
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun saveScan(scan: BarcodeScan) {
        viewModelScope.launch {
            try {
                barcodeScanDao.insertScan(scan)
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
    
    fun clearResult() {
        _scanResult.value = null
    }
    
    private fun analyzeGlutenSafety(productInfo: ProductInfo): SafetyAnalysis {
        val text = "${productInfo.name} ${productInfo.brand} ${productInfo.ingredients}".lowercase()
        
        // Simple gluten detection logic (in real app, use more sophisticated analysis)
        val glutenKeywords = listOf(
            "wheat", "barley", "rye", "triticale", "spelt", "kamut", 
            "malt", "brewer's yeast", "wheat flour", "barley flour"
        )
        
        val containsGluten = glutenKeywords.any { keyword -> text.contains(keyword) }
        
        val safeKeywords = listOf("gluten free", "gluten-free", "certified gluten free")
        val claimsSafe = safeKeywords.any { keyword -> text.contains(keyword) }
        
        return when {
            claimsSafe -> SafetyAnalysis("SAFE", 0.9, emptyList())
            containsGluten -> SafetyAnalysis("UNSAFE", 0.8, listOf("Contains gluten ingredients"))
            else -> SafetyAnalysis("UNKNOWN", 0.3, listOf("Unable to determine gluten content"))
        }
    }
    
    data class ProductInfo(
        val name: String?,
        val brand: String?,
        val ingredients: String?
    )
    
    data class SafetyAnalysis(
        val status: String,
        val confidence: Double,
        val warnings: List<String>
    )
}
