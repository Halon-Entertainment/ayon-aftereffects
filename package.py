name = "aftereffects"
title = "AfterEffects"
# Halon fork of ynput/ayon-aftereffects (forked from 0.2.12; merged upstream 0.3.5 via ENG-4877)
version = "1.1.0-halon.2"
app_host_name = "aftereffects"
client_dir = "ayon_aftereffects"
project_can_override_addon_version = True

ayon_server_version = ">=1.1.2"
ayon_required_addons = {
    "core": ">=1.8.0",
}
ayon_compatible_addons = {
    "deadline": ">=0.7.0",
}
