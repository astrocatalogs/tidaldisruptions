#! /bin/bash
set -e

PATH=/opt/local/bin:/usr/local/bin:$PATH ; export PATH
LD_LIBRARY_PATH=/usr/local/lib:/opt/local/lib ; export LD_LIBRARY_PATH

cd /var/www/html/tde/astrocats
python3.5 -m astrocats.scripts.webcat -c tde &
pids[0]=$!
python3.5 -m astrocats.scripts.webcat -c tde -by &
pids[1]=$!
#python3.5 -m astrocats.tidaldisurptions.scripts.dupecat &
#$pids[2]=$!
#python3.5 -m astrocats.tidaldisurptions.scripts.conflictcat &
#$pids[3]=$!
#python3.5 -m astrocats.tidaldisurptions.scripts.bibliocat &
#$pids[4]=$!
#python3.5 -m astrocats.tidaldisurptions.scripts.erratacat &
#$pids[5]=$!
#python3.5 -m astrocats.tidaldisurptions.scripts.hostcat &
#$pids[6]=$!
#python3.5 -m astrocats.tidaldisurptions.scripts.hammertime &
#$pids[7]=$!
#python3.5 -m astrocats.tidaldisurptions.scripts.histograms &
#$pids[8]=$!
python3.5 -m astrocats.tidaldisurptions.scripts.atelscbetsiaucs &
pids[2]=$!
for pid in ${pids[*]}; do
	wait $pid
done
