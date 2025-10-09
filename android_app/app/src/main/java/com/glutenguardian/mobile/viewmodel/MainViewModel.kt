package com.glutenguardian.mobile.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.glutenguardian.mobile.data.BarcodeScan
import com.glutenguardian.mobile.data.HealthLog
import com.glutenguardian.mobile.database.AppDatabase
import com.glutenguardian.mobile.dao.BarcodeScanDao
import com.glutenguardian.mobile.dao.HealthLogDao
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {
    
    private val database = AppDatabase.getDatabase(application)
    private val barcodeScanDao: BarcodeScanDao = database.barcodeScanDao()
    private val healthLogDao: HealthLogDao = database.healthLogDao()
    
    private val _recentScans = MutableStateFlow<List<BarcodeScan>>(emptyList())
    val recentScans: StateFlow<List<BarcodeScan>> = _recentScans.asStateFlow()
    
    private val _recentHealthLogs = MutableStateFlow<List<HealthLog>>(emptyList())
    val recentHealthLogs: StateFlow<List<HealthLog>> = _recentHealthLogs.asStateFlow()
    
    init {
        loadRecentData()
    }
    
    private fun loadRecentData() {
        viewModelScope.launch {
            try {
                val scans = barcodeScanDao.getRecentScans(10)
                val logs = healthLogDao.getRecentHealthLogs(10)
                
                _recentScans.value = scans
                _recentHealthLogs.value = logs
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
    
    fun refreshData() {
        loadRecentData()
    }
}
