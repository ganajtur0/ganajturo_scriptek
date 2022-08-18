#!/bin/sh

api_url=https://menetrendek.hu/menetrend/interface/index.php

honnan_query=budapest
hova_query=győr

station_query(){
	megallok=$(curl -s -X POST "$api_url" -H 'Content-Type: application/json' -d '{"func":"getStationOrAddrByText","params": { "inputText":"'"$1"'" } }')
	chosen=$(echo "$megallok" | jq '.results[].lsname' | dmenu -l 10)
	echo $( echo "$megallok" | jq '.results[] | select(.lsname=='"$chosen"')' )
}

json_key(){
	echo "$1" | jq '.'"$2"''
}

honnan=$(station_query "$honnan_query")
hova=$(station_query "$hova_query")

curl -s -X POST https://menetrendek.hu/menetrend/interface/index.php -H 'Content-Type: application/json;charset=utf8' -d '{
	"func": "getRoutes",
	"params": {
		"datum":"2022-09-01",
		"erk_stype": "megallo",
		"honnan": '"$(json_key "$honnan" lsname)"',
		"honnan_ls_id": '"$(json_key "$honnan" ls_id)"',
		"honnan_settlement_id": '"$(json_key "$honnan" settlement_id)"',
		"honnan_site_code": '"$(json_key "$honnan" site_code)"',
		"hova": '"$(json_key "$hova" lsname)"',
		"hova_ls_id": '"$(json_key "$hova" ls_id)"',
		"hova_settlement_id": '"$(json_key "$hova" settlement_id)"',
		"hova_site_code": '"$(json_key "$hova" site_code)"',
		"naptipus":"0",
		"hour":69,
		"min":420,
		"preferencia":"0"
	}
}' > sample_megallok.json
