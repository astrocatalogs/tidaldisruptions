#! /bin/bash
set -e

PATH=/opt/local/bin:/usr/local/bin:$PATH ; export PATH
LD_LIBRARY_PATH=/usr/local/lib:/opt/local/lib ; export LD_LIBRARY_PATH

cd /var/www/html/tde/astrocats
python3.5 -m astrocats.scripts.webcat -c tde &
pids[0]=$!
python3.5 -m astrocats.scripts.webcat -c tde -by &
pids[1]=$!
#python3.5 -m astrocats.tidaldisruptions.scripts.dupecat &
#$pids[2]=$!
#python3.5 -m astrocats.tidaldisruptions.scripts.conflictcat &
#$pids[3]=$!
#python3.5 -m astrocats.tidaldisruptions.scripts.bibliocat &
#$pids[4]=$!
#python3.5 -m astrocats.tidaldisruptions.scripts.erratacat &
#$pids[5]=$!
python3.5 -m astrocats.scripts.hostcat -c tde &
pids[2]=$!
python3.5 -m astrocats.scripts.hammertime -c tde &
pids[3]=$!
#python3.5 -m astrocats.tidaldisruptions.scripts.histograms &
#$pids[8]=$!
python3.5 -m astrocats.tidaldisruptions.scripts.atelscbetsiaucs &
pids[4]=$!
for pid in ${pids[*]}; do
	wait $pid
done
