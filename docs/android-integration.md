# Android Integration Guide

This guide shows how to integrate the Home Assistant Supervisor API Proxy into your Android application.

## Quick Start

### 1. Add Dependencies

Add these dependencies to your `app/build.gradle` file:

```gradle
dependencies {
    // Retrofit for API calls
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    
    // OkHttp for HTTP client
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.12.0'
    
    // Coroutines for async operations
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
    
    // Android Architecture Components
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'
    implementation 'androidx.lifecycle:lifecycle-livedata-ktx:2.7.0'
}
```

### 2. Copy Client Files

Copy these files to your project:
- `SupervisorApiClient.kt` → `app/src/main/java/your/package/`
- Update the package name to match your project

### 3. Initialize the Client

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var apiService: SupervisorApiService
    private lateinit var repository: SupervisorApiRepository
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize API client
        apiService = SupervisorApiClient.create(
            baseUrl = "http://192.168.1.100:8099", // Your HA IP
            authToken = "your_supervisor_token"     // Your token
        )
        
        repository = SupervisorApiRepository(apiService)
    }
}
```

### 4. Make API Calls

```kotlin
// Using Repository (Recommended)
lifecycleScope.launch {
    when (val result = repository.getAddons()) {
        is ApiResult.Success -> {
            val addons = result.data
            // Update UI with addons
        }
        is ApiResult.Error -> {
            // Handle error
            Log.e("API", result.message)
        }
        is ApiResult.Loading -> {
            // Show loading indicator
        }
    }
}

// Direct API calls
lifecycleScope.launch {
    try {
        val response = apiService.getAddons()
        if (response.isSuccessful) {
            val addons = response.body()?.data
            // Use addons
        }
    } catch (e: Exception) {
        Log.e("API", "Error", e)
    }
}
```

## Configuration Options

### Basic Configuration

```kotlin
val apiService = SupervisorApiClient.create(
    baseUrl = "http://192.168.1.100:8099",
    authToken = "your_token_here"
)
```

### Advanced Configuration

```kotlin
val apiService = SupervisorApiClient.create(
    baseUrl = "https://192.168.1.100:8099",
    authToken = "your_token_here",
    timeout = 60L,                    // 60 seconds timeout
    enableLogging = BuildConfig.DEBUG, // Logging in debug mode only
    allowInsecureSSL = false          // Allow self-signed certificates
)
```

### Configuration Helper

```kotlin
// For HTTP connections
val config = SupervisorConfig.create(
    homeAssistantIp = "192.168.1.100",
    port = 8099,
    authToken = "your_token"
)

// For HTTPS connections
val secureConfig = SupervisorConfig.createSecure(
    homeAssistantIp = "192.168.1.100",
    port = 8099,
    authToken = "your_token"
)

val apiService = SupervisorApiClient.create(
    baseUrl = config.baseUrl,
    authToken = config.authToken,
    timeout = config.timeout,
    enableLogging = config.enableLogging,
    allowInsecureSSL = config.allowInsecureSSL
)
```

## Using with ViewModel

### Create ViewModel

```kotlin
class HomeAssistantViewModel(
    private val repository: SupervisorApiRepository
) : ViewModel() {
    
    private val _addons = MutableLiveData<ApiResult<List<AddonInfo>>>()
    val addons: LiveData<ApiResult<List<AddonInfo>>> = _addons
    
    private val _health = MutableLiveData<ApiResult<HealthResponse>>()
    val health: LiveData<ApiResult<HealthResponse>> = _health
    
    fun loadAddons() {
        _addons.value = ApiResult.Loading()
        viewModelScope.launch {
            _addons.value = repository.getAddons()
        }
    }
    
    fun checkHealth() {
        _health.value = ApiResult.Loading()
        viewModelScope.launch {
            _health.value = repository.getHealth()
        }
    }
    
    fun startAddon(slug: String) {
        viewModelScope.launch {
            when (repository.startAddon(slug)) {
                is ApiResult.Success -> loadAddons() // Refresh
                is ApiResult.Error -> { /* Handle error */ }
                else -> {}
            }
        }
    }
}
```

### Use in Activity/Fragment

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var viewModel: HomeAssistantViewModel
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Setup ViewModel
        val apiService = SupervisorApiClient.create(/* config */)
        val repository = SupervisorApiRepository(apiService)
        viewModel = ViewModelProvider(this) { 
            object : ViewModelProvider.Factory {
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    @Suppress("UNCHECKED_CAST")
                    return HomeAssistantViewModel(repository) as T
                }
            }
        }[HomeAssistantViewModel::class.java]
        
        // Observe data
        observeViewModel()
        
        // Load initial data
        viewModel.loadAddons()
        viewModel.checkHealth()
    }
    
    private fun observeViewModel() {
        viewModel.addons.observe(this) { result ->
            when (result) {
                is ApiResult.Loading -> showLoading()
                is ApiResult.Success -> {
                    hideLoading()
                    updateUI(result.data)
                }
                is ApiResult.Error -> {
                    hideLoading()
                    showError(result.message)
                }
            }
        }
    }
}
```

