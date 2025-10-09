package com.glutenguardian.mobile.dao

import androidx.room.*
import com.glutenguardian.mobile.data.HealthLog
import kotlinx.coroutines.flow.Flow

@Dao
interface HealthLogDao {
    @Query("SELECT * FROM health_logs ORDER BY createdAt DESC")
    fun getAllHealthLogs(): Flow<List<HealthLog>>
    
    @Query("SELECT * FROM health_logs ORDER BY createdAt DESC LIMIT :limit")
    suspend fun getRecentHealthLogs(limit: Int): List<HealthLog>
    
    @Query("SELECT * FROM health_logs WHERE date >= :fromDate ORDER BY date DESC, time DESC")
    suspend fun getHealthLogsFromDate(fromDate: String): List<HealthLog>
    
    @Query("SELECT * FROM health_logs WHERE date BETWEEN :startDate AND :endDate ORDER BY date DESC, time DESC")
    suspend fun getHealthLogsBetweenDates(startDate: String, endDate: String): List<HealthLog>
    
    @Query("SELECT * FROM health_logs WHERE symptoms LIKE '%' || :symptom || '%' ORDER BY createdAt DESC")
    suspend fun getHealthLogsBySymptom(symptom: String): List<HealthLog>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertHealthLog(healthLog: HealthLog): Long
    
    @Update
    suspend fun updateHealthLog(healthLog: HealthLog)
    
    @Delete
    suspend fun deleteHealthLog(healthLog: HealthLog)
    
    @Query("DELETE FROM health_logs")
    suspend fun deleteAllHealthLogs()
    
    @Query("SELECT DISTINCT date FROM health_logs ORDER BY date DESC")
    suspend fun getAllDates(): List<String>
}
