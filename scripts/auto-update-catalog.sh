#! /bin/bash
set -e

PATH=/opt/local/bin:/usr/local/bin:$PATH ; export PATH
LD_LIBRARY_PATH=/usr/local/lib:/opt/local/lib ; export LD_LIBRARY_PATH

cd /var/www/html/tde/astrocats
python -m astrocats tidaldisruptions git-pull
python -m astrocats tidaldisruptions import
SNEUPDATE=$?
echo $SNEUPDATE
if [[ $SNEUPDATE == 0 ]]; then
	astrocats/tidaldisruptions/scripts/generate-web.sh
	python -m astrocats tidaldisruptions git-pull
	python -m astrocats tidaldisruptions git-push
	#stamp=$(date +"%Y-%m-%d %k:%M")
	#./commit-and-push-repos.sh "Auto update: $stamp"
fi
