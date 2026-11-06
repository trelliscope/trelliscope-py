# Writes the R reference files that test_r_compatibility.py compares against.
# Run from the repo root with the trelliscope R package installed:
#   Rscript trelliscope/tests/external_data/r_reference/make_reference.R
# Generated with trelliscope 0.1.14.
library(trelliscope)

ref_dir <- "trelliscope/tests/external_data/r_reference"
out <- tempfile()
info <- tempfile(fileext = ".html")
writeLines("<h1>Reference info</h1>", info)

df <- data.frame(
  species = c("setosa", "versicolor", "virginica"),
  n = c(50, 50, 50),
  panel = panel_url(c(
    "https://example.com/a.png",
    "https://example.com/b.png",
    "https://example.com/c.png"
  ))
)

disp <- df |>
  as_trelliscope_df(name = "ref", path = out, key_cols = "species") |>
  set_default_layout(ncol = 2, sidebar = TRUE, visible_filters = c("species", "n")) |>
  set_info_html(info) |>
  set_theme(primary = "#c80000") |>
  add_inputs(
    input_text("notes", label = "Notes"),
    input_radio("flag", options = c("yes", "no")),
    input_number("score", min = 0, max = 10),
    email = "someone@example.com",
    vars = c("species")
  )
write_trelliscope(disp)

file.copy(file.path(out, "config.jsonp"), ref_dir, overwrite = TRUE)
file.copy(file.path(out, "displays", "ref", "displayInfo.jsonp"), ref_dir,
  overwrite = TRUE)