## Available API Methods

### Health & Discovery

```kotlin
// Health check
val health: ApiResult<HealthResponse> = repository.getHealth()

// API discovery
val discovery: ApiResult<ApiDiscoveryResponse> = repository.getApiDiscovery()
```

### Add-on Management

```kotlin
// List all add-ons
val addons: ApiResult<List<AddonInfo>> = repository.getAddons()

// Get specific add-on
val addon: ApiResult<AddonInfo> = repository.getAddon("addon-slug")

// Install add-on
val result: ApiResult<ApiResponse> = repository.installAddon("addon-slug")

// Start/Stop add-on
val startResult: ApiResult<ApiResponse> = repository.startAddon("addon-slug")
val stopResult: ApiResult<ApiResponse> = repository.stopAddon("addon-slug")

// Get add-on stats
val response = apiService.getAddonStats("addon-slug")
if (response.isSuccessful) {
    val stats = response.body()?.data
    Log.d("Stats", "CPU: ${stats?.cpuPercent}%")
}
```

### Backup Management

```kotlin
// List backups
val backups: ApiResult<List<BackupInfo>> = repository.getBackups()

// Create backup
val request = CreateBackupRequest(
    name = "My Backup",
    addons = listOf("addon1", "addon2"), // null for all
    folders = listOf("config", "ssl"),   // null for all
    password = "backup_password"         // optional
)
val result: ApiResult<ApiResponse> = repository.createBackup(request)

// Restore backup
val restoreRequest = RestoreBackupRequest(
    addons = listOf("addon1"),
    folders = listOf("config"),
    homeassistant = true,
    password = "backup_password"
)
val restoreResult = apiService.restoreFullBackup("backup-slug", restoreRequest)
```

### System Information

```kotlin
// Get system info
val supervisor: ApiResult<SupervisorInfo> = repository.getSupervisorInfo()
val core: ApiResult<CoreInfo> = repository.getCoreInfo()

// System operations
val updateResult = apiService.updateSupervisor()
val restartResult = apiService.restartCore()
```

## Error Handling

### Using ApiResult

```kotlin
when (val result = repository.getAddons()) {
    is ApiResult.Loading -> {
        // Show loading indicator
        progressBar.visibility = View.VISIBLE
    }
    is ApiResult.Success -> {
        // Handle success
        progressBar.visibility = View.GONE
        val addons = result.data
        updateAddonsList(addons)
    }
    is ApiResult.Error -> {
        // Handle error
        progressBar.visibility = View.GONE
        val message = result.message
        val code = result.code // HTTP status code (optional)
        
        // Show error to user
        Snackbar.make(rootView, "Error: $message", Snackbar.LENGTH_LONG).show()
        
        // Log error
        Log.e("API", "Error $code: $message")
    }
}
```

### Direct Response Handling

