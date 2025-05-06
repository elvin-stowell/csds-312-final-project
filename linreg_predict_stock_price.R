library(tidymodels)
library(dplyr)

# Load data
model_data_50d_noNA <- readRDS("~/PROJECT/model_data_50d_noNA.rds")

# Ticker-aware split
set.seed(38)
tickers <- unique(model_data_50d_noNA$Ticker)
train_tickers <- sample(tickers, size = floor(0.9 * length(tickers)))
train_data_full <- model_data_50d_noNA %>% filter(Ticker %in% train_tickers)
test_data_full  <- model_data_50d_noNA %>% filter(!Ticker %in% train_tickers)

# Prepare modeling datasets
train_data_model <- train_data_full %>% select(-Ticker, -Date)
test_data_model  <- test_data_full %>% select(-Ticker, -Date)

# Start timer
start_time <- Sys.time()

# Recipe
lm_rec <- recipe(Return_50d ~ ., data = train_data_model) %>%
  step_zv(all_predictors()) %>%
  step_normalize(all_numeric_predictors())

# Linear model spec
lm_mod <- linear_reg() %>%
  set_engine("lm") %>%
  set_mode("regression")

# Workflow
lm_wf <- workflow() %>%
  add_model(lm_mod) %>%
  add_recipe(lm_rec)

# Fit model
lm_fit <- fit(lm_wf, data = train_data_model)

# Predict on test set
lm_test_preds <- predict(lm_fit, new_data = test_data_model) %>%
  bind_cols(test_data_full %>% select(Ticker, Date, Return_50d))

# Evaluate
results <- metrics(lm_test_preds, truth = Return_50d, estimate = .pred)
print(results)

# Save outputs
saveRDS(lm_fit, "~/PROJECT/model_preds/lm/lm_model_full_train.rds")
saveRDS(lm_test_preds, "~/PROJECT/model_preds/lm/lm_test_predictions_full.rds")

# Save runtime log
end_time <- Sys.time()
duration <- round(end_time - start_time, 2)
log_filename <- "~/PROJECT/runtime_analysis/lm_model_log_full.txt"
timing_info <- paste("Linear model run on full training set",
                     "\nStart time:", format(start_time, "%H:%M:%S"),
                     "\nEnd time:", format(end_time, "%H:%M:%S"),
                     "\nElapsed time:", duration, attr(duration, "units"))
writeLines(timing_info, con = log_filename)

cat("Elapsed time:", duration, attr(duration, "units"), "\n")
