#!/usr/bin/env bash
# pixi global mistakenly points the samtools wrapper to samtools.pl, so we need to revert this change
#sed -i "s/samtools.pl/samtools/" /root/.pixi/bin/samtools

# Install & redistribute ANNOVAR for educational purpose, with permission granted by the author of ANNOVAR on April 19, 2024
curl https://www.openbioinformatics.org/annovar/download/0wgxR2rIVP/annovar.latest.tar.gz -o - | tar zxvf - --strip-components=1 -C $HOME/.pixi/bin
