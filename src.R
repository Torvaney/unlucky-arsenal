library(readr)
library(magrittr)
library(dplyr)
library(ggplot2)


plot_positions <- function(data, team_name, team_colour, text_colour) {
  data %>%
    mutate(season = factor(season)) %>%
    filter(name == team_name,
           position > 0) %>%
    mutate(percent_label = sprintf("%1.2f", percent),
           percent_label = ifelse(
             percent_label == "0.00",
             "",
             percent_label
           )) %>%
    ggplot(aes(x = season, y = position)) +
    geom_tile(aes(fill = percent)) +
    geom_text(aes(label = percent_label,
                  colour = percent)) +
    geom_hline(yintercept = 4.5, colour = text_colour) +
    geom_hline(yintercept = 17.5, colour = text_colour) +
    scale_y_reverse(limits = c(21, 0), breaks = seq(20, 1, -1)) +
    scale_x_discrete(position = "top") +
    scale_colour_gradient(low = "white", high = text_colour,
                          limits = c(-0.2, 0.7)) +
    scale_fill_gradient(low = "white", high = team_colour,
                        limits = c(0, 0.7)) +
    theme_minimal() +
    theme(panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          axis.title = element_blank(),
          legend.position = "none")
}


save_blog_and_print <- function(plot, plot_name, plot_width = 20, plot_height = 14, plot_units = "cm") {
  fname <- paste0("figures/blog/", plot_name, ".png")
  
  ggsave(
    filename = fname,
    plot = plot,
    device = "png",
    width = plot_width,
    height = plot_height,
    units = plot_units
  )
  
  print(plot)
}
