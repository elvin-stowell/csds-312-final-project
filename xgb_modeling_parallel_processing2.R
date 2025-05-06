library(tidymodels)
library(xgboost)
library(dplyr)
library(doParallel)
library(foreach)

# Load data
model_data_50d_noNA <- readRDS("~/PROJECT/RDS_files/model_data_50d_noNA.rds")

# Ticker-aware split
set.seed(39)
tickers <- unique(model_data_50d_noNA$Ticker)
train_tickers <- sample(tickers, size = floor(0.9 * length(tickers)))
train_data_full <- model_data_50d_noNA %>% filter(Ticker %in% train_tickers)
test_data_full  <- model_data_50d_noNA %>% filter(!Ticker %in% train_tickers)

# Modeling data (drop Ticker/Date for training)
train_data_model <- train_data_full %>% select(-Ticker, -Date)
test_data_model  <- test_data_full %>% select(-Ticker, -Date)

# Sample sizes
sample_sizes <- sort(c(10000, 25000, 50000, 100000, 200000, 300000, 400000, 500000, 750000, 1000000, 1500000))

# Set up parallel backend
n_cores <- parallel::detectCores(logical = FALSE)
cl <- makeCluster(n_cores)
registerDoParallel(cl)

# Parallel loop
foreach(n = sample_sizes, .packages = c("tidymodels", "xgboost", "dplyr")) %dopar% {
  start_time <- Sys.time()
  message(paste0("[", n, "] Started at ", format(start_time, "%H:%M:%S")))
  
  set.seed(124)
  train_subset <- train_data_model %>% slice_sample(n = n)
  
  # Recipe
  xgb_rec <- recipe(Return_50d ~ ., data = train_subset) %>%
    step_zv(all_predictors()) %>%
    step_normalize(all_numeric_predictors())
  
  # Model
  xgb_mod <- boost_tree(trees = 300, learn_rate = 0.1, tree_depth = 6) %>%
    set_engine("xgboost") %>%
    set_mode("regression")
  
  # Workflow
  xgb_wf <- workflow() %>%
    add_model(xgb_mod) %>%
    add_recipe(xgb_rec)
  
  # Fit and predict
  xgb_fit <- fit(xgb_wf, data = train_subset)
  xgb_test_preds <- predict(xgb_fit, new_data = test_data_model) %>%
    bind_cols(test_data_full %>% select(Ticker, Date, Return_50d))
  
  # # Save predictions
  # preds_filename <- paste0("~/PROJECT/model_preds/xgb_new/xgb_test_predictions_", format(n, scientific = FALSE), ".rds")
  # saveRDS(xgb_test_preds, preds_filename)
  # fit_filename <- paste0("~/PROJECT/model_preds/xgb_new/xgb_fit_", format(n, scientific = FALSE), ".rds")
  # saveRDS(xgb_fit, fit_filename)
  # 
  # # Save timing log
  # end_time <- Sys.time()
  # duration <- round(end_time - start_time, 2)
  # log_filename <- paste0("~/PROJECT/runtime_analysis/xgb_new/xgb_model_log_", format(n, scientific = FALSE), ".txt")
  # timing_info <- paste("Sample size:", n,
  #                      "\nStart time:", format(start_time, "%H:%M:%S"),
  #                      "\nEnd time:", format(end_time, "%H:%M:%S"),
  #                      "\nElapsed time:", duration, attr(duration, "units"))
  # writeLines(timing_info, con = log_filename)
  # 
  # message(paste0("[", n, "] Finished at ", format(end_time, "%H:%M:%S"),
  #                " — Duration: ", duration, " ", attr(duration, "units")))
}

stopCluster(cl)
message("All tasks complete.")
