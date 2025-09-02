/**
 * Home Assistant Supervisor API Client for Android
 * 
 * This package provides a complete Retrofit-based client for communicating
 * with the Home Assistant Supervisor API Proxy from Android applications.
 */

package com.homeassistant.supervisor.client

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import retrofit2.Response
import retrofit2.http.*
import java.util.concurrent.TimeUnit
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import okhttp3.ResponseBody
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager
import java.security.cert.X509Certificate
import android.util.Log
import com.google.gson.annotations.SerializedName
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import kotlinx.coroutines.launch
import java.util.*

/**
 * Data classes for API responses
 */

// Health Check Response
data class HealthResponse(
    @SerializedName("status") val status: String,
    @SerializedName("timestamp") val timestamp: Long,
    @SerializedName("supervisor_connection") val supervisorConnection: Boolean,
    @SerializedName("version") val version: String
)

// API Discovery Response
data class ApiDiscoveryResponse(
    @SerializedName("message") val message: String,
    @SerializedName("version") val version: String,
    @SerializedName("endpoints") val endpoints: Map<String, Any>
)

// Add-on Data Classes
data class AddonInfo(
    @SerializedName("slug") val slug: String,
    @SerializedName("name") val name: String,
    @SerializedName("description") val description: String,
    @SerializedName("version") val version: String,
    @SerializedName("version_latest") val versionLatest: String,
    @SerializedName("installed") val installed: Boolean,
    @SerializedName("available") val available: Boolean,
    @SerializedName("build") val build: Boolean,
    @SerializedName("url") val url: String?,
    @SerializedName("detached") val detached: Boolean,
    @SerializedName("repository") val repository: String,
    @SerializedName("state") val state: String,
    @SerializedName("boot") val boot: String,
    @SerializedName("options") val options: Map<String, Any>,
    @SerializedName("schema") val schema: Map<String, Any>,
    @SerializedName("network") val network: Map<String, Any>?,
    @SerializedName("host_network") val hostNetwork: Boolean,
    @SerializedName("host_pid") val hostPid: Boolean,
    @SerializedName("host_ipc") val hostIpc: Boolean,
    @SerializedName("host_dbus") val hostDbus: Boolean,
    @SerializedName("privileged") val privileged: List<String>,
    @SerializedName("apparmor") val apparmor: String,
    @SerializedName("devices") val devices: List<String>,
    @SerializedName("auto_update") val autoUpdate: Boolean,
    @SerializedName("ingress") val ingress: Boolean,
    @SerializedName("ingress_url") val ingressUrl: String?,
    @SerializedName("ingress_panel") val ingressPanel: Boolean
)

data class AddonsListResponse(
    @SerializedName("data") val data: List<AddonInfo>
)

data class AddonResponse(
    @SerializedName("data") val data: AddonInfo
)

data class AddonStatsResponse(
    @SerializedName("data") val data: AddonStats
)

data class AddonStats(
    @SerializedName("cpu_percent") val cpuPercent: Double,
    @SerializedName("memory_usage") val memoryUsage: Long,
    @SerializedName("memory_limit") val memoryLimit: Long,
    @SerializedName("memory_percent") val memoryPercent: Double,
    @SerializedName("network_rx") val networkRx: Long,
    @SerializedName("network_tx") val networkTx: Long,
    @SerializedName("blk_read") val blkRead: Long,
    @SerializedName("blk_write") val blkWrite: Long
)

// Backup Data Classes
data class BackupInfo(
    @SerializedName("slug") val slug: String,
    @SerializedName("name") val name: String,
    @SerializedName("date") val date: String,
    @SerializedName("type") val type: String,
    @SerializedName("protected") val protected: Boolean,
    @SerializedName("compressed") val compressed: Boolean,
    @SerializedName("location") val location: String?,
    @SerializedName("addons") val addons: List<BackupAddonInfo>,
    @SerializedName("folders") val folders: List<String>,
    @SerializedName("homeassistant") val homeassistant: String,
    @SerializedName("size") val size: Long
)

data class BackupAddonInfo(
    @SerializedName("slug") val slug: String,
    @SerializedName("name") val name: String,
    @SerializedName("version") val version: String
)

data class BackupsListResponse(
    @SerializedName("data") val data: List<BackupInfo>
)

data class BackupResponse(
    @SerializedName("data") val data: BackupInfo
)

data class CreateBackupRequest(
    @SerializedName("name") val name: String?,
    @SerializedName("addons") val addons: List<String>?,
    @SerializedName("folders") val folders: List<String>?,
    @SerializedName("password") val password: String?
)

