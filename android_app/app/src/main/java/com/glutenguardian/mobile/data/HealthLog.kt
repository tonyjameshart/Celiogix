package com.glutenguardian.mobile.data

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "health_logs")
data class HealthLog(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val date: String, // ISO date string
    val time: String, // HH:MM format
    val meal: String, // Breakfast, Lunch, Dinner, Snack, Other
    val items: String, // Items consumed
    val risk: String, // none, low, med, high
    val onsetMinutes: Int, // Minutes from consumption to symptoms
    val severity: Int, // 0-10 scale
    val bristolType: Int, // 1-7 Bristol Stool Scale
    val recipe: String,
    val symptoms: String, // Comma-separated symptoms
    val notes: String,
    val hydrationLiters: Double, // Daily hydration in liters
    val fiberGrams: Double, // Daily fiber in grams
    val mood: String, // Emoji mood
    val energyLevel: Int, // 1-10 scale
    val createdAt: Date = Date()
)
