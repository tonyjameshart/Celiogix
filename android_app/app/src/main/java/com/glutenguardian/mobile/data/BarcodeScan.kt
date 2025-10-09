package com.glutenguardian.mobile.data

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "barcode_scans")
data class BarcodeScan(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val barcode: String,
    val productName: String,
    val brand: String,
    val ingredients: String,
    val safetyStatus: String, // SAFE, UNSAFE, POSSIBLY_UNSAFE, UNKNOWN
    val confidence: Double,
    val warnings: String,
    val scanDate: Date = Date()
)