data class RestoreBackupRequest(
    @SerializedName("addons") val addons: List<String>?,
    @SerializedName("folders") val folders: List<String>?,
    @SerializedName("homeassistant") val homeassistant: Boolean?,
    @SerializedName("password") val password: String?
)

// System Information Data Classes
data class SupervisorInfo(
    @SerializedName("version") val version: String,
    @SerializedName("version_latest") val versionLatest: String,
    @SerializedName("update_available") val updateAvailable: Boolean,
    @SerializedName("channel") val channel: String,
    @SerializedName("arch") val arch: String,
    @SerializedName("supported") val supported: Boolean,
    @SerializedName("healthy") val healthy: Boolean,
    @SerializedName("timezone") val timezone: String,
    @SerializedName("logging") val logging: String,
    @SerializedName("ip_address") val ipAddress: String,
    @SerializedName("wait_boot") val waitBoot: Int,
    @SerializedName("debug") val debug: Boolean,
    @SerializedName("debug_block") val debugBlock: Boolean,
    @SerializedName("addons") val addons: List<AddonInfo>,
    @SerializedName("addons_repositories") val addonsRepositories: List<String>
)

data class SupervisorInfoResponse(
    @SerializedName("data") val data: SupervisorInfo
)

data class CoreInfo(
    @SerializedName("version") val version: String,
    @SerializedName("version_latest") val versionLatest: String,
    @SerializedName("update_available") val updateAvailable: Boolean,
    @SerializedName("machine") val machine: String,
    @SerializedName("ip_address") val ipAddress: String,
    @SerializedName("port") val port: Int,
    @SerializedName("ssl") val ssl: Boolean,
    @SerializedName("watchdog") val watchdog: Boolean,
    @SerializedName("boot_time") val bootTime: Double,
    @SerializedName("state") val state: String
)

data class CoreInfoResponse(
    @SerializedName("data") val data: CoreInfo
)

// Job Data Classes
data class JobInfo(
    @SerializedName("uuid") val uuid: String,
    @SerializedName("name") val name: String,
    @SerializedName("reference") val reference: String?,
    @SerializedName("done") val done: Boolean,
    @SerializedName("child_jobs") val childJobs: List<String>,
    @SerializedName("progress") val progress: Int,
    @SerializedName("stage") val stage: String?,
    @SerializedName("errors") val errors: List<String>
)

data class JobsListResponse(
    @SerializedName("data") val data: List<JobInfo>
)

data class JobResponse(
    @SerializedName("data") val data: JobInfo
)

// Generic API Response
data class ApiResponse(
    @SerializedName("result") val result: String,
    @SerializedName("message") val message: String?
)

/**
 * Retrofit API Interface
 */
interface SupervisorApiService {
    
    // Health and Discovery
    @GET("/api/v1/health")
    suspend fun getHealth(): Response<HealthResponse>
    
    @GET("/api/v1/discovery")
    suspend fun getApiDiscovery(): Response<ApiDiscoveryResponse>
    
    // Add-on Management
    @GET("/api/v1/addons")
    suspend fun getAddons(): Response<AddonsListResponse>
    
    @GET("/api/v1/addons/{slug}")
    suspend fun getAddon(@Path("slug") slug: String): Response<AddonResponse>
    
    @POST("/api/v1/addons/{slug}")
    suspend fun updateAddon(
        @Path("slug") slug: String,
        @Body options: Map<String, Any>
    ): Response<ApiResponse>
    
    @POST("/api/v1/addons/{slug}/install")
    suspend fun installAddon(@Path("slug") slug: String): Response<ApiResponse>
    
    @POST("/api/v1/addons/{slug}/uninstall")
    suspend fun uninstallAddon(@Path("slug") slug: String): Response<ApiResponse>
    
    @POST("/api/v1/addons/{slug}/start")
    suspend fun startAddon(@Path("slug") slug: String): Response<ApiResponse>
    
    @POST("/api/v1/addons/{slug}/stop")
    suspend fun stopAddon(@Path("slug") slug: String): Response<ApiResponse>
    
    @POST("/api/v1/addons/{slug}/restart")
    suspend fun restartAddon(@Path("slug") slug: String): Response<ApiResponse>
    
    @POST("/api/v1/addons/{slug}/update")
    suspend fun updateAddonVersion(@Path("slug") slug: String): Response<ApiResponse>
    
    @GET("/api/v1/addons/{slug}/logs")
    suspend fun getAddonLogs(
        @Path("slug") slug: String,
        @Query("follow") follow: Boolean? = null
    ): Response<ResponseBody>
    
    @GET("/api/v1/addons/{slug}/stats")
    suspend fun getAddonStats(@Path("slug") slug: String): Response<AddonStatsResponse>
    
