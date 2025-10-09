package com.glutenguardian.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.glutenguardian.mobile.ui.theme.GlutenGuardianTheme
import com.glutenguardian.mobile.viewmodel.HealthLogViewModel
import java.text.SimpleDateFormat
import java.util.*

class HealthLogActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            GlutenGuardianTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    HealthLogScreen()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HealthLogScreen(
    viewModel: HealthLogViewModel = viewModel()
) {
    val context = LocalContext.current
    val isSaving by viewModel.isSaving.collectAsState()
    
    // Form state
    var date by remember { mutableStateOf(SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date())) }
    var time by remember { mutableStateOf(SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date())) }
    var meal by remember { mutableStateOf("Dinner") }
    var items by remember { mutableStateOf("") }
    var risk by remember { mutableStateOf("none") }
    var onsetMinutes by remember { mutableStateOf(0) }
    var severity by remember { mutableStateOf(0) }
    var bristolType by remember { mutableStateOf(4) }
    var recipe by remember { mutableStateOf("") }
    var symptoms by remember { mutableStateOf("") }
    var notes by remember { mutableStateOf("") }
    var hydrationLiters by remember { mutableStateOf(0.0) }
    var fiberGrams by remember { mutableStateOf(0.0) }
    var mood by remember { mutableStateOf("😊") }
    var energyLevel by remember { mutableStateOf(5) }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { (context as ComponentActivity).finish() }) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Back")
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "Health Log Entry",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Form content
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Card {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "Basic Information",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        // Date and Time
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            OutlinedTextField(
                                value = date,
                                onValueChange = { date = it },
                                label = { Text("Date (YYYY-MM-DD)") },
                                modifier = Modifier.weight(1f)
                            )
                            
                            OutlinedTextField(
                                value = time,
                                onValueChange = { time = it },
                                label = { Text("Time (HH:MM)") },
                                modifier = Modifier.weight(1f)
                            )
                        }
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        // Meal type
                        Text(
                            text = "Meal Type",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        val mealOptions = listOf("Breakfast", "Lunch", "Dinner", "Snack", "Other")
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            mealOptions.forEach { option ->
                                FilterChip(
                                    onClick = { meal = option },
                                    label = { Text(option) },
                                    selected = meal == option
                                )
                            }
                        }
                    }
                }
            }
            
            item {
                Card {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "Food & Symptoms",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        OutlinedTextField(
                            value = items,
                            onValueChange = { items = it },
                            label = { Text("Items Consumed") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        OutlinedTextField(
                            value = recipe,
                            onValueChange = { recipe = it },
                            label = { Text("Recipe (optional)") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        // Risk level
                        Text(
                            text = "Risk Level",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        val riskOptions = listOf("none", "low", "med", "high")
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            riskOptions.forEach { option ->
                                FilterChip(
                                    onClick = { risk = option },
                                    label = { Text(option) },
                                    selected = risk == option
                                )
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        // Onset and Severity
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            OutlinedTextField(
                                value = onsetMinutes.toString(),
                                onValueChange = { 
                                    onsetMinutes = it.toIntOrNull() ?: 0 
                                },
                                label = { Text("Onset (min)") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                modifier = Modifier.weight(1f)
                            )
                            
                            OutlinedTextField(
                                value = severity.toString(),
                                onValueChange = { 
                                    severity = it.toIntOrNull()?.coerceIn(0, 10) ?: 0 
                                },
                                label = { Text("Severity (0-10)") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                modifier = Modifier.weight(1f)
                            )
                        }
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        OutlinedTextField(
                            value = symptoms,
                            onValueChange = { symptoms = it },
                            label = { Text("Symptoms (comma-separated)") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        OutlinedTextField(
                            value = notes,
                            onValueChange = { notes = it },
                            label = { Text("Notes") },
                            modifier = Modifier.fillMaxWidth(),
                            minLines = 2
                        )
                    }
                }
            }
            
            item {
                Card {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "Bristol Stool Scale",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        val bristolOptions = listOf(
                            1 to "1 - Separate hard lumps (constipation)",
                            2 to "2 - Lumpy sausage",
                            3 to "3 - Cracked sausage",
                            4 to "4 - Smooth sausage (normal)",
                            5 to "5 - Soft blobs",
                            6 to "6 - Fluffy pieces",
                            7 to "7 - Watery (diarrhea)"
                        )
                        
                        bristolOptions.forEach { (type, description) ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .selectable(
                                        selected = bristolType == type,
                                        onClick = { bristolType = type }
                                    )
                                    .padding(vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                RadioButton(
                                    selected = bristolType == type,
                                    onClick = { bristolType = type }
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = description,
                                    style = MaterialTheme.typography.bodyMedium
                                )
                            }
                        }
                    }
                }
            }
            
            item {
                Card {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "Gluten Guardian Tracking",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        // Hydration and Fiber
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            OutlinedTextField(
                                value = hydrationLiters.toString(),
                                onValueChange = { 
                                    hydrationLiters = it.toDoubleOrNull() ?: 0.0 
                                },
                                label = { Text("Hydration (L)") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                modifier = Modifier.weight(1f)
                            )
                            
                            OutlinedTextField(
                                value = fiberGrams.toString(),
                                onValueChange = { 
                                    fiberGrams = it.toDoubleOrNull() ?: 0.0 
                                },
                                label = { Text("Fiber (g)") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                modifier = Modifier.weight(1f)
                            )
                        }
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        // Mood
                        Text(
                            text = "Mood",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        val moodOptions = listOf("😊", "😐", "😣", "😢", "😡")
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            moodOptions.forEach { option ->
                                FilterChip(
                                    onClick = { mood = option },
                                    label = { Text(option) },
                                    selected = mood == option
                                )
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        // Energy Level
                        Text(
                            text = "Energy Level (1-10)",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Slider(
                            value = energyLevel.toFloat(),
                            onValueChange = { energyLevel = it.toInt() },
                            valueRange = 1f..10f,
                            steps = 8,
                            modifier = Modifier.fillMaxWidth()
                        )
                        
                        Text(
                            text = "Energy Level: $energyLevel/10",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            item {
                // Save button
                Button(
                    onClick = {
                        val healthLog = com.glutenguardian.mobile.data.HealthLog(
                            date = date,
                            time = time,
                            meal = meal,
                            items = items,
                            risk = risk,
                            onsetMinutes = onsetMinutes,
                            severity = severity,
                            bristolType = bristolType,
                            recipe = recipe,
                            symptoms = symptoms,
                            notes = notes,
                            hydrationLiters = hydrationLiters,
                            fiberGrams = fiberGrams,
                            mood = mood,
                            energyLevel = energyLevel
                        )
                        viewModel.saveHealthLog(healthLog)
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isSaving
                ) {
                    if (isSaving) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(16.dp),
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                    }
                    Text(if (isSaving) "Saving..." else "Save Health Log")
                }
                
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}
