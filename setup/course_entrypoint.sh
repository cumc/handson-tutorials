#!/bin/bash

repo_dir=handson-tutorials
BUCKET_ACCESS_KEY=${BUCKET_ACCESS_KEY:-""}
BUCKET_SECRET_KEY=${BUCKET_SECRET_KEY:-""}

cd /root/

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

# Sync the contents directory
AWS_ACCESS_KEY_ID=$BUCKET_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$BUCKET_SECRET_KEY aws s3 sync s3://opcenter-bucket-ada686a0-ccdb-11ee-b922-02ebafc2e5cf/tutorial_data /root/handson-tutorials/contents --exclude "annovar_software/*"


# Sync the annovar software
AWS_ACCESS_KEY_ID=$BUCKET_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$BUCKET_SECRET_KEY aws s3 sync s3://opcenter-bucket-ada686a0-ccdb-11ee-b922-02ebafc2e5cf/annovar_software/ /usr/local/bin --exclude "*" --include "*.pi"
chmod +x /usr/local/bin/*.pl

# Fix plink.multivariate
mv /root/handson-tutorials/contents/misc/plink.multivariate /usr/local/bin && chmod +x /usr/local/bin/plink.multivariate
