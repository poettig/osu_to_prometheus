import json
import logging
import time

import requests

from prometheus_client import start_http_server, Gauge

BASEURL = "https://osu.ppy.sh"
API_PATH = "/api/v2"
API_URL = f"{BASEURL}{API_PATH}"

labels = ["user_id", "username"]
gauges = {
	"total_hits": Gauge("osu_total_hitobjects_hit", "Total number of hitobjects hit by the user on maps with a leaderboard.", labels),
	"play_count": Gauge("osu_playcount", "Number of plays done by the user, including fails and retries, on a map with a leaderboard.", labels),
	"ranked_score": Gauge("osu_ranked_score", "Total of every best score achieved by the user on a map with a leaderboard.", labels),
	"total_score": Gauge("osu_total_score", "Total of every score achieved by the user on a map with a leaderboard.", labels),
	"global_rank": Gauge("osu_rank", "Rank of the user on the global pp leaderboard.", labels),
	"country_rank": Gauge("osu_rank_country", "Rank of the user on the country-based pp leaderboard.", labels),
	"level": Gauge("osu_level", "The level of the user.", labels),
	"pp": Gauge("osu_pp", "The pp score of the user.", labels),
	"hit_accuracy": Gauge("osu_accuracy", "The accuracy of the user averaged over all plays, better plays are weighted more (like with pp).", labels),
	"grade_counts_ss": Gauge("osu_ss_count", "The number of SS plays achieved by the user.", labels),
	"grade_counts_ssh": Gauge("osu_ss_modded_count", "The number of modded SS plays achieved by the user.", labels),
	"grade_counts_s": Gauge("osu_s_count", "The number of S plays achieved by the user.", labels),
	"grade_counts_sh": Gauge("osu_s_modded_count", "The number of modded S plays achieved by the user.", labels),
	"grade_counts_a": Gauge("osu_a_count", "The number of A plays achieved by the user.", labels),
	"play_time": Gauge("osu_total_seconds_played", "The total number of seconds the user was actively playing a map.", labels),
}


def get_token(config):
	response = requests.post(
		f"{BASEURL}/oauth/token",
		json={
			"client_id": config["client_id"],
			"client_secret": config["client_secret"],
			"grant_type": "client_credentials",
			"scope": "public"
		}
	)

	if response.status_code != 200:
		raise ValueError("Failed to fetch token.")

	return response.json()["access_token"]


def main():
	logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
	with open("config.json", "r") as fh:
		config = json.load(fh)

	start_http_server(config["port"])
	access_token = get_token(config)

	while True:
		for user_id in config["user_ids"]:
			response = requests.get(
				f"{API_URL}/users/{user_id}/osu",
				headers={"Authorization": f"Bearer {access_token}"},
				params={"key": "id"}
			)

			if response.status_code != 200:
				logging.warning(f"Failed to fetch user info for user id {user_id}: {response.status_code} - {response.content.decode('utf-8')}")

			# Convert stats to workable format
			data = response.json()
			stats = data["statistics"]
			stats["level"] = stats["level"]["current"]
			for key, value in stats["grade_counts"].items():
				stats[f"grade_counts_{key}"] = value

			for key, value in stats.items():
				if key in gauges:
					gauges[key].labels(user_id=data["id"], username=data["username"]).set(value)

			logging.info(f"Update for user {data['username']} ({user_id}) completed.")

		time.sleep(config["refresh_interval_seconds"])


if __name__ == "__main__":
	main()