    // Backup Management
    @GET("/api/v1/backups")
    suspend fun getBackups(): Response<BackupsListResponse>
    
    @POST("/api/v1/backups")
    suspend fun createBackup(@Body request: CreateBackupRequest): Response<ApiResponse>
    
    @GET("/api/v1/backups/{slug}")
    suspend fun getBackup(@Path("slug") slug: String): Response<BackupResponse>
    
    @DELETE("/api/v1/backups/{slug}")
    suspend fun deleteBackup(@Path("slug") slug: String): Response<ApiResponse>
    
    @POST("/api/v1/backups/{slug}/restore/full")
    suspend fun restoreFullBackup(
        @Path("slug") slug: String,
        @Body request: RestoreBackupRequest
    ): Response<ApiResponse>
    
    @POST("/api/v1/backups/{slug}/restore/partial")
    suspend fun restorePartialBackup(
        @Path("slug") slug: String,
        @Body request: RestoreBackupRequest
    ): Response<ApiResponse>
    
    // System Information
    @GET("/api/v1/supervisor/info")
    suspend fun getSupervisorInfo(): Response<SupervisorInfoResponse>
    
    @POST("/api/v1/supervisor/update")
    suspend fun updateSupervisor(): Response<ApiResponse>
    
    @GET("/api/v1/core/info")
    suspend fun getCoreInfo(): Response<CoreInfoResponse>
    
    @POST("/api/v1/core/update")
    suspend fun updateCore(): Response<ApiResponse>
    
    @POST("/api/v1/core/restart")
    suspend fun restartCore(): Response<ApiResponse>
    
    // Job Management
    @GET("/api/v1/jobs")
    suspend fun getJobs(): Response<JobsListResponse>
    
    @GET("/api/v1/jobs/{uuid}")
    suspend fun getJob(@Path("uuid") uuid: String): Response<JobResponse>
}

/**
 * API Result wrapper for handling success/error states
 */
sealed class ApiResult<T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error<T>(val message: String, val code: Int? = null) : ApiResult<T>()
    data class Loading<T>(val message: String = "Loading...") : ApiResult<T>()
}

/**
 * Repository class for API communication
 */
class SupervisorApiRepository(private val apiService: SupervisorApiService) {
    
    companion object {
        private const val TAG = "SupervisorApiRepository"
    }
    
