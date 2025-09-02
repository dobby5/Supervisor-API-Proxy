/**
 * Example usage of the Home Assistant Supervisor API Client in an Android Activity
 * This demonstrates how to integrate the API client into your Android application
 */

package com.homeassistant.supervisor.example

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.homeassistant.supervisor.client.*
import kotlinx.coroutines.*
import androidx.lifecycle.lifecycleScope

/**
 * Example Activity showing how to use the Supervisor API Client
 */
class MainActivity : AppCompatActivity() {
    
    private lateinit var apiService: SupervisorApiService
    private lateinit var repository: SupervisorApiRepository
    private lateinit var viewModel: SupervisorViewModel
    
    // Example configuration
    private val baseUrl = "http://192.168.1.100:8099" // Replace with your Home Assistant IP
    private val authToken = "your_supervisor_token_here" // Replace with your actual token
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        setupApiClient()
        setupViewModel()
        observeData()
        
        // Initial data load
        viewModel.checkHealth()
        viewModel.loadAddons()
        viewModel.loadBackups()
    }
    
    private fun setupApiClient() {
        // Create API client with configuration
        apiService = SupervisorApiClient.create(
            baseUrl = baseUrl,
            authToken = authToken,
            timeout = 30L,
            enableLogging = BuildConfig.DEBUG, // Enable logging in debug mode
            allowInsecureSSL = false // Set to true only for development with self-signed certs
        )
        
        // Create repository
        repository = SupervisorApiRepository(apiService)
        
        // Create ViewModel
        viewModel = ViewModelProvider(this, object : ViewModelProvider.Factory {
            override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T {
                @Suppress("UNCHECKED_CAST")
                return SupervisorViewModel(repository) as T
            }
        })[SupervisorViewModel::class.java]
    }
    
    private fun setupViewModel() {
        // ViewModel is already created in setupApiClient()
    }
    
    private fun observeData() {
        // Observe health status
        viewModel.health.observe(this) { result ->
            when (result) {
                is ApiResult.Loading -> {
                    showLoading("Checking health...")
                }
                is ApiResult.Success -> {
                    hideLoading()
                    val health = result.data
                    showToast("Health: ${health.status}")
                    Log.i("Health", "Supervisor connection: ${health.supervisorConnection}")
                }
                is ApiResult.Error -> {
                    hideLoading()
                    showToast("Health check failed: ${result.message}")
                    Log.e("Health", "Error: ${result.message}")
                }
            }
        }
        
        // Observe add-ons list
        viewModel.addons.observe(this) { result ->
            when (result) {
                is ApiResult.Loading -> {
                    showLoading("Loading add-ons...")
                }
                is ApiResult.Success -> {
                    hideLoading()
                    val addons = result.data
                    showToast("Loaded ${addons.size} add-ons")
                    updateAddonsList(addons)
                    Log.i("Addons", "Loaded ${addons.size} add-ons")
                }
                is ApiResult.Error -> {
                    hideLoading()
                    showToast("Failed to load add-ons: ${result.message}")
                    Log.e("Addons", "Error: ${result.message}")
                }
            }
        }
        
        // Observe backups list
        viewModel.backups.observe(this) { result ->
            when (result) {
                is ApiResult.Loading -> {
                    showLoading("Loading backups...")
                }
                is ApiResult.Success -> {
                    hideLoading()
                    val backups = result.data
                    showToast("Found ${backups.size} backups")
                    updateBackupsList(backups)
                    Log.i("Backups", "Loaded ${backups.size} backups")
                }
                is ApiResult.Error -> {
                    hideLoading()
                    showToast("Failed to load backups: ${result.message}")
                    Log.e("Backups", "Error: ${result.message}")
                }
            }
        }
    }
    
    private fun updateAddonsList(addons: List<AddonInfo>) {
        // Update your RecyclerView adapter here
        // Example implementation:
        addons.forEach { addon ->
            Log.d("Addon", "${addon.name}: ${addon.state} (${addon.version})")
        }
    }
    
    private fun updateBackupsList(backups: List<BackupInfo>) {
        // Update your RecyclerView adapter here
        // Example implementation:
        backups.forEach { backup ->
            Log.d("Backup", "${backup.name}: ${backup.date} (${backup.size} bytes)")
        }
    }
    
    // Example button click handlers
    fun onStartAddonClick(addonSlug: String) {
        lifecycleScope.launch {
            showLoading("Starting $addonSlug...")
            val result = repository.startAddon(addonSlug)
            hideLoading()
            
            when (result) {
                is ApiResult.Success -> {
                    showToast("Add-on $addonSlug started successfully")
                    viewModel.loadAddons() // Refresh the list
                }
                is ApiResult.Error -> {
                    showToast("Failed to start $addonSlug: ${result.message}")
                }
                else -> {}
            }
        }
    }
    
    fun onStopAddonClick(addonSlug: String) {
        lifecycleScope.launch {
            showLoading("Stopping $addonSlug...")
            val result = repository.stopAddon(addonSlug)
            hideLoading()
            
            when (result) {
                is ApiResult.Success -> {
                    showToast("Add-on $addonSlug stopped successfully")
                    viewModel.loadAddons() // Refresh the list
                }
                is ApiResult.Error -> {
                    showToast("Failed to stop $addonSlug: ${result.message}")
                }
                else -> {}
            }
        }
    }
    
    fun onCreateBackupClick() {
        val backupName = "Backup_${System.currentTimeMillis()}"
        lifecycleScope.launch {
            showLoading("Creating backup...")
            val request = CreateBackupRequest(
                name = backupName,
                addons = null, // null means include all add-ons
                folders = null, // null means include all folders
                password = null // optional password protection
            )
            val result = repository.createBackup(request)
            hideLoading()
            
            when (result) {
                is ApiResult.Success -> {
                    showToast("Backup created successfully")
                    viewModel.loadBackups() // Refresh the list
                }
                is ApiResult.Error -> {
                    showToast("Failed to create backup: ${result.message}")
                }
                else -> {}
            }
        }
    }
    
    fun onGetSystemInfoClick() {
        lifecycleScope.launch {
            showLoading("Loading system info...")
            
            val supervisorResult = repository.getSupervisorInfo()
            val coreResult = repository.getCoreInfo()
            
            hideLoading()
            
            when {
                supervisorResult is ApiResult.Success && coreResult is ApiResult.Success -> {
                    val supervisor = supervisorResult.data
                    val core = coreResult.data
                    
                    val info = """
                        Supervisor: ${supervisor.version}
                        Core: ${core.version}
                        Healthy: ${supervisor.healthy}
                        State: ${core.state}
                    """.trimIndent()
                    
                    showToast(info)
                    Log.i("SystemInfo", info)
                }
                supervisorResult is ApiResult.Error -> {
                    showToast("Failed to get supervisor info: ${supervisorResult.message}")
                }
                coreResult is ApiResult.Error -> {
                    showToast("Failed to get core info: ${coreResult.message}")
                }
            }
        }
    }
    
    // Direct API usage examples (without ViewModel)
    private fun directApiExamples() {
        lifecycleScope.launch {
            try {
                // Direct health check
                val healthResponse = apiService.getHealth()
                if (healthResponse.isSuccessful) {
                    val health = healthResponse.body()
                    Log.i("DirectAPI", "Health: ${health?.status}")
                }
                
                // Direct add-on list
                val addonsResponse = apiService.getAddons()
                if (addonsResponse.isSuccessful) {
                    val addons = addonsResponse.body()?.data
                    Log.i("DirectAPI", "Add-ons count: ${addons?.size}")
                }
                
                // Direct backup creation
                val backupRequest = CreateBackupRequest("MyBackup", null, null, null)
                val backupResponse = apiService.createBackup(backupRequest)
                if (backupResponse.isSuccessful) {
                    Log.i("DirectAPI", "Backup created: ${backupResponse.body()?.result}")
                }
                
            } catch (e: Exception) {
                Log.e("DirectAPI", "Error in direct API call", e)
            }
        }
    }
    
    // Utility methods
    private fun showLoading(message: String) {
        // Show your loading indicator here
        // Example: progressBar.visibility = View.VISIBLE
        Log.d("Loading", message)
    }
    
    private fun hideLoading() {
        // Hide your loading indicator here
        // Example: progressBar.visibility = View.GONE
    }
    
    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}

