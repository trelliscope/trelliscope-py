library(trelliscope)
library(tidyverse)
library(gapminder)
 
# Grammar of graphics
 panel_dat <- (ggplot(gapminder, aes(year, lifeExp)) +
   geom_point() +
   facet_panels(~country + continent)) |>
   nest_panels() 

 
 # grammar of wrangling
 meta_dat <- gapminder|>
   group_by(country, continent) |>
   summarise(
     mean_lifeexp = mean(lifeExp),
     min_lifeexp = min(lifeExp),
     max_lifeexp = max(lifeExp),
     mean_gdp = mean(gdpPercap),
     first_year = min(year),
     latitude = first(latitude),
     longitude = first(longitude),
     .groups = "drop"
   ) |>
   ungroup() |>
   mutate(
     first_date = as.Date(paste0(first_year, "-01-01")),
     first_datetime = as.POSIXct.Date(first_date),
     continent = as.factor(continent),
     wiki_link = paste0("https://en.wikipedia.org/wiki/", country)
   )
 
 joined_dat <- left_join(panel_dat, meta_dat, 
                         by = join_by(country, continent))

 # grammar of dashboard
 trell <- joined_dat |>
   as_trelliscope_df(name = "gapminder") |>
   write_panels() |>
   write_trelliscope()
   view_trelliscope()