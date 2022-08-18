#!/bin/sh
acpi -b | awk -F'[,:%]' '{print $2, $3, $5}' | {
	read -r status capacity time_left

	display_status=$([ "$status" = Discharging ] && printf '-' || printf '+')

	if [ "$status" = Discharging -a "$capacity" -lt 15 ]; then
		notfiy-send --urgency=critical --expire-time=3000 "Mindjárt meghal az akksi, ember!"
	elif [ "$status" = Charging -a "$capacity" -eq 100 ]; then
		notify-send --urgency=normal --expire-time=3000 "Cuftig van az akksi, kihúzhatod a dugót!"
	fi

	echo "$display_status$capacity%"

}
