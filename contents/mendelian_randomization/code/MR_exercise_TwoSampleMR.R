####Two Sample MR Exercise#####
####Updated: April 16, 2024#######

##A list of function and their usage can be found here: https://mrcieu.github.io/TwoSampleMR/reference/index.html##

install.packages("remotes")
library(remotes)

remotes::install_github("MRCIEU/TwoSampleMR")
remotes::install_github("MRCIEU/MendelianRandomization")
remotes::install_github("MRCIEU/MRInstruments")

library(TwoSampleMR)
library(MendelianRandomization)
library(ggplot2)
library(data.table)
library(MRInstruments) 


### Part I.1 ###

##Exposure data: IEU GWAS ID ieu-a-300##
exp_dat1 <- extract_instruments(outcomes = 'ieu-a-300')
exp_dat1 <- clump_data(exp_dat1)

##Load OUTCOME data ####
###extracting outcome data
outcome_dat1 <- extract_outcome_data(snps=exp_dat1$SNP, outcomes='ieu-a-7', proxies = 1, rsq = 0.8, align_alleles = 1, palindromes = 1, maf_threshold = 0.3)
outcome_dat1$outcome <- "CHD"
dat1 <- harmonise_data(exp_dat1, outcome_dat1, action = 2)

####MR ANALYSIS####
res1 <- mr(dat1, method_list=c("mr_ivw", "mr_egger_regression", "mr_weighted_median"))
generate_odds_ratios(res1)
p1 <- mr_scatter_plot(res1, dat1)
p1[[1]]

res_single1 <- mr_singlesnp(dat1, all_method = c("mr_ivw", "mr_egger_regression","mr_weighted_median"))
p2 <- mr_forest_plot(res_single1)
p2[[1]]


###SENSITIVITY ANALYSIS
mr_heterogeneity(dat1) # Test for heterogeneity
mr_pleiotropy_test(dat1) # Test for pleiotropy

Part 1.2

################RE-RUN the analysis with MI as the outcome############
#### MI outcome dataset is "ieu-a-798"#######
####Same analysis as above except for extracting the instruments from the new outcome dataset#####

##Exposure data: IEU GWAS ID ieu-a-300##
exp_dat2 <- extract_instruments(outcomes = 'ieu-a-300')
exp_dat2 <- clump_data(exp_dat2)

##Load OUTCOME data ####
###extracting outcome data
outcome_dat2 <- extract_outcome_data(snps=exp_dat2$SNP, outcomes='ieu-a-798', proxies = 1, rsq = 0.8, align_alleles = 1, palindromes = 1, maf_threshold = 0.3)
outcome_dat2$outcome <- "MI"
dat2 <- harmonise_data(exp_dat2, outcome_dat2, action = 2)

####MR ANALYSIS####
res2 <- mr(dat2, method_list=c("mr_ivw", "mr_egger_regression", "mr_weighted_median"))
generate_odds_ratios(res2)
p3 <- mr_scatter_plot(res2, dat2)
p3[[1]]

res_single2 <- mr_singlesnp(dat2, all_method = c("mr_ivw", "mr_egger_regression","mr_weighted_median"))
p4 <- mr_forest_plot(res_single2)
p4[[1]]

###SENSITIVITY ANALYSIS
mr_heterogeneity(dat2) # Test for heterogeneity
mr_pleiotropy_test(dat2) # Test for pleiotropy

### Part II ###

###Import exposure data for all exposures:

data(metab_qtls)

# Define a vector containing the 16 phenotypes
selected_phenotypes <- c("LDL.C", "LDL.D", "S.LDL.C", "S.LDL.L", "S.LDL.P", 
                         "M.LDL.C", "M.LDL.CE", "M.LDL.L", "M.LDL.P", "M.LDL.PL", 
                         "L.LDL.C", "L.LDL.CE", "L.LDL.FC", "L.LDL.L", "L.LDL.P", "L.LDL.PL")

# Subset the data 
metab_exp_dat <- subset(metab_qtls, phenotype %in% selected_phenotypes)
metab_exp_dat <- format_metab_qtls (metab_exp_dat)
metab_exp_dat <- clump_data(metab_exp_dat)

#Outcome data is CHD
outcome_dat3 <- extract_outcome_data(snps=metab_exp_dat$SNP, outcomes='ieu-a-7', proxies = 1, rsq = 0.8, align_alleles = 1, palindromes = 1, maf_threshold = 0.3)
outcome_dat3$outcome <- "CHD"

##HARMONIZE
dat3 <- harmonise_data(metab_exp_dat, outcome_dat3, action = 2)

####MR ANALYSIS####
res3 <- mr(dat3, method_list=c("mr_ivw"))
generate_odds_ratios(res3)
p5 <- mr_scatter_plot(res3, dat3)
p5[1:16]

res_single3 <- mr_singlesnp(dat3, all_method = c("mr_ivw"))
p6 <- mr_forest_plot(res_single3)
p6[1:16]

###SENSITIVITY ANALYSIS
mr_heterogeneity(dat3) # Test for heterogeneity
mr_pleiotropy_test(dat3) # Test for pleiotropy


### Part III ###

###Import exposure data for all exposures:

data(metab_qtls)

# Define a vector containing the 33 phenotypes
selected_phenotypes <- c("L.VLDL.CE", "L.VLDL.C", "L.VLDL.FC", "L.VLDL.L", "L.VLDL.PL", "L.VLDL.P", "L.VLDL.TG", 
                         "M.VLDL.CE", "M.VLDL.C", "M.VLDL.FC", "M.VLDL.L", "M.VLDL.PL", "M.VLDL.P", "M.VLDL.TG",
                         "S.VLDL.C", "S.VLDL.FC", "S.VLDL.L", "S.VLDL.PL", "S.VLDL.P", "S.VLDL.TG", "VLDL.D",
                         "XL.VLDL.L", "XL.VLDL.PL", "XL.VLDL.P", "XL.VLDL.TG", "XS.VLDL.L", "XS.VLDL.PL", "XS.VLDL.P", 
                         "XS.VLDL.TG", "XXL.VLDL.L", "XXL.VLDL.PL", "XXL.VLDL.P", "XXL.VLDL.TG")

# Subset the data 
metab_exp_datVLDL <- subset(metab_qtls, phenotype %in% selected_phenotypes)
metab_exp_datVLDL <- format_metab_qtls (metab_exp_datVLDL)
metab_exp_datVLDL <- clump_data(metab_exp_datVLDL)

#Outcome data is CHD
outcome_dat4 <- extract_outcome_data(snps=metab_exp_datVLDL$SNP, outcomes='ieu-a-7', proxies = 1, rsq = 0.8, align_alleles = 1, palindromes = 1, maf_threshold = 0.3)
outcome_dat4$outcome <- "CHD"

##HARMONIZE
dat4 <- harmonise_data(metab_exp_datVLDL, outcome_dat4, action = 2)

####MR ANALYSIS####

res4 <- mr(dat4, method_list=c("mr_ivw"))
generate_odds_ratios(res4)
p7 <- mr_scatter_plot(res4, dat4)
p7[1:33] 

res_single4 <- mr_singlesnp(dat4, all_method = c("mr_ivw"))
p8 <- mr_forest_plot(res_single4)
p8[1:33]


###SENSITIVITY ANALYSIS
mr_heterogeneity(dat4) # Test for heterogeneity
mr_pleiotropy_test(dat4) # Test for pleiotropy
