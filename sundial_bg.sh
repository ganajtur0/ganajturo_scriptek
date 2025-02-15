#!/usr/bin/bash

. SETTINGS.sh

now=$(date +%s)
sunset=$(date --date="$(./sundial --lat="$latitude" --lon="$longitude" --sunset)" +%s)

if [ "$now" -ge "$sunset" ]; then
	feh --no-fehbg --bg-fill "$wp_nt" &
else
	feh --no-fehbg --bg-fill "$wp_dt" &
fi
