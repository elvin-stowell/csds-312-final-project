library(tidymodels)
library(xgboost)
library(dplyr)
library(doParallel)

# Load full dataset
full_data <- readRDS("market_cap_fundamentals.rds")

# Standard 80/20 random split
set.seed(42)
split <- initial_split(full_data, prop = 0.8)
train_data_full <- training(split)
test_data_full  <- testing(split)

# Remove Ticker and date columns for modeling
to_model <- function(df) {
  df %>% 
    select(-ticker, -contains("_date"))
}

train_data <- to_model(train_data_full)
test_data  <- to_model(test_data_full)

# Track training time
start_time <- Sys.time()

# Recipe
xgb_rec <- recipe(market_cap ~ ., data = train_data) %>%
  step_zv(all_predictors()) %>%
  step_normalize(all_numeric_predictors())

# Model spec
xgb_mod <- boost_tree(
  trees = 300,
  learn_rate = 0.1,
  tree_depth = 6
) %>%
  set_engine("xgboost") %>%
  set_mode("regression")

# Workflow
xgb_wf <- workflow() %>%
  add_model(xgb_mod) %>%
  add_recipe(xgb_rec)

# Fit model
xgb_fit <- fit(xgb_wf, data = train_data)

# Predict and evaluate
xgb_preds <- predict(xgb_fit, new_data = test_data) %>%
  bind_cols(test_data %>% select(market_cap))

results <- metrics(xgb_preds, truth = market_cap, estimate = .pred)
print(results)

# Save model
saveRDS(xgb_fit, "~/PROJECT/Financials_Analysis/predict_market_cap/xgb/xgb_fundamentals_market_cap_model.rds")

# Save predictions
saveRDS(xgb_preds, "~/PROJECT/Financials_Analysis/predict_market_cap/xgb/xgb_fundamentals_market_cap_predictions.rds")

# End time
end_time <- Sys.time()
cat("Elapsed time:", round(end_time - start_time, 2), "\n")
