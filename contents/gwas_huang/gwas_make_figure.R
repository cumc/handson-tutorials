assoc_adj <- read.table("gwas_example_final.assoc.logistic",header=TRUE)

assoc_adj_final <- assoc_adj[which(!is.na(assoc_adj$P)& !is.na(assoc_adj$OR)& !is.na(assoc_adj$STAT)),]

assoc_adj_final_sig<- assoc_adj_final[assoc_adj_final[,12]<0.00000005,] 
print(assoc_adj_final_sig)

assoc_adj_final_sug<- assoc_adj_final[assoc_adj_final[,12]<0.00001,] 

library(qqman) 
pdf("assoc_adj_final.manhattan.pdf")
manhattan(assoc_adj_final,main = "Manhattan Plot", ylim = c(0, 10)) 
dev.off()

pdf("assoc_adj_final.qq.pdf") 
qq(assoc_adj_final$P,main = "Q-Q Plot", ylim = c(0, 10)) 
dev.off()

print (paste("lambd gc:", median((assoc_adj_final$ STAT)^2)/qchisq(0.5, 1, low=F)))


