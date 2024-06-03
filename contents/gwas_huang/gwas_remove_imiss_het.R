imiss <- read.table("gwas_example.imiss",header=TRUE)
het <- read.table("gwas_example.het",header=TRUE) 

upplimit <- mean(het$F)+(3*sd(het$F)) 
lowlimit <- mean(het$F)-(3*sd(het$F))

het.remove <- het[which(het$F < lowlimit | het$F > upplimit),c("FID","IID")]
imiss.remove <- imiss[which(imiss$F_MISS > 0.02),c("FID","IID")] 

write.table(rbind(het.remove,imiss.remove) ,"gwas_example.imiss-vs-het.remove", append = FALSE, quote = FALSE, sep = " ", row.names = FALSE, col.names = FALSE)

print("wrote IDs to remove to gwas_example.imiss-vs-het.remove")