    // Health and Discovery
    suspend fun getHealth(): ApiResult<HealthResponse> {
        return try {
            val response = apiService.getHealth()
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!)
            } else {
                ApiResult.Error("Health check failed", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Health check error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    suspend fun getApiDiscovery(): ApiResult<ApiDiscoveryResponse> {
        return try {
            val response = apiService.getApiDiscovery()
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!)
            } else {
                ApiResult.Error("API discovery failed", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "API discovery error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    // Add-on Management
    suspend fun getAddons(): ApiResult<List<AddonInfo>> {
        return try {
            val response = apiService.getAddons()
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!.data)
            } else {
                ApiResult.Error("Failed to fetch add-ons", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Get add-ons error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    suspend fun getAddon(slug: String): ApiResult<AddonInfo> {
        return try {
            val response = apiService.getAddon(slug)
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!.data)
            } else {
                ApiResult.Error("Failed to fetch add-on: $slug", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Get add-on error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    suspend fun installAddon(slug: String): ApiResult<ApiResponse> {
        return try {
            val response = apiService.installAddon(slug)
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!)
            } else {
                ApiResult.Error("Failed to install add-on: $slug", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Install add-on error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    suspend fun startAddon(slug: String): ApiResult<ApiResponse> {
        return try {
            val response = apiService.startAddon(slug)
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!)
            } else {
                ApiResult.Error("Failed to start add-on: $slug", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Start add-on error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    suspend fun stopAddon(slug: String): ApiResult<ApiResponse> {
        return try {
            val response = apiService.stopAddon(slug)
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!)
            } else {
                ApiResult.Error("Failed to stop add-on: $slug", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Stop add-on error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    // Backup Management
    suspend fun getBackups(): ApiResult<List<BackupInfo>> {
        return try {
            val response = apiService.getBackups()
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!.data)
            } else {
                ApiResult.Error("Failed to fetch backups", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Get backups error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    suspend fun createBackup(request: CreateBackupRequest): ApiResult<ApiResponse> {
        return try {
            val response = apiService.createBackup(request)
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!)
            } else {
                ApiResult.Error("Failed to create backup", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Create backup error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    // System Information
    suspend fun getSupervisorInfo(): ApiResult<SupervisorInfo> {
        return try {
            val response = apiService.getSupervisorInfo()
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!.data)
            } else {
                ApiResult.Error("Failed to fetch supervisor info", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Get supervisor info error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
    
    suspend fun getCoreInfo(): ApiResult<CoreInfo> {
        return try {
            val response = apiService.getCoreInfo()
            if (response.isSuccessful && response.body() != null) {
                ApiResult.Success(response.body()!!.data)
            } else {
                ApiResult.Error("Failed to fetch core info", response.code())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Get core info error", e)
            ApiResult.Error(e.message ?: "Unknown error")
        }
    }
}

/**
 * HTTP Client Builder with SSL support and authentication
 */
object SupervisorApiClient {
    
    private const val DEFAULT_TIMEOUT = 30L // seconds
    
    fun create(
        baseUrl: String,
        authToken: String? = null,
        timeout: Long = DEFAULT_TIMEOUT,
        enableLogging: Boolean = false,
        allowInsecureSSL: Boolean = false
    ): SupervisorApiService {
        
        val okHttpBuilder = OkHttpClient.Builder()
            .connectTimeout(timeout, TimeUnit.SECONDS)
            .readTimeout(timeout, TimeUnit.SECONDS)
            .writeTimeout(timeout, TimeUnit.SECONDS)
        
        // Add authentication interceptor
        if (authToken != null) {
            okHttpBuilder.addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $authToken")
                    .build()
                chain.proceed(request)
            }
        }
        
        // Add logging interceptor for debugging
        if (enableLogging) {
            val loggingInterceptor = HttpLoggingInterceptor { message ->
                Log.d("SupervisorAPI", message)
            }.apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            okHttpBuilder.addInterceptor(loggingInterceptor)
        }
        
        // Allow insecure SSL for development (not recommended for production)
        if (allowInsecureSSL) {
            val trustAllManager = object : X509TrustManager {
                override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) {}
                override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) {}
                override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
            }
            
            val sslContext = SSLContext.getInstance("SSL")
            sslContext.init(null, arrayOf<TrustManager>(trustAllManager), java.security.SecureRandom())
            
            okHttpBuilder.sslSocketFactory(sslContext.socketFactory, trustAllManager)
            okHttpBuilder.hostnameVerifier { _, _ -> true }
        }
        
        val retrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpBuilder.build())
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        
        return retrofit.create(SupervisorApiService::class.java)
    }
}

/**
 * Example ViewModel for UI integration
 */
class SupervisorViewModel(private val repository: SupervisorApiRepository) : ViewModel() {
    
    private val _addons = MutableLiveData<ApiResult<List<AddonInfo>>>()
    val addons: LiveData<ApiResult<List<AddonInfo>>> = _addons
    
    private val _health = MutableLiveData<ApiResult<HealthResponse>>()
    val health: LiveData<ApiResult<HealthResponse>> = _health
    
    private val _backups = MutableLiveData<ApiResult<List<BackupInfo>>>()
    val backups: LiveData<ApiResult<List<BackupInfo>>> = _backups
    
    fun loadAddons() {
        _addons.value = ApiResult.Loading("Loading add-ons...")
        viewModelScope.launch {
            _addons.value = repository.getAddons()
        }
    }
    
    fun checkHealth() {
        _health.value = ApiResult.Loading("Checking health...")
        viewModelScope.launch {
            _health.value = repository.getHealth()
        }
    }
    
    fun loadBackups() {
        _backups.value = ApiResult.Loading("Loading backups...")
        viewModelScope.launch {
            _backups.value = repository.getBackups()
        }
    }
    
    fun startAddon(slug: String) {
        viewModelScope.launch {
            val result = repository.startAddon(slug)
            // Handle result and update UI
            when (result) {
                is ApiResult.Success -> {
                    // Reload add-ons to get updated state
                    loadAddons()
                }
                is ApiResult.Error -> {
                    Log.e("SupervisorViewModel", "Failed to start addon: ${result.message}")
                }
                else -> {}
            }
        }
    }
    
    fun stopAddon(slug: String) {
        viewModelScope.launch {
            val result = repository.stopAddon(slug)
            when (result) {
                is ApiResult.Success -> {
                    loadAddons()
                }
                is ApiResult.Error -> {
                    Log.e("SupervisorViewModel", "Failed to stop addon: ${result.message}")
                }
                else -> {}
            }
        }
    }
    
    fun createBackup(name: String) {
        viewModelScope.launch {
            val request = CreateBackupRequest(name = name, addons = null, folders = null, password = null)
            val result = repository.createBackup(request)
            when (result) {
                is ApiResult.Success -> {
                    loadBackups()
                }
                is ApiResult.Error -> {
                    Log.e("SupervisorViewModel", "Failed to create backup: ${result.message}")
                }
                else -> {}
            }
        }
    }
}