[app]
title = Nyx Engine
package.name = nyxengine
package.domain = org.void
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0
requirements = python3, kivy, plyer, google-genai
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, VIBRATE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
