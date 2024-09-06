#!/bin/bash

repo_dir=`pwd`/handson-tutorials

# Clone GitHub repo
cd && git clone https://github.com/cumc/handson-tutorials.git

# Download external resources
mkdir -p $repo_dir/contents/ldpred2
curl -o "$repo_dir/contents/ldpred2/ldpred.ipynb" https://raw.githubusercontent.com/cumc/bioworkflows/master/ldpred/ldpred.ipynb
curl -o "$repo_dir/contents/ldpred2/ldpred2_example.ipynb" https://raw.githubusercontent.com/cumc/bioworkflows/master/ldpred/ldpred2_example.ipynb

mkdir -p $repo_dir/contents/archive/clumping
curl -o "$repo_dir/contents/archive/clumping/clumping.ipynb" https://raw.githubusercontent.com/cumc/bioworkflows/master/GWAS/LD_Clumping.ipynb

mkdir -p $repo_dir/contents/ngs_qc_annotation/
mkdir -p $repo_dir/contents/ngs_qc_annotation/pipelines
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/VCF_QC.ipynb" https://raw.githubusercontent.com/cumc/xqtl-protocol/main/code/data_preprocessing/genotype/VCF_QC.ipynb
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/genotype_formatting.ipynb" https://raw.githubusercontent.com/cumc/xqtl-protocol/main/code/data_preprocessing/genotype/genotype_formatting.ipynb
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/GWAS_QC.ipynb" https://raw.githubusercontent.com/cumc/xqtl-protocol/main/code/data_preprocessing/genotype/GWAS_QC.ipynb
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/PCA.ipynb" https://raw.githubusercontent.com/cumc/xqtl-protocol/main/code/data_preprocessing/genotype/PCA.ipynb
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/annovar.ipynb" https://raw.githubusercontent.com/cumc/bioworkflows/master/variant-annotation/annovar.ipynb

# Remove outputs from notebooks
mkdir -p ~/.parallel && touch ~/.parallel/will-cite
find "$repo_dir/contents" -type f -name "*.ipynb" | parallel -j $(nproc) "jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace {}"

# Prepare the get-data command
ln -s $repo_dir/setup/.synapseConfig $HOME/.synapseConfig
echo -e "#!/bin/bash\n" > $HOME/.pixi/bin/get-data && chmod +x $HOME/.pixi/bin/get-data
echo "synapse get -r syn18700992 --downloadLocation $repo_dir/contents" >> $HOME/.pixi/bin/get-data
#get-data

# Sync necessary resources: annovar software and data
BUCKET_ACCESS_KEY=${BUCKET_ACCESS_KEY:-""}
BUCKET_SECRET_KEY=${BUCKET_SECRET_KEY:-""}
# (AWS_ACCESS_KEY_ID=$BUCKET_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$BUCKET_SECRET_KEY aws s3 sync s3://gao-851725442056/AGIS/annovar_software/ $HOME/.pixi/bin --exclude "*" --include "*.pl" && chmod +x $HOME/.pixi/bin/*.pl) || (echo -e "\033[1;31mWarning: Cannot install ANNOVAR program due to license restriction. Exercise involving ANNOVAR annotations will not work unless you manually install ANNOVAR to $HOME/.pixi/bin folder of the tutorials.\033[0m" && true)
# Sync the handout directory
AWS_ACCESS_KEY_ID=$BUCKET_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$BUCKET_SECRET_KEY aws s3 sync s3://rockefeller-course/AGIS/ $HOME/handson-tutorials/contents --exclude "*.ipynb"

# Fix plink.multivariate
mv $repo_dir/contents/archive/plink.multivariate $HOME/.pixi/bin && chmod +x $HOME/.pixi/bin/plink.multivariate

# Fix an issue with jupyter_client version for docker image built on June 24, 2024 --- a lower version was installed by default because of an issue with sos-notebook setup.py at this point
micromamba install -n python_libs jupyter_client=8.6.2 -y
# Fix an issue with LDSC conda package as of June 2024, by creating separate environment
micromamba create -f $repo_dir/contents/chicago_hgen471/data/lab7/ldsc/environment.yml -y
# Fix an issue with metaxcan conda package as of June 2024, by creating separate environment
micromamba create -f $repo_dir/contents/chicago_hgen471/data/lab7/imlabtools.yaml -y
