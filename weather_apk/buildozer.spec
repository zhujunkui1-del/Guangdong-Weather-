[app]

# (str) Title of your application
title = GuangdongWeather

# (str) Package name
package.name = weather

# (str) Package domain (needed for android/ios packaging)
package.domain = org.guangdong

# (str) Source code where the main.py live
source.dir = .

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy,urllib3

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 

# (str) Android NDK version to use
#android.ndk = 

# (bool) Use --private data storage
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the SDK/NDK/ANT
# android.skip_update = False

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (int) overrides automatic versionCode computation
# android.numeric_version = 1

# Python for android (p4a) specific

# (str) python-for-android fork to use
#p4a.fork = kivy

# (str) python-for-android branch to use
#p4a.branch = develop

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds
#p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument
#p4a.port =


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage
# build_dir = ./.buildozer

# (str) Path to build output
# bin_dir = ./bin
