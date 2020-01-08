#! /bin/bash
set -e

PATH=/opt/local/bin:/usr/local/bin:$PATH ; export PATH
LD_LIBRARY_PATH=/usr/local/lib:/opt/local/lib ; export LD_LIBRARY_PATH

cd /var/www/html/tde/astrocats
python -m astrocats.scripts.webcat -c tde &
pids[0]=$!
python -m astrocats.scripts.webcat -c tde -by &
pids[1]=$!
#python -m astrocats.tidaldisruptions.scripts.dupecat &
#$pids[2]=$!
#python -m astrocats.tidaldisruptions.scripts.conflictcat &
#$pids[3]=$!
python -m astrocats.scripts.bibliocat -c tde &
pids[2]=$!
#python -m astrocats.tidaldisruptions.scripts.erratacat &
#$pids[5]=$!
python -m astrocats.scripts.hostcat -c tde &
pids[3]=$!
python -m astrocats.scripts.hammertime -c tde &
pids[4]=$!
#python -m astrocats.tidaldisruptions.scripts.histograms &
#$pids[8]=$!
python -m astrocats.scripts.atelscbetsiaucs -c tde &
pids[5]=$!
for pid in ${pids[*]}; do
	wait $pid
done
cd /var/www/html/tde/astrocats/astrocats/tidaldisruptions/output/html
bash thumbs.sh
cd /var/www/html/tde/astrocats
