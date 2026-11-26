package com.example.sih_test_1

import android.Manifest
import android.content.pm.PackageManager
import android.content.Intent
import android.location.LocationManager
import android.net.Uri
import android.os.Build
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private var pendingLocation: MethodChannel.Result? = null
    private val sessionKeyAlias = "virasatai_session_key"

    private fun sessionKey(): SecretKey {
        val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (store.getKey(sessionKeyAlias, null) as? SecretKey)?.let { return it }
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        generator.init(KeyGenParameterSpec.Builder(sessionKeyAlias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build())
        return generator.generateKey()
    }

    private fun saveSession(value: String): Boolean {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, sessionKey())
        val payload = cipher.iv + cipher.doFinal(value.toByteArray(Charsets.UTF_8))
        return getSharedPreferences("virasatai_session", MODE_PRIVATE).edit()
            .putString("encrypted", Base64.encodeToString(payload, Base64.NO_WRAP)).commit()
    }

    private fun readSession(): String? {
        val prefs = getSharedPreferences("virasatai_session", MODE_PRIVATE)
        val encoded = prefs.getString("encrypted", null) ?: return null
        return try {
            val payload = Base64.decode(encoded, Base64.NO_WRAP)
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.DECRYPT_MODE, sessionKey(), GCMParameterSpec(128, payload.copyOfRange(0, 12)))
            String(cipher.doFinal(payload.copyOfRange(12, payload.size)), Charsets.UTF_8)
        } catch (_: Exception) {
            prefs.edit().remove("encrypted").commit()
            null
        }
    }

    private fun fetchLocation(result: MethodChannel.Result) {
        val manager = getSystemService(LOCATION_SERVICE) as LocationManager
        val provider = when {
            checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED &&
                manager.isProviderEnabled(LocationManager.GPS_PROVIDER) -> LocationManager.GPS_PROVIDER
            manager.isProviderEnabled(LocationManager.NETWORK_PROVIDER) -> LocationManager.NETWORK_PROVIDER
            else -> null
        }
        if (provider == null) {
            result.error("LOCATION_OFF", "Turn on phone location", null)
            return
        }
        if (Build.VERSION.SDK_INT >= 30) {
            manager.getCurrentLocation(provider, null, mainExecutor) { location ->
                if (location == null) result.error("NO_FIX", "Could not get current location", null)
                else result.success(mapOf("latitude" to location.latitude,
                    "longitude" to location.longitude, "accuracyM" to location.accuracy.toDouble()))
            }
        } else {
            val location = manager.getLastKnownLocation(provider)
            if (location == null) result.error("NO_FIX", "Could not get current location", null)
            else result.success(mapOf("latitude" to location.latitude,
                "longitude" to location.longitude, "accuracyM" to location.accuracy.toDouble()))
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 701) {
            val result = pendingLocation ?: return
            pendingLocation = null
            if (grantResults.any { it == PackageManager.PERMISSION_GRANTED }) fetchLocation(result)
            else result.error("LOCATION_DENIED", "Location permission denied", null)
        }
    }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "virasatai/session")
            .setMethodCallHandler { call, result ->
                try {
                    when (call.method) {
                        "read" -> result.success(readSession())
                        "write" -> {
                            val value = call.arguments as? String
                            if (value == null) result.error("INVALID_DATA", "Expected session", null)
                            else if (saveSession(value)) result.success(null)
                            else result.error("SAVE_FAILED", "Could not save session", null)
                        }
                        "clear" -> {
                            getSharedPreferences("virasatai_session", MODE_PRIVATE)
                                .edit().remove("encrypted").commit()
                            result.success(null)
                        }
                        else -> result.notImplemented()
                    }
                } catch (_: Exception) {
                    result.error("SESSION_STORAGE", "Could not access saved session", null)
                }
            }
        val preferences = getSharedPreferences("virasatai_reports", MODE_PRIVATE)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "virasatai/reports")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "read" -> result.success(preferences.getString("pending", "[]"))
                    "location" -> {
                        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED ||
                            checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
                            fetchLocation(result)
                        } else if (preferences.getBoolean("location_permission_asked", false)) {
                            result.error("LOCATION_DENIED", "Enable location permission in phone settings", null)
                        } else {
                            preferences.edit().putBoolean("location_permission_asked", true).apply()
                            pendingLocation = result
                            requestPermissions(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION,
                                Manifest.permission.ACCESS_COARSE_LOCATION), 701)
                        }
                    }
                    "write" -> {
                        val value = call.arguments as? String
                        if (value == null) result.error("INVALID_DATA", "Expected text", null)
                        else {
                            val saved = preferences.edit().putString("pending", value).commit()
                            if (saved) result.success(null)
                            else result.error("SAVE_FAILED", "Could not save report draft", null)
                        }
                    }
                    else -> result.notImplemented()
                }
            }
        val reviewPreferences = getSharedPreferences("virasatai_reviews", MODE_PRIVATE)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "virasatai/reviews")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "read" -> result.success(reviewPreferences.getString("pending", "[]"))
                    "write" -> {
                        val value = call.arguments as? String
                        if (value == null) result.error("INVALID_DATA", "Expected text", null)
                        else if (reviewPreferences.edit().putString("pending", value).commit()) result.success(null)
                        else result.error("SAVE_FAILED", "Could not save review", null)
                    }
                    else -> result.notImplemented()
                }
            }
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "virasatai/maps")
            .setMethodCallHandler { call, result ->
                if (call.method != "open") {
                    result.notImplemented()
                    return@setMethodCallHandler
                }
                val query = call.argument<String>("query")?.trim()
                if (query.isNullOrEmpty()) {
                    result.error("INVALID_QUERY", "A place name is required", null)
                    return@setMethodCallHandler
                }
                try {
                    val intent = Intent(Intent.ACTION_VIEW,
                        Uri.parse("geo:0,0?q=${Uri.encode(query)}"))
                    startActivity(intent)
                    result.success(null)
                } catch (_: Exception) {
                    result.error("MAP_UNAVAILABLE", "No maps application is available", null)
                }
            }
    }
}
