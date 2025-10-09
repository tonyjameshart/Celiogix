package com.glutenguardian.mobile.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.glutenguardian.mobile.data.HealthLog
import com.glutenguardian.mobile.database.AppDatabase
import com.glutenguardian.mobile.dao.HealthLogDao
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class HealthLogViewModel(application: Application) : AndroidViewModel(application) {
    
    private val database = AppDatabase.getDatabase(application)
    private val healthLogDao: HealthLogDao = database.healthLogDao()
    
    private val _isSaving = MutableStateFlow(false)
    val isSaving: StateFlow<Boolean> = _isSaving.asStateFlow()
    
    private val _saveResult = MutableStateFlow<SaveResult?>(null)
    val saveResult: StateFlow<SaveResult?> = _saveResult.asStateFlow()
    
    fun saveHealthLog(healthLog: HealthLog) {
        viewModelScope.launch {
            _isSaving.value = true
            
            try {
                val id = healthLogDao.insertHealthLog(healthLog)
                _saveResult.value = SaveResult.Success("Health log saved successfully")
            } catch (e: Exception) {
                _saveResult.value = SaveResult.Error("Failed to save health log: ${e.message}")
            } finally {
                _isSaving.value = false
            }
        }
    }
    
    fun clearSaveResult() {
        _saveResult.value = null
    }
    
    sealed class SaveResult {
        data class Success(val message: String) : SaveResult()
        data class Error(val message: String) : SaveResult()
    }
}
