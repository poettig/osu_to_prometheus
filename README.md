# osu! to prometheus exporter
This tool exports osu! user statistics into prometheus metrics for a specified set of user ids.
Just copy the config.json.template to a new file config.json, fill out the required values and start the program.
A systemd service is provided.

This uses the osu! API v2 with the client credential flow.
Documentation can be found under https://osu.ppy.sh/docs/index.html#client-credentials-grant, you can request a client_id and client_secret on your profile: https://osu.ppy.sh/home/account/edit
