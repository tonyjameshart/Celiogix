package com.glutenguardian.mobile.viewmodel

import android.app.Application
import android.os.Environment
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.glutenguardian.mobile.database.AppDatabase
import com.glutenguardian.mobile.dao.BarcodeScanDao
import com.glutenguardian.mobile.dao.HealthLogDao
import com.opencsv.CSVWriter
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.*

class ExportViewModel(application: Application) : AndroidViewModel(application) {
    
    private val database = AppDatabase.getDatabase(application)
    private val barcodeScanDao: BarcodeScanDao = database.barcodeScanDao()
    private val healthLogDao: HealthLogDao = database.healthLogDao()
    
    private val _exportStatus = MutableStateFlow(ExportStatus())
    val exportStatus: StateFlow<ExportStatus> = _exportStatus.asStateFlow()
    
    private val _exportedFiles = MutableStateFlow<List<File>>(emptyList())
    val exportedFiles: StateFlow<List<File>> = _exportedFiles.asStateFlow()
    
    init {
        loadExportedFiles()
    }
    
    fun exportHealthLogs() {
        viewModelScope.launch {
            _exportStatus.value = ExportStatus(isLoading = true, message = "Exporting health logs...")
            
            try {
                val healthLogs = healthLogDao.getAllHealthLogs()
                val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
                val fileName = "health_logs_$timestamp.csv"
                val file = createCsvFile(fileName)
                
                FileWriter(file).use { writer ->
                    CSVWriter(writer).use { csvWriter ->
                        // Write header
                        csvWriter.writeNext(arrayOf(
                            "Date", "Time", "Meal", "Items", "Risk", "Onset_Minutes", 
                            "Severity", "Bristol_Type", "Recipe", "Symptoms", "Notes",
                            "Hydration_Liters", "Fiber_Grams", "Mood", "Energy_Level", "Created_At"
                        ))
                        
                        // Write data
                        healthLogs.collect { logs ->
                            logs.forEach { log ->
                                csvWriter.writeNext(arrayOf(
                                    log.date,
                                    log.time,
                                    log.meal,
                                    log.items,
                                    log.risk,
                                    log.onsetMinutes.toString(),
                                    log.severity.toString(),
                                    log.bristolType.toString(),
                                    log.recipe,
                                    log.symptoms,
                                    log.notes,
                                    log.hydrationLiters.toString(),
                                    log.fiberGrams.toString(),
                                    log.mood,
                                    log.energyLevel.toString(),
                                    log.createdAt.toString()
                                ))
                            }
                        }
                    }
                }
                
                _exportStatus.value = ExportStatus(
                    isLoading = false,
                    message = "Health logs exported successfully",
                    isSuccess = true
                )
                loadExportedFiles()
                
            } catch (e: Exception) {
                _exportStatus.value = ExportStatus(
                    isLoading = false,
                    message = "Failed to export health logs: ${e.message}",
                    isSuccess = false
                )
            }
        }
    }
    
    fun exportBarcodeScans() {
        viewModelScope.launch {
            _exportStatus.value = ExportStatus(isLoading = true, message = "Exporting barcode scans...")
            
            try {
                val scans = barcodeScanDao.getAllScans()
                val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
                val fileName = "barcode_scans_$timestamp.csv"
                val file = createCsvFile(fileName)
                
                FileWriter(file).use { writer ->
                    CSVWriter(writer).use { csvWriter ->
                        // Write header
                        csvWriter.writeNext(arrayOf(
                            "Barcode", "Product_Name", "Brand", "Ingredients", 
                            "Safety_Status", "Confidence", "Warnings", "Scan_Date"
                        ))
                        
                        // Write data
                        scans.collect { scanList ->
                            scanList.forEach { scan ->
                                csvWriter.writeNext(arrayOf(
                                    scan.barcode,
                                    scan.productName,
                                    scan.brand,
                                    scan.ingredients,
                                    scan.safetyStatus,
                                    scan.confidence.toString(),
                                    scan.warnings,
                                    scan.scanDate.toString()
                                ))
                            }
                        }
                    }
                }
                
                _exportStatus.value = ExportStatus(
                    isLoading = false,
                    message = "Barcode scans exported successfully",
                    isSuccess = true
                )
                loadExportedFiles()
                
            } catch (e: Exception) {
                _exportStatus.value = ExportStatus(
                    isLoading = false,
                    message = "Failed to export barcode scans: ${e.message}",
                    isSuccess = false
                )
            }
        }
    }
    
