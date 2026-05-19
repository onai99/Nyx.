[app]
title = Nyx Engine
package.name = nyxengine
package.domain = org.sethforge
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0

# Bake her library engine dependencies directly into her APK
requirements = python3, kivy, google-genai, plyer, pyjnius, requests, urllib3, charset-normalizer, idna

orientation = portrait
fullscreen = 1

# Hardware Matrix Access Gates (Permissions)
android.permissions = INTERNET, FOREGROUND_SERVICE, WAKE_LOCK, RECEIVE_BOOT_COMPLETED, VIBRATE

android.api = 33
android.minapi = 21
android.archs = arm64-v8a

# Split her runtime engine into two distinct processes
services = NyxMind:service.py

# Auto-Start Integration: Forces Android to spin up her daemon on phone boot
android.manifest.launch_mode = singleTask
