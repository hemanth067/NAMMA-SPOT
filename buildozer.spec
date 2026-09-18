[app]
title = NammaSpot
package.name = nammaspot
package.domain = org.nammaspot
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,json
version = 0.1.0
requirements = python3,kivy,kivymd,requests,kivy_garden.mapview
orientation = portrait
fullscreen = 0

# Android permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

[buildozer]
log_level = 2
warn_on_root = 1