```kotlin
lifecycleScope.launch {
    try {
        val response = apiService.getAddons()
        if (response.isSuccessful) {
            val addons = response.body()?.data
            // Handle success
        } else {
            val errorCode = response.code()
            val errorBody = response.errorBody()?.string()
            // Handle HTTP error
            Log.e("API", "HTTP $errorCode: $errorBody")
        }
    } catch (e: Exception) {
        // Handle network/other errors
        Log.e("API", "Network error", e)
        when (e) {
            is java.net.SocketTimeoutException -> {
                // Handle timeout
            }
            is java.net.ConnectException -> {
                // Handle connection error
            }
            else -> {
                // Handle other errors
            }
        }
    }
}
```

## RecyclerView Integration

### Add-ons List Adapter

```kotlin
class AddonsAdapter(
    private val onAddonClick: (AddonInfo) -> Unit,
    private val onStartClick: (String) -> Unit,
    private val onStopClick: (String) -> Unit
) : RecyclerView.Adapter<AddonsAdapter.ViewHolder>() {
    
    private val addons = mutableListOf<AddonInfo>()
    
    class ViewHolder(private val binding: ItemAddonBinding) : 
        RecyclerView.ViewHolder(binding.root) {
        
        fun bind(addon: AddonInfo, 
                onAddonClick: (AddonInfo) -> Unit,
                onStartClick: (String) -> Unit,
                onStopClick: (String) -> Unit) {
            
            binding.addonName.text = addon.name
            binding.addonState.text = addon.state
            binding.addonVersion.text = addon.version
            
            // State-based UI
            when (addon.state) {
                "started" -> {
                    binding.stateIndicator.setColorFilter(Color.GREEN)
                    binding.startButton.visibility = View.GONE
                    binding.stopButton.visibility = View.VISIBLE
                }
                "stopped" -> {
                    binding.stateIndicator.setColorFilter(Color.RED)
                    binding.startButton.visibility = View.VISIBLE
                    binding.stopButton.visibility = View.GONE
                }
                else -> {
                    binding.stateIndicator.setColorFilter(Color.GRAY)
                    binding.startButton.visibility = View.GONE
                    binding.stopButton.visibility = View.GONE
                }
            }
            
            // Click listeners
            binding.root.setOnClickListener { onAddonClick(addon) }
            binding.startButton.setOnClickListener { onStartClick(addon.slug) }
            binding.stopButton.setOnClickListener { onStopClick(addon.slug) }
        }
    }
    
    fun updateAddons(newAddons: List<AddonInfo>) {
        addons.clear()
        addons.addAll(newAddons)
        notifyDataSetChanged()
    }
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemAddonBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(addons[position], onAddonClick, onStartClick, onStopClick)
    }
    
    override fun getItemCount() = addons.size
}
```

### Usage in Activity

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var addonsAdapter: AddonsAdapter
    
    private fun setupRecyclerView() {
        addonsAdapter = AddonsAdapter(
            onAddonClick = { addon ->
                // Show addon details
                showAddonDetails(addon)
            },
            onStartClick = { slug ->
                viewModel.startAddon(slug)
            },
            onStopClick = { slug ->
                viewModel.stopAddon(slug)
            }
        )
        
        binding.recyclerView.apply {
            adapter = addonsAdapter
            layoutManager = LinearLayoutManager(this@MainActivity)
        }
    }
    
    private fun observeAddons() {
        viewModel.addons.observe(this) { result ->
            when (result) {
                is ApiResult.Success -> {
                    addonsAdapter.updateAddons(result.data)
                }
                // Handle other states
            }
        }
    }
}
```

## Best Practices

### 1. Network Security

```kotlin
// Use HTTPS in production
val apiService = SupervisorApiClient.create(
    baseUrl = "https://your-domain.com:8099",
    authToken = authToken,
    allowInsecureSSL = false // Never true in production
)

