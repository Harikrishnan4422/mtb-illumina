library(ggplot2)

# Read the input file
args <- commandArgs(trailingOnly = TRUE)
input_file <- read.table(args[1], header = FALSE, sep = "\t")
samplename <- args[2]
data <- input_file[c(2:7), ]
colnames(data) <- c("Taxa", "percentage")
data$Taxa <- factor(data$Taxa, levels = c("Archaea", "Bacteria", "Fungi", "Homo sapiens", "Viruses", "Unclassified"))
ggplot(data, aes(x = Taxa, y = percentage)) +
  geom_bar(stat = "identity", fill = "orange", width = 0.5) +
  theme(
    axis.line = element_line(color = "black"),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    plot.background = element_rect(fill = "white"),
    axis.text.x = element_text(size = 17, color = "black", margin = margin(0.15, 0, 0, 0, "cm")),   # Set x-axis text
    axis.text.y = element_text(size = 17, color = "black"),   # Set y-axis text
    axis.title.x = element_text(size = 19, face = "bold", margin = margin(0.3, 0, 0, 0, "cm")),    # Adjust size and font weight for x-axis label
    axis.title.y = element_text(size = 19, face = "bold", margin = margin(0, 0.3, 0, 0, "cm"))     # Adjust size and font weight for y-axis label
  ) +
  xlab("Taxa") +
  ylab("Percentage of read density")
# Save the plot
ggsave(
  file = paste0(samplename, "histogram.png"),
  width = 10.5,
  height = 6,
  units = "in",
  dpi = 600)
