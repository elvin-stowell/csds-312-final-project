# Load libraries
library(tidymodels)
library(kknn)
library(dplyr)

# Load data
full_data <- readRDS("market_cap_fundamentals.rds")

# Standard 80/20 split (not by ticker)
set.seed(42)
split <- initial_split(full_data, prop = 0.8)
train_data_full <- training(split)
test_data_full  <- testing(split)

# Drop ticker and date columns, remove NAs
clean_data <- function(df) {
  df %>%
    select(-ticker, -contains("_date")) %>%
    drop_na()
}

train_data <- clean_data(train_data_full)
test_data  <- clean_data(test_data_full)

# Start timer
start_time <- Sys.time()

# Preprocessing recipe
knn_rec <- recipe(market_cap ~ ., data = train_data) %>%
  step_zv(all_predictors()) %>%
  step_normalize(all_numeric_predictors())

# Model spec
knn_mod <- nearest_neighbor(
  neighbors = 5,
  weight_func = "rectangular"
) %>%
  set_engine("kknn") %>%
  set_mode("regression")

# Workflow
knn_wf <- workflow() %>%
  add_recipe(knn_rec) %>%
  add_model(knn_mod)

# Fit model
knn_fit <- fit(knn_wf, data = train_data)

# Predict and evaluate
knn_preds <- predict(knn_fit, new_data = test_data) %>%
  bind_cols(test_data %>% select(market_cap))

# Evaluate
results <- metrics(knn_preds, truth = market_cap, estimate = .pred)
print(results)

# Save model + predictions
saveRDS(knn_fit, "~/PROJECT/Financials_Analysis/predict_market_cap/knn/knn_market_cap_model.rds")
saveRDS(knn_preds, "~/PROJECT/Financials_Analysis/predict_market_cap/knn/knn_market_cap_predictions.rds")

# End timer
end_time <- Sys.time()
cat("Elapsed time:", round(end_time - start_time, 2), "\n")
