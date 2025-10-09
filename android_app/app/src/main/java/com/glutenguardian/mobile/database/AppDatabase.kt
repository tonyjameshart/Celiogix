package com.glutenguardian.mobile.database

import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import android.content.Context
import com.glutenguardian.mobile.data.BarcodeScan
import com.glutenguardian.mobile.data.HealthLog
import com.glutenguardian.mobile.dao.BarcodeScanDao
import com.glutenguardian.mobile.dao.HealthLogDao

@Database(
    entities = [BarcodeScan::class, HealthLog::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun barcodeScanDao(): BarcodeScanDao
    abstract fun healthLogDao(): HealthLogDao
    
    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null
        
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "gluten_guardian_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
