package com.glutenguardian.mobile.dao

import androidx.room.*
import com.glutenguardian.mobile.data.BarcodeScan
import kotlinx.coroutines.flow.Flow

@Dao
interface BarcodeScanDao {
    @Query("SELECT * FROM barcode_scans ORDER BY scanDate DESC")
    fun getAllScans(): Flow<List<BarcodeScan>>
    
    @Query("SELECT * FROM barcode_scans ORDER BY scanDate DESC LIMIT :limit")
    suspend fun getRecentScans(limit: Int): List<BarcodeScan>
    
    @Query("SELECT * FROM barcode_scans WHERE barcode = :barcode")
    suspend fun getScanByBarcode(barcode: String): BarcodeScan?
    
    @Query("SELECT * FROM barcode_scans WHERE productName LIKE '%' || :query || '%' OR brand LIKE '%' || :query || '%' OR ingredients LIKE '%' || :query || '%' ORDER BY scanDate DESC")
    suspend fun searchScans(query: String): List<BarcodeScan>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertScan(scan: BarcodeScan): Long
    
    @Update
    suspend fun updateScan(scan: BarcodeScan)
    
    @Delete
    suspend fun deleteScan(scan: BarcodeScan)
    
    @Query("DELETE FROM barcode_scans")
    suspend fun deleteAllScans()
}