/**
 * RecyclerView Adapter example for Add-ons
 */
class AddonsAdapter(
    private val addons: MutableList<AddonInfo>,
    private val onStartClick: (String) -> Unit,
    private val onStopClick: (String) -> Unit
) : androidx.recyclerview.widget.RecyclerView.Adapter<AddonsAdapter.AddonViewHolder>() {
    
    class AddonViewHolder(view: View) : androidx.recyclerview.widget.RecyclerView.ViewHolder(view) {
        // Bind your views here using findViewById or view binding
    }
    
    override fun onCreateViewHolder(parent: android.view.ViewGroup, viewType: Int): AddonViewHolder {
        val view = android.view.LayoutInflater.from(parent.context)
            .inflate(R.layout.item_addon, parent, false)
        return AddonViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: AddonViewHolder, position: Int) {
        val addon = addons[position]
        // Bind addon data to views
        // Example:
        // holder.nameTextView.text = addon.name
        // holder.stateTextView.text = addon.state
        // holder.startButton.setOnClickListener { onStartClick(addon.slug) }
        // holder.stopButton.setOnClickListener { onStopClick(addon.slug) }
    }
    
    override fun getItemCount() = addons.size
    
    fun updateAddons(newAddons: List<AddonInfo>) {
        addons.clear()
        addons.addAll(newAddons)
        notifyDataSetChanged()
    }
}

/**
 * Configuration class for easy setup
 */
data class SupervisorConfig(
    val baseUrl: String,
    val authToken: String?,
    val timeout: Long = 30L,
    val enableLogging: Boolean = false,
    val allowInsecureSSL: Boolean = false
) {
    companion object {
        fun create(homeAssistantIp: String, port: Int = 8099, authToken: String?): SupervisorConfig {
            return SupervisorConfig(
                baseUrl = "http://$homeAssistantIp:$port",
                authToken = authToken
            )
        }
        
        fun createSecure(homeAssistantIp: String, port: Int = 8099, authToken: String?): SupervisorConfig {
            return SupervisorConfig(
                baseUrl = "https://$homeAssistantIp:$port",
                authToken = authToken
            )
        }
    }
}