#!/bin/bash

repo_dir=handson-tutorials
BUCKET_ACCESS_KEY=${BUCKET_ACCESS_KEY:-""}
BUCKET_SECRET_KEY=${BUCKET_SECRET_KEY:-""}

cd

# Clone GitHub repo
git clone https://github.com/cumc/handson-tutorials.git

# Download external resources
mkdir -p $repo_dir/contents/ldpred2
curl -o "$repo_dir/contents/ldpred2/ldpred.ipynb" https://raw.githubusercontent.com/cumc/bioworkflows/master/ldpred/ldpred.ipynb
curl -o "$repo_dir/contents/ldpred2/ldpred2_example.ipynb" https://raw.githubusercontent.com/cumc/bioworkflows/master/ldpred/ldpred2_example.ipynb

mkdir -p $repo_dir/contents/clumping
curl -o "$repo_dir/contents/clumping/clumping.ipynb" https://raw.githubusercontent.com/cumc/bioworkflows/master/GWAS/LD_Clumping.ipynb

mkdir -p $repo_dir/contents/ngs_qc_annotation/
mkdir -p $repo_dir/contents/ngs_qc_annotation/pipelines
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/VCF_QC.ipynb" https://raw.githubusercontent.com/cumc/xqtl-protocol/main/code/data_preprocessing/genotype/VCF_QC.ipynb
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/genotype_formatting.ipynb" https://raw.githubusercontent.com/cumc/xqtl-protocol/main/code/data_preprocessing/genotype/genotype_formatting.ipynb
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/GWAS_QC.ipynb" https://raw.githubusercontent.com/cumc/xqtl-protocol/main/code/data_preprocessing/genotype/GWAS_QC.ipynb
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/PCA.ipynb" https://raw.githubusercontent.com/cumc/xqtl-protocol/main/code/data_preprocessing/genotype/PCA.ipynb
curl -o "$repo_dir/contents/ngs_qc_annotation/pipelines/annovar.ipynb" https://raw.githubusercontent.com/cumc/bioworkflows/master/variant-annotation/annovar.ipynb

# Remove outputs from notebooks
find "$repo_dir/contents" -type f -name "*.ipynb" | parallel -j $(nproc) "jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace {}"


# Sync the contents directory
AWS_ACCESS_KEY_ID=$BUCKET_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$BUCKET_SECRET_KEY aws s3 sync s3://opcenter-bucket-ada686a0-ccdb-11ee-b922-02ebafc2e5cf/tutorial_data /root/handson-tutorials/contents

# Sync the annovar software
(AWS_ACCESS_KEY_ID=$BUCKET_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$BUCKET_SECRET_KEY aws s3 sync s3://opcenter-bucket-ada686a0-ccdb-11ee-b922-02ebafc2e5cf/annovar_software/ /usr/local/bin --exclude "*" --include "*.pl" && chmod +x /usr/local/bin/*.pl) || (echo -e "\033[1;31mWarning: Cannot install ANNOVAR program due to license restriction. Exercise involving ANNOVAR annotations will not work unless you manually install ANNOVAR to the /usr/local/bin folder of the tutorials.\033[0m" && true)

# Fix plink.multivariate
mv /root/handson-tutorials/contents/archive/plink.multivariate /usr/local/bin && chmod +x /usr/local/bin/plink.multivariate
