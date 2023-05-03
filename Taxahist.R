# Load the required library
library(ggplot2)
# Read the input file
args <- commandArgs(trailingOnly = TRUE) 
input_file <- read.table(args[1],header=F, sep="\t") # read table
samplename <- args[2] # read sample name
data <- input_file[c(2:8),]
colnames(data) <- c("taxa", "percentage")
# Plot the histogram
ggplot(data, aes(x=taxa, y=percentage)) +
  geom_bar(stat="identity",fill="orange") +
  theme(axis.line = element_line(color="black"), # Add axis lines
panel.grid.major = element_blank(), # Remove major grid lines
panel.grid.minor = element_blank(), # Remove minor grid lines
plot.background = element_rect(fill = "white")
) +
  xlab("Taxa") +
  ylab("Percentage") +
  ggtitle("Percentage distribution of taxa")
ggsave(file=paste0(samplename,"histogram.png"), width = 8, height = 6, units = "in", dpi = 600)
