source("src.R")

sim_positions <- read_csv("data/positions.csv")

for (team in unique(sim_positions$name)) {
  plot <- plot_positions(sim_positions, team, "gray20", "black") +
    ggtitle(team)
  
  ggsave(paste0("figures/", team, ".png"), width = 20, height = 20, units = "cm")
}