// Certificate pinning for extra security
val certificatePinner = CertificatePinner.Builder()
    .add("your-domain.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

### 2. Token Management

```kotlin
class TokenManager(private val context: Context) {
    private val prefs = context.getSharedPreferences("ha_prefs", Context.MODE_PRIVATE)
    
    var authToken: String?
        get() = prefs.getString("auth_token", null)
        set(value) = prefs.edit().putString("auth_token", value).apply()
    
    fun clearToken() {
        prefs.edit().remove("auth_token").apply()
    }
}
```

### 3. Connection Testing

```kotlin
class ConnectionTester(private val repository: SupervisorApiRepository) {
    
    suspend fun testConnection(): Boolean {
        return try {
            when (val result = repository.getHealth()) {
                is ApiResult.Success -> result.data.supervisorConnection
                else -> false
            }
        } catch (e: Exception) {
            false
        }
    }
}
```

### 4. Background Processing

```kotlin
class BackgroundSyncService : Service() {
    
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    fun syncData() {
        scope.launch {
            try {
                // Sync add-ons
                repository.getAddons().let { result ->
                    if (result is ApiResult.Success) {
                        // Cache data locally
                        cacheAddons(result.data)
                    }
                }
                
                // Sync other data...
                
            } catch (e: Exception) {
                Log.e("BackgroundSync", "Sync failed", e)
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()
    }
}
```

### 5. Offline Support

```kotlin
class OfflineRepository(
    private val apiRepository: SupervisorApiRepository,
    private val localDatabase: LocalDatabase
) {
    
    suspend fun getAddons(): ApiResult<List<AddonInfo>> {
        return try {
            // Try API first
            val apiResult = apiRepository.getAddons()
            if (apiResult is ApiResult.Success) {
                // Cache successful result
                localDatabase.cacheAddons(apiResult.data)
                apiResult
            } else {
                // Fallback to cache
                val cached = localDatabase.getCachedAddons()
                if (cached.isNotEmpty()) {
                    ApiResult.Success(cached)
                } else {
                    apiResult // Return original error
                }
            }
        } catch (e: Exception) {
            // Network error, try cache
            val cached = localDatabase.getCachedAddons()
            if (cached.isNotEmpty()) {
                ApiResult.Success(cached)
            } else {
                ApiResult.Error("No network connection and no cached data")
            }
        }
    }
}
```

## Troubleshooting

### Common Issues

**1. Connection Refused**
```kotlin
// Check if the proxy is running
lifecycleScope.launch {
    val result = repository.getHealth()
    if (result is ApiResult.Error) {
        // Proxy is not accessible
        showError("Cannot connect to Home Assistant. Check IP and port.")
    }
}
```

**2. Authentication Failed**
```kotlin
// Verify token
if (authToken.isNullOrBlank()) {
    showError("No authentication token configured")
    return
}

// Test with a simple call
val healthResult = repository.getHealth()
if (healthResult is ApiResult.Error && healthResult.code == 401) {
    showError("Invalid authentication token")
}
```

**3. SSL Certificate Issues**
```kotlin
// For development with self-signed certificates
val apiService = SupervisorApiClient.create(
    baseUrl = "https://192.168.1.100:8099",
    authToken = authToken,
    allowInsecureSSL = true // Only for development!
)
```

**4. Timeout Issues**
```kotlin
// Increase timeout for slow networks
val apiService = SupervisorApiClient.create(
    baseUrl = baseUrl,
    authToken = authToken,
    timeout = 60L // 60 seconds
)
```

### Logging and Debugging

```kotlin
// Enable detailed logging
val apiService = SupervisorApiClient.create(
    baseUrl = baseUrl,
    authToken = authToken,
    enableLogging = true
)

// Check logs for HTTP requests/responses
// Look for "SupervisorAPI" tag in logcat

// Manual logging in your code
Log.d("HomeAssistant", "Starting addon: $slug")
Log.e("HomeAssistant", "API error: ${result.message}")
```

## Sample App

A complete sample application demonstrating all features is available in the `android-client/` directory. It includes:

- Complete UI with RecyclerView
- Error handling and loading states  
- Background sync
- Settings screen for configuration
- Material Design components
- Offline support

To run the sample:

1. Import the project into Android Studio
2. Update the configuration in `MainActivity.kt`
3. Add your Home Assistant IP and token
4. Build and run on device or emulator