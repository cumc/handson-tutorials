#!/bin/bash

mkdir -p $HOME/bin
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
echo -e "#!/bin/bash\n" > $HOME/bin/get-data && chmod +x $HOME/bin/get-data
echo "synapse get -r syn18700992 --downloadLocation $repo_dir/contents" >> $HOME/bin/get-data
#get-data

# Download data-set
BUCKET_ACCESS_KEY=${BUCKET_ACCESS_KEY:-""}
BUCKET_SECRET_KEY=${BUCKET_SECRET_KEY:-""}
AWS_ACCESS_KEY_ID=$BUCKET_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$BUCKET_SECRET_KEY aws s3 sync s3://rockefeller-course/AGIS/ $HOME/handson-tutorials/contents --exclude "*.ipynb"

# Fix plink.multivariate
mv $repo_dir/contents/archive/plink.multivariate $HOME/bin && chmod +x $HOME/bin/plink.multivariate

# Install & redistribute ANNOVAR for educational purpose, with permission granted by the author of ANNOVAR on April 19, 2024
curl https://www.openbioinformatics.org/annovar/download/0wgxR2rIVP/annovar.latest.tar.gz -o - | tar zxvf - --strip-components=1 -C $HOME/bin

cd $HOME/handson-tutorials/contents
jupyter-lab