    fun exportAllData() {
        viewModelScope.launch {
            _exportStatus.value = ExportStatus(isLoading = true, message = "Exporting all data...")
            
            try {
                val healthLogs = healthLogDao.getAllHealthLogs()
                val scans = barcodeScanDao.getAllScans()
                val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
                val fileName = "all_data_$timestamp.csv"
                val file = createCsvFile(fileName)
                
                FileWriter(file).use { writer ->
                    CSVWriter(writer).use { csvWriter ->
                        // Write combined header
                        csvWriter.writeNext(arrayOf(
                            "Type", "Date", "Time", "Meal", "Items", "Risk", "Onset_Minutes",
                            "Severity", "Bristol_Type", "Recipe", "Symptoms", "Notes",
                            "Hydration_Liters", "Fiber_Grams", "Mood", "Energy_Level",
                            "Barcode", "Product_Name", "Brand", "Ingredients", "Safety_Status",
                            "Confidence", "Warnings", "Created_At"
                        ))
                        
                        // Write health logs
                        healthLogs.collect { logs ->
                            logs.forEach { log ->
                                csvWriter.writeNext(arrayOf(
                                    "HEALTH_LOG",
                                    log.date,
                                    log.time,
                                    log.meal,
                                    log.items,
                                    log.risk,
                                    log.onsetMinutes.toString(),
                                    log.severity.toString(),
                                    log.bristolType.toString(),
                                    log.recipe,
                                    log.symptoms,
                                    log.notes,
                                    log.hydrationLiters.toString(),
                                    log.fiberGrams.toString(),
                                    log.mood,
                                    log.energyLevel.toString(),
                                    "", "", "", "", "", "", "", log.createdAt.toString()
                                ))
                            }
                        }
                        
                        // Write scans
                        scans.collect { scanList ->
                            scanList.forEach { scan ->
                                csvWriter.writeNext(arrayOf(
                                    "BARCODE_SCAN",
                                    "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                                    scan.barcode,
                                    scan.productName,
                                    scan.brand,
                                    scan.ingredients,
                                    scan.safetyStatus,
                                    scan.confidence.toString(),
                                    scan.warnings,
                                    scan.scanDate.toString()
                                ))
                            }
                        }
                    }
                }
                
                _exportStatus.value = ExportStatus(
                    isLoading = false,
                    message = "All data exported successfully",
                    isSuccess = true
                )
                loadExportedFiles()
                
            } catch (e: Exception) {
                _exportStatus.value = ExportStatus(
                    isLoading = false,
                    message = "Failed to export data: ${e.message}",
                    isSuccess = false
                )
            }
        }
    }
    
    fun deleteExportedFile(file: File) {
        viewModelScope.launch {
            try {
                if (file.exists()) {
                    file.delete()
                    loadExportedFiles()
                }
            } catch (e: Exception) {
                _exportStatus.value = ExportStatus(
                    isLoading = false,
                    message = "Failed to delete file: ${e.message}",
                    isSuccess = false
                )
            }
        }
    }
    
    private fun createCsvFile(fileName: String): File {
        val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        return File(downloadsDir, fileName)
    }
    
    private fun loadExportedFiles() {
        viewModelScope.launch {
            try {
                val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                val csvFiles = downloadsDir.listFiles { file ->
                    file.isFile && file.name.endsWith(".csv") && (
                        file.name.startsWith("health_logs_") ||
                        file.name.startsWith("barcode_scans_") ||
                        file.name.startsWith("all_data_")
                    )
                }?.toList() ?: emptyList()
                
                _exportedFiles.value = csvFiles.sortedByDescending { it.lastModified() }
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
    
    data class ExportStatus(
        val isLoading: Boolean = false,
        val message: String = "",
        val isSuccess: Boolean = false
    )
}
